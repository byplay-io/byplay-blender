import time
import json

from byplay.backend.async_post import async_post
from byplay.backend.sys_info import sys_info
from byplay.config import Config


class AmplitudeLogger:
    def __init__(self, api_key, api_uri="https://api.amplitude.com/httpapi"):
        self.api_key = api_key
        self.api_uri = api_uri
        self.is_logging = True

    def turn_on_logging(self):
        self.is_logging = True

    def turn_off_logging(self):
        self.is_logging = False

    def _is_None_or_not_str(self, value):
        if value is None or type(value) is not str:
            return True

    def create_event(self, **kwargs):
        event = {}
        user_id = kwargs.get('user_id', None)
        device_id = kwargs.get('device_id', None)
        if self._is_None_or_not_str(user_id) and self._is_None_or_not_str(device_id):
            return None

        if self._is_None_or_not_str(user_id):
            event["device_id"] = device_id
        else:
            event["user_id"] = user_id

        event_type = kwargs.get('event_type', None)
        if self._is_None_or_not_str(event_type):
            return None

        event["event_type"] = event_type

        # integer epoch time in milliseconds
        if "time" in kwargs:
            event["time"] = kwargs["time"]
        else:
            event["time"] = int(time.time() * 1000)

        if "ip" in kwargs:
            event["ip"] = kwargs["ip"]

        event_properties = kwargs.get('event_properties', None)
        if event_properties is not None and type(event_properties) == dict:
            event["event_properties"] = event_properties

        sys = sys_info()
        event["platform"] = "Houdini plugin"
        event["os_name"] = sys["os.name"]
        event["os_version"] = sys["os.version"]
        event["app_version"] = "houdini-plugin:{}".format(Config.build())
        event["device_model"] = "houdini:{}:{}".format(sys["houdini.version"], sys["houdini.platform"])

        event_package = [
            ('api_key', self.api_key),
            ('event', json.dumps([event])),
        ]

        # print(event_package)

        # ++ many other properties
        # details: https://amplitude.zendesk.com/hc/en-us/articles/204771828-HTTP-API
        return event_package


    def log_event(self, event):
        if event is not None and type(event) == list:
            if self.is_logging:
                result = async_post(self.api_uri, data=event)
                return result


AMPLITUDE = AmplitudeLogger(api_key="5e18757a01b9d84a19dfddb7f0835a28")


def log_amplitude(event_type, **props):
    global AMPLITUDE
    if Config.mute_amplitude():
        return
    AMPLITUDE.log_event(
        AMPLITUDE.create_event(
            device_id="blender-plugin",
            event_type=event_type,
            user_id=Config.user_id(),
            event_properties=props
        )
    )
