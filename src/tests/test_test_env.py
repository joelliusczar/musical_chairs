import sys
import os

def test_show_path():
	print(os.environ['PYTHONPATH'])
	print(sys.path)

def test_print_schema():
	from musical_chairs_libs.services import EnvManager
	EnvManager.print_expected_schema()