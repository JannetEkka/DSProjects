#!/usr/bin/env bash
# Join the scene MP3s and lay them over a Playwright recording: mux.sh recording.webm audio_dir out.mp4
set -euo pipefail
video=$1; audio_dir=$2; out=$3
list=$(mktemp)
for f in "$audio_dir"/scene*.mp3; do echo "file '$(realpath "$f")'" >> "$list"; done
ffmpeg -y -loglevel error -f concat -safe 0 -i "$list" -c copy "$audio_dir/narration.mp3"
ffmpeg -y -loglevel error -i "$video" -i "$audio_dir/narration.mp3" \
  -c:v libx264 -pix_fmt yuv420p -preset veryfast -crf 23 -c:a aac -b:a 128k -shortest "$out"
rm -f "$list"
ffprobe -v error -show_entries format=duration -of csv=p=0 "$out"
