import logging as builtin_logging
import sys
import os

api_log_level = os.environ.get(
	"MCR_API_LOG_LEVEL",
	""
) or builtin_logging.getLevelName(builtin_logging.WARNING)
radio_log_level = os.environ.get(
	"MCR_RADIO_LOG_LEVEL",
	""
) or builtin_logging.getLevelName(builtin_logging.WARNING)


formatter = builtin_logging.Formatter(
	"[%(asctime)s][%(levelname)s][%(filename)s: %(funcName)s]: %(message)s"
)


handler = builtin_logging.FileHandler(
	"musical_chairs.log",
	encoding="utf-8"
)

handler.setFormatter(formatter)


logger = builtin_logging.getLogger("mc")


logger.setLevel(api_log_level)
logger.addHandler(handler)



radioLogger = builtin_logging.getLogger("mc_radio")
radioLogger.setLevel(radio_log_level)

radioDefaultHandler = builtin_logging.FileHandler(
	"musical_chairs_radio.log",
	encoding="utf-8"
)
radioDefaultHandler.setFormatter(formatter)
radioDefaultHandler.setLevel(radio_log_level)

stdOutHandler = builtin_logging.StreamHandler(sys.stderr)
stdOutHandler.setFormatter(formatter)
stdOutHandler.addFilter(
	lambda record: record.levelno < builtin_logging.WARNING
)

stdErrHandler = builtin_logging.StreamHandler(sys.stderr)
stdErrHandler.setFormatter(formatter)
stdErrHandler.setLevel(builtin_logging.WARNING)

radioLogger.addHandler(stdOutHandler)
radioLogger.addHandler(stdErrHandler)
radioLogger.addHandler(radioDefaultHandler)

queueLogger = builtin_logging.getLogger("mc_radio.queue")
queueHandler = builtin_logging.FileHandler(
	"musical_chairs_queue.log",
	encoding="utf-8"
)
queueHandler.setFormatter(
	builtin_logging.Formatter(
		"Queue: [%(asctime)s]: %(message)s"
	)
)
queueLogger.addHandler(queueHandler)
# queueLogger.addHandler(stdOutHandler)
# queueLogger.addHandler(stdErrHandler)
# queueLogger.addHandler(radioDefaultHandler)

