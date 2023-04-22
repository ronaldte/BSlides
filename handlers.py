# File: handlers.py
# Author: Ronald Telmanik
# Licence: GPL 3.0
# Description: Handlers used with addon

import bpy
from bpy.app.handlers import persistent


@persistent
def update_scene_number_handler(scene):
    """Used to update slide number"""
    # list of all slides with enabled render
    visible = [s for s in bpy.data.scenes if s.bslides.render_slide]

    # slide does not have a slide number
    try:
        ob = scene.objects["Slide Number"]
    except KeyError:
        return

    # slide is hidden, dont count it
    try:
        idx = visible.index(scene)
    except ValueError:
        return

    ob.data.body = f"{idx+1}/{len(visible)}"


@persistent
def stop_looping_animation_handler(scene):
    """Stops animation from looping"""
    if scene.frame_current == scene.frame_end:
        bpy.ops.screen.animation_cancel(restore_frame=False)