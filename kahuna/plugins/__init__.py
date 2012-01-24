#!/usr/bin/env jython

import os

# Automatically set the __all__ variable with all
# the available plugins.

plugin_dir = "kahuna/plugins"

__all__ = []
for filename in os.listdir(plugin_dir):
    filename = plugin_dir + "/" + filename
    if os.path.isfile(filename):
        basename = os.path.basename(filename)
        base, extension = os.path.splitext(basename)
        if extension == ".py" and not basename.startswith("_"):
            __all__.append(base)

