import json
import logging as builtin_logging
from datetime import datetime, timezone
from logging import config, Formatter, Filter
from typing import Any, Optional, override, Union
from .config_accessors import ConfigAcessors

LOG_RECORD_BUILTIN_ATTRS = {
    "args",
    "asctime",
    "created",
    "exc_info",
    "exc_text",
    "filename",
    "funcName",
    "levelname",
    "levelno",
    "lineno",
    "module",
    "msecs",
    "message",
    "msg",
    "name",
    "pathname",
    "process",
    "processName",
    "relativeCreated",
    "stack_info",
    "thread",
    "threadName",
    "taskName",
}

api_log_level = ConfigAcessors.api_log_level()
radio_log_level = ConfigAcessors.radio_log_level()

class JsonFormatter(Formatter):

	def __init__(
		self, 
		*,
		fmt_keys: Optional[dict[str, str]]=None
	):
		super().__init__()
		self.fmt_keys = fmt_keys if fmt_keys is not None else {}

	@override
	def format(self, record: builtin_logging.LogRecord) -> str:
		entry = self.__prepare_log_dict__(record)
		return json.dumps(entry)
	
	def __prepare_log_dict__(self, record: builtin_logging.LogRecord):
		alwaysFields = {
			"message": record.message,
			"timestamp": datetime.fromtimestamp(
				record.created,
				tz=timezone.utc
			).isoformat()
		}

		if record.exc_info is not None:
			alwaysFields["exc_info"] = self.formatException(record.exc_info)

		if record.stack_info is not None:
			alwaysFields["stack_info"] = self.formatStack(record.stack_info)

		entry = {
			key: getattr(record, val) for key, val in self.fmt_keys.items()
				if hasattr(record, val)
		}

		entry.update(alwaysFields)

		for key, val in record.__dict__.items():
			if key not in LOG_RECORD_BUILTIN_ATTRS:
				entry[key] = val

		return entry


class InfoOnlyFilter(Filter):

	def filter(
		self,
		record: builtin_logging.LogRecord
	) -> Union[bool,builtin_logging.LogRecord]:
		return record.levelno < builtin_logging.WARNING
	

our_config: dict[str, Any] = {
	"version": 1,
	"disable_existing_loggers": False,
	"filters": {},
	"formatters": {
		"boring": {
			"format": "[%(asctime)s][%(name)%][%(levelname)s][%(filename)s: "+
				"%(funcName)s]: %(message)s"
		},
		"json": {
			"()": JsonFormatter,
			"fmt_keys": {
				"level": "levelname",
				"message": "message",
				"timestamp": "timestamp",
				"logger": "name",
				"module": "module",
				"function": "funcName",
				"line": "lineno",
				"thread_name": "threadname"
			}
		},
		"queue": {
			"format": "Queue: [%(asctime)s]: %(message)s"
		}
	},
	"handlers": {
		"boring": {
			"class": "logging.handlers.RotatingFileHandler",
			"level": api_log_level,
			"formatter": "boring",
			"filename": "musical_chairs.log",
			"maxBytes": 10000,
      "backupCount": 3
		},
		"json": {
			"class": "logging.handlers.RotatingFileHandler",
			"level": api_log_level,
			"formatter": "json",
			"filename": "musical_chairs.jsonl",
			"maxBytes": 10000,
      "backupCount": 3
		},
		"stdout": {
      "class": "logging.StreamHandler",
      "formatter": "boring",
      "stream": "ext://sys.stdout"
    },
		"stderr": {
      "class": "logging.StreamHandler",
      "formatter": "boring",
      "stream": "ext://sys.stderr"
    }
	},
	"filters": {
		"infoOnly": {
			"class": "InfoOnlyFilter"
		}
	},
	"loggers": {
		"root": {
			"level": "DEBUG",
			"handlers": [
				"json"
			]
		},
		"radio": {
			"level": radio_log_level,
			"handlers": [
				"json"
			]
		},
		"api": {
			"level": api_log_level,
			"handlers": [
				"json"
			]
		},
		"scheduled": {
			"handlers": [
				"json"
			]
		},
	}
}


config.dictConfig(config=our_config)

radioLogger = builtin_logging.getLogger("radio")
logger = builtin_logging.getLogger("api")
queueLogger = builtin_logging.getLogger("radio.queue")
scheduledServiceLogger = builtin_logging.getLogger("scheduled")



