import sys
import os

def test_show_path():
	print(os.environ['PYTHONPATH'])
	print(sys.path)