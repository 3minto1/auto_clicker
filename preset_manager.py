import json
import os


class PresetManager:
    def __init__(self, presets_file="presets.json"):
        self.presets_file = presets_file
        self.presets = {}
        self._load_presets()

    def _load_presets(self):
        if os.path.exists(self.presets_file):
            with open(self.presets_file, 'r') as f:
                self.presets = json.load(f)

    def _save_presets(self):
        with open(self.presets_file, 'w') as f:
            json.dump(self.presets, f, indent=2, ensure_ascii=False)

    def get_preset_names(self):
        return list(self.presets.keys())

    def get_preset(self, name):
        return self.presets.get(name, None)

    def save_preset(self, name, config):
        self.presets[name] = config
        self._save_presets()

    def delete_preset(self, name):
        if name in self.presets:
            del self.presets[name]
            self._save_presets()
            return True
        return False

    def rename_preset(self, old_name, new_name):
        if old_name in self.presets and new_name not in self.presets:
            self.presets[new_name] = self.presets.pop(old_name)
            self._save_presets()
            return True
        return False
