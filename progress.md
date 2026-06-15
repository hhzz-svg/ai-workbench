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

## 2026-06-15 - Task: Tighten showcase gallery layout and prompts
### What was done
- Reworked the Mondo poster gallery into a balanced 2x2 layout so the section no longer leaves an empty column.
- Added the GitHub README's 小王子 example to fill the visual design gallery.
- Updated the Mondo prompt text and style notes to match the source README wording.

### Testing
- Checked that all four Mondo prompt strings are present exactly as quoted in the source README examples.
- Served `landing-page` through a temporary local HTTP server and verified in Chrome that the Mondo gallery renders as two equal columns, all images load, and the page has no horizontal overflow.
- Confirmed the temporary local HTTP server and preview tab were closed after verification.

### Notes
- `landing-page/index.html` - Changed the visual poster gallery layout from uneven span-based cards to a 2x2 grid and updated prompt/style copy.
- `landing-page/assets/mondo-prince.jpg` - Added optimized 小王子 Mondo example image from the referenced GitHub repository.
- `progress.md` - Added this task record because the repository files were modified.
- Rollback: revert this commit or remove `landing-page/assets/mondo-prince.jpg` and restore the previous gallery CSS/content in `landing-page/index.html`.

## 2026-06-15 - Task: Replace English poster showcase with BMW case poster
### What was done
- Replaced the English PDA research poster showcase with the provided BMW 7-Series Project English case poster.
- Updated the scenario title, description, image alt text, and input prompt to match the BMW business case poster.
- Removed the old PDA poster asset from the landing page assets.

### Testing
- Optimized the provided BMW poster image into `landing-page/assets/english-bmw-poster.jpg`.
- Checked that the landing page references the BMW poster and prompt, and no longer references the old PDA poster text or asset.
- Served `landing-page` through a temporary local HTTP server and verified in Chrome that the BMW poster loads, the old PDA reference is absent, and the page has no horizontal overflow.

### Notes
- `landing-page/index.html` - Updated the English poster showcase copy and image reference from the PDA research poster to the BMW 7-Series business case poster.
- `landing-page/assets/english-bmw-poster.jpg` - Added the optimized BMW poster image from the provided source file.
- `landing-page/assets/english-pda-poster.jpg` - Removed the previous English PDA poster image.
- `progress.md` - Added this task record because the repository files were modified.
- Rollback: revert this commit or restore `landing-page/index.html`, remove `landing-page/assets/english-bmw-poster.jpg`, and restore `landing-page/assets/english-pda-poster.jpg` from the previous commit.
