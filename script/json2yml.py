import json
import yaml
import pprint

with open('send_pic.json') as f:
    content = f.read()
ss = yaml.load(content)
print(ss)
