from .public import *
from .secret import *

import os

if os.getenv('USE_DEV_SETTINGS', 'False').lower() == 'true':
    from .developer import *
    print("DEV SETTINGS IMPORTED")
