import os
from tg_helpers import *
import importlib
from collections import defaultdict

__all__ = []
__plugins__=defaultdict(lambda:None)

@export
#@log
def items():
    return __plugins__.items()

@export
def get(str):
    p=__plugins__[str]
    return p[0] if p else p

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
            if hasattr(module, 'PLUGINS'):
                __plugins__.update(module.PLUGINS)

        except Exception as inst:
            pass

__all__.sort()
