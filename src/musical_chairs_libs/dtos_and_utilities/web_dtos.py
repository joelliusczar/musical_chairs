
class TrackingInfo:
	
	def __init__(
			self,
			userAgent: str="",
			ipv6Address: str="",
			ipv4Address: str=""
		) -> None:
		self.userAgent = userAgent
		self.ipv6Address = ipv6Address
		self.ipv4Address = ipv4Address
