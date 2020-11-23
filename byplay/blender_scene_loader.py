import logging
import bpy
from byplay.recording_local_storage import RecordingLocalStorage


class BlenderSceneLoader:
    def __init__(self, recording_id: str, report, context):
        self.recording_id = recording_id
        self.report = report
        self.context = context
        self.recording_storage = RecordingLocalStorage()
        self.blend_path = self.recording_storage.blend_path(self.recording_id)
        self.camera_object = None
        self.compositing_group = None

    def _copy_scene_properties(self, scene_from, scene_to):
        scene_to.render.resolution_x = scene_from.render.resolution_x
        scene_to.render.resolution_y = scene_from.render.resolution_y
        scene_to.render.fps = scene_from.render.fps
        scene_to.frame_end = scene_from.frame_end

    def load_scene(self, with_compositing=False):
        with bpy.data.libraries.load(self.blend_path) as (data_from, data_to):
            data_to.scenes = data_from.scenes
            data_to.objects = data_from.objects
            if with_compositing:
                data_to.node_groups = data_from.node_groups

        for group in data_to.node_groups:
            if group is not None:
                self.compositing_group = group

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
            self.report({'INFO'}, "No exrs found")
            return

        existing = set([n for n in bpy.data.images])
        for exr_path in exrs:
            bpy.ops.image.open(filepath=exr_path)

        newly_added = set([n for n in bpy.data.images]).difference(existing)
        loaded = []
        for i in newly_added:
            i.name = "ENV_{}_{}".format(self.recording_id, i.name)
            loaded.append(i.name)

        some_exr = None
        for img in bpy.data.images:
            if img.filepath in exrs:
                some_exr = img
                break

        if some_exr is None:
            return

        self.report({'INFO'}, "Loaded exr images: {}; setting {} as world environment".format(loaded, some_exr.name))
        world = self.context.scene.world
        env_texture = None
        for k in world.node_tree.nodes:
            if k.type == "TEX_ENVIRONMENT" and 'byplay' in k:
                self.report({'INFO'}, "Found existing world TexEnvironment, setting env")
                env_texture = k
        if env_texture is None:
            self.report({'INFO'}, "Creating world TexEnvironment")
            env_texture = world.node_tree.nodes.new("ShaderNodeTexEnvironment")
            env_texture['byplay'] = True
        env_texture.image = some_exr

        self.context.scene.world.node_tree.links.new(
            env_texture.outputs[0],
            world.node_tree.nodes["Background"].inputs[0]
        )

    def load_compositing(self):
        self.context.scene.use_nodes = True
        self.context.scene.render.film_transparent = True
        node_tree = self.context.scene.node_tree

        if self.compositing_group is None:
            self.report({'WARNING'}, "Byplay compositing group didn't load")
            return

        group_instance = node_tree.nodes.new("CompositorNodeGroup")
        group_instance.node_tree = self.compositing_group
        group_instance.width = 250
        all_render_layers = [n for n in node_tree.nodes if n.type == "R_LAYERS"]
        if len(all_render_layers) > 0:
            render_layer = all_render_layers[0]
            node_tree.links.new(render_layer.outputs[0], group_instance.inputs[0])
            self.report({"INFO"}, "Connecting byplay node to Render Layers")

        all_composites = [n for n in node_tree.nodes if n.type == "COMPOSITE"]
        if len(all_composites) > 0:
            composite = all_composites[0]
            node_tree.links.new(group_instance.outputs[0], composite.inputs[0])
            self.report({"INFO"}, "Connecting byplay node to Composite")
