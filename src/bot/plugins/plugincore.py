from collections import defaultdict
from tg_helpers import *


def register_plugin(name,desc):
    def actual_decorator(plugin):
        mod = sys.modules[plugin.__module__]
        if not hasattr(mod, 'PLUGINS'):
            mod.PLUGINS = defaultdict(lambda:None)
        mod.PLUGINS[name]=(plugin(name),desc)
        return plugin
    return actual_decorator


class PluginCore(defaultdict):
    def __init__(self, *args, **kwds):
        pass

    @log
    def get_help(self,command):
        return ""

    @log
    def process(self,cmd,args):
        return "Not implemented"