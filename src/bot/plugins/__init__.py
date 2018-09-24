import os
from tg_helpers import *
import importlib

__all__ = []
__plugins__=dict()

@export
#@log
def items():
    return __plugins__.items()

####### find and register plugins
basedir = os.path.dirname(__file__)

res = os.listdir(basedir)
print(res)
for entry in res:
    fullpath = os.path.join(basedir, entry)
    # plugins as .py files or subfolders
    if not fullpath.startswith("_") and os.path.isdir(fullpath) and "__init__.py" in os.listdir(fullpath):
        #register plugin in subdolder
        try:
            module=importlib.import_module("{}.{}".format(__name__,entry))
            __all__.append(entry)
            __plugins__[entry]=module
        except Exception as inst:
            pass

__all__.sort()
