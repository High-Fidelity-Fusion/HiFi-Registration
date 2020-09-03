import re
from urllib.request import urlretrieve

dev_settings_path = "hifireg/hifireg/settings/developer.py"

def wget(url, dest_path):
    urlretrieve(url, dest_path)

def get_current_database_postfix():
    try:
        with open(dev_settings_path, "r") as f:
            for line in f:
                match_list = re.findall("hifiregdb_(.*)'", line)
                if match_list:
                    return match_list[0]
    except FileNotFoundError:
        pass
    return "dev"
    
def replace_database_postfix(postfix_default):
    postfix = input(f"Enter your database postfix [{postfix_default}]: ")
    postfix = postfix if postfix else postfix_default
    
    db_original = "hifiregdb_dev"
    db_new = f"hifiregdb_{postfix}"

    print(f"Your database name is: {db_new}")

    with open(dev_settings_path, "r") as f:
        lines = f.readlines()
    with open(dev_settings_path, "w") as f:
        for line in lines:
            f.write(re.sub(db_original, db_new, line))

def get_dev_settings(url, dest_path):
    postfix_default = get_current_database_postfix()
    wget(url, dest_path)
    replace_database_postfix(postfix_default)
