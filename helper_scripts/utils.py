import yaml


def load_yaml_file(config_file_name):
    config_string = f"./config/{config_file_name}"
    with open(config_string) as file:
        config = yaml.full_load(file)
    return config
