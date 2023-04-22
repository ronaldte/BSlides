# File: text.py
# Author: Ronald Telmanik
# Licence: GPL 3.0
# Description: Functionality for text

import bpy
from bpy.types import Operator
from bpy.props import (
    EnumProperty,
    StringProperty,
    BoolProperty,
    IntProperty,
    FloatProperty,
    FloatVectorProperty,
)
from datetime import datetime
from mathutils import Vector
from .utils import (
    camera_center,
    create_title,
)


class BSLIDES_OT_change_case_text(Operator):
    """Changes text to all uppercase"""

    bl_idname = "bslides.upper_case"
    bl_label = "Text All Uppercase"
    bl_options = {"REGISTER", "UNDO"}

    case: EnumProperty(
        name="Text CaseType",
        description="Type of case to convert text to",
        items=(
            ("UPPER", "UPPERCASE", "Convert text in all UPPERCASE"),
            ("LOWER", "lowercase", "Convert text in all lowercase"),
        ),
        default="UPPER",
    )

    @classmethod
    def poll(cls, context):
        ob = context.object
        return ob and ob.type == "FONT"

    def execute(self, context):
        ob = context.object
        text = ob.data.body
        case = self.case

        if case == "UPPER":
            text = text.upper()
        elif case == "LOWER":
            text = text.lower()

        ob.data.body = text

        return {"FINISHED"}


class BSLIDES_OT_generate_date_time(Operator):
    """Creates new text object with current date"""

    bl_idname = "bslides.date_text"
    bl_label = "Generate Date"
    bl_options = {"REGISTER", "UNDO"}

    separator: StringProperty(
        name="Date Separator",
        description="Character used to separate date parts",
        default="-",
    )

    time: BoolProperty(
        name="Include time",
        description="Add current time to the date",
        default=False,
    )

    time_new_line: BoolProperty(
        name="Time Underneath Date",
        description="Format so Time is below date",
        default=True,
    )

    time_format: EnumProperty(
        name="Time Format",
        description="Time format in text object",
        items=(
            ("24", "24H", "Use time in 24H day format"),
            ("12", "12H", "Use time in 12H day format"),
        ),
        default="24",
    )

    @classmethod
    def poll(cls, context):
        return True

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True

        layout.prop(self, "separator", text="Date Separator")

        row = layout.row(heading="Time")
        row.prop(self, "time", text="")
        if self.time:
            row = layout.row(align=True, heading="Format")
            row.prop(self, "time_format", expand=True)
            row = layout.row(heading="Position")
            row.prop(self, "time_new_line", text="Below")

    def execute(self, context):
        text_dat = bpy.data.curves.new(type="FONT", name="Date")
        text_dat.align_x = "CENTER"

        spr = self.separator

        now = datetime.today()
        text_dat.body = now.strftime(f"%d{spr}%m{spr}%Y")

        if self.time_new_line:
            spr = "\n"
        else:
            spr = " "

        if self.time:
            if self.time_format == "24":
                text_dat.body += now.strftime(f"{spr}%H:%M")
            if self.time_format == "12":
                text_dat.body += now.strftime(f"{spr}%I:%M %p")

        text_obj = bpy.data.objects.new(name="Date", object_data=text_dat)
        context.scene.collection.objects.link(text_obj)

        return {"FINISHED"}


class BSLIDES_OT_indentation(Operator):
    """Adds or removes indentation"""

    bl_idname = "bslides.indentation"
    bl_label = "Indentate Text"
    bl_options = {"REGISTER", "UNDO"}

    direction: EnumProperty(
        name="Text Indentation",
        description="Direction of text indendation",
        items=(
            ("IN", "Indentation", "Add space to before line"),
            ("OUT", "Outdent", "Remove space from beforetext"),
        ),
        default="IN",
    )

    spaces: IntProperty(
        name="Number of Spaces",
        default=4,
        description="Number of spaces used in indent or outdent",
    )

    @classmethod
    def poll(cls, context):
        ob = context.object
        return ob and ob.type == "FONT"

    def execute(self, context):
        dr = self.direction
        spc = self.spaces
        ob = context.object
        txt = ob.data.body.splitlines()

        if dr == "IN":
            txt = [f"{' '*spc}{line}" for line in txt]

        elif dr == "OUT":
            new_txt = []
            for line in txt:
                ldng_spc = len(line) - len(line.lstrip())
                if ldng_spc > spc:
                    new_txt.append(line[spc:])
                else:
                    new_txt.append(line.lstrip())
            txt = new_txt

        ob.data.body = "\n".join(txt)

        return {"FINISHED"}


class BSLIDES_OT_merge_text(Operator):
    """Merges all text objects into one"""

    bl_idname = "bslides.merge_text"
    bl_label = "Merge Text"
    bl_options = {"REGISTER", "UNDO"}

    new_line_divide: BoolProperty(
        name="Separate Objects",
        description="Separate each text object with new line",
        default=True,
    )

    @classmethod
    def poll(cls, context):
        return all([o.type == "FONT" for o in context.selected_objects])

    def execute(self, context):
        objs = context.selected_objects
        text_objs = [o for o in objs if o.type == "FONT"]

        sep = "\n" if self.new_line_divide else ""

        for o in text_objs[1:]:
            text_objs[0].data.body += sep + o.data.body
            context.scene.collection.objects.unlink(o)

        return {"FINISHED"}


class BSLIDES_OT_horizontal_alignment(Operator):
    """Changes text horizontal alignment"""

    bl_idname = "bslides.horizontal_alignment"
    bl_label = "Horizontal Text Alignment"
    bl_options = {"REGISTER", "UNDO"}

    side: EnumProperty(
        name="Horizontal Text Alignment Side",
        description="Side to which align text horizontally",
        items=(
            ("LEFT", "Left", "Allign text with left margin"),
            ("RIGHT", "Right", "Allign text with right margin"),
            ("CENTER", "Center", "Center content within text box"),
            ("JUSTIFY", "Justify", "Distribute text evenlty in text box"),
        ),
        default="LEFT",
    )

    @classmethod
    def poll(cls, context):
        ob = context.object
        return ob and ob.type == "FONT"

    def execute(self, context):
        side = self.side
        context.object.data.align_x = side

        return {"FINISHED"}


class BSLIDES_OT_align_text_objects(Operator):
    """Align Text Objects based on selected"""

    bl_idname = "bslides.align_text_objects"
    bl_label = "Align Text Objects"
    bl_options = {"REGISTER", "UNDO"}

    spacing: FloatProperty(
        name="Spacing",
        description="Spacing size between joined text",
        default=-1,
    )

    @classmethod
    def poll(cls, context):
        text_objs = [o.type == "FONT" for o in context.selected_objects]
        return text_objs and all(text_objs)

    def execute(self, context):
        objs = context.selected_objects

        pivot_ob = objs[0]
        inv = pivot_ob.rotation_euler.to_matrix()
        inv.invert()

        # stacking object on each other e.g y-axis
        move_vec = Vector((0.0, self.spacing, 0.0))

        # aligne vector to local axis in Blender
        vec_rot = move_vec @ inv

        for idx, obj in enumerate(objs[1:], start=1):
            obj.location = pivot_ob.location + idx * vec_rot
            obj.rotation_euler = pivot_ob.rotation_euler

        return {"FINISHED"}


class BSLIDES_OT_generate_toc(Operator):
    """Generates Table of Contents from slides"""

    bl_idname = "bslides.generate_toc"
    bl_label = "Generate Table of Contents"
    bl_options = {"REGISTER", "UNDO"}

    bullet_point: StringProperty(
        name="Bullet Point Style",
        description="Character used to start each title line",
        default="-",
    )

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        text_dat = bpy.data.curves.new(type="FONT", name="ToC")
        text_dat.body = ""

        scenes = [s for s in bpy.data.scenes if s.bslides.render_slide]

        for s in scenes:
            titles = [t for t in s.objects if t.name.lower().startswith("title")]

            if len(titles) > 1:
                self.report({"INFO"}, f"{s.name} has multiple titles")

            if titles:
                text_dat.body += f"{self.bullet_point} {titles[0].data.body}\n"

        text_obj = bpy.data.objects.new(name="ToC", object_data=text_dat)
        context.scene.collection.objects.link(text_obj)

        return {"FINISHED"}


class BSLIDES_OT_add_text_color(Operator):
    """Create New RGB Color for Text Object"""

    bl_idname = "bslides.add_text_color"
    bl_label = "Add RGB Text Color"
    bl_options = {"REGISTER", "UNDO"}

    color: FloatVectorProperty(
        name="Color",
        description="Color used for text object",
        subtype="COLOR",
        size=4,
        default=(1, 1, 1, 1),
        max=1.0,
        min=0.0,
    )

    @classmethod
    def poll(cls, context):
        return context.object

    def execute(self, context):
        ob = context.object

        mat = bpy.data.materials.new("Color")
        mat.use_nodes = True

        # reset default nodes
        mat.node_tree.nodes.remove(mat.node_tree.nodes.get("Principled BSDF"))

        output_node = mat.node_tree.nodes.get("Material Output")
        output_node.location = (200, 0)
        rgb_node = mat.node_tree.nodes.new("ShaderNodeRGB")

        mat.node_tree.links.new(rgb_node.outputs["Color"], output_node.inputs[0])

        # set material color
        rgb_node.outputs[0].default_value = self.color

        # set material for 0th position
        materials = list(ob.data.materials)

        ob.data.materials.clear()
        ob.data.materials.append(mat)

        for m in materials:
            ob.data.materials.append(m)

        return {"FINISHED"}


class BSLIDES_OT_new_font_style(Operator):
    """Creates a new font style"""

    bl_idname = "bslides.new_font_style"
    bl_label = "Add New Font Style"

    @classmethod
    def poll(cls, context):
        ob = context.object
        return ob and ob.type == "FONT"

    def execute(self, context):
        wm = context.window_manager
        fs = wm.bslides.font_styles
        ob = context.object

        item = fs.add()
        item.source_ob = ob.data

        wm.bslides.font_styles_index = len(fs) - 1

        return {"FINISHED"}


class BSLIDES_OT_delete_font_style(Operator):
    """Removes currently selected font style"""

    bl_idname = "bslides.delete_font_style"
    bl_label = "Remove Selected Font Style"

    @classmethod
    def poll(cls, context):
        ob = context.object
        return ob and ob.type == "FONT"

    def execute(self, context):
        wm = context.window_manager
        fs = wm.bslides.font_styles
        fs_idx = wm.bslides.font_styles_index

        fs.remove(fs_idx)

        wm.bslides.font_styles_index = min(max(0, fs_idx - 1), len(fs) - 1)

        return {"FINISHED"}


class BSLIDES_OT_apply_font_style(Operator):
    """Apply selected font style to selected object"""

    bl_idname = "bslides.apply_font_style"
    bl_label = "Apply Font Style"

    @classmethod
    def poll(cls, context):
        ob = context.object
        fs = context.window_manager.bslides.font_styles
        return ob and fs and ob.type == "FONT"

    def execute(self, context):
        ob = context.object
        fs = context.window_manager.bslides.font_styles
        fs_idx = context.window_manager.bslides.font_styles_index
        style = fs[fs_idx].source_ob

        props = [p.identifier for p in style.bl_rna.properties if not p.is_readonly]

        for p in props:
            if (not p.startswith("texspace")) and (p not in ["name", "body"]):
                setattr(ob.data, p, getattr(style, p))

        return {"FINISHED"}


class BSLIDES_OT_new_title(Operator):
    """Creates new title"""

    bl_idname = "bslides.new_title"
    bl_label = "New Slide Title"

    @classmethod
    def poll(cls, content):
        return True

    def execute(self, context):

        scene = context.scene
        cam = scene.camera

        create_title(cam, scene)

        return {"FINISHED"}


class BSLIDES_OT_convert_title(Operator):
    """Convert existing text to title"""

    bl_idname = "bslides.convert_title"
    bl_label = "Convert Text Title"
    bl_options = {"REGISTER", "UNDO"}

    copy_rot: BoolProperty(
        name="Copy Rotation", default=True, description="Copy rotation of camera"
    )
    center_loc: BoolProperty(
        name="Center Location", default=True, description="Center title location"
    )

    @classmethod
    def poll(cls, context):
        ob = context.object
        return ob and ob.type == "FONT"

    def execute(self, context):
        scene = context.scene
        cam = scene.camera

        ob = context.object
        ob.name = f"Title_{ob.name}"

        if self.copy_rot:
            ob.rotation_euler = cam.rotation_euler

        if self.center_loc:
            ob.location = camera_center(cam, scene)
            ob.data.align_x = "CENTER"
            ob.data.align_y = "CENTER"

        return {"FINISHED"}


classes = (
    BSLIDES_OT_change_case_text,
    BSLIDES_OT_generate_date_time,
    BSLIDES_OT_indentation,
    BSLIDES_OT_merge_text,
    BSLIDES_OT_horizontal_alignment,
    BSLIDES_OT_align_text_objects,
    BSLIDES_OT_generate_toc,
    BSLIDES_OT_add_text_color,
    BSLIDES_OT_new_font_style,
    BSLIDES_OT_delete_font_style,
    BSLIDES_OT_apply_font_style,
    BSLIDES_OT_new_title,
    BSLIDES_OT_convert_title,
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
