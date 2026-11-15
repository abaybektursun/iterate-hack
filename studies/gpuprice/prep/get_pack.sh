#!/usr/bin/env bash
# Download the GPU price pack v0.1.1-handover into runs/gpuprice/ (not committed), check it, build the venv,
# and run the starter demo. Run from the repository root: bash studies/gpuprice/prep/get_pack.sh
set -euo pipefail
D=runs/gpuprice
ZIP_ID=1_TeAyT2SYBg3HcLCaFxeWVhA2K3rtN7j
SHA=f0b52af28c52545732208bcc4905facd9b941aa5779da683e1d9884c283b7c7c
mkdir -p $D/pack
[ -f $D/pack.zip ] || uvx gdown $ZIP_ID -O $D/pack.zip
echo "$SHA  $D/pack.zip" | sha256sum -c -
unzip -q -o $D/pack.zip -d $D/pack
P=$PWD/$D/pack/gpu-price-pack-v0.1.1-handover
(cd $P && ! sha256sum -c MANIFEST.sha256 | grep -v ': OK$')
[ -d $D/.venv ] || uv venv -q $D/.venv
uv pip install -q --python $D/.venv/bin/python duckdb pandas numpy pyarrow
PYTHON=$PWD/$D/.venv/bin/python bash $P/starter/run_demo.sh $P $PWD/$D/demo 2026-10-24
