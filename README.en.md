# Claude Code: scans → DXF → IFC model → visualisations (Windows)

[Polski](README.md) · English

A Claude Code plugin for architects. You describe in plain language what you need, and Claude redraws scanned building documentation into DXF, builds an IFC model and renders visualisations in Blender. You do not need to know the scripts — they run in the background.

Version for Windows 10/11. macOS version: [claude-architekt-mac](https://github.com/arrzarr81/claude-architekt-mac).

The plugin's internal instructions are written in Polish, but Claude replies in the language you write in.

## Installation (once, about 20 minutes)

You need a Claude **Pro** plan (to try it out) or **Max** (for daily work). An NVIDIA graphics card makes rendering much faster but is not required.

**How to open PowerShell:** press the Windows key, type `powershell` and press Enter. A window opens where you type commands. Confirm each command with Enter. Use PowerShell, not "Command Prompt" (cmd) — the commands below are for PowerShell.

1. In PowerShell, type two commands:

   ```
   winget install --id Git.Git -e
   irm https://claude.ai/install.ps1 | iex
   ```

   The first command installs **Git**. It is needed for two reasons: on Windows, Claude Code runs its own commands through it (the "Git Bash" program that comes with Git), and the plugin saves the project history in it after each step, so you can always go back to an earlier version of the drawings if a change goes wrong. The second command installs **Claude Code**.
2. Close the PowerShell window and open it again (as above).
3. Create a folder for your projects and go to it. If you have a **D:** drive (File Explorer → This PC), use it:

   ```
   mkdir D:\Projects
   cd D:\Projects
   ```

   Without a D: drive, type the same with `C:` instead of `D:`. If the folder already exists, `mkdir` shows a red error you can ignore. Do not keep projects on the Desktop or in Documents if OneDrive syncs them.
4. Type `claude` and sign in with your Claude account. Then type in Claude Code:

   ```
   /plugin marketplace add arrzarr81/claude-architekt-windows
   /plugin install architekt@claude-architekt-windows
   ```

5. Write: **"Prepare my computer for work."** Claude installs Python, the libraries and Blender by itself and checks that they work. When Windows asks for administrator permission, click "Yes".

## New project

Each building is a separate folder, with no spaces or special characters in its name. Open PowerShell and type (replace `Project1` with your project name, and `D:` with `C:` if you have no D: drive):

```
mkdir D:\Projects\Project1
cd D:\Projects\Project1
explorer .
```

The last command opens the folder in File Explorer: drag your scans (PDF, JPG) into it. Then go back to the PowerShell window, type `claude` and write "new project".

**Coming back to a project the next day:** open PowerShell, type `cd D:\Projects\Project1`, then `claude`. Claude always works in the folder it was started in and sees only its contents.

## Working

Example requests:

- "Make a list of the drawings in `folder.pdf`."
- "Redraw the ground floor plan from page 66 to DXF and compare it with the scan."
- "Build an IFC model from the plans and the section."
- "Render a view from the street at golden hour."
- "Put the plans and renders into an A3 PDF."

Give corrections precisely: "the garden wall is 38 cm, the scan on page 66 shows 30 cm". Claude asks for permission before running commands. At first, approve them one by one.

## Results

- **DXF**: AutoCAD, BricsCAD or LibreCAD (in AutoCAD, save as DWG).
- **IFC**: Autodesk Viewer (viewer.autodesk.com), free account; an uploaded file stays available for 30 days.
- **Renders and sheets** (PNG, PDF): in the project folder.

## Long sessions

When you switch topics, type `/handoff`, then `/clear`. The state of work is saved in `HANDOFF.md`, and the new conversation loads it automatically.

## Updating the plugin

In Claude Code: `/plugin marketplace update claude-architekt-windows`.

## What's inside

| Skill | What it does |
|---|---|
| `przygotuj-komputer` | installs Python, libraries and Blender (winget), checks the GPU |
| `nowy-projekt` | folders, `CLAUDE.md` with project rules, `HANDOFF.md`, git |
| `spis-arkuszy` | reviews scans, list of drawings |
| `skan-do-dxf` | redraws a plan / section / elevation to DXF, compares with the scan, DWG |
| `model-ifc` | IFC4 model from the plans, design variants |
| `wizualizacja` | IFC → OBJ → Blender (Cycles, OptiX/CUDA/HIP), preview and final render |
| `zestawienie-pdf` | A3 PDF from drawings and renders |

Plus the `/handoff` command and a hook that loads `HANDOFF.md` on start, after `/clear` and after automatic compaction.

Redrawing from scans is typically accurate to ±10–20 cm: a working draft and a basis for design, not a measured survey.

MIT licence.
