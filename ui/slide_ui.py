# File: slide_ui.py
# Author: Ronald Telmanik
# Licence: GPL 3.0
# Description: UI for Slide tab

import bpy
from bpy.types import (
    UIList,
    Panel,
    GizmoGroup,
)


class BSLIDES_UL_slide(UIList):
    """List containing all slides in .blend file and provides basic operations"""

    def draw_item(
        self, context, layout, data, item, icon, active_data, active_propname
    ):
        self.use_filter_invert = False

        if self.layout_type in {"DEFAULT", "COMPACT"}:
            row = layout.row(align=True)

            # scene icon and name
            row.prop(
                item, "name", text="", icon_value=icon, emboss=False, translate=False
            )

            # render slide control icon
            icon = (
                "RESTRICT_RENDER_OFF"
                if item.bslides.render_slide
                else "RESTRICT_RENDER_ON"
            )
            layout.prop(item.bslides, "render_slide", text="", icon=icon, emboss=False)

            # slide number
            # only show when slide number object is initialized
            if "Slide Number" in bpy.data.objects:
                icon = (
                    "RADIOBUT_ON"
                    if item.bslides.slide_number_enable
                    else "RADIOBUT_OFF"
                )
                layout.prop(
                    item.bslides,
                    "slide_number_enable",
                    text="",
                    icon=icon,
                    emboss=False,
                )

        elif self.layout_type in {"GRID"}:
            layout.alignment = "CENTER"
            layout.label(text=item.name, icon_value=icon)


class SlidePanel:
    """Base class for slide panel"""

    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "BSlides"


class BSLIDES_PT_slide(SlidePanel, Panel):
    """Panel for slide"""

    bl_idname = "BSLIDES_PT_slide"
    bl_label = "Slides"

    def draw(self, context):
        layout = self.layout

        row = layout.row(align=True)
        row.operator("bslides.preview_slide", text="Preview Slide")

        col = layout.column(align=True)
        col.operator(operator="bslides.new_presentation", text="New Presentation")

        col.template_list(
            "BSLIDES_UL_slide",
            "",
            bpy.data,
            "scenes",
            context.window_manager.bslides,
            "active_scene_index",
        )
        cf = col.column_flow(align=True)
        cf.operator("bslides.new_slide", icon="ADD", text="")

        is_alone = len(bpy.data.scenes) > 1

        if is_alone:
            cf.operator("bslides.remove_slide", icon="REMOVE", text="")

        wm = context.window_manager
        if wm.bslides.slide_number_change:
            row = layout.row(align=True)
            row.label(text="Slide Number Changed", icon="ERROR")
            row.operator("bslides.update_slide_number", text="", icon="FILE_REFRESH")


class BSLIDES_PT_slide_number(SlidePanel, Panel):
    """Panel for slide numbers"""

    bl_parent_id = "BSLIDES_PT_slide"
    bl_label = "Slide Number"

    @classmethod
    def poll(cls, context):
        return True

    def draw(self, context):
        layout = self.layout

        row = layout.row(align=True)
        if bpy.data.objects.get("Slide Number"):
            row.prop(context.scene.bslides, "slide_number_enable")
            row.operator("bslides.update_slide_number", text="", icon="FILE_REFRESH")
        else:
            row.operator("bslides.new_slide_number", text="New Slide Number")


class BSLIDES_GG_slideshow_control(GizmoGroup):
    """Slideshow control buttons"""

    bl_idname = "GG_prevslide"
    bl_label = "Gizmo button for previous slide"
    bl_space_type = "VIEW_3D"
    bl_region_type = "WINDOW"
    bl_options = {"PERSISTENT", "SCALE"}

    def __init__(self):
        self.spacing = 70
        self.offset = 40

        # standard color and scale from Blender C source
        self.color = (0, 0, 0)
        self.alpha = 0.5
        self.color_highlight = (0.8, 0.8, 0.8)
        self.alpha_highlight = 0.4
        self.scale_basis = (80 * 0.30) / 2

    @classmethod
    def poll(cls, context):
        return not context.space_data.show_region_header

    def create_button(self, icon, operator):
        mpr = self.gizmos.new("GIZMO_GT_button_2d")
        mpr.icon = icon
        mpr.draw_options = {"BACKDROP", "OUTLINE"}
        mpr.target_set_operator(operator)

        mpr.color = self.color
        mpr.alpha = self.alpha
        mpr.color_highlight = self.color_highlight
        mpr.alpha_highlight = self.alpha_highlight
        mpr.scale_basis = self.scale_basis

        return mpr

    def draw_prepare(self, context):
        # load position from addon preferences
        preferences = context.preferences
        addon_pref = preferences.addons["blender_slides"].preferences

        spacing = self.spacing
        width = self.location[addon_pref.control_location][0]
        height = self.location[addon_pref.control_location][1]

        # define position of buttons
        self.next.matrix_basis[0][3] = width
        self.next.matrix_basis[1][3] = height

        self.previous.matrix_basis[0][3] = width - spacing
        self.previous.matrix_basis[1][3] = height

        self.cancel.matrix_basis[0][3] = width + spacing
        self.cancel.matrix_basis[1][3] = height

    def setup(self, context):
        mpr = self.create_button(icon="TRIA_RIGHT", operator="bslides.next_slide")
        self.next = mpr

        mpr = self.create_button(icon="TRIA_LEFT", operator="bslides.previous_slide")
        self.previous = mpr

        mpr = self.create_button(icon="X", operator="bslides.exit_slideshow")
        self.cancel = mpr

        region = context.region
        width = region.width
        height = region.height

        offset = self.offset
        spacing = self.spacing

        # button position definition
        self.location = {
            "BC": (width / 2, offset),
            "TC": (width / 2, height - offset),
            "BL": (offset + spacing, offset),
            "BR": (width - offset - spacing, offset),
            "TL": (offset + spacing, height - offset),
            "TR": (width - offset - spacing, height - offset),
        }


classes = (
    BSLIDES_UL_slide,
    BSLIDES_PT_slide,
    BSLIDES_PT_slide_number,
    BSLIDES_GG_slideshow_control,
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
