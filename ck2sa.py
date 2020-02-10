import sys
from pathlib import Path

from ck2sa.ck2save import CK2Save
from ck2sa.exceptions import CK2JsonError


script_dir = Path(__file__).parent.resolve()
ck2json_exe_p = script_dir / "ck2json/target/release/ck2json.exe"
ck2_save_path = script_dir / "data/Ironman_England.ck2"


if __name__ == '__main__':
    try:
        ck2save = CK2Save(ck2json_exe_p, ck2_save_path)
    except CK2JsonError as e:
        print(e)
        sys.exit()

    # Output some stats
    print(f"{len(ck2save._keys)} keys: {ck2save._keys}")

    print(f"Game version: {ck2save.version}")

    print(f"Start date: {ck2save.start_date}")
    print(f"Current date: {ck2save.date}")
    print(f"Time played: {ck2save.time_played} days")

    print(f"Player: [{ck2save.player_id}] {ck2save.player_name} ({ck2save.player_age}yo)")
    print(f"Realm: {ck2save.player_realm}")

    # print(f"Character history:\n{ck2save._json['character_history']}")
    # print()
    # print(ck2save.player_character)
    # print()
    # print(ck2save._json["character"]["33350"])
    print(ck2save.player_history)
