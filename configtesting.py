import configparser, os

config_obj = configparser.ConfigParser()
config_obj.read("DuplicatorConfig.cfg")
defaultpath = config_obj["default_output"]
files_needed = config_obj["files_to_look_for"]
print("Repair ticket is inside: ", os.path.isfile("D:/vdspc_image_vone/AXI-EZLEONG-NB[@$@]2022-08-11-08-31-30"+"/"+files_needed["VDSPC"]))