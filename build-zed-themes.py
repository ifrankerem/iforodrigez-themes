"""Build the Zed theme family from the VS Code theme files.

The VS Code JSONs are the source of truth: every color here is read out of
themes/*.json, so a color change only has to be made once. Run after editing a
VS Code theme:

    python3 build-zed-themes.py
"""

import json, os

REPO   = os.path.dirname(os.path.abspath(__file__))
VSCODE = os.path.join(REPO, "vscode")
OUT    = os.path.join(REPO, "zed", "themes", "iforodrigez.json")

SCHEMA = "https://zed.dev/schema/themes/v0.2.0.json"


def rgba(color, alpha=None):
    """Normalize a VS Code color to Zed's 8-digit #RRGGBBAA, optionally
    replacing the alpha channel (0.0-1.0)."""
    c = color.lstrip("#")
    if len(c) == 6:
        c += "ff"
    if alpha is not None:
        c = c[:6] + "%02x" % round(alpha * 255)
    return "#" + c.lower()


def blend(fg, bg, amount):
    """Mix fg toward bg. amount=0 keeps fg, amount=1 returns bg."""
    f = [int(fg.lstrip("#")[i:i + 2], 16) for i in (0, 2, 4)]
    b = [int(bg.lstrip("#")[i:i + 2], 16) for i in (0, 2, 4)]
    return "#" + "".join("%02x" % round(x + (y - x) * amount) for x, y in zip(f, b)) + "ff"


def scope_color(theme, scope):
    """Foreground of the first tokenColors rule containing a scope."""
    for rule in theme["tokenColors"]:
        if scope in rule["scope"]:
            return rule["settings"]["foreground"]
    raise KeyError(scope)


def style(theme):
    c   = theme["colors"]
    sem = theme["semanticTokenColors"]

    bg      = c["editor.background"]
    fg      = c["editor.foreground"]
    accent  = c["editorCursor.foreground"]          # the keyword color of this ink level
    border  = c["sideBar.border"]
    surface = c["editorWidget.background"]          # popups sit one step above
    comment = scope_color(theme, "comment")
    op      = scope_color(theme, "keyword.operator")

    kw, ty  = sem["keyword"], sem["type"]
    fn, st  = sem["function"], sem["string"]
    num, mc = sem["number"], sem["macro"]

    green   = c["gitDecoration.untrackedResourceForeground"]
    blue    = c["gitDecoration.modifiedResourceForeground"]
    red     = c["editorError.foreground"]

    def hi(color, **kw_):
        h = {"color": rgba(color), "font_style": None, "font_weight": None}
        h.update(kw_)
        return h

    def state(color):
        """A status color plus the background and border Zed derives from it."""
        return rgba(color), rgba(color, 0.10), rgba(color, 0.40)

    st_error    = state(red)
    st_warning  = state(c["editorWarning.foreground"])
    st_info     = state(c["editorInfo.foreground"])
    st_success  = state(green)
    st_created  = state(green)
    st_modified = state(blue)
    st_deleted  = state(red)
    st_conflict = state(c["gitDecoration.conflictingResourceForeground"])
    st_renamed  = state(blue)
    st_ignored  = state(c["gitDecoration.ignoredResourceForeground"])
    st_hidden   = state(c["tab.inactiveForeground"])
    st_predict  = state(comment)
    st_unreach  = state(c["editorLineNumber.foreground"])

    ansi = lambda name: c["terminal.ansi" + name]

    s = {
        "background": rgba(bg),
        "background.appearance": "opaque",
        "border": rgba(border),
        "border.variant": rgba(border),
        "border.focused": rgba(accent, 0.40),
        "border.selected": rgba(accent),
        "border.transparent": "#00000000",
        "border.disabled": rgba(border),

        "elevated_surface.background": rgba(surface),
        "surface.background": rgba(c["sideBar.background"]),
        "panel.background": rgba(c["panel.background"]),
        "panel.focused_border": rgba(accent),
        "panel.indent_guide": rgba(c["tree.indentGuidesStroke"]),
        "panel.indent_guide_active": rgba(accent, 0.40),
        "panel.indent_guide_hover": rgba(accent, 0.40),
        "pane.focused_border": rgba(accent, 0.40),
        "pane_group.border": rgba(border),
        "status_bar.background": rgba(c["statusBar.background"]),
        "title_bar.background": rgba(c["titleBar.activeBackground"]),
        "title_bar.inactive_background": rgba(c["titleBar.inactiveBackground"]),
        "toolbar.background": rgba(bg),
        "tab_bar.background": rgba(c["editorGroupHeader.tabsBackground"]),
        "tab.active_background": rgba(c["tab.activeBackground"]),
        "tab.inactive_background": rgba(c["tab.inactiveBackground"]),

        "element.background": rgba(bg),
        "element.hover": rgba(c["list.hoverBackground"]),
        "element.active": rgba(c["list.activeSelectionBackground"]),
        "element.selected": rgba(c["list.activeSelectionBackground"]),
        "element.disabled": "#00000000",
        "ghost_element.background": "#00000000",
        "ghost_element.hover": rgba(c["list.hoverBackground"]),
        "ghost_element.active": rgba(c["list.activeSelectionBackground"]),
        "ghost_element.selected": rgba(c["list.activeSelectionBackground"]),
        "ghost_element.disabled": "#00000000",
        "drop_target.background": rgba(accent, 0.20),

        "text": rgba(fg),
        "text.muted": rgba(c["sideBarTitle.foreground"]),
        "text.placeholder": rgba(c["input.placeholderForeground"]),
        "text.disabled": rgba(c["tab.inactiveForeground"]),
        "text.accent": rgba(accent),
        "link_text.hover": rgba(ty),

        "icon": rgba(fg),
        "icon.muted": rgba(c["sideBarTitle.foreground"]),
        "icon.disabled": rgba(c["tab.inactiveForeground"]),
        "icon.placeholder": rgba(c["input.placeholderForeground"]),
        "icon.accent": rgba(accent),

        "editor.background": rgba(bg),
        "editor.foreground": rgba(fg),
        "editor.gutter.background": rgba(c["editorGutter.background"]),
        "editor.subheader.background": rgba(surface),
        "editor.active_line.background": rgba(c["editor.lineHighlightBackground"]),
        "editor.highlighted_line.background": rgba(c["editor.lineHighlightBackground"]),
        "editor.line_number": rgba(c["editorLineNumber.foreground"]),
        "editor.active_line_number": rgba(c["editorLineNumber.activeForeground"]),
        "editor.invisible": rgba(c["editorWhitespace.foreground"]),
        "editor.wrap_guide": rgba(c["editorRuler.foreground"]),
        "editor.active_wrap_guide": rgba(c["editorIndentGuide.activeBackground1"]),
        "editor.indent_guide": rgba(c["editorIndentGuide.background1"]),
        "editor.indent_guide_active": rgba(c["editorIndentGuide.activeBackground1"]),
        "editor.document_highlight.read_background": rgba(c["editor.wordHighlightBackground"]),
        "editor.document_highlight.write_background": rgba(c["editor.wordHighlightStrongBackground"]),
        "editor.document_highlight.bracket_background": rgba(accent, 0.25),
        "search.match_background": rgba(c["editor.findMatchHighlightBackground"]),

        "scrollbar.thumb.background": rgba(c["scrollbarSlider.background"]),
        "scrollbar.thumb.hover_background": rgba(c["scrollbarSlider.hoverBackground"]),
        "scrollbar.thumb.border": "#00000000",
        "scrollbar.track.background": rgba(bg),
        "scrollbar.track.border": rgba(border),

        "terminal.background": rgba(c["terminal.background"]),
        "terminal.foreground": rgba(c["terminal.foreground"]),
        "terminal.bright_foreground": rgba(c["terminal.ansiBrightWhite"]),
        "terminal.dim_foreground": rgba(blend(c["terminal.foreground"], bg, 0.45)),
        "terminal.ansi.background": rgba(c["terminal.background"]),
    }

    for name in ("Black", "Red", "Green", "Yellow", "Blue", "Magenta", "Cyan", "White"):
        key = name.lower()
        s["terminal.ansi." + key] = rgba(ansi(name))
        s["terminal.ansi.bright_" + key] = rgba(ansi("Bright" + name))
        s["terminal.ansi.dim_" + key] = rgba(blend(ansi(name), bg, 0.45))

    for name, (color, back, brdr) in (
        ("error", st_error), ("warning", st_warning), ("info", st_info),
        ("success", st_success), ("created", st_created), ("modified", st_modified),
        ("deleted", st_deleted), ("conflict", st_conflict), ("renamed", st_renamed),
        ("ignored", st_ignored), ("hidden", st_hidden), ("predictive", st_predict),
        ("unreachable", st_unreach),
    ):
        s[name] = color
        s[name + ".background"] = back
        s[name + ".border"] = brdr

    s["hint"] = rgba(comment)
    s["hint.background"] = rgba(comment, 0.10)
    s["hint.border"] = rgba(comment, 0.40)

    s["players"] = [
        {"cursor": rgba(col), "background": rgba(col), "selection": rgba(col, 0.24)}
        for col in (accent, mc, fn, ty, num, st, blue, green)
    ]
    s["accents"] = [rgba(col) for col in (accent, mc, fn, ty, num, st)]

    s["syntax"] = {
        "attribute":                hi(ty),
        "boolean":                  hi(num),
        "comment":                  hi(comment, font_style="italic"),
        "comment.doc":              hi(comment, font_style="italic"),
        "constant":                 hi(num),
        "constructor":              hi(fn),
        "diff.plus":                hi(green),
        "diff.minus":               hi(red),
        "embedded":                 hi(fg),
        "emphasis":                 hi(ty, font_style="italic"),
        "emphasis.strong":          hi(ty, font_weight=700),
        "enum":                     hi(ty),
        "function":                 hi(fn),
        "function.method":          hi(fn),
        "function.definition":      hi(fn),
        "hint":                     hi(comment, font_style="italic"),
        "keyword":                  hi(kw),
        "label":                    hi(fg),
        "link_text":                hi(st, font_style="italic"),
        "link_uri":                 hi(ty),
        "namespace":                hi(ty),
        "number":                   hi(num),
        "operator":                 hi(op),
        "predictive":               hi(comment, font_style="italic"),
        "preproc":                  hi(op),
        "primary":                  hi(fg),
        "property":                 hi(sem["property"]),
        "punctuation":              hi(op),
        "punctuation.bracket":      hi(op),
        "punctuation.delimiter":    hi(op),
        "punctuation.list_marker":  hi(mc),
        "punctuation.markup":       hi(mc),
        "punctuation.special":      hi(mc),
        "selector":                 hi(fn),
        "selector.pseudo":          hi(ty),
        "string":                   hi(st),
        "string.escape":            hi(num),
        "string.regex":             hi(st),
        "string.special":           hi(num),
        "string.special.symbol":    hi(num),
        "tag":                      hi(mc),
        "text.literal":             hi(st),
        "title":                    hi(fn, font_weight=700),
        "type":                     hi(ty),
        "variable":                 hi(fg),
        "variable.parameter":       hi(sem["parameter"]),
        "variable.special":         hi(mc),
        "variant":                  hi(ty),
    }
    return s


# drive the variant list off the VS Code manifest, same as generate-previews.py
pkg = json.load(open(os.path.join(VSCODE, "package.json")))
themes = []
for entry in pkg["contributes"]["themes"]:
    src = os.path.join(VSCODE, entry["path"].lstrip("./"))
    themes.append({
        "name": entry["label"],
        "appearance": "dark",
        "style": style(json.load(open(src))),
    })

family = {
    "$schema": SCHEMA,
    "name": pkg["displayName"],
    "author": "ifrankerem",
    "themes": themes,
}

os.makedirs(os.path.dirname(OUT), exist_ok=True)
with open(OUT, "w") as f:
    json.dump(family, f, indent=2)
    f.write("\n")
print("%s — %d themes" % (OUT, len(themes)))
