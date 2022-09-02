import configparser, os

config_obj = configparser.ConfigParser(interpolation = None)
config_obj.read("DuplicatorConfig.cfg")
#defaultpath = dict(config_obj.items("query"))
queries = config_obj["query"]
print(queries['q1'])