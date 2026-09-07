# iforodrigez

A dark theme for **VS Code** and **Zed** where the UI chrome gets out of the way: no gradients, no tinted panels, one accent color.

Twelve variants on two axes. **Ink** is how loud the syntax colors are — `low`, `medium`, `high`. **Background** is how dark the surfaces sit — `0` is pitch black, `3` is the gray VS Code ships with. Pick a cell:

| | low | medium | high |
|---|---|---|---|
| **0** &nbsp;`#000000` | [<img src="images/low0.png" width="240">](images/low0.png) | [<img src="images/medium0.png" width="240">](images/medium0.png) | [<img src="images/high0.png" width="240">](images/high0.png) |
| **1** &nbsp;`#0A0A0A` | [<img src="images/low1.png" width="240">](images/low1.png) | [<img src="images/medium1.png" width="240">](images/medium1.png) | [<img src="images/high1.png" width="240">](images/high1.png) |
| **2** &nbsp;`#151515` | [<img src="images/low2.png" width="240">](images/low2.png) | [<img src="images/medium2.png" width="240">](images/medium2.png) | [<img src="images/high2.png" width="240">](images/high2.png) |
| **3** &nbsp;`#1F1F1F` | [<img src="images/low3.png" width="240">](images/low3.png) | [<img src="images/medium3.png" width="240">](images/medium3.png) | [<img src="images/high3.png" width="240">](images/high3.png) |

Click any cell for the full-size shot. The two axes are independent — moving along one never touches the other. The screenshots are rendered from the VS Code theme files; the Zed themes carry the same colors.

## Layout

```
vscode/            VS Code extension — package.json + themes/
zed/               Zed extension — extension.toml + themes/iforodrigez.json
images/            previews, shared by both
generate-previews.py   rebuilds images/ from the VS Code themes
build-zed-themes.py    rebuilds zed/themes/iforodrigez.json from the VS Code themes
```

The VS Code theme files are the single source of truth. `build-zed-themes.py` translates them into Zed's theme schema, so a color only ever has to be changed in one place.

## Ink

| Token | low | medium | high |
|---|---|---|---|
| foreground | `#D6D6C1` | `#E5E5D4` | `#F8F8F2` |
| keyword | `#C57C27` | `#E4881C` | `#FD971F` |
| string | `#C4BA5B` | `#D3C864` | `#E6DB74` |
| function | `#84AB37` | `#93C430` | `#A6E22E` |
| type, class | `#4FB8CC` | `#58C6DB` | `#66D9EF` |
| number | `#8D5EE0` | `#9A6BEF` | `#AE81FF` |
| macro | `#C42A62` | `#E02267` | `#F92672` |
| comment | `#5E5C51` | `#676457` | `#75715E` |

`high` is full saturation. `medium` drops saturation 20% and lightness 10%; `low` drops them 32% and 17%. The accent — cursor, active tab border, badges, buttons, focus ring — is the keyword color of the level you picked.

## Background

| Surface | 0 | 1 | 2 | 3 |
|---|---|---|---|---|
| editor, sidebar, tabs, panel, terminal | `#000000` | `#0A0A0A` | `#151515` | `#1F1F1F` |
| popups, dropdowns, suggest widget | `#0B0B0B` | `#131313` | `#1C1C1C` | `#252525` |
| borders | `#141414` | `#1B1B1B` | `#222222` | `#292929` |

Every neutral surface moves together — editor, sidebar, popups, borders, hover and selection bands — so layer separation survives instead of flattening into one gray. Popups always sit one step above their surroundings, which is what keeps a dropdown reading as a floating thing rather than a hole. Lighter greys move less than dark ones, so line numbers and dimmed text stay readable at every level.

## Install — VS Code

Grab the `.vsix` from [Releases](https://github.com/ifrankerem/iforodrigez-themes/releases) and install it:

```sh
code --install-extension iforodrigez-theme-1.3.0.vsix
```

If you use VS Code profiles, install into each profile explicitly. A theme registered globally will **not** appear in a profile's theme picker:

```sh
code --install-extension iforodrigez-theme-1.3.0.vsix --profile <profile-name>
```

Then `Ctrl+K Ctrl+T` and pick a variant.

To build the `.vsix` yourself:

```sh
cd vscode && npx @vscode/vsce package
```

## Install — Zed

Either drop the theme family in as a user theme:

```sh
mkdir -p ~/.config/zed/themes
cp zed/themes/iforodrigez.json ~/.config/zed/themes/
```

…or install the whole `zed/` directory as a dev extension: `zed: install dev extension` from the command palette, then pick the `zed/` folder.

Either way, `cmd-k cmd-t` (`ctrl-k ctrl-t` on Linux) and pick a variant, or set it in `settings.json`:

```json
{
  "theme": "iforodrigez high 0"
}
```

## Editing

Colors live in `vscode/themes/iforodrigez-<ink><level>-color-theme.json`. Save and run **Developer: Reload Window** to see changes in VS Code.

After a color change, regenerate the Zed themes and the screenshots:

```sh
python3 build-zed-themes.py
python3 generate-previews.py
firefox --headless --screenshot images/low0.png --window-size=1280,800 file://$PWD/iforodrigez-low-0.html
```

Both scripts read the variant list out of `vscode/package.json`, so adding a variant needs no edit in either.
