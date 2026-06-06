import json
import re
import sys
import datetime
import requests

def load_json_config(filename):
    try:
        with open(filename, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"[ERROR] Required file '{filename}' is missing! Please create it first.")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"[ERROR] Malformed syntax inside '{filename}'. Check JSON markup validity.")
        sys.exit(1)

def extract_protected_ids(content):
    """
    Scans the configuration context file to extract baseline indices.
    All matching IDs found inside active limits will be protected.
    """
    protected = set()
    lines = content.split('\n')
    for line in lines:
        cleaned = line.strip()
        if not cleaned:
            continue
        match = re.match(r"^(\d+)\s+(\d+)", cleaned)
        if match:
            card_id = match.group(1).zfill(8)
            protected.add(card_id)
    return protected

def format_release_date(date_str):
    """Converts YYYY-MM-DD into 'Month DD, YYYY' format."""
    if not date_str or date_str == "9999-12-31":
        return ""
    try:
        dt = datetime.datetime.strptime(date_str, "%Y-%m-%d")
        return dt.strftime("%B %d, %Y")
    except ValueError:
        return ""

def main():
    file_path = "lflist.conf"
    
    # 1. Load context dictionaries out of local JSON configuration models
    sets_data = load_json_config("sets.json")
    structures_data = load_json_config("structures.json")
    
    # Combine dictionaries into a single combined lookups block
    retro_sets_dict = {**sets_data.get("retro", {}), **structures_data.get("retro", {})}
    target_sets_dict = {**sets_data.get("afterBattlePackEpicDawn", {}), **structures_data.get("afterBattlePackEpicDawn", {})}

    # Create master interleaved ordering sequences sorted strictly by release date strings
    retro_sets_order = sorted(retro_sets_dict.keys(), key=lambda x: retro_sets_dict[x])
    target_sets_order = sorted(target_sets_dict.keys(), key=lambda x: target_sets_dict[x])

    # 2. Read live local Banlist file data
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
    except FileNotFoundError:
        print(f"[ERROR] local target file '{file_path}' missing.")
        sys.exit(1)

    # 3. Dynamic Automated Version Tracker Incrementer Rule
    version_match = re.search(r"!BP\+V(\d+)\.(\d+)\.(\d+)", content)
    if version_match:
        major, middle, minor = version_match.group(1), version_match.group(2), version_match.group(3)
        new_version = f"!BP+V{major}.{middle}.{int(minor) + 1}"
        content = content.replace(version_match.group(0), new_version)
        print(f"[+] Configuration tracker bumped to: {new_version}")

    # Process protected layout mappings
    protected_ids = extract_protected_ids(content)
    print(f"[+] Protected {len(protected_ids)} configuration baseline items from forced copy replacement override updates.")

    # 4. Fetch the database cards payload
    print("[*] Accessing Yu-Gi-Oh! card tracking index structural API layout...")
    try:
        response = requests.get("https://db.ygoprodeck.com/api/v7/cardinfo.php")
        all_cards_data = response.json().get("data", [])
        print(f"[+] Tracking database queried! Parsing {len(all_cards_data)} runtime entries...")
    except Exception as e:
        print(f"[CRITICAL ERROR] Failed connecting onto structural target API source endpoints: {e}")
        sys.exit(1)

    # Initialize dynamic storage blocks mapping structural rulesets
    retro_by_set = {set_n: {} for set_n in retro_sets_order}
    links_by_set = {target: {} for target in target_sets_order}
    pendulums_by_set = {target: {} for target in target_sets_order}
    limited_by_set = {target: {} for target in target_sets_order}

    retro_count, link_count, pend_count, lim_count = 0, 0, 0, 0

    # 5. Process tracking entities mapping criteria rules sets
    for card in all_cards_data:
        card_id = str(card.get("id")).zfill(8)
        card_name = card.get("name")
        card_type = card.get("type", "").lower()
        card_sets = card.get("card_sets", [])
        
        valid_retro_matches = []
        valid_target_matches = []

        for s in card_sets:
            set_name = s.get("set_name", "")
            # Clean and normalize the API set name to eliminate spacing and punctuation variables
            clean_api_set = re.sub(r'[^a-z0-9]', '', set_name.lower())
            
            # Check against Retro Sets using normalized matching filters
            for r_set in retro_sets_order:
                clean_config_set = re.sub(r'[^a-z0-9]', '', r_set.lower())
                if clean_config_set in clean_api_set:
                    valid_retro_matches.append({
                        "config_set": r_set,
                        "date": retro_sets_dict.get(r_set, "9999-12-31")
                    })
            
            # Check against Modern Target Sets using normalized matching filters
            for target in target_sets_order:
                clean_config_target = re.sub(r'[^a-z0-9]', '', target.lower())
                if clean_config_target in clean_api_set:
                    valid_target_matches.append({
                        "config_set": target,
                        "date": target_sets_dict.get(target, "9999-12-31")
                    })

        # --- EVALUATION ENGINE ---
        # Sort collections ascending by configuration-defined dates to prioritize the earliest valid printing
        if valid_retro_matches:
            valid_retro_matches.sort(key=lambda x: x["date"])
            matched_retro = valid_retro_matches[0]["config_set"]
            
            if card_id not in protected_ids:
                retro_by_set[matched_retro][card_id] = f"{card_id} 3 --{card_name}"
                retro_count += 1
            continue

        if valid_target_matches:
            valid_target_matches.sort(key=lambda x: x["date"])
            matched_target = valid_target_matches[0]["config_set"]

            if "link" in card_type:
                links_by_set[matched_target][card_id] = f"{card_id} 0 --{card_name}"
                link_count += 1
            elif "pendulum" in card_type:
                pendulums_by_set[matched_target][card_id] = f"{card_id} 0 --{card_name}"
                pend_count += 1
            else:
                limited_by_set[matched_target][card_id] = f"{card_id} 1 --{card_name}"
                lim_count += 1

    print(f"[+] Assigned {retro_count} cards into Retro 3-Copy collection buckets.")
    print(f"[+] Loaded {link_count} Link mechanics, {pend_count} Pendulums, and {lim_count} modern target listings.")

    # String Compilation Logic Block Generator Utility Ruleset helper
    def build_section_text(grouped_dict, ordering_list, dates_lookup):
        lines = []
        for set_name in ordering_list:
            cards_in_set = grouped_dict[set_name]
            if cards_in_set:
                raw_date = dates_lookup.get(set_name, "")
                formatted_date = f" ({format_release_date(raw_date)})" if raw_date else ""
                lines.append(f"\n# From {set_name}{formatted_date}")
                for c_id in sorted(cards_in_set.keys()):
                    lines.append(cards_in_set[c_id])
        return "\n".join(lines).strip()

    # Combine data lookups for presentation layer processing
    all_dates_lookup = {**retro_sets_dict, **target_sets_dict}

    sorted_retro = build_section_text(retro_by_set, retro_sets_order, all_dates_lookup)
    sorted_links = build_section_text(links_by_set, target_sets_order, all_dates_lookup)
    sorted_pendulums = build_section_text(pendulums_by_set, target_sets_order, all_dates_lookup)
    sorted_limited = build_section_text(limited_by_set, target_sets_order, all_dates_lookup)

    # 6. Build Structural Placement Injection Modifications Rulesets
    retro_replacement = f"# Start of retro 3 copy cards\n{sorted_retro}\n# End of retro 3 copy cards"
    limited_replacement = (
        "# Start of new limited cards\n"
        "# --- Banned Link Mechanics (Forced to 0) ---\n"
        f"{sorted_links}\n\n"
        "# --- Banned Pendulum Mechanics (Forced to 0) ---\n"
        f"{sorted_pendulums}\n\n"
        "# --- Allowed Expansions (Post Battle Pack @ Limit 1) ---\n"
        f"{sorted_limited}\n"
        "# End of new limited cards"
    )

    # Validate structural safety placeholders mappings dynamically
    if "# Start of retro 3 copy cards" not in content:
        content = content.replace("# Start of new limited cards", "# Start of retro 3 copy cards\n# End of retro 3 copy cards\n\n# Start of new limited cards")

    if "# Start of retro 3 copy cards" in content and "# Start of new limited cards" in content:
        content = re.sub(r"# Start of retro 3 copy cards.*?# End of retro 3 copy cards", retro_replacement, content, flags=re.DOTALL)
        content = re.sub(r"# Start of new limited cards.*?# End of new limited cards", limited_replacement, content, flags=re.DOTALL)
        print("[+] Content mapped out cleanly and processed successfully inside active markers data channels!")
    else:
        print("[ERROR] Custom context file is missing required injection region pointers structural layouts!")
        sys.exit(1)

    # 7. Flush memory stream changes directly write back onto clean storage lines values
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)
    
    print("[SUCCESS] Processing cycle completed! lflist.conf file completely compiled!")

if __name__ == "__main__":
    main()