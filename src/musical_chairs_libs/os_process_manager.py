import os

class OSProcessManager:

	def getpid(self) -> int:
		return os.getpid()

	def end_process(self, procId: int) -> None:
		try:
			os.kill(procId, 15)
		except:
			pass