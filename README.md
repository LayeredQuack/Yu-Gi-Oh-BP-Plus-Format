# Yu-Gi-Oh-BP-Format

A Ban list that tries to capture the power level of Yu-Gi-Oh decks from 2012. All Link Monsters are banned.

---

## ⚙️ Automation Workflow

This project utilizes an automated pipeline to query live card records, calculate historical release boundaries, protect custom adjustments, and generate a fully structured format configuration file.

To maintain or build the project files, follow these structural execution steps:

### Step 1: Sync Database Manifests

Run the tracking manifest sync script. This script fetches all legal card sets, core expansions, structure decks, and starter products directly from official API channels. It automatically determines their chronological placement relative to the format's historic cutoff boundary and builds cleanly ordered indexes.

```bash
python fetchLatestPacks.py
```

**Output Artifacts**: Automatically regenerates `sets.json` and `structures.json` sorted purely by release timeline.

### Step 2: Manage Custom Format Exceptions

Do not edit `lflist.conf` directly. All custom banlist configurations, direct adjustments, and archetype legal shifts must be written manually inside the designated **BP+ Exceptions** area within the template file:

**Target File**: `lflist.template.conf`

### Step 3: Compile the Format File

Run the main compilation pipeline engine. This script reads your updated configuration template, processes all baseline cards, extracts protected explicit target exceptions, maps unmatched pieces into their native categories chronologically, and compiles the final product.

```bash
python updateScript.py
```

**Result**: The execution grabs the raw configurations from `lflist.template.conf`, increments the format version tracker string, builds the interleaved data tiers, and completely overwrites `lflist.conf` cleanly with the final active build layout.

## 📜 Changelog

### Version 1.0.5
- **+++ UNLIMITED +++**
  - Tri-Wight
  - Box of Friends
  - First of the Dragons
- **+++ SEMI-LIMITED +++**
  - Unexpected Dai
  - Flawless Perfection of the Tenyi
- **+++ CODE CHANGES +++**
  - `fetchLatestPacks.py` grabs the release dates of all sets/structures and writes them to file in chronological order.
  - `updateScript.py` reads from `lflist.template.conf`, correctly associates a card with the set/structure it is first released in, interleaves sets and structures chronologically, and completely overwrites `lflist.conf`.

### Version 1.0.4
- Cards associated with the first set/structure they appear in, instead of the last set/structure.
- **+++ UNLIMITED +++**
  - Elemental HERO Honest Neos
- **+++ SEMI-LIMITED +++**
  - Formula Synchron
  - T.G. Hyper Librarian
  - Charge of the Light Brigade
  - Treasure Panda
  - Advanced Ritual Art
- **+++ LIMITED +++**
  - Skill Drain (was at 3)
  - E - Emergency Call (was at 3)
  - Droll & Lock Bird (was at 3)
  - Instant Fusion (was at 3)
  - Gozen Match (was at 3)
  - Maxx "C" (was at 3)
  - Super Polymerization (was at 3)
  - Brilliant Fusion (was at 3)
  - Rescue Cat (was at 0)
  - Magician of Faith (was at 0)
  - Catapult Turtle (was at 0)
  - Dandylion (was at 0)
  - Dark Magician of Chaos (was at 0)
  - Thousand-Eyes Restrict (was at 0)
- **+++ BANNED +++**
  - Kashtira Fenrir (was at 1)
  - Kashtira Unicorn (was at 1)
  - Red-Eyes Dark Dragoon (was at 1)

### Version 1.0.3
- Restructure order of Current Banlist, Base Banlist, and BP+ Exceptions.
- Base Banlist Set to March 2012.
- **+++ LIMITED +++**
  - Trishula, Dragon of the Ice Barrier
  - Goyo Guardian
  - Ultimate Flame Swordsman
  - Fighting Flame Dragon
- **+++ SEMI-LIMITED +++**
  - Flower Cardians

### Version 1.0.2
- Updated to latest sets and structures.
- Added python scripts to automatically update format.

### Version 1.0.1
- Penguin Archetype is unlimited.
- Legendary Fisherman support increased from limited.
- Man-eating Black Shark fusion and material is unlimited.
- Flame Swordsman Archetype is unlimited.
- Flower Cardian Archetype is unlimited.
- War Rock Archetype is unlimited.
- Dinowrestler support increased from limited.

### Initial List
- Merging of the Edison List with the April 2025 Ban List.
- Black Luster Soldier - Envoy of the Beginning moved from forbidden to limited.
- Card Trooper is unlimited.