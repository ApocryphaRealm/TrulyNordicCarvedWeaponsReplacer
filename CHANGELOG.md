# TrulyNordicCarvedWeaponsReplacer - changelog

Written as changes happen, not reconstructed afterwards (rule 61). Each version carries its
**version-ledger status**, so this file cannot quietly claim more than the ledger does:

* **working** - observed running in game
* **untested** - built and packaged, not yet confirmed
* **failed** - built but crashed or malfunctioned; the number was reclaimed
* **scratch** - a hypothesis-test build that never held a real number

## 1.0.0 - 2026-11-10 - untested

### Added
- Installer option: the classic four-flanged mace instead of the default six-flanged one.
- Models swapped per weapon record through SkyPatcher, matched by the vanilla first-person model, so enchanted and added copies change too and other mods' vanilla-path Nordic meshes are not overwritten; first-person models and the shield ship at the vanilla paths.
- The Nordic War Axe: a new carved model (bearded blade, square hammer poll, triquetra), first-person model included, swapped by its record like the other weapons.
- New carved steel models for the Dragonborn Nordic sword, battleaxe, greatsword, warhammer, dagger, mace, bow and shield, each keeping what the weapon is (edges, head, silhouette) with black leather wrapped grips and carved knotwork, in our own 2K TruePBR textures.

### Changed
- The battleaxe, warhammer and war axe end in a straight forged pommel (a hand stop and a blunt knob) instead of a hooked butt; the length and the grip are unchanged.
- The shield sits where the vanilla shield does: its back and grip match vanilla's, so the arm no longer passes through it when held and it sits on the back like vanilla's.

### Fixed
- The Nordic bow is visible again and equips normally - its skinned parts now carry the shader's Skinned flag.
- The shield could be seen through from behind: the back of the board and of the steel crest faced the wrong way. Every face now points outward.
- The shield's collision is rebuilt from the corrected model.