import json
import subprocess
from collections import OrderedDict
from datetime import date

from .exceptions import CK2JsonError


IGNORED_KEYS = ("ironman", "count", "player_portrait", "game_speed", "mapmode", "dyn_title", "unit", "sub_unit",
                "delayed_event", "relation", "religion", "religion_group", "culture", "culture_group", "bloodline",
                "active_ambition", "active_focus", "active_plot", "active_faction", "combat", "war", "active_war",
                "previous_war", "next_outbreak_id", "disease_outbreak", "disease", "offmap_powers", "wonder_upgrade",
                "generated_societies", "generated_artifacts", "trade_route", "vc_data", "achievement")


class CK2Save:
    _title_map = {"b": {"t": "Barony", "m": "Baron", "f": "Baroness"},
                  "c": {"t": "County", "m": "Count", "f": "Countess"},
                  "d": {"t": "Duchy", "m": "Duke", "f": "Duchess"},
                  "k": {"t": "Kingdom", "m": "King", "f": "Queen"},
                  "e": {"t": "Empire", "m": "Emperor", "f": "Empress"}}

    def __init__(self, ck2json_exe_p, ck2_save_path):
        self._ck2json_exe_p = ck2json_exe_p
        self._ck2_save_path = ck2_save_path

        try:
            completed_process = subprocess.run([str(self._ck2json_exe_p), str(self._ck2_save_path)],
                                                capture_output=True, check=True)
        except subprocess.CalledProcessError as e:
            stderr = e.stderr.decode("utf8")
            raise CK2JsonError(f"ck2json.exe failed with: [{e.returncode}] {stderr}") from e
        # Parse the json output of ck2json with a special object_pairs_hook to deal with repeated keys
        self._json = json.loads(completed_process.stdout, object_pairs_hook=CK2Save.parse_object_pairs)
        # Delete the completed_process to preserve some memory now that it is no longer required
        del completed_process

        self.player_character = self._json["character"][self.player_id]

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
    def time_played(self):
        cy, cm, cd = self.date.split(".")
        sy, sm, sd = self.start_date.split(".")
        current_date, start_date = date(int(cy), int(cm), int(cd)), date(int(sy), int(sm), int(sd))
        time_delta = current_date - start_date
        return time_delta.days

    @property
    def player_id(self):
        return str(self._json["player"]["id"])

    @property
    def player_name(self):
        return self._json["player_name"]

    @property
    def player_realm(self):
        return CK2Save._expand_title(self._json["player_realm"])

    @property
    def player_age(self):
        return self._json["player_age"]

    @property
    def player_history(self):
        player_history = []
        character_history = self._json["character_history"]
        for entry in character_history:
            _character_id, ascension_date, score = str(entry["identity"]), entry["date"], entry["score"]
            _character = self._json["character"][_character_id]
            name = _character["bn"]
            # If character identity is player_id, "oh" won't exist for character so use player_realm instead
            _realm = self._json["player_realm"] if _character_id == self.player_id else _character["oh"]
            # Expand _realm into a title based on whether the character is marked as female or not
            _mode = "f" if "fem" in _character else "m"
            title = CK2Save._expand_title(_realm, mode=_mode)
            # Create a ruler dict and append it to player_history
            ruler = {"name": name, "title": title, "ascension_date": ascension_date, "score": score}
            player_history.append(ruler)
        return player_history

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

    @staticmethod
    def _expand_title(realm, mode="t"):
        tier, location = realm.split("_")
        return f"{CK2Save._title_map[tier][mode]} of {location.capitalize()}"
