from dataclasses import dataclass
from starlette.datastructures import URL

@dataclass
class TrackingInfo:
	url: URL
	userAgent: str=""
	ipv6Address: str=""
	ipv4Address: str=""
	method: str=""