# encoding: utf-8
import sys
from pprint import pformat
from typing import TYPE_CHECKING

from future.utils import iteritems

from . import base

if TYPE_CHECKING:

    class settings(object):  # try pleasing linters 🤔
        ACTIVITY_DEFAULT_VERSION = ""  # type: str
        ACTIVITY_DEFAULT_TASK_LIST = ""  # type: str
        ACTIVITY_START_TO_CLOSE_TIMEOUT = ""  # type: str
        ACTIVITY_SCHEDULE_TO_CLOSE_TIMEOUT = ""  # type: str
        ACTIVITY_SCHEDULE_TO_START_TIMEOUT = ""  # type: str
        ACTIVITY_HEARTBEAT_TIMEOUT = ""  # type: str
        METROLOGY_BUCKET = ""  # type: str
        METROLOGY_PATH_PREFIX = ""  # type: str
        SIMPLEFLOW_S3_HOST = ""  # type: str
        SIMPLEFLOW_S3_SSE = ""  # type: str
        WORKFLOW_DEFAULT_DECISION_TASK_TIMEOUT = ""  # type: str


def put_setting(key, value):
    setattr(sys.modules[__name__], key, value)
    _keys.add(key)


def configure(dct):
    for k, v in iteritems(dct):
        put_setting(k, v)


def print_settings():
    for key in sorted(_keys):
        value = getattr(sys.modules[__name__], key)
        print("{}={}".format(key, pformat(value)))


# initialize a list of settings names
_keys = set()

# look for settings and initialize them
configure(base.load())
