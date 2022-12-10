import logging



formatter = logging.Formatter("%(asctime)s %(message)s")

handler = logging.FileHandler("musical_chairs.log", encoding="utf-8")
debugOnlyhandler = logging.FileHandler(
	"musical_chairs-debug.log",
	encoding="utf-8"
)

handler.setFormatter(formatter)
debugOnlyhandler.setFormatter(formatter)

logger = logging.getLogger("mc")
debugLogger = logging.getLogger("mc.debug")

logger.setLevel(logging.INFO)
debugLogger.setLevel(logging.DEBUG)

logger.addHandler(handler)
debugLogger.addHandler(debugOnlyhandler)



