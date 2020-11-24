import logging
import sys
import time
import traceback
from datetime import datetime

import random

from byplay.backend.async_post import async_post
from byplay.backend.sys_info import sys_info
from byplay.config import Config


def generate_random_key(length):
    return ''.join(random.choice('0123456789abcdef') for _ in range(length))


STORE_URL = "https://o244219.ingest.sentry.io/api/5530947/store/"
AUTH = """Sentry sentry_version=7,
sentry_timestamp={timestamp},
sentry_key=7c3247f0e9614dd0a853f2ac89e4505d,
sentry_client=byplay-blender-python/1.0""".replace("\n", "")


def _try_user_id():
    try:
        return Config.user_id()
    except Exception as e:
        print(e)
        logging.error(e)
        return "[unk]"


def capture_exception():
    logging.info("Capturing exception")
    exc_type, exc_value, exc_traceback = sys.exc_info()
    logging.error(exc_value)
    try:
        payload = {
            'event_id': generate_random_key(32),
            'platform': 'python',
            'culpit': '-',
            'timestamp': str(datetime.utcnow()),
            'dist': Config.build(),
            'tags': sys_info(),
            'user': {
                'id': _try_user_id(),
            },
            "exception": {
                "values": [{
                    "type": exc_type.__name__,
                    "value": ", ".join(exc_value.args),
                    "stacktrace": {
                        "frames": list(
                            map(
                                lambda f: {
                                    'filename': f[0],
                                    'lineno': f[1] + 1,
                                    'function': f[2]
                                },
                                traceback.extract_tb(exc_traceback)
                            )
                        )
                    }
                }]
            }
        }
        async_post(
            STORE_URL,
            headers={"X-Sentry-Auth": AUTH.format(timestamp=int(time.time()))},
            json=payload
        )
    except Exception as sending_exception:
        print(sending_exception)
        # raise sending_exception
        logging.error(sending_exception)