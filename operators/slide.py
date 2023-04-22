# File: slide.py
# Author: Ronald Telmanik
# Licence: GPL 3.0
# Description: Functionality for a slide

import bpy
import os
from mathutils.geometry import intersect_point_line
from mathutils import Color
from math import radians
from bpy.types import Operator
from bpy.props import (
    StringProperty,
    EnumProperty,
    BoolProperty,
)
from .utils import (
    set_default_world_background,
    camera_origin,
    camera_center,
    create_title,
)


class BSLIDES_OT_run_slideshow(Operator):
    """Starts the presentation in fullscreen"""

    bl_idname = "bslides.run_slideshow"
    bl_label = "Run Presentation"

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        try:
            bpy.ops.screen.userpref_show("INVOKE_DEFAULT")
            screen = bpy.data.screens["temp"]
        except KeyError:
            self.report({"ERROR"}, "An error occured during fullscreen operator.")
            return {"CANCELLED"}

        area = screen.areas[0]
        area.type = "VIEW_3D"
        area.spaces[0].region_3d.view_perspective = "CAMERA"

        context.space_data.show_gizmo_navigate = False
        context.space_data.overlay.show_overlays = False
        context.space_data.show_region_header = False

        context.space_data.shading.type = "RENDERED"

        bpy.ops.wm.window_fullscreen_toggle()

        # instead of using blender context, use context overriden by window
        # i created to display slideshow
        if area:
            override = {"area": area, "region": area.regions[0]}
            if bpy.ops.view3d.view_center_camera.poll(override):
                bpy.ops.view3d.view_center_camera(override)

        # activate keymaps
        context.window_manager.keyconfigs.addon.keymaps[0].keymap_items[
            "bslides.next_slide"
        ].active = True
        context.window_manager.keyconfigs.addon.keymaps[0].keymap_items[
            "bslides.previous_slide"
        ].active = True
        context.window_manager.keyconfigs.addon.keymaps[0].keymap_items[
            "bslides.exit_slideshow"
        ].active = True

        # deactivate default keymap
        fo = [
            km
            for km in bpy.context.window_manager.keyconfigs.default.keymaps[
                "Frames"
            ].keymap_items
            if km.name == "Frame Offset"
        ]
        for km in fo:
            km.active = False

        return {"FINISHED"}


class BSLIDES_OT_exit_slideshow(Operator):
    """Stops the slideshow by exiting the window, returning to Blender"""

    bl_idname = "bslides.exit_slideshow"
    bl_label = "Exit Slideshow"

    def execute(self, context):
        try:
            screen = bpy.data.screens["temp"]
        except KeyError:
            self.report({"ERROR"}, "An error occured slideshow exit operator.")
            return {"CANCELLED"}

        bpy.ops.wm.window_close("INVOKE_DEFAULT")

        # deactivate keymaps
        context.window_manager.keyconfigs.addon.keymaps[0].keymap_items[
            "bslides.next_slide"
        ].active = False
        context.window_manager.keyconfigs.addon.keymaps[0].keymap_items[
            "bslides.previous_slide"
        ].active = False
        context.window_manager.keyconfigs.addon.keymaps[0].keymap_items[
            "bslides.exit_slideshow"
        ].active = False

        # restore default keymap
        fo = [
            km
            for km in bpy.context.window_manager.keyconfigs.default.keymaps[
                "Frames"
            ].keymap_items
            if km.name == "Frame Offset"
        ]
        for km in fo:
            km.active = True

        return {"FINISHED"}


class BSLIDES_OT_next_slide(Operator):
    """Switches active scene to the next scene"""

    bl_idname = "bslides.next_slide"
    bl_label = "Next Slide"

    def execute(self, context):
        current_slide = context.scene
        scenes = list(bpy.data.scenes)
        idx = scenes.index(current_slide) + 1

        while idx < len(scenes):
            if scenes[idx].bslides.render_slide:
                bpy.context.window.scene = scenes[idx]
                bpy.context.window_manager.bslides.active_scene_index = idx
                break

            idx += 1

        context.scene.frame_current = 0

        preferences = context.preferences
        addon_pref = preferences.addons["blender_slides"].preferences
        if addon_pref.autoplay_animations:
            bpy.ops.screen.animation_play()

        return {"FINISHED"}


class BSLIDES_OT_previous_slide(Operator):
    """Switches active scene to the previous scene"""

    bl_idname = "bslides.previous_slide"
    bl_label = "Previous Slide"

    def execute(self, context):
        current_slide = context.scene
        scenes = list(bpy.data.scenes)
        idx = scenes.index(current_slide) - 1
        while idx >= 0:
            if scenes[idx].bslides.render_slide:
                bpy.context.window.scene = scenes[idx]
                bpy.context.window_manager.bslides.active_scene_index = idx
                break

            idx -= 1

        context.scene.frame_current = 0

        preferences = context.preferences
        addon_pref = preferences.addons["blender_slides"].preferences
        if addon_pref.autoplay_animations:
            bpy.ops.screen.animation_play()

        return {"FINISHED"}


class BSLIDES_OT_new_slide(Operator):
    """Creates new slide"""

    bl_idname = "bslides.new_slide"
    bl_label = "New Slide"
    bl_options = {"REGISTER", "UNDO"}

    slide_name: StringProperty(default="Slide")

    inc_title: BoolProperty(
        name="Include Title", description="Include title", default=True
    )

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        scene = bpy.data.scenes.new(name=self.slide_name)

        # create new world
        if context.scene.world:
            scene.world = context.scene.world.copy()
        else:
            world = bpy.data.worlds.new("World")
            world.use_nodes = True
            scene.world = world
            set_default_world_background(world)

        bpy.context.window.scene = scene

        # create and link camera, world align, front look
        cam_data = bpy.data.cameras.new("Camera")
        cam_ob = bpy.data.objects.new("Camera", cam_data)
        cam_ob.location = (0, 0, 0)
        cam_ob.rotation_euler = (radians(90), 0, 0)
        scene.collection.objects.link(cam_ob)
        scene.camera = cam_ob

        # camera rotation,location modified, force matrix_world recalculation
        bpy.context.view_layer.update()

        # create a title
        if self.inc_title:
            create_title(cam_ob, scene)

        return {"FINISHED"}


class BSLIDES_OT_remove_slide(Operator):
    """Removes active(curret) slide"""

    bl_idname = "bslides.remove_slide"
    bl_label = "Remove Current Slide"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        scene = bpy.context.scene
        bpy.data.scenes.remove(scene, do_unlink=True)
        return {"FINISHED"}


class BSLIDES_OT_new_presentation(Operator):
    """Initializes new presentation, removing all slides leaving only one"""

    bl_idname = "bslides.new_presentation"
    bl_label = "Create New Presentation"

    @classmethod
    def poll(cls, context):
        return True

    def invoke(self, context, event):
        return context.window_manager.invoke_confirm(self, event)

    def execute(self, context):
        bpy.ops.bslides.new_slide()
        scene = context.scene

        scenes = bpy.data.scenes
        for s in scenes:
            if s is not scene:
                scenes.remove(s, do_unlink=True)

        scene.name = "00_Slide"

        return {"FINISHED"}


class BSLIDES_OT_apply_template(Operator):
    """Apply selected template to currentslide"""

    bl_idname = "bslides.apply_template"
    bl_label = "Apply Current Template To Slide"

    @classmethod
    def poll(cls, context):
        t_name = context.scene.bslides.template
        return t_name not in [c.name for c in context.scene.collection.children]

    def execute(self, context):
        t_name = context.scene.bslides.template
        coll = bpy.data.collections[t_name]
        context.scene.collection.children.link(coll)
        return {"FINISHED"}


class BSLIDES_OT_unlink_template(Operator):
    """Unlink selected template from current slide"""

    bl_idname = "bslides.unlink_template"
    bl_label = "Unlink Current Template From Slide"

    @classmethod
    def poll(cls, context):
        t_name = context.scene.bslides.template
        return t_name in [c.name for c in context.scene.collection.children]

    def execute(self, context):
        t_name = context.scene.bslides.template
        coll = bpy.data.collections[t_name]
        context.scene.collection.children.unlink(coll)
        return {"FINISHED"}


class BSLIDES_OT_new_template(Operator):
    """Create new empty template in current slide"""

    bl_idname = "bslides.new_template"
    bl_label = "Create New Template In Current Slide"
    bl_options = {"REGISTER", "UNDO"}

    template_name: StringProperty(
        name="Template Name", description="Name of newly create template", default=""
    )

    @classmethod
    def poll(cls, context):
        return True

    def invoke(self, context, event):
        return context.window_manager.invoke_props_popup(self, event)

    def execute(self, context):
        name = self.template_name

        if not name:
            name = "Template"
        else:
            name = f"Template-{name}"

        coll = bpy.data.collections.new(name)
        context.scene.collection.children.link(coll)

        return {"FINISHED"}


class BSLIDES_OT_slide_number(Operator):
    """Creates new slide number object in .blend file"""

    bl_idname = "bslides.new_slide_number"
    bl_label = "Create New Slide Number Object"

    @classmethod
    def poll(cls, context):
        return "Slide Number" not in bpy.data.objects

    def execute(self, context):
        text_dat = bpy.data.curves.new(type="FONT", name="Slide Number")
        text_obj = bpy.data.objects.new(name="Slide Number", object_data=text_dat)

        context.scene.collection.objects.link(text_obj)
        context.scene.bslides.slide_number_enable = True

        context.scene.frame_set(context.scene.frame_current)

        return {"FINISHED"}


class BSLIDES_OT_update_slide_number(Operator):
    """Update slide number text object on slides"""

    bl_idname = "bslides.update_slide_number"
    bl_label = "Update Slide Number"

    @classmethod
    def poll(cls, context):
        return "Slide Number" in bpy.data.objects

    def execute(self, context):
        scenes = bpy.data.scenes

        slide_number_obj = bpy.data.objects.get("Slide Number")

        for s in scenes:
            if s.bslides.slide_number_enable:
                if "Slide Number" not in s.objects:
                    s.collection.objects.link(slide_number_obj)
            else:
                if "Slide Number" in s.objects:
                    s.collection.objects.unlink(slide_number_obj)
            s.frame_set(context.scene.frame_current)

        wm = context.window_manager
        wm.bslides.slide_number_change = False

        return {"FINISHED"}


class BSLIDES_OT_reset_background(Operator):
    """Resets background of slide"""

    bl_idname = "bslides.reset_slide_background"
    bl_label = "Reset Slide Background"

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        world = context.scene.world

        if world and world.users < 2:
            # someone if still referencing this world
            bpy.data.worlds.remove(world)

        world = bpy.data.worlds.new("World")
        world.use_nodes = True
        context.scene.world = set_default_world_background(world)

        return {"FINISHED"}


class BSLIDES_OT_apply_all_background(Operator):
    """Applies current background settings to all slides"""

    bl_idname = "bslides.apply_all_slide_background"
    bl_label = "Apply to All"

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        scene = context.scene
        scenes_all = list(bpy.data.scenes)
        scenes_all.remove(scene)

        world = scene.world

        for s in scenes_all:
            if world and s.world.users < 2:
                bpy.data.worlds.remove(s.world)
            s.world = world.copy()

        return {"FINISHED"}


class BSLIDES_OT_apply_resolution(Operator):
    """Applies current resolution settings to all slides"""

    bl_idname = "bslides.apply_all_resolution"
    bl_label = "Apply to All"

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        scene = context.scene
        scenes_all = list(bpy.data.scenes)
        scenes_all.remove(scene)

        rd = scene.render

        resolution = (rd.resolution_x, rd.resolution_y)

        for s in scenes_all:
            s.render.resolution_x = resolution[0]
            s.render.resolution_y = resolution[1]

        return {"FINISHED"}


class BSLIDES_OT_center(Operator):
    """Centers object in front of camera"""

    bl_idname = "bslides.center_object"
    bl_label = "Center Object"
    bl_options = {"REGISTER", "UNDO"}

    copy_rotation: BoolProperty(
        name="Copy Camera Rotation",
        description="Applies camera rotation to object",
        default=False,
    )

    center_origin: BoolProperty(
        name="Center Object Origin",
        description="Change Object Origin to Center Mass",
        default=False,
    )

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        ob = context.object

        cam = context.scene.camera
        scene = context.scene

        if self.center_origin:
            bpy.ops.object.origin_set(type="ORIGIN_CENTER_OF_MASS")

        cam_origin = camera_origin(cam)
        cam_center = camera_center(cam, scene)

        ob_loc = ob.matrix_world.normalized().to_translation()
        loc = intersect_point_line(ob_loc, cam_origin, cam_center)

        ob.location = loc[0]

        if self.copy_rotation:
            ob.rotation_euler = cam.rotation_euler

        return {"FINISHED"}


class BSLIDES_OT_3D_cursor_to_center(Operator):
    """Moves 3D cursor to camera center"""

    bl_idname = "bslides.center_3d_cursor"
    bl_label = "Center 3D Cursor"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        cam = context.scene.camera
        scene = context.scene

        cam_origin = camera_origin(cam)
        cam_center = camera_center(cam, scene)

        context.scene.cursor.location = cam_center

        return {"FINISHED"}


class BSLIDES_OT_copy_ob_to_all(Operator):
    """Copies object to all slides"""

    bl_idname = "bslides.copy_to_all"
    bl_label = "Copy Object To All Slides"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        scene = context.scene
        ob = context.object

        for s in bpy.data.scenes:
            if s is not scene:
                s.collection.objects.link(ob.copy())

        return {"FINISHED"}


class BSLIDES_OT_preview_slide(Operator):
    """Previews slide like during the slide show"""

    bl_idname = "bslides.preview_slide"
    bl_label = "Preview Slide"

    @classmethod
    def poll(cls, context):
        return [area for area in bpy.context.screen.areas if area.type == "VIEW_3D"]

    def execute(self, context):
        # Override context for view center so that it uses 3D View
        for area in bpy.context.screen.areas:
            if area.type == "VIEW_3D":
                override = {"area": area, "region": area.regions[0]}
                # Set camera view
                area.spaces[0].region_3d.view_perspective = "CAMERA"

                # Align boundries for camera view
                if bpy.ops.view3d.view_center_camera.poll(override):
                    bpy.ops.view3d.view_center_camera(override)

        # Zoom camera
        bpy.ops.view3d.zoom_camera_1_to_1()

        return {"FINISHED"}


classes = (
    BSLIDES_OT_run_slideshow,
    BSLIDES_OT_exit_slideshow,
    BSLIDES_OT_next_slide,
    BSLIDES_OT_previous_slide,
    BSLIDES_OT_new_slide,
    BSLIDES_OT_remove_slide,
    BSLIDES_OT_new_presentation,
    BSLIDES_OT_apply_template,
    BSLIDES_OT_unlink_template,
    BSLIDES_OT_new_template,
    BSLIDES_OT_slide_number,
    BSLIDES_OT_update_slide_number,
    BSLIDES_OT_reset_background,
    BSLIDES_OT_apply_all_background,
    BSLIDES_OT_apply_resolution,
    BSLIDES_OT_center,
    BSLIDES_OT_3D_cursor_to_center,
    BSLIDES_OT_copy_ob_to_all,
    BSLIDES_OT_preview_slide,
)


def register():
    for cls in classes:
        try:
            bpy.utils.register_class(cls)
        except ValueError:
            bpy.utils.unregister_class(cls)
            bpy.utils.register_class(cls)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
