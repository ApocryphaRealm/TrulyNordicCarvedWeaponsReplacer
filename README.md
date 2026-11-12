# Truly Nordic Carved Weapons Replacer

New models for the Dragonborn Nordic weapons and shield: steel forged and carved in the Nordic way, with black leather
wrapped grips and knotwork filling every face, and carved sheaths for the swords and the dagger. Each weapon keeps what
it is - its edges, its head, its silhouette - and is rebuilt to be realistic in proportion, thickness and construction.

## The models
| Item | New look |
|---|---|
| Nordic Sword | single-edged curved blade, one-piece half guard sweeping up, hooked pommel, a bold carved braid running to the point; a falchion-shaped sheath |
| Nordic Battleaxe | a tall upper horn, one long curved cutting edge down to a single beard point, a curved back spike; steel haft forged with the head, carved knot fields, a forged knob pommel |
| Nordic Greatsword | double-edged blade, carved guards and ricasso, a triquetra medallion on a level boss at the lower guard, two wrapped grips; a straight sheath on the back |
| Nordic Warhammer | hammer face and curved pick, a triquetra ring centred on the face, a forged knob pommel |
| Nordic War Axe | bearded blade with a square hammer poll, a triquetra at the widest point, a forged knob pommel |
| Nordic Dagger | kukri form, a world serpent carved along the belly; its own sheath |
| Nordic Mace | six-flanged head with pointed striking edges, a biting maw on every flange |
| Nordic Bow | all-steel bow, a carved riser plate (a triquetra in a woven field inside a braid border) and a braid band along the riser; the string still draws and follows the arrow |
| Nordic Shield | the carved crest filled out to the rim, the four points in place; sits on the arm and on the back where the vanilla shield does |

The sheaths are black leather in one piece with a carved steel mouth and tip, and stay on the hip (the greatsword's on
the back) when the weapon is drawn.

## The files
Install ONE of the four main files. Each has its own installer with three choices, each shown with a picture: the
sword (curved saber, the default, or a straight sword), the mace (six-flanged, the default, or the classic four-flanged
one, both with pointed striking edges) and the shield (carved, the default, or clean). Only the chosen model is installed, at the one path every record
uses, so nothing is left over. To change a choice later, reinstall and pick again.

| Main file | What it does |
|---|---|
| Replacer - No ESP | No plugin. SkyPatcher swaps the weapons' models per record (`SKSE\Plugins\SkyPatcher\weapon\TrulyNordicCarvedWeaponsReplacer\`), matched by the first-person model, so enchanted copies and copies other mods add change too. Needs SkyPatcher. |
| Replacer - ESP | `TrulyNordicCarvedWeapons.esp`, a light plugin setting the models on the Nordic weapon records and their enchanted versions. No SkyPatcher. |
| Standalone - Nordic quality | `TrulyNordicCarvedWeapons - Standalone.esp`, a light plugin that adds the set as new items and leaves the vanilla Nordic pieces alone. Each is forged where its Nordic counterpart is (same perk, materials and forge heading) and tempered the same way, with the Nordic piece's stats. |
| Standalone - Ebony quality | The same plugin name and items with the matching ebony piece's damage or armour rating, value, weight, material keyword and recipes (ebony ingots, Ebony Smithing, the ebony heading). |

Both Replacer files ship the first-person models and the shield as loose files at the vanilla paths (SkyPatcher cannot
reach them): put the mod below any other Nordic weapon or shield replacer. The Standalone files ship every file at this
mod's own paths and change no vanilla file.

Standalone items: Carved Nordic Sword, Carved Nordic War Axe, Carved Nordic Battleaxe, Carved Nordic Greatsword, Carved
Nordic Warhammer, Carved Nordic Dagger, Carved Nordic Mace, Carved Nordic Bow, Carved Nordic Shield.

Textures: our own TruePBR set (base colour, normal, RMAOS) at 2K, under `textures\pbr\ApocryphaTest\TrulyNordic\`.

## Requirements
- Skyrim Special Edition or Anniversary Edition with the Dragonborn DLC (included in both).
- SKSE64. SkyPatcher for the Replacer - No ESP file only.
- A TruePBR-capable renderer: Community Shaders with its TruePBR support.

## Building from source
`tools\build_all.sh` runs the pipeline: `gb_blender.py` (Blender + PyNifly: decimation and checks, face orientation,
the sheaths, blood shapes, the bow's weights), `textures.py` (BC7 DDS), `assemble.py` (game NIFs on the vanilla
structure, the sheath as the `Scb` shape), `silhouette.py`, `verify.py` (read-back: shader block, texture paths and the
face-direction check of `winding.py`) and `build-packages.py` (the four main files, each with its installer and a picture for every model option). The
Standalone plugins are built with houseCARL from `standalone_spec.py` / `standalone_assign.py` / `standalone_finish.py`.
The source models and maps come from the design work folder named in `tools\items.py`.
