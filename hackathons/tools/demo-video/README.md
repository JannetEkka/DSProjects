# Demo videos, recorded in a cloud session

Every hackathon entry needs a demo video, and Jannet is away for most of the build windows. This is how Claude records one without a screen or a microphone: a headless browser records the app, a free neural voice reads the narration, and ffmpeg joins the two. Tested in a cloud session on 2026-10-06.

1. **Write the narration** as `script.txt`, one scene per paragraph, with a blank line between scenes.
2. **Generate the voice**, one MP3 per scene. It prints each scene's length.
   ```bash
   pip install edge-tts
   python narrate.py script.txt audio/            # default voice en-IN-NeerjaNeural
   ```
3. **Record the app** with Playwright, holding each scene for as long as its narration runs. Use the Chromium already installed in the session (`npm i playwright`, never `playwright install`):
   ```js
   import { chromium } from 'playwright';
   const browser = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium' });
   const ctx = await browser.newContext({
     viewport: { width: 1280, height: 720 },
     recordVideo: { dir: 'rec', size: { width: 1280, height: 720 } },
   });
   const page = await ctx.newPage();
   await page.goto('http://localhost:8000');
   await page.waitForTimeout(6200);   // scene01 length
   // ...one block of clicks and waits per scene
   await ctx.close();                 // writes rec/*.webm
   await browser.close();
   ```
4. **Join them** into an MP4 (H.264 + AAC, which plays everywhere):
   ```bash
   ./mux.sh rec/<file>.webm audio/ demo.mp4
   ```

The finished MP4 is attached to a GitHub release in the entry's repo, so there's a public link without anyone's YouTube account. Jannet can re-upload it to YouTube, or record her own voice over it, if a form asks for that.
