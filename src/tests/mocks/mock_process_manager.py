from musical_chairs_libs.dtos_and_utilities import OSProcessManager


class MockOSProcessManager(OSProcessManager):

	def __init__(self, mockProcId: int) -> None:
			self.mockProcId = mockProcId

	def getpid(self) -> int:
		oldId = self.mockProcId
		self.mockProcId += 1
		return oldId

	def end_process(self, procId: int) -> None:
		pass