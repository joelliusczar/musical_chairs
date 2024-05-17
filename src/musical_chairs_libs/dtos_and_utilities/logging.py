import logging as builtin_logging
import sys



formatter = builtin_logging.Formatter(
	"[%(asctime)s][%(levelname)s]: %(message)s"
)
	

handler = builtin_logging.FileHandler(
	"musical_chairs.log",
	encoding="utf-8"
)

handler.setFormatter(formatter)


logger = builtin_logging.getLogger("mc")


logger.setLevel(builtin_logging.INFO)
logger.addHandler(handler)



radioLogger = builtin_logging.getLogger("mc_radio")
radioLogger.setLevel(builtin_logging.DEBUG)

radioDefaultHandler = builtin_logging.FileHandler(
	"musical_chairs_radio.log",
	encoding="utf-8"
)
radioDefaultHandler.setFormatter(formatter)
radioDefaultHandler.setLevel(builtin_logging.DEBUG)

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

