import logging as builtin_logging



formatter = builtin_logging.Formatter("%(asctime)s %(message)s")

handler = builtin_logging.FileHandler("musical_chairs.log", encoding="utf-8")
debugOnlyhandler = builtin_logging.FileHandler(
	"musical_chairs-debug.log",
	encoding="utf-8"
)

handler.setFormatter(formatter)
debugOnlyhandler.setFormatter(formatter)

logger = builtin_logging.getLogger("mc")
debugLogger = builtin_logging.getLogger("mc.debug")

logger.setLevel(builtin_logging.INFO)
debugLogger.setLevel(builtin_logging.DEBUG)

logger.addHandler(handler)
debugLogger.addHandler(debugOnlyhandler)



