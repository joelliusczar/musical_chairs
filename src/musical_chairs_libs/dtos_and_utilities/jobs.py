from typing import Optional
from .generic_dtos import (
	FrozenIdItem,
)

class JobInfo(FrozenIdItem):
	jobtype: str
	status: Optional[str]
	instructions: str
	queuedtimestamp: float
	completedtimestamp: Optional[float]