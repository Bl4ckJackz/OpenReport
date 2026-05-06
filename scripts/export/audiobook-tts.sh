#!/usr/bin/env bash
# audiobook-tts.sh — genera MP3 audiobook della relazione.
#
# Feature:
# - Legge markdown/testo
# - Skip code block, URL, tabelle
# - Pausa fra sezioni
# - Concatena paragrafi in unico MP3 (o chapter per capitolo)
#
# Usage:
#   audiobook-tts.sh <file.md> --lang it [--output-dir audio/]
#                    [--chapter-per-h1] [--speed 1.0]
set -uo pipefail

FILE=""
LANG="it"
OUTPUT_DIR=""
CHAPTER_PER_H1=0
SPEED=1.0

while [ $# -gt 0 ]; do
  case "$1" in
    --lang) LANG="$2"; shift 2 ;;
    --output-dir) OUTPUT_DIR="$2"; shift 2 ;;
    --chapter-per-h1) CHAPTER_PER_H1=1; shift ;;
    --speed) SPEED="$2"; shift 2 ;;
    *) FILE="$1"; shift ;;
  esac
done

if [ -z "$FILE" ] || [ ! -f "$FILE" ]; then
  echo "Usage: $0 <file.md> [--lang it] [--output-dir audio/] [--chapter-per-h1]" >&2
  exit 2
fi

# Rileva TTS disponibile
TTS_CMD=""
ESPEAK_ARGS=""
if command -v espeak-ng >/dev/null 2>&1; then
  TTS_CMD="espeak-ng"
  ESPEAK_ARGS="-v $LANG -s $(echo "$SPEED * 175" | bc 2>/dev/null || echo 175)"
elif command -v say >/dev/null 2>&1; then
  TTS_CMD="say"
elif command -v pico2wave >/dev/null 2>&1; then
  TTS_CMD="pico2wave"
else
  echo "[ERR] nessun TTS disponibile" >&2
  echo "  Linux: apt install espeak-ng" >&2
  echo "  macOS: 'say' built-in" >&2
  echo "  Windows: installa espeak-ng per Windows" >&2
  exit 3
fi

# Converter MP3 preferibile se ffmpeg/lame disponibili
MP3_CONVERTER=""
if command -v ffmpeg >/dev/null 2>&1; then
  MP3_CONVERTER="ffmpeg"
elif command -v lame >/dev/null 2>&1; then
  MP3_CONVERTER="lame"
fi

OUTPUT_DIR="${OUTPUT_DIR:-${FILE%.md}-audiobook}"
mkdir -p "$OUTPUT_DIR"

# Split per capitoli (H1) se richiesto
python3 << EOF > "$OUTPUT_DIR/chapters.txt"
import re, pathlib
text = pathlib.Path("$FILE").read_text(encoding="utf-8")
text = re.sub(r'\`\`\`[\s\S]*?\`\`\`', '', text)  # code blocks
text = re.sub(r'\|[^\n]+\|', '', text)  # tables
text = re.sub(r'!\[.*?\]\(.*?\)', '', text)  # images
text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)  # links
text = re.sub(r'https?://\S+', ' ', text)
text = re.sub(r'[#*_\[\]\`\\{}]', '', text)

chapters = []
if $CHAPTER_PER_H1:
    parts = re.split(r'^# (.+)$', text, flags=re.MULTILINE)
    # parts = ['', 'title1', 'body1', 'title2', 'body2', ...]
    if len(parts) > 1:
        for i in range(1, len(parts), 2):
            chapters.append((parts[i].strip(), parts[i+1] if i+1 < len(parts) else ''))
    else:
        chapters.append(("full", text))
else:
    chapters.append(("full", text))

for idx, (title, body) in enumerate(chapters, 1):
    safe = re.sub(r'\W+', '-', title)[:40]
    filename = f"ch{idx:02d}-{safe}"
    with open(f"$OUTPUT_DIR/{filename}.txt", "w", encoding="utf-8") as f:
        f.write(body.strip())
    print(f"{filename}|{title}")
EOF

CHAPTER_COUNT=0
while IFS='|' read -r filename title; do
  CHAPTER_COUNT=$((CHAPTER_COUNT + 1))
  TXT_FILE="$OUTPUT_DIR/${filename}.txt"
  WAV_FILE="$OUTPUT_DIR/${filename}.wav"
  MP3_FILE="$OUTPUT_DIR/${filename}.mp3"

  echo "[$CHAPTER_COUNT] $title"

  case "$TTS_CMD" in
    espeak-ng)
      espeak-ng $ESPEAK_ARGS -f "$TXT_FILE" -w "$WAV_FILE" 2>/dev/null || true
      ;;
    say)
      say -v Alice -r $(echo "$SPEED * 200" | bc 2>/dev/null || echo 200) -f "$TXT_FILE" -o "$WAV_FILE" --data-format=LEF32@22050
      ;;
    pico2wave)
      pico2wave -l="${LANG}-${LANG^^}" -w "$WAV_FILE" "$(cat "$TXT_FILE")" 2>/dev/null || true
      ;;
  esac

  if [ -n "$MP3_CONVERTER" ] && [ -f "$WAV_FILE" ]; then
    case "$MP3_CONVERTER" in
      ffmpeg) ffmpeg -y -i "$WAV_FILE" -codec:a libmp3lame -qscale:a 4 "$MP3_FILE" 2>/dev/null ;;
      lame) lame --quiet "$WAV_FILE" "$MP3_FILE" ;;
    esac
    rm -f "$WAV_FILE"
  fi
done < "$OUTPUT_DIR/chapters.txt"

TOTAL_SIZE=$(du -sh "$OUTPUT_DIR" | cut -f1)
echo ""
echo "[OK] Audiobook generato in $OUTPUT_DIR/ ($CHAPTER_COUNT capitoli, $TOTAL_SIZE)"
