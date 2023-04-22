# BSlides - Blender Addon for slides
# Author: Ronald Telmanik
# Licence: GPL 3.0
# Description: Entry point of addon

bl_info = {
    "name": "Blender Slides",
    "author": "Ronald Telmanik",
    "description": "Tools to make creating presentations easier",
    "blender": (2, 83, 0),
    "version": (1, 2, 0),
    "location": "View3D > Sidebar > BSlides",
    "warning": "",
    "category": "Generic",
}

import bpy
from bpy.props import (
    BoolProperty,
    StringProperty,
    IntProperty,
    PointerProperty,
    EnumProperty,
)
from bpy.types import (
    Operator,
    AddonPreferences,
)

from .operators.utils import slide_control_header
from .operators.export import BSLIDES_OT_install_packages
from .properties import (
    BSLIDES_PG_wm,
    BSLIDES_PG_scene,
    BSLIDES_PG_text,
)
from .handlers import update_scene_number_handler, stop_looping_animation_handler

from .icons import load_icons, unload_icons

from .operators import export, slide, text
from .ui import design_ui, export_ui, slide_ui, text_ui
from . import properties


class BSLIDES_addonpreference(AddonPreferences):
    """Addon preference menu"""

    bl_idname = __name__

    control_location: EnumProperty(
        name="Slideshow Control Location",
        description="Location Of Control Buttons During Slideshow",
        items=(
            ("TC", "Top Center", ""),
            ("TL", "Top Left", ""),
            ("TR", "Top Right", ""),
            ("BC", "Bottom Center", ""),
            ("BL", "Bottom Left", ""),
            ("BR", "Bottom Right", ""),
        ),
        default="TC",
    )

    def loop_animations_update(self, context):
        preferences = context.preferences
        addon_pref = preferences.addons["blender_slides"].preferences
        if not addon_pref.loop_animations:
            bpy.app.handlers.frame_change_post.append(stop_looping_animation_handler)
        else:
            bpy.app.handlers.frame_change_post.remove(stop_looping_animation_handler)

    loop_animations: BoolProperty(
        name="Loop Animations",
        description="Loop animation when playing animation",
        default=False,
        update=loop_animations_update,
    )

    autoplay_animations: BoolProperty(
        name="Auto Play Animations",
        description="Auto Play animations when switching slides",
        default=True,
    )

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True

        row = layout.row(align=True)
        row.prop(self, "control_location")

        if BSLIDES_OT_install_packages.poll(context):
            layout.label(
                text="To Export as PDF, some packages have to be installed.",
                icon="ERROR",
            )
            layout.operator(
                operator="bslides.install_packages", text="Install Packages"
            )
        else:
            layout.label(text="All Packages are Installed.", icon="CHECKMARK")

        layout.use_property_split = False
        row = layout.row(align=True)
        row.prop(self, "loop_animations")
        row.prop(self, "autoplay_animations")
        if self.loop_animations and self.autoplay_animations:
            layout.label(
                text="This combination will result in endless cycling!", icon="ERROR"
            )

        layout.operator(
            "wm.url_open",
            text="Documentation",
            icon="HELP",
        ).url = "https://github.com/ronaldte/blender_slides/wiki/Manual"


modules = (
    export,
    slide,
    text,
    design_ui,
    export_ui,
    slide_ui,
    text_ui,
    properties,
)

classes = (BSLIDES_addonpreference,)

keymaps = []


def register():
    for m in modules:
        m.register()

    for c in classes:
        bpy.utils.register_class(c)

    kc = bpy.context.window_manager.keyconfigs.addon
    if kc:
        km = kc.keymaps.new(name="3D View", space_type="VIEW_3D")
        kmi = km.keymap_items.new(
            "bslides.next_slide", type="RIGHT_ARROW", value="PRESS"
        )
        kmi.active = False
        keymaps.append((km, kmi))

        kmi = km.keymap_items.new(
            "bslides.previous_slide", type="LEFT_ARROW", value="PRESS"
        )
        kmi.active = False
        keymaps.append((km, kmi))

        kmi = km.keymap_items.new("bslides.exit_slideshow", type="ESC", value="PRESS")
        kmi.active = False
        keymaps.append((km, kmi))

    bpy.app.handlers.frame_change_post.append(update_scene_number_handler)

    bpy.types.VIEW3D_HT_header.append(slide_control_header)

    load_icons()

    BSLIDES_OT_install_packages.install_python_user_path()

    addon_pref = bpy.context.preferences.addons["blender_slides"].preferences
    if not addon_pref.loop_animations:
        bpy.app.handlers.frame_change_post.append(stop_looping_animation_handler)

    bpy.types.WindowManager.bslides = PointerProperty(type=BSLIDES_PG_wm)
    bpy.types.Scene.bslides = PointerProperty(type=BSLIDES_PG_scene)
    bpy.types.TextCurve.bslides = PointerProperty(type=BSLIDES_PG_text)


def unregister():

    for km, kmi in keymaps:
        km.keymap_items.remove(kmi)
    keymaps.clear()

    bpy.types.VIEW3D_HT_header.remove(slide_control_header)

    bpy.app.handlers.frame_change_post.remove(update_scene_number_handler)

    addon_pref = bpy.context.preferences.addons["blender_slides"].preferences
    if not addon_pref.loop_animations:
        bpy.app.handlers.frame_change_post.remove(stop_looping_animation_handler)

    for m in modules:
        m.unregister()

    unload_icons()

    del bpy.types.WindowManager.bslides
    del bpy.types.Scene.bslides
    del bpy.types.TextCurve.bslides

    for c in classes:
        bpy.utils.unregister_class(c)
