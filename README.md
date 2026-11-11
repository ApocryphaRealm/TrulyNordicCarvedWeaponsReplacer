# Truly Nordic Carved Weapons Replacer

New models for the Dragonborn Nordic weapons and shield: steel forged and carved in the Nordic way, with black leather
wrapped grips and knotwork filling every face. Each weapon keeps what it is - its edges, its head, its silhouette - and
is rebuilt to be realistic in proportion, thickness and construction.

## What it changes
| Item | New look |
|---|---|
| Nordic Sword | single-edged curved blade, one-piece half guard sweeping up, hooked pommel, bold carved braid |
| Nordic Battleaxe | steel haft forged in one piece with the head, carved knot fields on both faces, a forged knob pommel |
| Nordic Greatsword | double-edged blade, carved guards and ricasso, two wrapped grips |
| Nordic Warhammer | hammer face and curved pick, a triquetra ring centred on the face, a forged knob pommel |
| Nordic War Axe | bearded blade with a square hammer poll, a triquetra at the widest point, a forged knob pommel |
| Nordic Dagger | kukri form, a world serpent carved along the belly |
| Nordic Mace | six-flanged head, a biting maw on every flange (installer option: the classic four-flanged mace) |
| Nordic Bow | all-steel bow, a triquetra on the riser; the string still draws and follows the arrow |
| Nordic Shield | the carved crest filled out to the rim, the four points in place; sits on the arm and on the back where the vanilla shield does |

Every enchanted variant uses the same model as its base weapon, so all of them change.

## How it works
- No plugin. The weapons' third-person, ground and inventory models are swapped per record by SkyPatcher
  (`SKSE\Plugins\SkyPatcher\weapon\TrulyNordicCarvedWeaponsReplacer\`), matched by the weapon's first-person model, so
  copies of these weapons added by other mods change too, and other mods that replace the vanilla Nordic meshes are left
  alone.
- The first-person models (which SkyPatcher cannot reach) and the shield (one model for every view) are loose files at
  the vanilla paths. Put this mod below any other Nordic weapon or shield replacer.
- Textures: our own TruePBR set (base colour, normal, RMAOS) at 2K, under `textures\pbr\ApocryphaTest\TrulyNordic\`.

## Requirements
- Skyrim Special Edition or Anniversary Edition with the Dragonborn DLC (included in both).
- SKSE64 and SkyPatcher.
- A TruePBR-capable renderer: Community Shaders with its TruePBR support.

## Installer
- Default: everything, with the six-flanged mace.
- Option: the classic mace (four flanges, the same biting maw).

## Building from source
`tools\build_all.sh` runs the pipeline: `gb_blender.py` (Blender + PyNifly: decimation and checks, blood shapes, the
bow's weights), `textures.py` (BC7 DDS), `assemble.py` (game NIFs on the vanilla structure), `verify.py` (read-back) and
`build-fomod.py` (the installer package). The source models and maps come from the design work folder named in
`tools\items.py`.
