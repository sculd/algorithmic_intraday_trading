import yaml

def load(filename):
    with open(filename, 'r') as ymlfile:
        cfg = yaml.load(ymlfile, Loader=yaml.FullLoader)
    return cfg

def get_positionsize(cfg):
    return int(cfg['trading']['positionsize'])

