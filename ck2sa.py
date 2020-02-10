"""ck2sa

Usage:
    ck2sa.py saveprop <save_name>
    ck2sa.py charhist <save_name>
"""
import csv
import sys
from pathlib import Path

from docopt import docopt

from ck2sa.ck2save import CK2Save
from ck2sa.exceptions import CK2JsonError


ck2json_exe_p = (Path(__file__).parent / "ck2json/target/release/ck2json.exe").resolve()
ck2_saves_dir = Path.home() / "Documents/Paradox Interactive/Crusader Kings II/save games"


if __name__ == '__main__':
    # Fail fast if the ck2_saves_dir doesn't exist
    if not ck2_saves_dir.exists():
        print(f"Error: no saves directory at '{ck2_saves_dir}'")
        sys.exit(1)

    args = docopt(__doc__)
    ck2_save_path = ck2_saves_dir / f"{args['<save_name>']}.ck2"
    # Fail fast if the constructed ck2_save_path doesn't exist
    if not ck2_save_path.exists():
        print(f"Error: no save at '{ck2_save_path}'")
        sys.exit(1)

    try:
        ck2save = CK2Save(ck2json_exe_p, ck2_save_path)
    except CK2JsonError as e:
        print(e)
        sys.exit(2)

    if args["saveprop"]:
        # print(f"{len(ck2save._keys)} keys: {ck2save._keys}")
        print(f"Game version: {ck2save.version}")
        print(f"Start date: {ck2save.start_date}")
        print(f"Current date: {ck2save.date}")
        print(f"Time played: {ck2save.time_played} days")
        print(f"Player: [{ck2save.player_id}] {ck2save.player_name} ({ck2save.player_age}yo)")
        print(f"Realm: {ck2save.player_realm}")
    elif args["charhist"]:
        field_headers = ["name", "title", "ascension_date", "score"]
        writer = csv.writer(sys.stdout, quoting=csv.QUOTE_NONNUMERIC)
        writer.writerow(field_headers)
        for h in ck2save.player_history:
            writer.writerow([h["name"], h["title"], h["ascension_date"], h["score"]])
