#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OUTPUT_DIR="$SCRIPT_DIR/gifs"
FPS="${FPS:-12}"
WIDTH="${WIDTH:-960}"
FFMPEG_BIN="${FFMPEG_BIN:-}"

mkdir -p "$OUTPUT_DIR"

if [[ -z "$FFMPEG_BIN" ]]; then
  if command -v ffmpeg >/dev/null 2>&1; then
    FFMPEG_BIN="$(command -v ffmpeg)"
  else
    FFMPEG_BIN="$(python3 -c 'import imageio_ffmpeg; print(imageio_ffmpeg.get_ffmpeg_exe())' 2>/dev/null || true)"
  fi
fi

if [[ -z "$FFMPEG_BIN" || ! -x "$FFMPEG_BIN" ]]; then
  echo "ffmpeg executable not found. Install ffmpeg or imageio-ffmpeg first."
  exit 1
fi

convert_one() {
  local input="$1"
  local base
  base="$(basename "$input" .mov)"
  local palette="$OUTPUT_DIR/${base}-palette.png"
  local output="$OUTPUT_DIR/${base}.gif"

  "$FFMPEG_BIN" -y -i "$input" \
    -vf "fps=${FPS},scale=${WIDTH}:-1:flags=lanczos,palettegen" \
    "$palette"

  "$FFMPEG_BIN" -y -i "$input" -i "$palette" \
    -lavfi "fps=${FPS},scale=${WIDTH}:-1:flags=lanczos[x];[x][1:v]paletteuse" \
    "$output"

  rm -f "$palette"
  echo "Generated $output"
}

for name in cut1 cut1-v2 cut4 cut4-v2 cut6 cut8; do
  input="$SCRIPT_DIR/${name}.mov"
  if [[ ! -f "$input" ]]; then
    echo "Skipping missing file: $input"
    continue
  fi
  convert_one "$input"
done

echo "Done. GIF files are in $OUTPUT_DIR"
