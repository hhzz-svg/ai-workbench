## 2026-06-15 - Task: Redesign showcase page for AI Workbench
### What was done
- Rebuilt the Cloudflare Pages showcase as a professional product page focused on the local AI creation workbench.
- Added real visual assets: a captured workbench screenshot, the provided academic poster rendered from PDF, and a short autoplay preview video generated from the workbench screenshot.
- Reframed the page around the core project strength: unified integration of PPT, paper polishing, academic poster, visual poster, and web presentation Skill interfaces.

### Testing
- Rendered the provided academic poster PDF to `landing-page/assets/academic-poster.jpg` and visually inspected the resulting image.
- Opened the redesigned landing page through a temporary local HTTP server in Chrome and confirmed the title, hero text, video source, image loading, and page width.
- Confirmed the preview video is 1920x1080 and 8 seconds long with `ffprobe`.
- Verified the temporary local HTTP server was stopped after preview.

### Notes
- `landing-page/index.html` - Replaced the old generic showcase with a professional workbench-focused page, including autoplay video, real screenshots, Skill matrix, workflow explanation, local-only notice, and artifact showcase.
- `landing-page/assets/workbench-console-wide.png` - Added the real local workbench screenshot used as the hero fallback and operation console preview.
- `landing-page/assets/academic-poster.jpg` - Added the rendered academic poster asset from the user-provided PDF.
- `landing-page/assets/workbench-demo.mp4` - Added the lightweight autoplay preview video generated from the workbench screenshot.
- `progress.md` - Added this task record because the repository files were modified.
- Rollback: restore `landing-page/index.html` from the previous commit and remove the three files under `landing-page/assets/`; if this log entry also needs to be removed, restore or edit `progress.md` accordingly.

## 2026-06-15 - Task: Replace showcase images with multiple poster scenarios
### What was done
- Replaced the single poster showcase with a multi-scene gallery covering Mondo-style visual posters, an English research poster, and an engineering academic poster.
- Added prompt/input notes next to each scenario so visitors can see what kind of request leads to each output.
- Optimized the new gallery images for web delivery before wiring them into the Cloudflare Pages showcase.

### Testing
- Downloaded and inspected representative Mondo poster examples from `joeseesun/qiaomu-mondo-poster-design`.
- Rendered the provided English PDA poster PDF into `landing-page/assets/english-pda-poster.jpg` and visually inspected it.
- Copied the provided academic poster image into `landing-page/assets/academic-sensor-poster.jpg` and visually inspected it.
- Served `landing-page` through a temporary local HTTP server and verified in Chrome that all images load, the video remains available, and the page has no horizontal overflow.

### Notes
- `landing-page/index.html` - Replaced the old single poster section with a multi-scene gallery and updated image references, navigation text, and scenario copy.
- `landing-page/assets/mondo-sapiens.jpg` - Added optimized visual poster example for a book/public account cover scenario.
- `landing-page/assets/mondo-interstellar.jpg` - Added optimized visual poster example for a cinematic public account cover scenario.
- `landing-page/assets/mondo-mood.jpg` - Added optimized visual poster example for a vertical social poster scenario.
- `landing-page/assets/english-pda-poster.jpg` - Added optimized English research poster image rendered from the provided PDF.
- `landing-page/assets/academic-sensor-poster.jpg` - Added the provided engineering academic poster image.
- `landing-page/assets/academic-poster.jpg` - Removed the previous single academic poster image because the showcase now uses the user-provided academic poster.
- `progress.md` - Added this task record because the repository files were modified.
- Rollback: revert this commit or restore `landing-page/index.html`, remove the five new gallery assets, and restore `landing-page/assets/academic-poster.jpg` from the previous commit.
