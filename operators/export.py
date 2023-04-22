# File: export.py
# Author: Ronald Telmanik
# Licence: GPL 3.0
# Description: Functionality for exporting

import subprocess
import sys
import os
import bpy
from bpy.types import Operator
import bpy
from .utils import get_python_path


class BSLIDES_OT_install_packages(Operator):
    """Installs Python packages into Blender for PDF export"""

    bl_idname = "bslides.install_packages"
    bl_label = "Install Packages"

    @classmethod
    def poll(cls, context):
        try:
            import PIL

            return False
        except ModuleNotFoundError:
            return True

    @classmethod
    def install_python_user_path(cls):
        """Install python into user sys.path"""
        # python --user path location is not in sys.path by default
        python_path = get_python_path()
        user_path = subprocess.check_output(
            [str(python_path), "-m", "site", "--user-site"]
        )

        # convert from byte to string without whitespaces
        user_path = user_path.decode("utf-8").strip()

        # in case it is not in path already
        if user_path not in sys.path:
            sys.path.append(user_path)

    def execute(self, context):
        python_path = get_python_path()

        subprocess.call([str(python_path), "-m", "ensurepip", "--user"])

        subprocess.call(
            [str(python_path), "-m", "pip", "install", "--user", "--upgrade", "pip"]
        )
        package_name = "Pillow"
        subprocess.call(
            [str(python_path), "-m", "pip", "install", "--user", package_name]
        )

        self.report({"INFO"}, "All set and done. PDF export now available")

        return {"FINISHED"}


class BSLIDES_OT_export_images(Operator):
    """This operator exportes all scenes as PDF file"""

    bl_idname = "bslides.export_scenes"
    bl_label = "Export Presentation"

    @classmethod
    def poll(cls, context):
        # Pillow is necessary for operator to work
        try:
            from PIL import Image

            return True
        except ModuleNotFoundError:
            return False

    def execute(self, context):
        addon = context.window_manager.bslides

        if addon.visible_slides and addon.hidden_slides:
            scenes = bpy.data.scenes
        elif addon.visible_slides:
            scenes = [s for s in bpy.data.scenes if s.bslides.render_slide]
        elif addon.hidden_slides:
            scenes = [s for s in bpy.data.scenes if not s.bslides.render_slide]

        path = lambda name: os.path.join(addon.output_directory, name)

        for scn in scenes:
            scn.render.filepath = path(scn.name)
            scn.render.image_settings.file_format = "JPEG"
            bpy.ops.render.render(write_still=True, use_viewport=True, scene=scn.name)

        if addon.file_format == "PDF":
            # start new pdf
            from PIL import Image

            # open exported images
            scene_images = []
            for img in scenes:
                scene_images.append(Image.open(path(f"{img.name}.JPG")))

            # start with first one add all another
            scene_images[0].save(
                path(f"{addon.file_name}.PDF"),
                "PDF",
                resolution=100.0,
                save_all=True,
                append_images=scene_images[1:],
            )

            # close and remove images
            for img in scene_images:
                img.close()
                os.remove(img.filename)

        return {"FINISHED"}


classes = (
    BSLIDES_OT_install_packages,
    BSLIDES_OT_export_images,
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
