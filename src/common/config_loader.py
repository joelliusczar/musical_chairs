import yaml
import os


def get_config():
    config_path = os.environ["radio_config"]

    config = None

    with open(config_path,"r") as stream:
        config =  yaml.safe_load(stream)
    return config

def get_http_config():
    config_path = os.environ["http_config"]

    with open(config_path,"r") as stream:
        config =  yaml.safe_load(stream)
    return config