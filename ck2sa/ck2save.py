import json
import subprocess
from collections import OrderedDict

from .exceptions import Ck2JsonError


IGNORED_KEYS = ("ironman", "count", "player_portrait", "game_speed", "mapmode", "dyn_title", "unit", "sub_unit",
                "delayed_event", "relation", "religion", "religion_group", "culture", "culture_group", "bloodline",
                "active_ambition", "active_focus", "active_plot", "active_faction", "combat", "war", "active_war",
                "previous_war", "next_outbreak_id", "disease_outbreak", "disease", "offmap_powers", "wonder_upgrade",
                "generated_societies", "generated_artifacts", "trade_route", "vc_data", "achievement")


class Ck2Save:
    def __init__(self, ck2json_exe_p, ck2_save_path):
        self._ck2json_exe_p = ck2json_exe_p
        self._ck2_save_path = ck2_save_path

        print(f"Running ck2json.exe against '{self._ck2_save_path}'...\n")
        try:
            completed_process = subprocess.run([str(self._ck2json_exe_p), str(self._ck2_save_path)],
                                                capture_output=True, check=True)
        except subprocess.CalledProcessError as e:
            stderr = e.stderr.decode("utf8")
            raise Ck2JsonError(f"ck2json.exe failed with: [{e.returncode}] {stderr}") from e
        # Parse the json output of ck2json with a special object_pairs_hook to deal with repeated keys
        self._json = json.loads(completed_process.stdout, object_pairs_hook=Ck2Save.parse_object_pairs)
        # Delete the completed_process to preserve some memory now that it is no longer required
        del completed_process

    @property
    def _keys(self):
        return [k for k in self._json.keys()]

    @property
    def version(self):
        return self._json["version"]

    @property
    def start_date(self):
        return self._json["start_date"]

    @property
    def date(self):
        return self._json["date"]

    @property
    def player_id(self):
        return str(self._json["player"]["id"])

    @property
    def player_name(self):
        return self._json["player_name"]

    @property
    def player_age(self):
        return self._json["player_age"]

    # Adapted https://stackoverflow.com/a/14902564
    @staticmethod
    def parse_object_pairs(pairs):
        def make_unique(key, d):
            unique_key, counter = key, 0
            while unique_key in d:
                counter += 1
                unique_key = f"{key}_{counter}"
            return unique_key

        d = OrderedDict()
        for key, value in pairs:
            if key in IGNORED_KEYS:
                continue
            if key in d:
                key = make_unique(key, d)
            d[key] = value
        return d
