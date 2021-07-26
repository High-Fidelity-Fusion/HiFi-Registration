import random
import string

def get_path_obfuscator():
    letters = string.ascii_letters + string.digits + "-._~"
    return ''.join(random.choice(letters) for i in range(50))
