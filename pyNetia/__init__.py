"""
Netia Player
By Jakub Orasiński
KudlatyWORKSHOP.com

Changelog:
- v.0.0.1 initial release
- v.0.0.2 app support, play media, select source
- v.0.1.0 homekit fix, class rename, netia_req_json rename, added SUPPORTED_APPS list, get_key refactor
- v.0.1.1 updated SUPPORTED_APPS list
- v.0.1.2 updated SUPPORTED_APPS list, code reformated
- v.0.1.3 strings cleanup, url reformat, minor fixes

"""

import time
import json
import logging
import requests

TIMEOUT_INTERNAL = 10  # timeout for internal requests (in seconds)
TIMEOUT_EXTERNAL = 60  # timeout for external requests (in seconds)

URL_STATE = "/Main/State/get"
URL_VOLUME = "/RemoteControl/Volume/get"
URL_KEY = "/RemoteControl/KeyHandling/sendKey?key="

URL_CHANNEL_LIST = "/Live/Channels/getList"
URL_CHANNEL_CURRENT = "/Live/Channels/getCurrent"
URL_CHANNEL_DETAILS = "/EPG/Programs/getRange?channelId="
URL_CHANNEL_IMAGE = "/EPG/Programs/getImage?channelId="

URL_APPLICATION_LIST = "/Applications/State/get"
URL_APPLICATION_OPEN = "/Applications/Lifecycle/open?appId="

URL_NETIA_EPG_LOGO = "http://epg.dms.netia.pl/xmltv/logo/black/"

AVAILABLE_KEYS = [
    "1",
    "2",
    "3",
    "4",
    "5",
    "6",
    "7",
    "8",
    "9",
    "0",
    "on_off",
    "mute",
    "volume_up",
    "volume_down",
    "channel_up",
    "channel_down",
    "back",
    "fullscreen",
    "menu",
    "up",
    "down",
    "left",
    "right",
    "ok",
    "play",
    "stop",
    "prev",
    "next",
    "rec",
    "guide",
    "delete",
    "red",
    "green",
    "yellow",
    "blue",
]

SUPPORTED_APPS = [
    "tv",
    "epg",
    "settings",
    "mediacenter",
    "hbogo",
    "kinoplex",
    "ninateka",
    "ipla",
    "abcvod",
    "premiumplus",
    "npvr",
    "goon",
    "netiatvshop",
    "psp",
    "filmbox",
    "tvnplayer",
    "netiacloud",
    "tubafm",
    "tvnmeteo",
    "tvpsport",
    "pinkvision",
    "erowizja",
    "ksw",
    "youtube",
]

_LOGGER = logging.getLogger(__name__)

_VERSION = "0.1.3"


class PyNetia(object):
    def __init__(self, host, port):
        """Initialize the Netia Player class."""
        self._host = host
        self._port = port
        self._url = f"http://{self._host}:{self._port}"
        self._available_keys = AVAILABLE_KEYS
        self._supported_apps = SUPPORTED_APPS
        self._application_list = {}

    def netia_set(self, url, content, log_errors=True):
        """Send key command via HTTP to Netia Player."""
        return_value = None
        if content is None:
            return False
        else:
            try:
                response = requests.post(
                    f"{self._url}{url}{content}", timeout=TIMEOUT_INTERNAL,
                )
            except requests.exceptions.HTTPError as exception_instance:
                if log_errors:
                    _LOGGER.error("HTTPError: %s", exception_instance)
            except requests.exceptions.Timeout as exception_instance:
                if log_errors:
                    _LOGGER.error("Timeout occurred: %s", exception_instance)
            except Exception as exception_instance:  # pylint: disable=broad-except
                if log_errors:
                    _LOGGER.error("Exception: %s", exception_instance)
            else:
                return_value = response.content
        return return_value

    def netia_req(self, url, log_errors=True):
        """ Send request via HTTP json to Netia Player."""
        return_value = None
        try:
            request = requests.get(f"{self._url}{url}", timeout=TIMEOUT_INTERNAL,)
        except requests.exceptions.HTTPError as exception_instance:
            if log_errors:
                _LOGGER.error("HTTPError: %s", exception_instance)
        except requests.exceptions.Timeout as exception_instance:
            if log_errors:
                _LOGGER.error("Timeout occurred: %s", exception_instance)
        except Exception as exception_instance:  # pylint: disable=broad-except
            if log_errors:
                _LOGGER.error("Exception: %s", exception_instance)
        else:
            if request.status_code == 200:
                return_value = json.loads(request.content.decode("utf-8"))
                if return_value is None and log_errors:
                    _LOGGER.error(
                        "Invalid response: %s, request path: %s", return_value, url
                    )
        return return_value

    def send_command(self, command):
        """Sends a command to the TV."""
        self.netia_set(URL_KEY, self.get_key(command))

    def get_app_list(self):
        """Get list of apps from device."""
        return_value = []
        resp = self.netia_req(URL_APPLICATION_LIST, True)
        if resp is not None:
            for i in range(len(resp)):
                app = resp[i]
                if app.get("id") in SUPPORTED_APPS:
                    if app.get("id") == "youtube":
                        app["name"] = "YouTube"
                    if app.get("name") is None:
                        app["name"] = "Unknown app"
                    return_value.append(app)
        return return_value

    def get_app_info(self):
        """Get information on app that is currently open."""
        return_value = {}
        resp = self.get_app_list()
        if resp is not None:
            self._application_list = resp
            for app in resp:
                if app.get("current") is True:
                    if app.get("id") in ["tv", "settings", "epg"]:
                        return_value["id"] = "tv"
                        return_value["name"] = "TV"
                        return_value["image"] = None
                    else:
                        return_value["id"] = app.get("id")
                        return_value["name"] = app.get("name")
                        return_value["image"] = self.get_app_picture(app.get("id"))
            if len(return_value) is 0:
                return_value["id"] = "tv"
                return_value["name"] = "TV"
                return_value["image"] = None
        return return_value

    @staticmethod
    def get_app_picture(app, log_errors=True):
        """Get application picture from Netia server."""
        url = f"{URL_NETIA_EPG_LOGO}{app}_290x172px.png"
        if app is None:
            return False
        else:
            try:
                response = requests.post(url, timeout=TIMEOUT_EXTERNAL)
            except requests.exceptions.HTTPError as exception_instance:
                if log_errors:
                    _LOGGER.error("HTTPError: %s", exception_instance)
            except requests.exceptions.Timeout as exception_instance:
                if log_errors:
                    _LOGGER.error("Timeout occurred: %s", exception_instance)
            except Exception as exception_instance:  # pylint: disable=broad-except
                if log_errors:
                    _LOGGER.error("Exception: %s", exception_instance)
            else:
                if response.status_code == 200:
                    return url

    def get_channel_info(self):
        """Get information on program that is shown on TV."""
        return_value = {}
        channel = self.netia_req(URL_CHANNEL_CURRENT, True)
        if channel is not None:
            return_value["id"] = channel.get("id")
            return_value["media_channel"] = channel.get("zap")
            return_value["channel_name"] = channel.get("name")
            return_value[
                "image"
            ] = f"{self._url}{URL_CHANNEL_IMAGE}{requests.utils.quote(channel.get('id'))}"
        else:
            return_value = None
        return return_value

    def get_channel_details(self, channel):
        """Get information on program that is shown on TV."""
        return_value = {}
        channel_id = requests.utils.quote(channel)
        timestamp = str(time.time())
        details_url = f"{URL_CHANNEL_DETAILS}{channel_id}&startTime={timestamp}&endTime={timestamp}"
        channel_details = self.netia_req(details_url, True)
        if channel_details is not None:
            channel_details = channel_details[0]
            return_value["media_channel"] = channel_details.get("channelZap")
            return_value["channel_name"] = channel_details.get("channelName")
            return_value["program_name"] = channel_details.get("name")
            return_value["program_media_type"] = channel_details.get("subcategory")
            return_value["media_episode"] = channel_details.get("episodeInfo")
            return_value["sound_mode"] = channel_details.get("audio")
            return_value["duration"] = channel_details.get("duration")
            return_value["start_time"] = channel_details.get("startTime")
            return_value["end_time"] = channel_details.get("endTime")
            return_value["image"] = f"{self._url}{channel_details.get('image')}"
        else:
            return_value = None
        return return_value

    def get_standby_status(self):
        """Get standby status: on, off."""
        return_value = "on"  # by default the Netia Player is in standby mode
        try:
            resp = self.netia_req(URL_STATE, False)
            if resp.get("standby") is False:
                return_value = "off"
            else:
                return_value = "on"
        except ConnectionError:  # pylint: disable=broad-except
            pass
        return return_value

    def get_key(self, key_name):
        """Check if key is available."""
        for key in self._available_keys:
            if key == key_name:
                return key
        return None

    def get_volume_info(self):
        """Get volume info."""
        resp = self.netia_req(URL_VOLUME, True)
        if not resp.get("error"):
            result = resp
            return result
        else:
            _LOGGER.error("JSON data error: %s", json.dumps(resp, indent=4))
        return None

    def available_keys(self):
        return self._available_keys

    def application_list(self):
        return self._application_list

    def supported_apps(self):
        return self._supported_apps

    def open_app(self, app):
        """Play content by URI."""
        self.netia_set(URL_APPLICATION_OPEN, app, False)

    def volume_up(self):
        """Volume up the media player."""
        self.netia_set(URL_KEY, self.get_key("volume_up"))

    def volume_down(self):
        """Volume down media player."""
        self.netia_set(URL_KEY, self.get_key("volume_down"))

    def mute_volume(self):
        """Send mute command."""
        self.netia_set(URL_KEY, self.get_key("mute"))

    def turn_on(self):
        """Turn the media player on."""
        self.netia_set(URL_KEY, self.get_key("on_off"))

    def turn_off(self):
        """Turn the media player off."""
        self.netia_set(URL_KEY, self.get_key("on_off"))

    def media_play(self):
        """Send play command."""
        self.netia_set(URL_KEY, self.get_key("play"))

    def media_pause(self):
        """Send media pause command to media player."""
        self.netia_set(URL_KEY, self.get_key("pause"))

    def media_stop(self):
        """Send media pause command to media player."""
        self.netia_set(URL_KEY, self.get_key("stop"))

    def media_next_track(self):
        """Send next track command."""
        self.netia_set(URL_KEY, self.get_key("channel_up"))

    def media_previous_track(self):
        """Send the previous track command."""
        self.netia_set(URL_KEY, self.get_key("channel_down"))
