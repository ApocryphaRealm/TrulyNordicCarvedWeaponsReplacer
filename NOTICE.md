# Notice

All models and textures in this mod were made for it by ApocryphaRealm: the geometry was built from scratch and the
texture maps (base colour, normal, RMAOS, the leather wrap) were painted procedurally by this project's own scripts.
No other mod's art ships in it.

The game NIFs reuse the structure of the Dragonborn DLC's own Nordic weapon and shield meshes (node layout, the blood
decal shaders, the first-person mace's scabbard ring) - Bethesda's data, present in every copy of the game, and
required for the weapons to behave as the game expects. The shader settings follow the plain TruePBR block that
PGPatcher writes for texture sets without a fuzz layer.

Tools used: Blender with PyNifly (mesh work), Microsoft texconv (BC7 compression), SkyPatcher (runtime model swap).

## Legacy of Ysgramor (the Replacer - Ebony files' optional step)

The "Carved Wolf Ebony weapons" choice puts this mod's own models on the Wolf Ebony weapons and shield of
**Legacy of Ysgramor** by **NordwarUA** ([Nexus 109963](https://www.nexusmods.com/skyrimspecialedition/mods/109963))
and of **Legacy of Ysgramor - My patches and fixes** by **Xtudo**
([Nexus 111121](https://www.nexusmods.com/skyrimspecialedition/mods/111121)). Nothing of either mod ships here: no
mesh, texture or plugin. This mod only places its own meshes at Legacy of Ysgramor's mesh paths and names those
records' FormIDs in SkyPatcher files that load only when their plugin is active. Legacy of Ysgramor's permissions
(recorded in this project's Ebony Wolf Armor and Weapons notice) allow modification and use of its assets with
credit, on Nexus only and never for sale; this mod stays within that and credits both authors.

## Licence
Truly Nordic Carved Weapons Replacer - Copyright (C) 2026 ApocryphaRealm.
This mod (its models, textures, SkyPatcher INIs and build scripts) is free software: you can redistribute it and/or
modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either
version 3 of the License, or (at your option) any later version. It is distributed in the hope that it will be
useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR
PURPOSE. See the GNU General Public License (LICENSE) for more details.
