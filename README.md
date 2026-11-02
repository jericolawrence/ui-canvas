# ui-canvas

A Claude Code plugin with one skill, `/ui-canvas`. It shows the UI from a task as editable HTML
frames on a design canvas:

- one titled row per section, flow or slice;
- frames named `<code> · <name>`;
- a header with the title and date, a blue sticky for sources, an orange one for guesses;
- for option work: Today, Option 1, Option 2 and a recommendation sticky in each row.

By default the canvas is a claude.ai Design artifact. It can instead go to a review site (a repo with
`build.mjs`, `features.json` and `explorations/`) when you ask for it or set `UI_CANVAS_REVIEW` to
its checkout.

## Install

In Claude Code:

```
/plugin marketplace add jericolawrence/ui-canvas
/plugin install ui-canvas@ui-canvas
```

Then type `/ui-canvas` with what you want drawn, for example
`/ui-canvas every sheet in the Drive feature`.

## Update

```
/plugin marketplace update ui-canvas
```

## Files

- `skills/ui-canvas/SKILL.md`: the look, frame format and publishing steps.
- `skills/ui-canvas/layout_canvas.py`: places frames, row titles and stickies into `canvas.json`.
