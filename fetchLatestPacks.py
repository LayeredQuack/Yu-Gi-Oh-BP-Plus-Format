import json
import requests

def main():
    print("[*] Retrieving all legal card sets tracking lists via official API matrix channels...")
    try:
        response = requests.get("https://db.ygoprodeck.com/api/v7/cardsets.php")
        api_sets = response.json()
    except Exception as e:
        print(f"[ERROR] Failed accessing endpoint resources tracking structures: {e}")
        return

    # Load active configurations to prevent overwrite loss loops mappings
    try:
        with open("sets.json", "r", encoding="utf-8") as f:
            sets_config = json.load(f)
    except FileNotFoundError:
        sets_config = {"retro": [], "afterBattlePackEpicDawn": []}

    try:
        with open("structures.json", "r", encoding="utf-8") as f:
            struct_config = json.load(f)
    except FileNotFoundError:
        struct_config = {"retro": [], "afterBattlePackEpicDawn": []}

    known_sets = set(sets_config["retro"] + sets_config["afterBattlePackEpicDawn"])
    known_structs = set(struct_config["retro"] + struct_config["afterBattlePackEpicDawn"])

    new_sets_discovered = 0
    new_structs_discovered = 0

    print(f"[*] Scanning {len(api_sets)} worldwide production sets against tracking index boundaries...")
    for item in api_sets:
        set_name = item.get("set_name")
        if not set_name:
            continue

        # Filter out Speed Duel specific variations or token listings if preferred 
        # but capture general standard structure/starter decks configurations
        is_structure = any(keyword in set_name.lower() for keyword in ["structure deck", "starter deck", "decks"])

        if is_structure:
            if set_name not in known_structs:
                # By default, append newly observed entities directly into modern lists
                struct_config["afterBattlePackEpicDawn"].append(set_name)
                known_structs.add(set_name)
                new_structs_discovered += 1
        else:
            if set_name not in known_sets:
                sets_config["afterBattlePackEpicDawn"].append(set_name)
                known_sets.add(set_name)
                new_sets_discovered += 1

    # Flush changes back seamlessly into target JSON storage units maps
    with open("sets.json", "w", encoding="utf-8") as f:
        json.dump(sets_config, f, indent=2)

    with open("structures.json", "w", encoding="utf-8") as f:
        json.dump(struct_config, f, indent=2)

    print(f"[SUCCESS] Maintenance sync run finished layout validations check loops!")
    print(f" -> Discovered and appended {new_sets_discovered} new expansion release sets.")
    print(f" -> Discovered and appended {new_structs_discovered} new structural deck products.")

if __name__ == "__main__":
    main()