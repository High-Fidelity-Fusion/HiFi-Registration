import random
import string

def get_path_obfuscator():
    letters = string.ascii_letters + string.digits + "-._~"
    return ''.join(random.choice(letters) for i in range(50))

def get_obfuscated_upload_to(directory):
  def upload_to(instance, filename):
    return '{0}/{1}_{2}'.format(directory, get_path_obfuscator(), filename)
  return upload_to