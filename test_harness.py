import sys
from musical_chairs_libs.config_loader import ConfigLoader
from musical_chairs_libs.queue_service import QueueService
from musical_chairs_libs.station_service import StationService
from musical_chairs_libs.radio_handle import RadioHandle




if __name__ == '__main__':
	print(sys.prefix)
	handle = RadioHandle("vg")
	res = handle.ices_get_next()
	display = handle.ices_get_metadata()
	print("done")

