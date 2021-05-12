import yaml
import os


def get_config():
    config_path = ""
    if "radio_config" in os.environ:
        config_path = os.environ["radio_config"]
    else:
        config_path = "../configs/config.yml"

    config = None

    with open(config_path,"r") as stream:
        config =  yaml.safe_load(stream)
    return config

def get_http_config():
    config_path = ""
    if "http_config" in os.environ:
        config_path = os.environ["http_config"]
    else:
        config_path = "../configs/web_config.yml"

    config = configparser.ConfigParser()

    with open(config_path,"r") as stream:
        config =  yaml.safe_load(stream)
    return config