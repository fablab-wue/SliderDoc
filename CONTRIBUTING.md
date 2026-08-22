<link rel="stylesheet" type="text/css" href="tools/SliderCtrl.css">
<style>
:root {
  --doc-title: "Contributing to SliderDoc";
  --doc-path: ".\\SliderDoc\\CONTRIBUTING.md";
}
</style>

# Contributing to SliderDoc

## Where to edit

| Topic | Path | Notes |
|-------|------|-------|
| UIC↔MC wire format | [contract/protocol.md](contract/protocol.md) | Regenerate [command cheat sheet](tools/render_command_cheatsheet.py) |
| UIC library API | [uic/api/overview.md](uic/api/overview.md) | Keep in sync with SliderCtrl source |
| JKSlider operator text | [uic/projects/jkslider/user-manual.md](uic/projects/jkslider/user-manual.md) | |
| JKSlider installer text | [uic/projects/jkslider/technical/](uic/projects/jkslider/technical/README.md) | Link [checklists](build/checklists/README.md) for scannable steps |
| MC firmware behaviour | [mc/*.md](mc/README.md) | Align with SliderMC source |
| Component catalog | [components/](components/README.md) | One file per module type |
| Generated assets | [assets/](assets/README.md), cheat-sheet folders | Run [tools/](tools/README.md) scripts; commit outputs |

## Conventions

- **Folders:** kebab-case (`motion-installer.md`, not `JKSlider_Technical_Manual_Motion.md`).
- **README:** Every folder has a `README.md` index for GitHub navigation.
- **Links inside SliderDoc:** relative paths.
- **Links from SliderCtrl / SliderMC:** full GitHub URLs to this repo (`https://github.com/fablab-wue/SliderDoc/blob/main/...`).

## Protocol command tables

`contract/protocol.md` is canonical prose. `tools/render_command_cheatsheet.py` (`GROUPS`) must stay aligned.

After editing either file:

```bash
python tools/render_command_cheatsheet.py
```

## Pre-commit checklist

1. Grep for stale paths: `manuals/`, `docs/ARCHITECTURE`, `../../SliderMC/docs`, `SliderDOC`.
2. Regenerate HTML/PDF/SVG if you changed protocol tables, pinouts, or cheat sheets.
3. Spot-check links from [README.md](README.md).

## Publishing docs site (future)

An [mkdocs.yml](mkdocs.yml) scaffold mirrors this tree. To enable GitHub Pages later:

1. `pip install mkdocs mkdocs-material`
2. `mkdocs serve` locally to preview
3. Enable Pages in repo Settings → build from `gh-pages` branch or GitHub Actions

No site deploy is configured in this pass.