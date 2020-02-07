import sys
import json
import subprocess
from collections import OrderedDict
from pathlib import Path


script_dir = Path(__file__).parent.resolve()
ck2json_exe_p = script_dir / "ck2json/target/release/ck2json.exe"
ck2_save_path = script_dir / "data/Ironman_England.ck2"

IGNORED_KEYS = ("ironman", "count", "player_portrait", "game_speed", "mapmode", "dyn_title", "unit", "sub_unit",
                "delayed_event", "relation", "religion", "religion_group", "culture", "culture_group", "bloodline",
                "active_ambition", "active_focus", "active_plot", "active_faction", "combat", "war", "active_war",
                "previous_war", "next_outbreak_id", "disease_outbreak", "disease", "offmap_powers", "wonder_upgrade",
                "generated_societies", "generated_artifacts", "trade_route", "vc_data", "achievement")


# Adapted https://stackoverflow.com/a/14902564
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


if __name__ == '__main__':
    print(f"Running ck2json.exe against '{ck2_save_path}'...\n")
    try:
        completed_process = subprocess.run([str(ck2json_exe_p), str(ck2_save_path)], capture_output=True, check=True)
    except subprocess.CalledProcessError as e:
        stderr = e.stderr.decode("utf8")
        print(f"ck2json.exe failed with: [{e.returncode}] {stderr}")
        sys.exit(1)
    # Parse the json output of ck2json with a special object_pairs_hook to deal with repeated keys
    ck2save = json.loads(completed_process.stdout, object_pairs_hook=parse_object_pairs)
    # Delete the completed_process to preserve some memory now that it is no longer required
    del completed_process
    # Output some stats
    # print(f"{len(ck2save)} keys:\n{ck2save.keys()}")
    print(f"Date: {ck2save['date']}")
    player_character_id = str(ck2save["player"]["id"])
    player_name = ck2save["player_name"]
    player_age = ck2save["player_age"]
    print(f"Player: [{player_character_id}] {player_name} ({player_age}yo)")
    player_character = ck2save["character"][player_character_id]
    # print(player_character)
    print(f"Character history:\n{ck2save['character_history']}")
