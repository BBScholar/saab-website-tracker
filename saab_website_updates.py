#! /bin/python3

import requests
from requests.auth import HTTPBasicAuth

import difflib


default_message = """
{class} site updated!
Our lord and savior Dr. Daniel Saab has updated the course site. 
See changes at {url}

Here is the diff:
{diff}
"""


def setup_fs(var_path):
    if os.path.exists(var_path) and not os.path.isfile(var_path):
        return;
    print("{} does not exist, creating directory now...", var_path)
    os.mkdir(var_path)

def send_discord_message(hook_url, ping_roles, message):
    s = ""
    for p in ping_roles:
        s += f"@{p}\n"
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


def create_diff(old_mod, new_mod, old_data, new_data):
    iter = difflib.unified_diff(old_data, new_data, fromfiledate=new_mod, tofiledate=old_mod))
    s = ""
    for i in iter:
        s += i;

    return s


def main(config_file):
    with open(config_file, "r") as file:
        config = yaml.safe_load(file)
    print(config)

    var_path = config["system"]["var_path"]
    setup_fs(var_path)

    discord_url = config["system"]["discord_hook"]
    for x in config["sites"]:
        url = config["sites"][x]["url"]
        username = config["sites"][x]["user"]
        password = config["sites"][x]["password"]

        auth = HTTPBasicAuth(username, password)

        old_mod_fn = var_path + f"{x.lower()}_mod"
        old_data_fn = var_path + f"{x.lower()}_data"

        new_res = requests.head(url, auth=auth)

        if new_res.status_code != 200:
            print(f"Cannot access {url}, failed with status code {new_res.status_code}")
            continue

        new_mod = new_res.headers["Last-Modified"]

        if not os.path.exists(old_mod_fn):
            print(f"{old_mod_fn} has no entry, creating now...")
            write_new_files(old_mod_fn, old_data_fn, new_mod, str(requests.get(url, auth=auth).content))
            continue
        
        with open(old_mod_fn, "r") as f:
            old_mod = f.read() 
        
        if new_mod == old_mod:
            print(f"No change to {url}.")
            continue 

        new_data = str(requests.get(url, auth=auth).content)

        with open(old_data_fn, "r") as f:
            old_data = f.read()

        new_data_lines=new_data.split("\\n")
        old_data_lines=old_data.split("\\n")

        # stuff with diff here
        diff =  create_diff(old_data, new_data, old_mod, new_mod)
        full_message = format(default_message, class=x, url=url, diff=diff)

        print(full_message)

        # stuff with discord here 
        send_discord_message(discord_url, [(x.upper() + "N")], full_message)

        # write new files back
        write_new_files(old_mod_fn, old_data_fn, new_mod, new_data)

