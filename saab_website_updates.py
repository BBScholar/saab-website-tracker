#! /bin/python3


import yaml 
import sys
import time
import requests
from requests.auth import HTTPBasicAuth
import os
import difflib

var_path = "/var/lib/saab/"


def setup_fs():
    if os.path.exists(var_path) and not os.path.isfile(var_path):
        return;
    print("{} does not existing, making directory now...", var_path)
    os.mkdir(var_path)

def send_email(email, recipiants, message, class_name):
    msg = f"echo \"{message}\" | mutt -e \"my_hdr From:{email}\" -s \"Saab Website Updated -- {class_name}\" -- " 
    for i in recipiants:
        msg = msg + i
    os.system(msg)
    
def main(config_file):
    
    with open(config_file, "r") as file:
        config = yaml.safe_load(file)
    print(config)


    default_headers = {
        "User-Agent": "Mozilla/5.0"
    };
    

    email = config["system"]["email"]
    for x in config["sites"]:
        url = config["sites"][x]["url"]
        username = config["sites"][x]["user"]
        password = config["sites"][x]["password"]

        new_req = requests.get(url, auth=HTTPBasicAuth(username, password), headers=default_headers)
        print(new_req.headers)
        new_modified = new_req.headers["last-modified"]
        print(new_modified)
        new_data = new_req.content
        # print(new_data)

        old_fn_prevmod = var_path + f"{x}_prevmod"
        old_fn_data = var_path + f"{x}_prevdata"

        if os.path.exists(old_fn_prevmod) and os.path.isfile(old_fn_prevmod):
            with open(old_fn_prevmod, 'r') as f:
                old_modified = f.read()

            if False and old_modified == new_modified:
                continue
            else:
                # read previous data file 
                with open(old_fn_data, "r") as f:
                    old_data = f.read()

                # take diff between files
                new_lines = str(new_data).split("\\n");
                old_lines = old_data.split("\\n");
                
                print(new_lines)
                print(sys.stdout.writelines(difflib.unified_diff(new_lines, old_lines, fromfiledate=new_modified, tofiledate=old_modified)))
                # send email 

                # rewrite data file
                with open(old_fn_prevmod, "w") as f:
                    f.write(new_modified)

                # rewrite last modified file 
                with open(old_fn_data, "w") as f:
                    f.write(str(new_data))
        else:
            with open(old_fn_prevmod, "w") as f:
                f.write(new_modified)
            with open(old_fn_data, "w") as f:
                f.write(str(new_data))


        # print(new_file.contents)


if __name__ == "__main__":
    args = len(sys.argv) - 1
    if(args < 1):
        print("Must enter config file")
        exit(1)
    setup_fs()
    main(sys.argv[1])
