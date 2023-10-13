import sys
from .local_file_src_stream import send_data as send_data_from_local
from .common_stream_helpers import get_station_id


if __name__ == "__main__":
	streamSource = sys.argv[1]
	dbName = sys.argv[2]
	stationName = sys.argv[3]
	ownerName = sys.argv[4]
	stationId = get_station_id(stationName, ownerName, dbName)
	if not stationId:
		raise RuntimeError(
			"station with owner"
			f" {ownerName} and name {stationName} not found"
		)


	if streamSource == "local":
		send_data_from_local(stationId, dbName)
	else:
		raise RuntimeError("unsupported option used for stream source")

