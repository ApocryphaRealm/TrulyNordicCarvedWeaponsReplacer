# TrulyNordicCarvedWeaponsReplacer - changelog

Written as changes happen, not reconstructed afterwards (rule 61). Each version carries its
**version-ledger status**, so this file cannot quietly claim more than the ledger does:

* **working** - observed running in game
* **untested** - built and packaged, not yet confirmed
* **failed** - built but crashed or malfunctioned; the number was reclaimed
* **scratch** - a hypothesis-test build that never held a real number

## 1.1.0 - 2026-11-11 - untested

### Added
- Standalone files: the vanilla Nordic pieces stay untouched and the carved set is added as new items (Carved Nordic Sword, War Axe, Battleaxe, Greatsword, Warhammer, Dagger, Mace, Bow and Shield), forged and tempered where and as the Nordic pieces are. Two main files: Nordic quality (the Nordic pieces' stats and recipes) and Ebony quality (the ebony pieces' damage or armour, value, weight, material and recipes). One light plugin name for both, so the quality can be switched without losing the items.
- Installer choice: a straight one-handed sword (the greatsword's blade and upper hilt at one-hand size, with its own sheath) in place of the curved sword, in every main file.
- Installer choice: a clean shield - the crest as a plain carved disc with the boss in the middle, no points, spikes or straps - in every main file.
- Every choice in the installers shows a picture of the model it installs.
- Sheaths: the curved sword, the straight sword, the greatsword and the dagger each have a carved sheath of black leather with a carved steel locket and tip. It stays on the hip or back when the weapon is drawn.

### Changed
- The release is four main files (Replacer - No ESP, Replacer - ESP, Standalone - Nordic quality, Standalone - Ebony quality), each with its own installer that asks for the sword, the mace and the shield; the ESP / No ESP choice is now the choice of file.
- The curved sword's blade engraving now runs all the way up to the point.
- The battleaxe has a new head: a tall upper horn, one long curved cutting edge down to a single sharp beard point, and a curved back spike.

### Fixed
- The greatsword's leather wrap above the guard could be seen through: its faces pointed inward. Every face now points outward, and the build now refuses any model with faces wound the wrong way.

## 1.0.0 - 2026-11-10 - untested

### Added
- Two ways to install, chosen in the installer: No ESP (SkyPatcher, recommended) or a light ESP that needs no SkyPatcher.
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