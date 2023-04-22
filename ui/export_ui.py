# File: export_ui.py
# Author: Ronald Telmanik
# Licence: GPL 3.0
# Description: UI for Export tab

import bpy
from bpy.types import Panel


class BSLIDES_PT_export(Panel):
    """Panel for export"""

    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "BSlides"
    bl_label = "Export"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        addon = context.window_manager.bslides
        layout = self.layout

        layout.prop(addon, "output_directory", text="")

        layout.use_property_split = True

        col = layout.column(heading="Saving")
        col.prop(
            addon,
            "visible_slides",
            text="Visible Slides",
        )
        col.prop(
            addon,
            "hidden_slides",
            text="Hidden Slides",
        )

        layout.prop(addon, "file_format", text="Format", expand=True)
        if addon.file_format == "PDF":
            layout.prop(addon, "file_name", text="File Name")

        if addon.visible_slides or addon.hidden_slides:
            layout.operator(operator="bslides.export_scenes", text="Export")


classes = (BSLIDES_PT_export,)


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
