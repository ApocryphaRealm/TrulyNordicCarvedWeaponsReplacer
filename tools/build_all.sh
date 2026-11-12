#!/bin/sh
# Runs the whole game build of Truly Nordic Carved Weapons Replacer, in order. Needs Blender 5.2 with PyNifly,
# Python 3 with numpy, scipy and Pillow, and texconv (paths in textures.py / below).
set -e
T="$(cd "$(dirname "$0")" && pwd)"
B="C:/Program Files/Blender Foundation/Blender 5.2/blender.exe"
python -I "$T/items.py"
CFG="D:/Claude output/4. plans/nordic-carved-redesign-20261110/package/work/blender_config.json"
for k in sword sword2 battleaxe greatsword warhammer waraxe dagger mace mace2 bow shield shield2 spear; do
  "$B" --background --factory-startup --python-exit-code 1 --python "$T/gb_blender.py" -- "$CFG" $k > "$(dirname "$CFG")/blender_$k.log" 2>&1
done
# the quiver / arrows: their own Blender step (no decimation; the arrows cut out of the quiver onto one arrow atlas)
"$B" --background --factory-startup --python-exit-code 1 --python "$T/gb_quiver.py" -- "$CFG" quiver > "$(dirname "$CFG")/blender_quiver.log" 2>&1
python -I "$T/quiver_atlas.py"
python -I "$T/textures.py"
python -I "$T/assemble.py"
python -I "$T/silhouette.py"
python -I "$T/verify.py"
python -I "$T/arrow_records.py"   # idempotent: adds the arrow records to the three plugins once
python -I "$T/additional_records.py"   # writes the optional file's light plugin (both qualities) from additional_spec.py, from scratch
python -I "$T/build-packages.py"
