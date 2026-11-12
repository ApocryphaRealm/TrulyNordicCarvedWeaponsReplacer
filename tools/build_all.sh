#!/bin/sh
# Runs the whole game build of Truly Nordic Carved Weapons Replacer, in order. Needs Blender 5.2 with PyNifly,
# Python 3 with numpy, scipy and Pillow, and texconv (paths in textures.py / below).
set -e
T="$(cd "$(dirname "$0")" && pwd)"
B="C:/Program Files/Blender Foundation/Blender 5.2/blender.exe"
python -I "$T/items.py"
CFG="D:/Claude output/4. plans/nordic-carved-redesign-20261110/package/work/blender_config.json"
for k in sword sword2 battleaxe greatsword warhammer waraxe dagger mace mace2 bow shield shield2; do
  "$B" --background --factory-startup --python-exit-code 1 --python "$T/gb_blender.py" -- "$CFG" $k > "$(dirname "$CFG")/blender_$k.log" 2>&1
done
python -I "$T/textures.py"
python -I "$T/assemble.py"
python -I "$T/silhouette.py"
python -I "$T/verify.py"
python -I "$T/build-packages.py"
