# File: properties.py
# Author: Ronald Telmanik
# Licence: GPL 3.0
# Description: Properties used throughout addon

import bpy
from bpy.types import PropertyGroup
from bpy.props import (
    StringProperty,
    BoolProperty,
    EnumProperty,
    IntProperty,
    CollectionProperty,
    PointerProperty,
)


class FontStyle(PropertyGroup):
    """Saving font style for furthure use"""

    name: StringProperty(
        name="Name of Font Style",
        description="Represents name of saved font style",
        default="Font Style",
    )

    source_ob: PointerProperty(
        type=bpy.types.TextCurve,
        name="Source Text Object",
        description="Hold pointer to the text object with style to save",
    )


class BSLIDES_PG_wm(PropertyGroup):
    """Represent all properties registered inside window_manager in Blender"""

    file_name: StringProperty(
        name="Output File Name",
        default="Presentation",
        subtype="FILE_NAME",
    )

    output_directory: StringProperty(
        name="Output Directory",
        description="Directory where will be presentation stored",
        default="//",
        subtype="DIR_PATH",
    )

    hidden_slides: BoolProperty(
        name="Render Hidden",
        description="Render all slides despiten hidden state",
        default=False,
    )

    visible_slides: BoolProperty(
        name="Render Visible",
        description="Render all visible slides",
        default=True,
    )

    file_format: EnumProperty(
        name="File Format",
        description="File format of final output",
        items=(
            ("PDF", "PDF", "Export presentation as PDF"),
            ("JPG", "JPG", "Export presentation as PNG images"),
        ),
        default="JPG",
    )

    def active_scene_index_update(self, context):
        """Updates active scene index"""
        scenes = bpy.data.scenes
        addon = context.window_manager.bslides
        context.window.scene = scenes[addon.active_scene_index]

    active_scene_index: IntProperty(
        name="Active Scene Index",
        default=0,
        description="Holds index value of currently active scene",
        update=active_scene_index_update,
    )

    slide_number_change: BoolProperty(
        name="Slide Number Change",
        description="Dirty bit for slide number change",
        default=False,
    )

    font_styles: CollectionProperty(
        type=FontStyle,
    )

    font_styles_index: IntProperty(
        name="Index of Font Style",
        description="Index of currently selected font style",
        default=0,
    )


class BSLIDES_PG_scene(PropertyGroup):
    """Represent all properties registered inside scene in Blender"""

    render_slide: BoolProperty(
        name="Render Slide",
        default=True,
        description="Render this slide during presentation",
    )

    def get_templates(self, context):
        """Fetches all templates inside .blend file"""
        collections = bpy.data.collections
        templates = []

        for c in collections:
            if c.name.lower().startswith("template"):
                templates.append((c.name, c.name, ""))

        # in case no templates were found in .blend file
        # blender CAN NOT use empty list
        if not len(templates):
            templates.append(("NONE", "Empty", ""))

        return templates

    template: EnumProperty(
        name="All Templates",
        description="Template used on this slide",
        items=get_templates,
    )

    def slide_number_change_update(self, context):
        """Updates slide number"""
        wm = context.window_manager
        wm.bslides.slide_number_change = True

    slide_number_enable: BoolProperty(
        name="Slide Number",
        description="Show slide number on slide",
        default=False,
        update=slide_number_change_update,
    )


class BSLIDES_PG_text(PropertyGroup):
    """Represent all properties registered inside text object in Blender"""

    def update_bold(self, context):
        ob = context.object
        val = ob.data.bslides.use_bold

        for l in ob.data.body_format:
            l.use_bold = val

    use_bold: BoolProperty(
        name="Bold Text",
        description="Change all text to bold",
        default=False,
        update=update_bold,
    )

    def update_italic(self, context):
        ob = context.object
        val = ob.data.bslides.use_italic

        for l in ob.data.body_format:
            l.use_italic = val

    use_italic: BoolProperty(
        name="Italic Text",
        description="Change all text to italic",
        default=False,
        update=update_italic,
    )

    def update_underline(self, context):
        ob = context.object
        val = ob.data.bslides.use_underline

        for l in ob.data.body_format:
            l.use_underline = val

    use_underline: BoolProperty(
        name="Underline Text",
        description="Change all text to underline",
        default=False,
        update=update_underline,
    )

    def update_small_caps(self, context):
        ob = context.object
        val = ob.data.bslides.use_small_caps

        for l in ob.data.body_format:
            l.use_small_caps = val

    use_small_caps: BoolProperty(
        name="Small Caps Text",
        description="Change all text to small caps",
        default=False,
        update=update_small_caps,
    )


classes = (
    FontStyle,
    BSLIDES_PG_wm,
    BSLIDES_PG_scene,
    BSLIDES_PG_text,
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
