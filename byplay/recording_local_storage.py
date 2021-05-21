import os
import logging
from byplay.config import Config
from os.path import join


class RecordingLocalStorage:
    def list_recording_ids(self):
        Config.read()
        recs = os.listdir(Config.recordings_dir())
        logging.info("List of files: {} -> {}".format(Config.recordings_dir(), recs))
        extracted = [rec_id for rec_id in recs if self.is_extracted(rec_id)]
        return list(sorted(extracted))

    def blend_path(self, recording_id):
        legacy_path = join(self.full_path(recording_id), "byplay_{}.blend".format(recording_id))
        ar_path = join(self.full_path(recording_id), "byplay_{}_ar_v1.blend".format(recording_id))
        if os.path.exists(ar_path):
            return ar_path
        return legacy_path

    def list_env_exr_paths(self, recording_id):
        assets_path = join(Config.recordings_dir(), recording_id, 'assets')
        paths = [join(assets_path, p) for p in os.listdir(assets_path) if p.endswith(".exr")]
        return paths

    def full_path(self, recording_id: str) -> str:
        return join(Config.recordings_dir(), recording_id)

    def is_extracted(self, recording_id: str):
        path = join(self.full_path(recording_id), ".extracted")
        exists = os.path.exists(path)
        logging.info("rec: {} / {}".format(path, exists))
        return exists