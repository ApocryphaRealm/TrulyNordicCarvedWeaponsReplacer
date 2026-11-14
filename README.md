# Truly Nordic Carved Weapons Replacer

New models for the Dragonborn Nordic weapons and shield: steel forged and carved in the Nordic way, with black leather
wrapped grips and knotwork filling every face, and carved sheaths for the swords and the dagger. Each weapon keeps what
it is - its edges, its head, its silhouette - and is rebuilt to be realistic in proportion, thickness and construction.

## The models
| Item | New look |
|---|---|
| Carved Nordic Sword | single-edged curved blade, one-piece half guard sweeping up, hooked pommel, a bold carved braid running to the point; a falchion-shaped sheath |
| Carved Nordic Battleaxe | a tall upper horn, one long curved cutting edge down to a single beard point, a curved back spike; steel haft forged with the head, carved knot fields, a forged knob pommel |
| Carved Nordic Greatsword | double-edged blade, carved guards and ricasso, a triquetra medallion on a level boss at the lower guard, two wrapped grips; a straight sheath on the back |
| Carved Nordic Warhammer | hammer face and curved pick, a triquetra ring centred on the face, a forged knob pommel |
| Carved Nordic War Axe | bearded blade with a square hammer poll, a triquetra at the widest point, a forged knob pommel |
| Carved Nordic Dagger | kukri form, the blade carved with weave and a ringed triquetra (or, in the installer, a world serpent); its own sheath |
| Carved Nordic Mace | six-flanged head with pointed striking edges, every flange carved with weave and a ringed triquetra |
| Carved Nordic Bow | all-steel bow, a carved riser plate (a triquetra in a woven field inside a braid border) and a braid band along the riser; the string still draws and follows the arrow |
| Carved Nordic Shield | the carved crest filled out to the rim, the four points in place; sits on the arm and on the back where the vanilla shield does |

The sheaths are black leather in one piece with a carved steel mouth and tip, and stay on the hip (the greatsword's on
the back) when the weapon is drawn.

## The files
Pick ONE Nordic file (Replacer - No ESP, Replacer - ESP or Standalone - Nordic quality) and, if you want the black and
gold Ebony look, ONE Ebony file (Replacer - Ebony - No ESP, Replacer - Ebony - ESP or Standalone - Ebony quality): the
Replacer - Ebony files put the look on the vanilla Ebony weapons, the Standalone - Ebony quality file adds it as a set
of new items beside them. Each main file has its own installer with four choices, each shown with a picture: the
sword (curved saber, the default, or a straight sword), the mace (six-flanged, the default, or the classic four-flanged
one, both with pointed striking edges), the shield (carved, the default, or clean) and the dagger (carved, the default,
or the serpent). Only the chosen model is installed, at the one path every record
uses, so nothing is left over. To change a choice later, reinstall and pick again.

| Main file | What it does |
|---|---|
| Replacer - No ESP | No plugin. SkyPatcher swaps the weapons' models per record (`SKSE\Plugins\SkyPatcher\weapon\TrulyNordicCarvedWeaponsReplacer\`), matched by the first-person model, so enchanted copies and copies other mods add change too. Needs SkyPatcher. |
| Replacer - ESP | `TrulyNordicCarvedWeapons.esp`, a light plugin setting the models on the Nordic weapon records and their enchanted versions. No SkyPatcher. |
| Replacer - Ebony - No ESP | The Carved Ebony look (black ebony steel, gold knotwork, gold haft rings) on the vanilla Ebony weapons, the Ebony arrow and the Ebony shield. No plugin: SkyPatcher swaps the models per record, matched by the vanilla Ebony first-person models, so enchanted and added copies change too, and renames the base pieces. Needs SkyPatcher. |
| Replacer - Ebony - ESP | The same through `TrulyNordicCarvedWeapons - Ebony Replacer.esp`, a light plugin setting the models and names on the 311 Ebony weapon records (the 8 base weapons and their enchanted copies), the arrow and the 16 Ebony shields. No SkyPatcher (except for the Legacy of Ysgramor choice below). |
| Standalone - Nordic quality | `TrulyNordicCarvedWeapons - Standalone.esp`, a light plugin that adds the set as new items and leaves the vanilla Nordic pieces alone. Each is forged where its Nordic counterpart is (same perk, materials and forge heading) and tempered the same way, with the Nordic piece's stats. |
| Standalone - Ebony quality | The same plugin name and items with the matching ebony piece's damage or armour rating, value, weight, material keyword and recipes (ebony ingots, Ebony Smithing, the ebony heading). |

The Replacer files ship the first-person models, the shield and the arrow in flight as loose files at the vanilla paths
(SkyPatcher cannot reach them): put the mod below any other Nordic or Ebony weapon or shield replacer. The Replacer -
Ebony files and our Ebony Wolf Armor and Weapons mod both replace the vanilla Ebony weapons - use one or the other for
them. The Standalone files ship every file at this mod's own paths and change no vanilla file.

**Legacy of Ysgramor (Replacer - Ebony files, last installer step).** "Carved Wolf Ebony weapons" puts the Carved Ebony
models you picked on Legacy of Ysgramor's Wolf Ebony sword, greatsword, dagger, battleaxe, war axe and shield, renamed
Carved Wolf Ebony Sword and so on. It works with NordwarUA's original (`NW_Companions_Replacer_Light.esp`) and with
Xtudo's fixes, whichever file you use: his light (ESL) version of the same plugin, his RMB and non-ESL versions, and his
standalone version (`NW_Wolf_Armor_Standalone.esp`). The models are loose files at Legacy of Ysgramor's own mesh paths,
so put this mod below Legacy of Ysgramor and its patches (Xtudo's Smaller Shields replaces the same shield file); the
names and the third-person models come from a SkyPatcher file per Legacy of Ysgramor plugin, each loading only when
that plugin is active, so nothing here needs Legacy of Ysgramor installed. The Wolf Ebony armour (helmet, armour,
gauntlets, boots) keeps its own look - this mod has weapons and a shield only. Without SkyPatcher the weapons still take
the new model and keep their Legacy of Ysgramor names.

Ebony names: the Replacer - Ebony files rename the Ebony pieces Carved Ebony Sword, Carved Ebony War Axe, ... Carved
Ebony Bow, Carved Ebony Arrow, Carved Ebony Shield; the ESP file also renames the enchanted copies ("Holy Carved Ebony
Warhammer", "Carved Ebony Greatsword of the Inferno"), the No ESP file the base pieces only, as with the Nordic files.
The ESP file copies each record from the base game's masters, so it undoes other mods' edits to those records when it
loads after them (the Unofficial Patch's, an enchantment overhaul's); with such mods, use the No ESP file or load the
ESP file first.

Standalone items (the same names at Nordic and Ebony quality): Carved Nordic Sword, Carved Nordic War Axe, Carved Nordic
Battleaxe, Carved Nordic Greatsword, Carved Nordic Warhammer, Carved Nordic Dagger, Carved Nordic Mace, Carved Nordic
Bow, Carved Nordic Shield, Carved Nordic Arrow. The installer's model choices (saber or straight sword, and so on) change
only the model, not the name.

Replacer names: the Replacer files rename the Nordic pieces to the same names - Carved Nordic Sword, ... Carved
Nordic Shield, Carved Nordic Arrow. The ESP file also renames the enchanted copies the same way ("Virtuous Carved
Nordic Sword", "Carved Nordic Mace of Fear"); the No ESP file renames the base pieces only, so a mod that re-enchants
and renames the enchanted copies (Thaumaturgy, for one) keeps its own names.

Optional file, Additional Weapons: carved weapons the game does not have, in their own light plugin
(`TrulyNordicCarvedWeapons - Additional Weapons.esp`), installed beside any main file, at Nordic or Ebony quality.
- **Carved Nordic Spear:** a winged spear with the triquetra on its head.
- **Carved Nordic Halberd:** a bearded blade with a triquetra, a carved back spike and a top blade, 163 units long.

Both are forged and tempered like the battleaxe and use the battleaxe moveset unless an installer step adds the keywords
that animation packs look for, through Keyword Item Distributor: spear packs, or Animated Armoury's halberd (which also
gives Simple Dodge's halberd dodge set).

Textures: our own TruePBR set (base colour, normal, RMAOS) at 2K, under `textures\pbr\TrulyNordic\`.

## Requirements
- Skyrim Special Edition or Anniversary Edition with the Dragonborn DLC (included in both).
- SKSE64. SkyPatcher for the Replacer - No ESP and Replacer - Ebony - No ESP files, and for the Legacy of Ysgramor
  names in either Replacer - Ebony file.
- Replacer - Ebony - ESP: Dawnguard (its plugin masters Skyrim.esm, Update.esm and Dawnguard.esm - the Ebony arrow's
  record comes from Dawnguard).
- A TruePBR-capable renderer: Community Shaders with its TruePBR support.

## Building from source
`tools\build_all.sh` runs the pipeline: `gb_blender.py` (Blender + PyNifly: decimation and checks, face orientation,
the sheaths, blood shapes, the bow's weights), `textures.py` (BC7 DDS), `assemble.py` (game NIFs on the vanilla
structure, the sheath as the `Scb` shape), `silhouette.py`, `verify.py` (read-back: shader block, texture paths and the
face-direction check of `winding.py`) and `build-packages.py` (the six main files, each with its installer and a picture for every model option). The
Ebony look is `ebony.py`; the Replacer - Ebony plugin, its SkyPatcher lines and the Legacy of Ysgramor tables are
`ebony_replacer.py` (it also checks Legacy of Ysgramor's FormID layouts with `--loyscan`). The
Standalone plugins are built with houseCARL from `standalone_spec.py` / `standalone_assign.py` / `standalone_finish.py`.
The source models and maps come from the design work folder named in `tools\items.py`.

## Credits
- **NordwarUA**, Legacy of Ysgramor ([Nexus 109963](https://www.nexusmods.com/skyrimspecialedition/mods/109963)), and
  **Xtudo**, Legacy of Ysgramor - My patches and fixes
  ([Nexus 111121](https://www.nexusmods.com/skyrimspecialedition/mods/111121)): the Wolf Ebony weapons the Replacer -
  Ebony files' optional step re-models. None of their files ship here (see NOTICE.md).
- SkyPatcher, by its author, for the runtime model and name swap.
