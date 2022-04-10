#!/usr/bin/python3
import yaml
from yamlinclude import YamlIncludeConstructor

YamlIncludeConstructor.add_to_loader_class(loader_class=yaml.FullLoader, base_dir='./')

def extends_list(list):
    extended_list =  []
    for each in list:
        extended_list.extend(each)

    return extended_list


with open('application/wm260/factory.yaml') as f:
    data = yaml.load(f, Loader=yaml.FullLoader)

extended_list = extends_list(data)

print(extended_list)