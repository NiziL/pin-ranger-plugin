"""
With this plugin, you can mark certain directories as "pinned", to denote
that they are a fixed part of your directory structure. The effect is that they
will be sorted first, and can be highlighted by a color scheme, using the key
'pin'.

New key bindings:

"++" pin a file or directory
"--" unpin it
"""

import os.path
import ranger.gui.context
import ranger.gui.widgets.browsercolumn
from ranger.container.directory import Directory
from ranger.api.commands import Command

# Load list of pinned files from database
TARGET_PATH = os.path.expanduser("~/.config/ranger/pinned")


def set_pinned_paths():
    if not os.path.exists(TARGET_PATH):
        open(TARGET_PATH, "w").close()
    ranger.pinned_paths = [
        line.rstrip("\n") for line in open(TARGET_PATH).readlines()
    ]


set_pinned_paths()

# Create a sorting method so that pinned files are displayed on top

def sort_by_pins(path):
    try:
        key = path.basename_natural_lower
        if path.path in ranger.pinned_paths:
            key.insert(0, ("", 0))
        return key
    except:
        return ("", 0)

# Register the sorting method
Directory.sort_dict["pin"] = sort_by_pins

# Extend colorscheme
ranger.gui.context.CONTEXT_KEYS.append("pin")
ranger.gui.context.Context.pin = False


# Add commands to pin files
class Pin(Command):
    def execute(self):
        f = open(TARGET_PATH, "r")
        files = f.read().rstrip("\n").split("\n")
        f.close()

        f = None

        for file in self.fm.thistab.get_selection():
            if file.path not in files:
                if not f:
                    f = open(TARGET_PATH, "a")
                f.write(file.path)
                f.write("\n")

        if f is not None:
            f.close()

        set_pinned_paths()


# Add commands to unpin files
class Unpin(Command):
    def execute(self):
        f = open(TARGET_PATH, "r")
        files = f.read().rstrip("\n").split("\n")
        f.close()

        new_files = list(files)
        for file in self.fm.thistab.get_selection():
            while file.path in new_files:
                new_files.remove(file.path)

        if len(new_files) != len(files):
            f = open(TARGET_PATH, "w")
            f.write("\n".join(new_files) + "\n")
            f.close()

        set_pinned_paths()


# Bind those commands to keys
old_hook_init = ranger.api.hook_init


def hook_init(fm):
    if old_hook_init:
        old_hook_init(fm)
    fm.execute_console("map ++ chain Pin; reset")
    fm.execute_console("map -- chain Unpin; reset")


ranger.api.hook_init = hook_init

# Bind a hook that injects the "pin" color key
hook_before_drawing = ranger.gui.widgets.browsercolumn.hook_before_drawing


def hook_before_drawing__pin(drawn, this_color):
    if drawn.path in ranger.pinned_paths:
        this_color.append("pin")
    return hook_before_drawing(drawn, this_color)


ranger.gui.widgets.browsercolumn.hook_before_drawing = hook_before_drawing__pin
