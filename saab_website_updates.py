#! /bin/python3

import os, sys, time
from datetime import datetime
import yaml
import pprint
import requests
from requests.auth import HTTPBasicAuth
import difflib


default_message = """
{class_code} site updated!
Our lord and savior Dr. Daniel Saab has updated the course site. 
See changes at {url}

Here is the diff:
{diff}
"""

default_headers = {
    "User-Agent": "Mozilla/5.0"
};


def setup_fs(var_path):
    if os.path.exists(var_path) and not os.path.isfile(var_path):
        return;
    print("{} does not exist, creating directory now...", var_path)
    os.mkdir(var_path)

def send_discord_message(hook_url, ping_id, message):
    s = ""
    if ping_id is not None:
        s += f"<@&{ping_id}>\n"
    s += message
    
    data= {
        "content": s
    }
    
    requests.post(hook_url, data=data)

def write_new_files(mod_fn, data_fn, mod, data):
        with open(mod_fn, "w") as f:
            f.write(mod)

        with open(data_fn, "w") as f:
            f.write(data)


def main(config_file):
    with open(config_file, "r") as file:
        config = yaml.safe_load(file)
    print(config)

    var_path = config["system"]["var_path"]
    setup_fs(var_path)

    records = dict()

    discord_url = config["system"]["discord_hook"]
    admin_discord_url = config["system"]["admin_hook"]
    for x in config["sites"]:
        url = config["sites"][x]["url"]
        username = config["sites"][x]["user"]
        password = config["sites"][x]["password"]

        ping_id = config["sites"][x]["ping_role_id"]

        auth = HTTPBasicAuth(username, password)

        old_mod_fn = var_path + f"{x.lower()}_mod"
        old_data_fn = var_path + f"{x.lower()}_data"

        # log some stuff
        records[x] = dict()

        new_res = requests.get(url, auth=auth, headers=default_headers)
        records[x]["status_code"] = new_res.status_code
        if new_res.status_code != 200:
            records[x]["failed"] = True
            print(f"Cannot access {url}, failed with status code {new_res.status_code}")
            continue
        records[x]["failed"] = False
        
        print(new_res.headers)
        new_mod = new_res.headers["last-modified"]
        new_data = new_res.content.decode("utf-8")

        if not os.path.exists(old_mod_fn):
            print(f"{old_mod_fn} has no entry, creating now...")
            records[x]["new_entry"] = True
            records[x]["modified"] = True
            send_discord_message(admin_discord_url, None, f"Creating entry for class {x}.")
            write_new_files(old_mod_fn, old_data_fn, new_mod, new_data)
            continue
        
        records[x]["new_entry"] = False
        with open(old_mod_fn, "r") as f:
            old_mod = f.read() 
        
        debug_pings = False 
        if not debug_pings and new_mod == old_mod:
            print(f"No change to {url}.")
            records[x]["modified"] = False
            continue 
        
        records[x]["modified"] = True

        with open(old_data_fn, "r") as f:
            old_data = f.read()

        new_data_lines = new_data.split("\n")
        old_data_lines = old_data.split("\n")

        # stuff with diff here
        res = list(difflib.unified_diff(old_data_lines, new_data_lines, fromfiledate=old_mod, tofiledate=new_mod))
        diff = ""
        for i in res:
            diff += i
            diff += "\n"

        full_message = default_message.format(class_code=x.upper(), url=url, diff=diff)
        print(full_message)

        # stuff with discord here 
        # send_discord_message(discord_url, [(x.upper() + "N")], full_message)
        send_discord_message(discord_url, ping_id, full_message)

        # write new files back
        write_new_files(old_mod_fn, old_data_fn, new_mod, new_data)

    # send debug message to admins
    admin_message = f"""
Website notifier logs:
Time/Date: {str(datetime.now())}
{pprint.pformat(records)}
"""

    send_discord_message(admin_discord_url, None, admin_message)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: Must provide path to config file")
        exit(1)

    main(sys.argv[1])
    exit(0)
