import re
import sys

def main():
    template_path = "lflist.template.conf"

    # 1. Read the raw template file
    try:
        with open(template_path, "r", encoding="utf-8") as f:
            content = f.read()
    except FileNotFoundError:
        print(f"[ERROR] Target file '{template_path}' missing.")
        sys.exit(1)

    # 2. Isolate the BP+ exceptions section to find our target exclusions
    exceptions_match = re.search(
        r"# start BP\+ exceptions(.*?)# End BP\+ exceptions", 
        content, 
        flags=re.DOTALL | re.IGNORECASE
    )
    
    if not exceptions_match:
        print("[ERROR] Could not find '# start BP+ exceptions' section markers in your template.")
        sys.exit(1)
        
    exceptions_text = exceptions_match.group(1)
    
    # Extract all 8-digit card IDs inside the exceptions block
    exception_ids = set()
    for line in exceptions_text.split('\n'):
        cleaned = line.strip()
        # Look for lines starting with an 8-digit ID followed by space and restriction level
        match = re.match(r"^(\d{8})\s+\d+", cleaned)
        if match:
            exception_ids.add(match.group(1))

    if not exception_ids:
        print("[!] No explicit card IDs found inside your 'BP+ exceptions' section. Nothing to clean.")
        sys.exit(0)

    print(f"[*] Found {len(exception_ids)} unique card IDs in BP+ exceptions to clean from base lists.")

    # 3. Define a helper block cleaner to scrub lines matching our target IDs
    def remove_targeted_ids(section_text, targets):
        cleaned_lines = []
        removed_cards = []
        
        for line in section_text.split('\n'):
            line_strip = line.strip()
            match = re.match(r"^(\d{8})\s+\d+", line_strip)
            
            if match and match.group(1) in targets:
                removed_cards.append(line_strip)
                continue  # Skip this line to remove it
                
            cleaned_lines.append(line)
            
        return "\n".join(cleaned_lines), removed_cards

    # 4. Extract, clean, and replace the Base Banlist section
    base_match = re.search(
        r"(# Base Banlist of Battle Pack:.*?\n)(.*?)(# End Base Banlist of Battle Pack:.*?\n)", 
        content, 
        flags=re.DOTALL
    )
    
    base_removed_log = []
    if base_match:
        header, base_body, footer = base_match.group(1), base_match.group(2), base_match.group(3)
        cleaned_base_body, base_removed_log = remove_targeted_ids(base_body, exception_ids)
        new_base_section = f"{header}{cleaned_base_body}{footer}"
        content = content.replace(base_match.group(0), new_base_section)

    # 5. Extract, clean, and replace the Current Banlist section
    current_match = re.search(
        r"(# Current Banlist.*?\n)(.*?)(# End Current Banlist\n)", 
        content, 
        flags=re.DOTALL
    )
    
    current_removed_log = []
    if current_match:
        header, current_body, footer = current_match.group(1), current_match.group(2), current_match.group(3)
        cleaned_current_body, current_removed_log = remove_targeted_ids(current_body, exception_ids)
        new_current_section = f"{header}{cleaned_current_body}{footer}"
        content = content.replace(current_match.group(0), new_current_section)

    # 6. Report the changes to the user
    total_removed = len(base_removed_log) + len(current_removed_log)
    
    if total_removed > 0:
        print(f"\n[+] Successfully cleaned up {total_removed} duplicate entries:")
        for item in base_removed_log:
            print(f"  [-] Removed from Base Banlist: {item}")
        for item in current_removed_log:
            print(f"  [-] Removed from Current Banlist: {item}")
            
        # 7. Overwrite the template file with the cleaned-up data
        with open(template_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"\n[SUCCESS] '{template_path}' has been stripped of duplicates and saved!")
    else:
        print("\n[+] Clean cycle complete! No duplicate references found in Base or Current lists.")

if __name__ == "__main__":
    main()