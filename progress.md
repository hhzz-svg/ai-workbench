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
