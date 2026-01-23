from dataclasses import dataclass
from typing import Optional
from .account_dtos import UserRoleDomain

@dataclass
class EventRecord:
	id: str
	userId: str
	action: str
	userAgentId: Optional[int]
	timestamp: float
	path: Optional[str]
	domain: str = UserRoleDomain.Site.value
	extraInfo: str=""
