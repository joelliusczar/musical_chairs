from dataclasses import dataclass

@dataclass
class TrackingInfo:
	userAgent: str=""
	ipv6Address: str=""
	ipv4Address: str=""