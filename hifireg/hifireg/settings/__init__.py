from .public import *

import os

if os.getenv('USE_DEV_SETTINGS', 'False').lower() == 'true':
    from .developer import *
