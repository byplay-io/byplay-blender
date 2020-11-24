bl_info = {
    "name": "Import: Byplay Camera Recording",
    "description": "Import Byplay's recorded camera tracking, point cloud and exr",
    "author": "Vadim Lobanov (Byplay)",
    "version": (1, 0, 1),
    "blender": (2, 80, 0),
    "location": "File > Import > Byplay Camera Recording",
    "warning": "",
    "doc_url": "https://byplay.io/docs/blender",
    "category": "Import",
}

import os
import sys
import logging

os.environ["BYPLAY_SYSTEM_DATA_PATH"] = "/Users/vadim/Library/Application Support/Byplay Desktop/preferences.json"
os.environ["BYPLAY_PLUGIN_LOG_PATH"] = "/Users/vadim/Library/Application Support/Byplay Desktop/blender.log"

byplay_plugin_path = "/Users/vadim/projects/byplay/byplay-blender"

if byplay_plugin_path not in sys.path:
    sys.path.append(byplay_plugin_path)


def menu_func(self, context):
    from byplay.byplay_import_operator import ByplayImportOperator
    self.layout.operator(ByplayImportOperator.bl_idname, text="Byplay Camera Recording")


def register():
    import bpy
    from byplay.byplay_import_operator import ByplayImportOperator
    from byplay.config import Config

    Config.setup_logger()

    logging.info("Registering Byplay plugin from " + byplay_plugin_path)
    bpy.utils.register_class(ByplayImportOperator)
    bpy.types.TOPBAR_MT_file_import.append(menu_func)


def unregister():
    import bpy
    from byplay.byplay_import_operator import ByplayImportOperator
    logging.info("Unregistering Byplay plugin from " + byplay_plugin_path)
    bpy.utils.unregister_class(ByplayImportOperator)
    bpy.types.TOPBAR_MT_file_import.remove(menu_func)


if __name__ == "__main__":
    register()
