"""Turn a narration script into one MP3 per scene, with free edge-tts voices.

Usage: python narrate.py script.txt out_dir [voice]
Scenes are separated by blank lines. Prints each scene's length in seconds,
so the browser recording can hold each scene for as long as its narration.
"""
import asyncio
import os
import ssl
import subprocess
import sys
from pathlib import Path

import edge_tts.communicate as communicate

# Cloud sessions reach the internet through a proxy with its own CA bundle.
CA_BUNDLE = "/root/.ccr/ca-bundle.crt"
if os.path.exists(CA_BUNDLE):
    communicate._SSL_CTX = ssl.create_default_context(cafile=CA_BUNDLE)


async def main(script: Path, out_dir: Path, voice: str) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    scenes = [s.strip() for s in script.read_text().split("\n\n") if s.strip()]
    proxy = os.environ.get("HTTPS_PROXY")
    for i, text in enumerate(scenes, 1):
        path = out_dir / f"scene{i:02d}.mp3"
        await communicate.Communicate(text, voice, proxy=proxy).save(str(path))
        seconds = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)],
            capture_output=True, text=True, check=True,
        ).stdout.strip()
        print(f"{path.name}\t{float(seconds):.1f}s")


if __name__ == "__main__":
    voice = sys.argv[3] if len(sys.argv) > 3 else "en-IN-NeerjaNeural"
    asyncio.run(main(Path(sys.argv[1]), Path(sys.argv[2]), voice))
