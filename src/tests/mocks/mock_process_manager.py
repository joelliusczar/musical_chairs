from musical_chairs_libs.services import ProcessService
from musical_chairs_libs.dtos_and_utilities import check_name_safety

class MockOSProcessManager(ProcessService):

	def __init__(self, mockProcId: int) -> None:
			self.mockProcId = mockProcId

	def getpid(self) -> int:
		oldId = self.mockProcId
		self.mockProcId += 1
		return oldId

	def end_process(self, procId: int) -> None:
		pass

	def startup_station(self, stationName: str) -> None:
		m = check_name_safety(stationName)
		if m:
			raise RuntimeError("Invalid station name was used")