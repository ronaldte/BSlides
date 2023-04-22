# File: design_ui.py
# Author: Ronald Telmanik
# Licence: GPL 3.0
# Description: UI for Design tab

import bpy
from bpy_extras.node_utils import find_node_input
from bpy.types import Panel


class DesignPanel:
    """Base Class for Design Panel"""

    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "BSlides"


class BSLIDES_PT_design(DesignPanel, Panel):
    """Panel for slide design"""

    bl_idname = "BSLIDES_PT_design"
    bl_label = "Design"

    @classmethod
    def poll(cls, context):
        return True

    def draw(self, context):
        layout = self.layout
        col = layout.column(align=True)
        col.operator("bslides.copy_to_all", text="Copy objects")
        col.operator(
            "bslides.center_object", text="Center Object"
        ).copy_rotation = False
        col.operator("bslides.center_3d_cursor", text="Center 3D Cursor")


class BSLIDES_PT_background(DesignPanel, Panel):
    """Panel for slide background color"""

    bl_parent_id = "BSLIDES_PT_design"
    bl_label = "Background Color"
    bl_options = {"DEFAULT_CLOSED"}

    @classmethod
    def poll(cls, context):
        return True

    def draw(self, context):
        layout = self.layout
        world = context.scene.world

        if world:
            layout.prop(world, "use_nodes", icon="NODETREE")

        layout.use_property_split = True

        if not world:
            layout.label(text="Scene has no world!", icon="ERROR")

        elif world.use_nodes:
            ntree = world.node_tree
            node = ntree.get_output_node("EEVEE")

            if node:
                input = find_node_input(node, "Surface")
                if input:
                    layout.template_node_view(ntree, node, input)
                else:
                    layout.label(text="Incompatible output node")
            else:
                layout.label(text="No output node")
        else:
            layout.prop(world, "color")

        layout.separator()

        row = layout.row(align=True)
        if world:
            row.operator("bslides.apply_all_slide_background", text="Apply to All")
        row.operator("bslides.reset_slide_background", text="Reset")


class BSLIDES_PT_template(DesignPanel, Panel):
    """Panel for slide tempalte"""

    bl_parent_id = "BSLIDES_PT_design"
    bl_label = "Template"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        layout = self.layout

        row = layout.row(align=True)
        row.prop(context.scene.bslides, "template", text="")
        row.operator("bslides.new_template", icon="ADD", text="")

        row = layout.row(align=True)
        template = context.scene.bslides.template
        if template != "NONE":
            if template in [c.name for c in context.scene.collection.children]:
                row.operator("bslides.unlink_template", text="Unlink")
            else:
                row.operator("bslides.apply_template", text="Apply")


class BSLIDES_PT_slide_ratio(DesignPanel, Panel):
    """Panel for slide ratio"""

    bl_parent_id = "BSLIDES_PT_design"
    bl_label = "Slide Ratio"
    bl_options = {"DEFAULT_CLOSED"}

    @classmethod
    def poll(cls, context):
        return True

    def draw(self, context):
        layout = self.layout

        rd = context.scene.render
        row = layout.row(align=True)
        row.prop(rd, "resolution_x", text="")
        row.prop(rd, "resolution_y", text="")

        row = layout.row(align=True)
        row.operator("bslides.apply_all_resolution", text="Apply to All")


classes = (
    BSLIDES_PT_design,
    BSLIDES_PT_background,
    BSLIDES_PT_template,
    BSLIDES_PT_slide_ratio,
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
