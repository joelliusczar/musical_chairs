import yaml
import os

def get_config():
    configPath = ''
    if 'radio_config' in os.environ:
        configPath = os.environ['radio_config']
    else:
        configPath = 'src/configs/config.yml'

    config = None

    with open(configPath,'r') as stream:
        config =  yaml.safe_load(stream)
    return config