#  exec(open("/Users/vadim/projects/byplay/byplay-blender/io_import_byplay_scene.py").read())
import bpy
import logging

from byplay.backend.amplitude_logger import log_amplitude
from byplay.backend.sentry import capture_exception
from byplay.recording_local_storage import RecordingLocalStorage
from byplay.blender_scene_loader import BlenderSceneLoader


def _get_recording_ids_search(_scene, _context):
    try:
        return list(
            reversed(
                sorted(
                    map(lambda x: (x, x, ""), RecordingLocalStorage().list_recording_ids())
                )
            )
        )
    except Exception as e:
        capture_exception()
        raise e


class ByplayImportOperator(bpy.types.Operator):
    bl_idname = "object.byplay_import_operator"
    bl_label = "Byplay"

    recording_id: bpy.props.EnumProperty(name="Recording id", items=_get_recording_ids_search)
    create_compositing_nodes: bpy.props.BoolProperty(name="Create compositing nodes", default=True)
    use_exr: bpy.props.BoolProperty(name="Set EXR environment", default=True)

    def _import_recording(self, context):
        log_amplitude("Blender import operator executed", recording_id=self.recording_id)
        logging.info(
            "Executing, rec id: {}, ccn: {}, exr: {}".format(
                self.recording_id,
                self.create_compositing_nodes,
                self.use_exr
            )
        )
        loader = BlenderSceneLoader(
            recording_id=self.recording_id,
            context=context,
            report=self.report
        )
        loader.load_scene(with_compositing=self.create_compositing_nodes)
        if self.create_compositing_nodes:
            loader.load_compositing()
        if self.use_exr:
            loader.load_exrs()
        self.report({'INFO'}, "Loaded recording {}".format(self.recording_id))
        logging.info("Success loaded " + self.recording_id)

    def execute(self, context):
        try:
            self._import_recording(context)
        except Exception as e:
            capture_exception()
            raise e

        return {'FINISHED'}

    def invoke(self, context, _event):
        try:
            wm = context.window_manager
            log_amplitude("Blender import operator opened")
            return wm.invoke_props_dialog(self)
        except Exception as e:
            capture_exception()
            raise e

    def _draw(self, _context):
        layout = self.layout
        col = layout.column()
        col.label(text="Importing a Byplay recording")
        col.prop(self, "recording_id")
        row = col.row()
        row.prop(self, "create_compositing_nodes")
        row = col.row()
        row.prop(self, "use_exr")

    def draw(self, context):
        try:
            self._draw(context)
        except Exception as e:
            capture_exception()
            raise e