# File: icons.py
# Author: Ronald Telmanik
# Licence: GPL 3.0
# Description: Module dealing with custom icons

import os
import bpy

preview_collections = {}


def load_icons():
    """Loads custom icons from icons folder into collection"""
    import bpy.utils.previews

    pcoll = bpy.utils.previews.new()

    my_icons_dir = os.path.join(os.path.dirname(__file__), "icons")

    for icon in os.listdir(my_icons_dir):
        file_name, file_extension = os.path.splitext(icon)
        if file_extension.lower() == ".png":
            pcoll.load(file_name, os.path.join(my_icons_dir, icon), "IMAGE")

    global preview_collections
    preview_collections["icons"] = pcoll


def unload_icons():
    """Removes all custom icons from collection"""
    for pcoll in preview_collections.values():
        bpy.utils.previews.remove(pcoll)
    preview_collections.clear()


def find_icon(icon_name):
    """Returns given icon from collection"""
    return preview_collections["icons"][icon_name].icon_id