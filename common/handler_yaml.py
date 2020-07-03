import yaml


def read_yaml(yaml_path):
    with open(yaml_path, encoding='UTF-8') as f:
        return yaml.load(f, Loader=yaml.SafeLoader)


def write_yaml(data, yaml_path):
    with open(yaml_path, 'w', encoding='UTF-8') as f:
        yaml.dump(data, f)
