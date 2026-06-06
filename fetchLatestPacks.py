import json
import requests
from datetime import datetime

def main():
    print("[*] Retrieving all legal card sets tracking lists via official API matrix channels...")
    try:
        response = requests.get("https://db.ygoprodeck.com/api/v7/cardsets.php")
        api_sets = response.json()
    except Exception as e:
        print(f"[ERROR] Failed accessing endpoint resources tracking structures: {e}")
        return

    # Temporary lists to hold items for sorting before dict generation
    retro_sets = []
    modern_sets = []
    retro_structs = []
    modern_structs = []

    # Format Cutoff: Battle Pack 1: Epic Dawn released on May 28, 2012
    CUTOFF_DATE = datetime.strptime("2012-05-28", "%Y-%m-%d")

    print(f"[*] Scanning {len(api_sets)} worldwide production sets to auto-sort by timeline...")
    for item in api_sets:
        set_name = item.get("set_name")
        if not set_name:
            continue

        release_date = item.get("tcg_date", "9999-12-31")
        
        # Determine target category timeline segment dynamically using the cutoff date
        is_retro = False
        if release_date and release_date != "9999-12-31":
            try:
                set_date = datetime.strptime(release_date, "%Y-%m-%d")
                if set_date < CUTOFF_DATE:
                    is_retro = True
            except ValueError:
                pass 

        # Separate standard card sets from Structure, Starter, and themed Decks
        is_structure = any(keyword in set_name.lower() for keyword in ["structure deck", "starter deck", "decks"])
        
        # Pack info as a tuple for easy chronological sorting
        set_data = (set_name, release_date)

        if is_structure:
            if is_retro:
                retro_structs.append(set_data)
            else:
                modern_structs.append(set_data)
        else:
            if is_retro:
                retro_sets.append(set_data)
            else:
                modern_sets.append(set_data)

    # --- CHRONOLOGICAL SORTING ENGINE ---
    # Sorts by the second element in the tuple (release_date string, e.g., "2002-03-29")
    retro_sets.sort(key=lambda x: x[1])
    modern_sets.sort(key=lambda x: x[1])
    retro_structs.sort(key=lambda x: x[1])
    modern_structs.sort(key=lambda x: x[1])

    # Convert sorted lists back into the final dictionary format
    sets_config = {
        "retro": {name: date for name, date in retro_sets},
        "afterBattlePackEpicDawn": {name: date for name, date in modern_sets}
    }
    
    struct_config = {
        "retro": {name: date for name, date in retro_structs},
        "afterBattlePackEpicDawn": {name: date for name, date in modern_structs}
    }

    # Flush changes back by completely overwriting target JSON storage files
    with open("sets.json", "w", encoding="utf-8") as f:
        json.dump(sets_config, f, indent=2)

    with open("structures.json", "w", encoding="utf-8") as f:
        json.dump(struct_config, f, indent=2)

    print(f"[SUCCESS] Fresh database overwrite completed successfully!")
    print(f" -> Chronologically wrote {len(retro_sets) + len(modern_sets)} expansion sets.")
    print(f" -> Chronologically wrote {len(retro_structs) + len(modern_structs)} structural decks.")

if __name__ == "__main__":
    main()