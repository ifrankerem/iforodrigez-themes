import json, os, html, glob

REPO = os.path.dirname(os.path.abspath(__file__))
OUT  = REPO
os.makedirs(OUT, exist_ok=True)

# (css class, text) — hand-tokenized C++ so the preview uses the theme's real inks
CODE = [
 [("pp","#include"),("s"," \"Server.hpp\"")],
 [("pp","#include"),("s"," <sys/poll.h>")],
 [],
 [("pp","#define"),("t"," MAX_CLIENTS "),("n","1024")],
 [],
 [("c","// accept a client, set it non-blocking, register with poll()")],
 [("k","int"),("t"," Server"),("o","::"),("f","acceptClient"),("o","("),("k","int"),("v"," listenFd"),("o",") {")],
 [("t","    sockaddr_in"),("v"," addr"),("o"," = {};")],
 [("t","    socklen_t"),("v","   len"),("o","  = "),("k","sizeof"),("o","("),("v","addr"),("o",");")],
 [],
 [("k","    int"),("v"," fd"),("o"," = "),("f","accept"),("o","("),("v","listenFd"),("o",", ("),("t","sockaddr"),("o"," *)&"),("v","addr"),("o",", &"),("v","len"),("o",");")],
 [("k","    if"),("o"," ("),("v","fd"),("o"," < "),("n","0"),("o",") {")],
 [("t","        std"),("o","::"),("v","cerr"),("o"," << "),("s","\"accept() failed\""),("o"," << "),("t","std"),("o","::"),("v","endl"),("o",";")],
 [("k","        return"),("o"," -"),("n","1"),("o",";")],
 [("o","    }")],
 [("f","    fcntl"),("o","("),("v","fd"),("o",", "),("m","F_SETFL"),("o",", "),("m","O_NONBLOCK"),("o",");")],
 [],
 [("k","    struct"),("t"," pollfd"),("v"," pfd"),("o",";")],
 [("v","    pfd"),("o","."),("p","fd"),("o","     = "),("v","fd"),("o",";")],
 [("v","    pfd"),("o","."),("p","events"),("o"," = "),("m","POLLIN"),("o"," | "),("m","POLLOUT"),("o",";")],
 [("v","    _pollFds"),("o","."),("f","push_back"),("o","("),("v","pfd"),("o",");")],
 [],
 [("v","    _clients"),("o","["),("v","fd"),("o","] = "),("k","new"),("t"," Client"),("o","("),("v","fd"),("o",", "),("n","4096"),("o",");")],
 [("k","    return"),("v"," fd"),("o",";")],
 [("o","}")],
]
ACTIVE_LINE = 11   # 1-based, gets the lineHighlight band

TREE = [("srv","folder","webserv"),("f","cpp","Server.cpp"),("f","hpp","Client.hpp"),
        ("f","cpp","Request.cpp"),("f","mod","Response.cpp"),("f","new","poll.cpp"),
        ("f","conf","default.conf"),("f","mk","Makefile")]

def build(theme_path, label):
    t = json.load(open(theme_path))
    c = t["colors"]; sem = t["semanticTokenColors"]
    comment = next(r["settings"]["foreground"] for r in t["tokenColors"]
                   if "comment" in r["scope"])
    op = next(r["settings"]["foreground"] for r in t["tokenColors"]
              if "keyword.operator" in r["scope"])
    ink = {"k": sem["keyword"], "t": sem["type"], "f": sem["function"],
           "s": sem["string"], "n": sem["number"], "m": sem["macro"],
           "v": sem["variable"], "p": sem["property"], "c": comment, "o": op,
           "pp": op}

    rows = []
    for i, line in enumerate(CODE, 1):
        spans = "".join('<span class="%s">%s</span>' % (cls, html.escape(txt))
                        for cls, txt in line) or "&nbsp;"
        cls = ' class="cur"' if i == ACTIVE_LINE else ""
        num = ' class="ln act"' if i == ACTIVE_LINE else ' class="ln"'
        rows.append('<div class="row%s"><span%s>%d</span><span class="code">%s</span></div>'
                    % (cls[7:-1] and " cur" or "", num, i, spans))

    tree = ""
    for kind, ico, name in TREE:
        col = {"folder": c["sideBar.foreground"],
               "new":  c["gitDecoration.untrackedResourceForeground"],
               "mod":  c["gitDecoration.modifiedResourceForeground"],
               }.get(ico if ico in ("new","mod") else kind, c["sideBar.foreground"])
        pad = 10 if kind == "srv" else 24
        weight = "600" if kind == "srv" else "400"
        tree += ('<div class="ti" style="padding-left:%dpx;color:%s;font-weight:%s">%s</div>'
                 % (pad, col, weight, html.escape(name)))

    css_ink = "\n".join(".%s{color:%s}" % (k, v) for k, v in ink.items())
    doc = f"""<!doctype html><meta charset="utf-8"><style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{background:{c['editor.background']};font-family:'Cascadia Mono NF','Hack','Liberation Mono',monospace;font-size:13px;-webkit-font-smoothing:antialiased}}
.win{{width:1280px;height:800px;display:flex;flex-direction:column;overflow:hidden}}
.title{{height:34px;background:{c['titleBar.activeBackground']};color:{c['titleBar.activeForeground']};
 border-bottom:1px solid {c['titleBar.border']};display:flex;align-items:center;justify-content:center;font-size:12px}}
.body{{flex:1;display:flex;min-height:0}}
.act{{width:48px;background:{c['activityBar.background']};border-right:1px solid {c['activityBar.border']};
 display:flex;flex-direction:column;align-items:center;padding-top:10px;gap:16px}}
.act i{{width:20px;height:20px;border:1.6px solid {c['activityBar.inactiveForeground']};border-radius:4px;display:block}}
.act i.on{{border-color:{c['activityBar.foreground']}}}
.badge{{background:{c['activityBarBadge.background']};color:{c['activityBarBadge.foreground']};
 font-size:9px;border-radius:8px;padding:1px 5px;font-weight:700}}
.side{{width:236px;background:{c['sideBar.background']};border-right:1px solid {c['sideBar.border']};
 display:flex;flex-direction:column}}
.sh{{padding:8px 10px;font-size:10.5px;letter-spacing:.9px;color:{c['sideBarSectionHeader.foreground']};
 background:{c['sideBarSectionHeader.background']};border-bottom:1px solid {c['sideBarSectionHeader.border']}}}
.ti{{padding:3.5px 10px;font-size:12.5px}}
.main{{flex:1;display:flex;flex-direction:column;min-width:0;background:{c['editor.background']}}}
.tabs{{height:35px;background:{c['editorGroupHeader.tabsBackground']};
 border-bottom:1px solid {c['editorGroupHeader.tabsBorder']};display:flex}}
.tab{{padding:0 16px;display:flex;align-items:center;font-size:12.5px;
 color:{c['tab.inactiveForeground']};border-right:1px solid {c['tab.border']}}}
.tab.on{{color:{c['tab.activeForeground']};background:{c['tab.activeBackground']};
 box-shadow:inset 0 2px 0 {c['tab.activeBorderTop']}}}
.crumb{{padding:5px 16px;font-size:11.5px;color:{c['breadcrumb.foreground']};background:{c['breadcrumb.background']}}}
.ed{{flex:1;padding:6px 0;overflow:hidden}}
.row{{display:flex;line-height:19.5px;height:19.5px}}
.row.cur{{background:{c['editor.lineHighlightBackground']}}}
.ln{{width:52px;text-align:right;padding-right:16px;color:{c['editorLineNumber.foreground']};flex:none}}
.ln.act{{color:{c['editorLineNumber.activeForeground']}}}
.code{{white-space:pre}}
{css_ink}
.term{{height:132px;background:{c['panel.background']};border-top:1px solid {c['panel.border']};display:flex;flex-direction:column}}
.pt{{display:flex;gap:18px;padding:7px 16px;font-size:11px}}
.pt b{{color:{c['panelTitle.activeForeground']};font-weight:500;padding-bottom:4px;
 border-bottom:1.5px solid {c['panelTitle.activeBorder']}}}
.pt s{{color:{c['panelTitle.inactiveForeground']};text-decoration:none}}
.tl{{padding:0 16px;line-height:18px;color:{c['terminal.foreground']};font-size:12.5px;white-space:pre}}
.g{{color:{c['terminal.ansiGreen']}}} .b{{color:{c['terminal.ansiBlue']}}}
.y{{color:{c['terminal.ansiYellow']}}} .r{{color:{c['terminal.ansiRed']}}}
.status{{height:24px;background:{c['statusBar.background']};color:{c['statusBar.foreground']};
 border-top:1px solid {c['statusBar.border']};display:flex;align-items:center;gap:16px;padding:0 12px;font-size:11.5px}}
.status .acc{{color:{c['statusBarItem.remoteForeground']};background:{c['statusBarItem.remoteBackground']};
 padding:1px 7px;border-radius:3px;font-weight:600}}
</style>
<div class="win">
 <div class="title">Server.cpp — webserv — {html.escape(label)}</div>
 <div class="body">
  <div class="act"><i class="on"></i><i></i><i></i><i></i><span class="badge">6</span></div>
  <div class="side"><div class="sh">EXPLORER</div>{tree}</div>
  <div class="main">
   <div class="tabs"><div class="tab on">Server.cpp</div><div class="tab">Client.hpp</div><div class="tab">default.conf</div></div>
   <div class="crumb">src &nbsp;&rsaquo;&nbsp; Server.cpp &nbsp;&rsaquo;&nbsp; Server::acceptClient</div>
   <div class="ed">{''.join(rows)}</div>
   <div class="term">
    <div class="pt"><b>TERMINAL</b><s>PROBLEMS</s><s>OUTPUT</s><s>DEBUG CONSOLE</s></div>
    <div class="tl"><span class="g">kero@fedora</span>:<span class="b">~/webserv</span>$ make -j8</div>
    <div class="tl"><span class="y">c++ -Wall -Wextra -Werror -std=c++98</span>  -c src/Server.cpp</div>
    <div class="tl"><span class="g">✓</span> webserv built  <span class="r">0 errors</span></div>
    <div class="tl"><span class="g">kero@fedora</span>:<span class="b">~/webserv</span>$ <span style="border-left:2px solid {c['terminalCursor.foreground']}">&nbsp;</span></div>
   </div>
  </div>
 </div>
 <div class="status"><span class="acc">main*</span><span>⊗ 0  ⚠ 1</span><span>Ln 11, Col 22</span><span>Spaces: 4</span><span>UTF-8</span><span>C++</span><span>{html.escape(label)}</span></div>
</div>"""
    p = os.path.join(OUT, label.replace(" ", "-") + ".html")
    open(p, "w").write(doc)
    return p

# drive the list off the extension manifest so new variants need no edit here
pkg = json.load(open(os.path.join(REPO, "package.json")))
for entry in pkg["contributes"]["themes"]:
    src = os.path.join(REPO, entry["path"].lstrip("./"))
    print(build(src, entry["label"]))
