# File: text_ui.py
# Author: Ronald Telmanik
# Licence: GPL 3.0
# Description: UI for text tab

import bpy
from bpy.types import (
    Panel,
    UIList,
)
from bpy_extras.node_utils import find_node_input
from ..icons import preview_collections, find_icon


class TextPanel:
    """Base class for Text panel"""

    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "BSlides"
    bl_options = {"DEFAULT_CLOSED"}


class BSLIDES_PT_text(TextPanel, Panel):
    """Panel for text"""

    bl_idname = "BSLIDES_PT_text"
    bl_label = "Text"

    @classmethod
    def poll(cls, context):
        return True

    def draw(self, context):
        pass


class BSLIDES_PT_style(TextPanel, Panel):
    """Panel containing style options for text object"""

    bl_parent_id = "BSLIDES_PT_text"
    bl_label = "Style"
    bl_options = {"HIDE_HEADER"}

    @classmethod
    def poll(cls, context):
        ob = context.object
        return ob and ob.type == "FONT"

    def draw(self, context):
        layout = self.layout
        ob = context.object

        # Blender says object will never be None,
        # sure, try deleting and here we go ...
        if not ob:
            return

        # align text

        if context.mode == "EDIT_TEXT":
            row = layout.row(align=True)
            row.operator("font.style_toggle", text="Bold", icon="BOLD").style = "BOLD"
            row.operator(
                "font.style_toggle", text="Italics", icon="ITALIC"
            ).style = "ITALIC"
            row.operator(
                "font.style_toggle", text="Underline", icon="UNDERLINE"
            ).style = "UNDERLINE"
            row.operator(
                "font.style_toggle", text="Small Caps", icon="SMALL_CAPS"
            ).style = "SMALL_CAPS"

            row = layout.row(align=True)
            row.operator("font.case_set", text="AAA").case = "UPPER"
            row.operator("font.case_set", text="aaa").case = "LOWER"

        elif context.mode == "OBJECT":
            if not context.object.name.lower().startswith("title"):
                row = layout.row(align=True)
                row.operator("bslides.convert_title", text="Convert Title")

            row = layout.row(align=True)
            row.operator(
                "bslides.merge_text", text="Merge Objects"
            ).new_line_divide = True
            row.operator("bslides.align_text_objects", text="Align Objects")

            layout.separator()

            row = layout.row(align=True)
            row.prop(ob.data.bslides, "use_bold", toggle=True, icon="BOLD", text="Bold")
            row.prop(
                ob.data.bslides, "use_italic", toggle=True, icon="ITALIC", text="Italic"
            )
            row.prop(
                ob.data.bslides,
                "use_underline",
                toggle=True,
                icon="UNDERLINE",
                text="Underline",
            )
            row.prop(
                ob.data.bslides,
                "use_small_caps",
                toggle=True,
                icon="SMALL_CAPS",
                text="Small Caps",
            )

            row = layout.row(align=True)
            row.operator(
                "bslides.horizontal_alignment", text="", icon="ALIGN_LEFT"
            ).side = "LEFT"
            row.operator(
                "bslides.horizontal_alignment", text="", icon="ALIGN_RIGHT"
            ).side = "RIGHT"
            row.operator(
                "bslides.horizontal_alignment", text="", icon="ALIGN_CENTER"
            ).side = "CENTER"
            row.operator(
                "bslides.horizontal_alignment", text="", icon="ALIGN_JUSTIFY"
            ).side = "JUSTIFY"
            row.separator()
            row.operator("bslides.upper_case", text="AAA").case = "UPPER"
            row.operator("bslides.upper_case", text="aaa").case = "LOWER"

            row = layout.row(align=True)
            row.operator(
                "bslides.indentation",
                text="",
                icon_value=find_icon("indent"),
            ).direction = "IN"
            row.operator(
                "bslides.indentation",
                text="",
                icon_value=find_icon("outdent"),
            ).direction = "OUT"

            layout.separator()

            col = layout.column(align=True)
            col.use_property_split = True
            col.prop(ob.data, "size")
            col.separator()


class BSLIDES_PT_spacing(TextPanel, Panel):
    """Panel containing spacing options for text object"""

    bl_parent_id = "BSLIDES_PT_text"
    bl_label = "Spacing"

    @classmethod
    def poll(cls, context):
        ob = context.object
        return ob and ob.type == "FONT" and context.mode == "OBJECT"

    def draw(self, context):
        layout = self.layout
        ob = context.object

        col = layout.column(align=True)
        col.use_property_split = True

        col.prop(ob.data, "space_character", text="Character")
        col.prop(ob.data, "space_word", text="Word")
        col.prop(ob.data, "space_line", text="Line")


class BSLIDES_PT_text_color(TextPanel, Panel):
    """Panel for text color"""

    bl_parent_id = "BSLIDES_PT_text"
    bl_label = "Color"

    @classmethod
    def poll(cls, context):
        ob = context.object
        return ob and ob.type == "FONT" and context.mode == "OBJECT"

    def draw(self, context):
        layout = self.layout
        ob = context.object

        layout.operator("bslides.add_text_color", text="Add Color")

        if ob.data.materials:
            mat = ob.data.materials[0]

            ntree = mat.node_tree
            node = ntree.get_output_node("EEVEE")

            if mat.use_nodes:
                if node:
                    input = find_node_input(node, "Surface")
                    if input:
                        layout.template_node_view(ntree, node, input)
                    else:
                        layout.label(text="Incompatible output node")
                else:
                    layout.label(text="No output node")
            else:
                layout.prop(mat, "diffuse_color", text="Base Color")
                layout.prop(mat, "metallic")
                layout.prop(mat, "specular_intensity", text="Specular")
                layout.prop(mat, "roughness")


class BSLIDES_PT_insert(TextPanel, Panel):
    """Panel containing insert operators"""

    bl_parent_id = "BSLIDES_PT_text"
    bl_label = "Insert"

    @classmethod
    def poll(cls, context):
        return context.mode == "OBJECT"

    def draw(self, context):
        layout = self.layout

        col = layout.column(align=True)
        col.operator("bslides.new_title", text="New Title")
        col.operator("bslides.date_text", text="Date")
        col.operator("bslides.generate_toc", text="Table of Contents")


class BSLIDES_UL_font_styles(UIList):
    """List containing all fonts stored for reference through presentation"""

    def draw_item(
        self, context, layout, data, item, icon, active_data, active_propname
    ):
        self.use_filter_invert = False

        if self.layout_type in {"DEFAULT", "COMPACT"}:
            layout.prop(
                item, "name", text="", icon="SYNTAX_OFF", emboss=False, translate=False
            )
        elif self.layout_type in {"GRID"}:
            layout.alignment = "CENTER"
            layout.label(text=item.name, icon_value=icon)


class BSLIDES_PT_fonts(TextPanel, Panel):
    """Panel for font management"""

    bl_parent_id = "BSLIDES_PT_text"
    bl_label = "Fonts"

    @classmethod
    def poll(cls, context):
        ob = context.object
        return ob and ob.type == "FONT" and context.mode == "OBJECT"

    def draw(self, context):
        layout = self.layout

        row = layout.row()

        col = row.column(align=True)

        col.template_list(
            "BSLIDES_UL_font_styles",
            "",
            context.window_manager.bslides,
            "font_styles",
            context.window_manager.bslides,
            "font_styles_index",
        )

        fs = context.window_manager.bslides.font_styles
        if fs:
            col.operator(
                "bslides.apply_font_style", icon="CHECKMARK", text="Apply Font Style"
            )

        row = row.column(align=True)
        row.operator("bslides.new_font_style", icon="ADD", text="")
        row.operator("bslides.delete_font_style", icon="REMOVE", text="")


classes = (
    BSLIDES_PT_text,
    BSLIDES_PT_style,
    BSLIDES_PT_spacing,
    BSLIDES_PT_text_color,
    BSLIDES_PT_insert,
    BSLIDES_UL_font_styles,
    BSLIDES_PT_fonts,
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
