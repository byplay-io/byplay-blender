#  exec(open("/Users/vadim/projects/byplay/byplay-blender/io_import_byplay_scene.py").read())
import bpy
from byplay.recording_local_storage import RecordingLocalStorage
from byplay.blender_scene_loader import BlenderSceneLoader


class ByplayImportOperator(bpy.types.Operator):
    bl_idname = "object.byplay_import_operator"
    bl_label = "Byplay"

    @staticmethod
    def _get_recording_ids_search(_scene, _context):
        return list(
            reversed(
                sorted(
                    map(lambda x: (x, x, ""), RecordingLocalStorage().list_recording_ids())
                )
            )
        )

    recording_id: bpy.props.EnumProperty(name="Recording id", items=_get_recording_ids_search)
    create_compositing_nodes: bpy.props.BoolProperty(name="Create compositing nodes", default=True)
    use_exr: bpy.props.BoolProperty(name="Set EXR environment", default=True)

    def execute(self, context):
        loader = BlenderSceneLoader(
            recording_id=self.recording_id,
            context=context,
            report=self.report
        )
        loader.load_scene()
        if self.create_compositing_nodes:
            loader.load_compositing()
        if self.use_exr:
            loader.load_exrs()
        self.report({'INFO'}, "Loaded recording {}".format(self.recording_id))

        return {'FINISHED'}

    def invoke(self, context, _event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

    def draw(self, context):
        layout = self.layout
        col = layout.column()
        col.label(text="Importing a Byplay recording")
        col.prop(self, "recording_id")
        row = col.row()
        row.prop(self, "create_compositing_nodes")
        row = col.row()
        row.prop(self, "use_exr")

    @staticmethod
    def menu_func(self, context):
        self.layout.operator(ByplayImportOperator.bl_idname, text="Byplay Camera Recording")

    @staticmethod
    def register():
        bpy.utils.register_class(ByplayImportOperator)
        bpy.types.TOPBAR_MT_file_export.append(ByplayImportOperator.menu_func)

    @staticmethod
    def unregister():
        bpy.utils.unregister_class(ByplayImportOperator)
        bpy.types.TOPBAR_MT_file_export.remove(ByplayImportOperator.menu_func)
