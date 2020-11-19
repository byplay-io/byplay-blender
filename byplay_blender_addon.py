import os
import bpy
import sys

os.environ["BYPLAY_SYSTEM_DATA_PATH"] = "/Users/vadim/Library/Application Support/Byplay Desktop/preferences.json"

byplay_plugin_path = "/Users/vadim/projects/byplay/byplay-blender"
if byplay_plugin_path not in sys.path:
    sys.path.append(byplay_plugin_path)

bl_info = {
    "name": "Import: Byplay Camera Recording",
    "description": "Import Byplay's recorded camera tracking, point cloud and exr",
    "author": "Vadim Lobanov (Byplay)",
    "version": (0, 0, 1),
    "blender": (2, 80, 0),
    "location": "File > Import > Byplay Camera Recording",
    "warning": "",
    "doc_url": "https://byplay.io/docs/blender",
    "category": "Import-Export",
}

from byplay.byplay_import_operator import ByplayImportOperator


def menu_func(self, context):
    self.layout.operator(ByplayImportOperator.bl_idname, text="Byplay Camera Recording")


def register():
    bpy.utils.register_class(ByplayImportOperator)
    bpy.types.TOPBAR_MT_file_import.append(menu_func)


def unregister():
    bpy.utils.unregister_class(ByplayImportOperator)
    bpy.types.TOPBAR_MT_file_import.remove(menu_func)


if __name__ == "__main__":
    register()