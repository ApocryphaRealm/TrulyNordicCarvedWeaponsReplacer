# TrulyNordicCarvedWeaponsReplacer - changelog

Written as changes happen, not reconstructed afterwards (rule 61). Each version carries its
**version-ledger status**, so this file cannot quietly claim more than the ledger does:

* **working** - observed running in game
* **untested** - built and packaged, not yet confirmed
* **failed** - built but crashed or malfunctioned; the number was reclaimed
* **scratch** - a hypothesis-test build that never held a real number

## 1.3.0 - 2026-11-13 - untested

### Changed
- The Standalone - Ebony quality installer shows each model choice in black and gold, and so does the Ebony quality choice of Additional Weapons.
- The Ebony quality files have their own look: black ebony steel with every carved braid, weave and symbol rim in polished gold, the dark carving floors kept for contrast, and the rings and bands on every haft and grip in gold. Every piece of the Standalone - Ebony quality file and the Ebony quality spear and halberd of Additional Weapons take it, sheaths, quiver and arrows included. The Nordic quality and Replacer files are unchanged.

## 1.2.0 - 2026-11-12 - untested

### Added
- Nordic arrows and quiver, carved anew: black fletching and barbed steel heads, in a carved leather quiver whose collar plate carries the triquetra on a dark disc inside a polished ring. The arrows drop out of the quiver on the back as the count falls, and the nocked arrow and the arrow in flight are the same carved arrow.
- Replacer files: the Nordic arrow takes the new quiver by its record (through SkyPatcher in No ESP, through the plugin in ESP), and the arrow in flight is a loose model at the vanilla path.
- Standalone files: Carved Nordic Arrows as new items with their own projectile, forged at the forge like the Nordic arrows; the Ebony quality file gives them the ebony arrow numbers and forges them from firewood and an ebony ingot with Ebony Smithing.
- New optional file, Additional Weapons: carved weapons the game does not have, in their own light plugin, installed beside any main file. The first is a carved spear with the triquetra on a dark ring at its head, carried on the back, forged and tempered, at Nordic or Ebony quality (an installer choice).
- Additional Weapons installer step, Spear animations: the spear uses the battleaxe moveset by default; the second choice adds the WeapTypeHalberd, 000WeapTypeSoS and WeapTypeSpear keywords to it through Keyword Item Distributor, so spear animation packs pick it up.
- Additional Weapons: a carved Nordic halberd. It has a bearded blade with a braid border, a woven field and the triquetra on a dark ring; a straight back spike and a narrow top blade, each with a carved braid; a dark ash haft with riveted langets and the black grip wrap. It is 163 units long, the length of Animated Armoury's halberds. It is carried on the back, forged and tempered, at Nordic or Ebony quality.
- Additional Weapons installer step, Halberd animations: the halberd uses the battleaxe moveset by default. The second choice adds Animated Armoury's WeapTypeHalberd keyword through Keyword Item Distributor, so Animated Armoury's halberd moveset and Simple Dodge's halberd dodge set pick it up.

### Changed
- The six-flanged mace is re-carved with the set's weave and a triquetra on a dark disc in a polished ring, in place of the biting maw.
- The dagger has a new default design carved with the set's braid and a black-ring triquetra; the serpent dagger stays as an installer option (Dagger step). Both daggers' guards are evenly rounded.
- One naming convention, Carved Nordic, across every file. The Replacer files now rename the Nordic weapons, the Nordic shield and the Nordic arrow to Carved Nordic Sword, Carved Nordic Shield, Carved Nordic Arrow and so on. The ESP file also renames the enchanted copies, keeping each enchantment's name: Virtuous Carved Nordic Sword, Carved Nordic Mace of Fear. The No ESP file renames the base pieces through SkyPatcher and leaves the enchanted copies' names to the game or the enchantment mod in use.
- Every carved Norse symbol now sits on a dark filled disc inside a polished ring: the lockets of the dagger, curved sword, straight sword and greatsword sheaths, the greatsword pommel and both plates of the bow riser. The models are unchanged; only the carving is repainted.

### Known
- The arrow in flight ships as a loose file at the vanilla path; when another mod also replaces it, give this mod the higher priority (lower in the Mod Organizer 2 list) for the carved arrow to show.

### Fixed
- The curved and straight swords' sheaths no longer clip into armour on the hip.

## 1.1.1 - 2026-11-12 - untested

### Fixed
- The curved sword's guard and pommel, the steel fittings of every sheath and the shields' crest points shade evenly; their edges were smoothed into the faces beside them.
- The battleaxe's carved cheek is one flat surface on each side, so the carving no longer bunches or streaks on the upper horn where it joins the blade; the polished bevel along the edge now takes the taper.
- The greatsword's carved braid is even all the way to the point; the in-game model had stretched it into a ladder from half way up the blade. The greatsword's blade is no longer simplified for the game, so its texture lies exactly as designed.

### Changed
- The battleaxe's triquetra sits on a dark disc inside a polished ring, as on the war axe and warhammer, with a slightly finer weave round it; the back spike's weave now runs the same way as the rest of the head.

## 1.1.0 - 2026-11-11 - untested

### Added
- Standalone files: the vanilla Nordic pieces stay untouched and the carved set is added as new items (Carved Nordic Sword, War Axe, Battleaxe, Greatsword, Warhammer, Dagger, Mace, Bow and Shield), forged and tempered where and as the Nordic pieces are. Two main files: Nordic quality (the Nordic pieces' stats and recipes) and Ebony quality (the ebony pieces' damage or armour, value, weight, material and recipes). One light plugin name for both, so the quality can be switched without losing the items.
- Installer choice: a straight one-handed sword (the greatsword's blade and upper hilt at one-hand size, with its own sheath) in place of the curved sword, in every main file.
- Installer choice: a clean shield - the crest as a plain carved disc with the boss in the middle, no points, spikes or straps - in every main file.
- Every choice in the installers shows a picture of the model it installs.
- Sheaths: the curved sword, the straight sword, the greatsword and the dagger each have a carved sheath of black leather with a carved steel locket and tip. It stays on the hip or back when the weapon is drawn.

### Changed
- Asset folder renamed: the models are under meshes\TrulyNordic and the textures under textures\pbr\TrulyNordic (the files themselves are unchanged).
- Both maces have pointed striking edges: the six-flanged mace (the default) and the classic four-flanged one (the installer option).
- The greatsword's lower-guard medallion sits on a level boss.
- The bow's riser is carved anew: a steel plate with a triquetra in a woven field inside a braid border, and a braid band running along the riser. It is still skinned to the vanilla bow's bones, so the string draws and follows the arrow.
- The release is four main files (Replacer - No ESP, Replacer - ESP, Standalone - Nordic quality, Standalone - Ebony quality), each with its own installer that asks for the sword, the mace and the shield; the ESP / No ESP choice is now the choice of file.
- The curved sword's blade engraving now runs all the way up to the point.
- The battleaxe has a new head: a tall upper horn, one long curved cutting edge down to a single sharp beard point, and a curved back spike.

### Fixed
- The flat carved faces of the greatsword's guards and pommel, the straight sword's guard and pommel and the bow's riser looked uneven under light, like a cushion, because their edges were smoothed into the bevel round them. They now shade flat; the shape and the carving are unchanged.
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