import bpy
import logging
from byplay.recording_local_storage import RecordingLocalStorage


class BlenderSceneLoader:
    def __init__(self, recording_id: str, report, context):
        self.recording_id = recording_id
        self.report = report
        self.context = context
        self.recording_storage = RecordingLocalStorage()
        self.blend_path = self.recording_storage.blend_path(self.recording_id)
        self.camera_object = None

    def _copy_scene_properties(self, scene_from, scene_to):
        scene_to.render.resolution_x = scene_from.render.resolution_x
        scene_to.render.resolution_y = scene_from.render.resolution_y
        scene_to.render.fps = scene_from.render.fps
        scene_to.frame_end = scene_from.frame_end

    def load_scene(self):
        with bpy.data.libraries.load(self.blend_path) as (data_from, data_to):
            data_to.scenes = data_from.scenes
            data_to.objects = data_from.objects

        current_scene = self.context.scene
        for scene in data_to.scenes:
            if scene is not None:
                self._copy_scene_properties(scene, current_scene)
                bpy.data.scenes.remove(scene)

        recording_collection = bpy.data.collections.new("Byplay_" + self.recording_id)
        current_scene.collection.children.link(recording_collection)
        objects = []
        for obj in data_to.objects:
            if obj is not None:
                recording_collection.objects.link(obj)
                objects.append(obj)
                if type(obj.data) == bpy.types.Camera:
                    self.camera_object = obj

    def load_exrs(self):
        exrs = self.recording_storage.list_env_exr_paths(self.recording_id)

        if len(exrs) == 0:
            return

        existing = set([n for n in bpy.data.images])
        for exr_path in exrs:
            bpy.ops.image.open(filepath=exr_path)

        newly_added = set([n for n in bpy.data.images]).difference(existing)
        for i in newly_added:
            i.name = "ENV_{}_{}".format(self.recording_id, i.name)

        some_exr = None
        for img in bpy.data.images:
            if img.filepath in exrs:
                some_exr = img
                break

        if some_exr is None:
            return
        world = self.context.scene.world
        env_texture = world.node_tree.nodes.new("ShaderNodeTexEnvironment")
        env_texture.image = some_exr

        self.context.scene.world.node_tree.links.new(
            env_texture.outputs[0],
            world.node_tree.nodes["Background"].inputs[0]
        )

    def load_compositing(self):
        self.context.scene.use_nodes = True
        self.context.scene.render.film_transparent = True

        if self.camera_object is None:
            self.report({'WARN'}, "Byplay camera didn't load")

        image_node = self.context.scene.node_tree.nodes.new("CompositorNodeImage")
        image_node.label = "Byplay_{}".format(self.recording_id)
        self.report({'INFO'}, "Created compositing node {}".format(image_node.label))

        image_node.image = self.camera_object.data.background_images[0].image
        image_node.frame_duration = self.context.scene.frame_end
