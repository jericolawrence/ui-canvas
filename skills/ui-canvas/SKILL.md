---
name: ui-canvas
description: Present the UI from this task as editable HTML frames on a design canvas (titled rows per section, frames named "<code> · <name>", header stickies). By default a claude.ai Design canvas artifact; a review-site exploration when asked. Use when the user types /ui-canvas, or asks for UI "laid out as a UI canvas".
disable-model-invocation: true
---

# UI canvas

This skill only says **how to show the result**. What goes on the canvas comes from the rest of the
user's prompt: screens from a repo, a redesign of a picture they sent, all the sheets of a feature,
new directions with options. Do that work the way the prompt asks, then lay it out as below.

`layout_canvas.py` sits next to this file (the base directory shown when the skill loads). It
places every frame, row title and sticky, so never hand-place coordinates.

## Where it goes

Pick one target, then follow its section under **Publishing**:

- **Design canvas artifact** (default): a claude.ai Design-type artifact, private, one per canvas.
  Use it unless the user asks for the review site.
- **Review site**: when the user names it, or `$UI_CANVAS_REVIEW` (a checkout path) is set. A review
  site is a repo with `build.mjs`, `features.json` and an `explorations/` folder; read its README
  first.

When the user asks for several canvases that belong together (one per phase, per feature area),
make one artifact each, give them a shared title prefix ("Wallet redesign · Phase A · …") and pin
them, so they sit together in the sidebar. There is no folder or group feature for artifacts.

## The look

- **One canvas per subject**, titled "<Subject> UI" unless the user names it. If the user points at
  an existing canvas, or says "in a page", add to it (a new page when asked) instead of making
  another.
- **Editable frames.** Each frame rebuilds the screen in real markup: text as text, buttons as
  `<button>`, icons as inline SVG (SF Symbols shapes for iOS), real colors, fonts and spacing from
  the source (the code, the design tokens, Figma, or the picture). Never a screenshot pasted in as
  the UI. A screenshot or the user's picture may sit as a reference frame beside its rebuild, titled
  "<code> · <name> · reference".
- **Frame size:** the device the UI is for; phone screens 390 wide, height to fit (390×844 by
  default). Sheets and dialogs are drawn over their dimmed parent screen, full frame.
- **Header** (above the first row): a `title1` note "<title> · <D Mon YYYY>", then 1–3 stickies
  side by side:
  - blue: what this canvas shows and where it came from (repo, branch + short commit, Figma file,
    or "from your picture"), and that comments on a frame mark what to change;
  - orange, only if there is something: what was spotted on the way (duplicates, states that
    couldn't be drawn and why, guesses made).
- **Rows:** one per section, flow or slice, in the source's order, with a `title1` note above
  naming it. A note about the row becomes a gray sticky at the end of it.
- **Options:** when the prompt asks for directions, each row reads left to right: Today frames
  ("<code> · <name> · today"), Option 1 frames, Option 2 frames, then the gray sticky saying what
  the options differ on and which is recommended and why. Mark the pick in its frame titles
  ("… · Option 2 (recommended)"). Show the 2–4 screens per option that best show the direction
  (empty, filled, error), not every frame.
- **Names:** every frame titled "<code> · <name>". Use the source's codes when it has them (a
  screen catalog, Figma frame codes), else short ones: the row's first letter + two digits (`S01`),
  or `<row>-O1-01` for options. File names: the code + `.dc.html`, `Main.dc.html` for the first.
- **Spacing:** the layout script places everything (80 px between frames, 380 px between rows, row
  titles 260 px above their row, header title at y −1000 and stickies at y −770).

## Frame format

One static HTML file per frame. The root element is the frame's exact size. No `{{…}}` bindings,
no handlers.

```html
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>S01 · Sort</title>
<script src="./support.js"></script>
</head>
<body>
<x-dc>
<helmet>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Lato:wght@400;700&display=swap">
<style>body{margin:0}button{cursor:pointer;margin:0}</style>
</helmet>
<div style="width:390px;height:844px;position:relative;overflow:hidden;background:#0E1118;font-family:Lato,-apple-system,sans-serif;color:#fff">
  …
</div>
</x-dc>
<script type="text/x-dc" data-dc-script data-props='{"$preview":{"width":390,"height":844}}'>
class Component extends DCLogic { renderVals() { return {}; } }
</script>
</body>
</html>
```

The `support.js` line and the `data-dc-script` block are what a Design artifact needs; a review
site's build reads only what is inside `<x-dc>` and ignores them, so one format serves both.
Set `$preview` to the frame's size.

## Layout

Write `<scratch>/layout.json`, then run the script; it writes `canvas.json` with every frame, row
title and sticky placed:

```json
{
  "title": "Drive sheets · 21 Oct 2026",
  "stickies": [
    {"fill": "blue", "text": "Every Drive sheet in the app repo (main, fea556239b), rebuilt as editable frames. Comment on a frame to mark what to change."},
    {"fill": "orange", "text": "Spotted on the way\nThe upload fix sheet needs a failed upload; drawn with sample data."}
  ],
  "page": {"id": "sheets", "name": "Sheets"},
  "rows": [
    {"title": "Sort and options", "note": "Opened from the ⋯ button on a file",
     "frames": [
       {"file": "Main.dc.html", "title": "S01 · Sort", "w": 390, "h": 844},
       {"file": "S02.dc.html", "title": "S02 · File options", "w": 390, "h": 844}
     ]}
  ]
}
```

```bash
python3 <skill dir>/layout_canvas.py <scratch>/layout.json <canvas folder>/canvas.json
```

`page` is optional (leave it out for a single-page canvas). Adding to an existing canvas: the script
keeps everything in its `canvas.json` and places the new rows below what is already on that page
(or on the new page). For a new Design artifact, set the `title` key in the written `canvas.json`
to the artifact's title (without the date) before publishing.

## Publishing

### Design canvas artifact

1. Start it from the Design type (`Artifact` quickstart with intent `design`, or the Design
   `type_url` from a types listing) with the canvas title. Read the type's instructions that come
   back and follow them where they differ from this file.
2. Work in `<scratch>/<canvas>/project/`: frames there, `canvas.json` from the layout script there.
3. Publish `canvas.json` and `Main.dc.html` first in one call (`url`, `root` = the folder holding
   `project/`, `file_path` = `canvas.json`, `files` map), then the rest in a few batched calls,
   each with only new files.
4. Render-check before reporting: load every frame in headless Chrome (with a stub `support.js`)
   and look at a contact sheet; fix any blank or broken frame.
5. Pin the artifact when it is one of a set, or when the user asked.

### Review site

1. Checkout: `$UI_CANVAS_REVIEW`. Feature id: a short kebab-case slug for the subject, unless the
   user names one; it is the folder and the URL (`explorations/<feature>/` → `/<feature>/`) and must
   not clash with an id in `features.json` unless the user points at that exploration.
2. Frames in `explorations/<feature>/`, images in its `img/` (`build.mjs` only copies `img/` and
   `png/`, and only rewrites `./img/…` paths). `canvas.json` from the layout script there.
3. Add one `features.json` entry, status always `Exploring` (only the user changes status):
   `{"id": "<feature>", "name": "<Subject> UI", "status": "Exploring", "source": "explorations/<feature>", "figma": null}`
4. `node build.mjs` must print `<Subject> UI: <n> frames on <p> pages …` with your frame count.
5. Commit `explorations/<feature>/` and `features.json` ("Add the <feature> exploration"), then
   `git pull --rebase` and push to `${UI_CANVAS_REVIEW_BRANCH:-main}`. If either fails, stop and
   report it with the commit hash; don't deploy what isn't on GitHub. Then deploy the way the
   README says (`bash deploy.sh`).

## Report

The link(s), frame count per canvas, the rows, the recommendation per row when there are options,
and anything in the orange sticky.
