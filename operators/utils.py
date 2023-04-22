# File: utils.py
# Author: Ronald Telmanik
# Licence: GPL 3.0
# Description: Utilitis for operators

import bpy
from mathutils import (
    Vector,
    Matrix,
)
import sys


def set_default_world_background(world):
    """Sets world to default color"""
    if not world:
        return None

    bg = world.node_tree.nodes["Background"]
    bg.inputs[0].default_value = (1.0, 1.0, 1.0, 1)
    bg.inputs[1].default_value = 1.5

    return world


def list_avg(l):
    """Calculates average of list"""
    return sum(l) / len(l)


def camera_origin(camera):
    """Calculater camera origin"""
    cam_loc = camera.matrix_world.normalized()
    return cam_loc.to_translation()


def camera_frame(camera, scene):
    """Returns list with 4 camera corners"""
    cam_loc = camera.matrix_world.normalized()
    return [cam_loc @ v for v in camera.data.view_frame(scene=scene)]


def camera_center(camera, scene):
    """Returns camera centers"""
    cam_frame = camera_frame(camera, scene)
    return Vector(
        (
            list_avg([v.x for v in cam_frame]),
            list_avg([v.y for v in cam_frame]),
            list_avg([v.z for v in cam_frame]),
        )
    )


def slide_control_header(self, context):
    row = self.layout.row(align=True)
    row.operator("bslides.previous_slide", text="", icon="TRIA_LEFT_BAR")
    row.operator("bslides.next_slide", text="", icon="TRIA_RIGHT_BAR")
    row = self.layout.row(align=True)
    row.operator("bslides.run_slideshow", text="", icon="PLAY")


def get_python_path():
    """Returns python path for Blender executable"""
    version = bpy.app.version

    if version > (2, 91, 0):
        python_path = sys.executable
    else:
        python_path = bpy.app.binary_path_python

    return python_path


def create_title(cam, scene):
    text_dat = bpy.data.curves.new(type="FONT", name="Title")
    text_dat.body = "Title"
    text_dat.size = 0.03
    text_dat.align_x = "CENTER"
    text_dat.align_y = "CENTER"

    text_obj = bpy.data.objects.new(name="Title_", object_data=text_dat)
    text_obj.location = camera_center(cam, scene)
    text_obj.rotation_euler = cam.rotation_euler
    scene.collection.objects.link(text_obj)
