#!/usr/bin/env python3
"""G29 native Yggdrasil atlas. Only provisional source locators, never reviewed claims."""
import argparse
import ast
import base64
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

REPO = "spoonman136668-ai/Yggdrasil"
SCHEMA = "yggdrasil.ice.source-locator.v1"
OUT = (".ice/code-atlas.json", ".ice/code-atlas.html", ".ice/code-atlas.ice")
EXT = (".py", ".ps1", ".yml", ".yaml", ".ice", ".md", ".json")


def require(ok, message):
    if not ok:
        raise RuntimeError("YGG_ATLAS_FAIL_CLOSED: " + message)


def git(root, *args):
    p = subprocess.run(["git", *args], cwd=root, capture_output=True)
    require(p.returncode == 0, "git failure: " + " ".join(args) +
            " " + p.stderr.decode("utf-8", errors="replace")[-160:])
    return p.stdout


def files_at(root, rev):
    return sorted(p.decode("utf-8") for p in
                  git(root, "ls-tree", "-rz", "--name-only", rev).split(b"\0")
                  if p and p.decode("utf-8") not in OUT and
                  p.decode("utf-8").endswith(EXT))


def snapshot(root, source):
    require(re.fullmatch(r"[0-9a-f]{40}", source) is not None, "source SHA invalid")
    require(git(root, "cat-file", "-t", source).strip() == b"commit", "source commit missing")
    head = git(root, "rev-parse", "HEAD").decode("ascii").strip()
    require(subprocess.run(["git", "merge-base", "--is-ancestor", source, head],
                           cwd=root, capture_output=True).returncode == 0,
            "source commit not ancestor")
    paths = files_at(root, source)
    require(paths == files_at(root, head), "indexed file set changed")
    files, symbols, imports = [], [], []
    for path in paths:
        raw = git(root, "show", source + ":" + path)
        require(raw == git(root, "show", head + ":" + path),
                "source blob changed: " + path)
        require((root / path).read_bytes().replace(b"\r\n", b"\n") ==
                raw.replace(b"\r\n", b"\n"), "working source mismatch: " + path)
        ext = Path(path).suffix
        kind = ("python" if ext == ".py" else "powershell" if ext == ".ps1"
                else "workflow" if path.startswith(".github/workflows/")
                else "research-ice" if ext == ".ice" else "document-or-data")
        link = "https://github.com/" + REPO + "/blob/" + source + "/" + path
        file = {"path": path, "sha256": hashlib.sha256(raw).hexdigest(),
                "kind": kind, "bytes": len(raw), "source_url": link}
        lines = raw.decode("utf-8-sig").splitlines()
        if kind == "python":
            tree = ast.parse("\n".join(lines), filename=path)
            def visit(nodes, prefix=""):
                for n in nodes:
                    if isinstance(n, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
                        name = (prefix + "." if prefix else "") + n.name
                        typ = "class" if isinstance(n, ast.ClassDef) else "function"
                        symbols.append({
                            "id": "yggdrasil:" + path + "::" + typ + "::" + name + "@" + str(n.lineno),
                            "file": path, "kind": typ, "name": name,
                            "start_line": n.lineno, "end_line": n.end_lineno,
                            "label": typ + " " + name, "evidence_basis": "syntax-only",
                            "source_url": link + "#L" + str(n.lineno) + "-L" + str(n.end_lineno)})
                        if isinstance(n, ast.ClassDef):
                            visit(n.body, name)
                    if isinstance(n, (ast.Import, ast.ImportFrom)):
                        target = n.module if isinstance(n, ast.ImportFrom) else ",".join(x.name for x in n.names)
                        imports.append({"file": path, "line": n.lineno,
                                        "literal": target or "",
                                        "evidence_basis": "lexical-not-type-resolved"})
            visit(tree.body)
        elif kind == "powershell":
            for line, value in enumerate(lines, 1):
                match = re.match(r"^\s*function\s+([a-zA-Z0-9_-]+)\b", value, re.I)
                if match:
                    name = match.group(1)
                    symbols.append({"id": "yggdrasil:" + path + "::function::" + name + "@" + str(line),
                                    "file": path, "kind": "powershell-function", "name": name,
                                    "start_line": line, "end_line": line,
                                    "label": "PowerShell " + name, "evidence_basis": "lexical-only",
                                    "source_url": link + "#L" + str(line)})
        elif kind == "workflow":
            for line, value in enumerate(lines[:30], 1):
                match = re.match(r"^name:\s*(.+?)\s*$", value)
                if match:
                    file["workflow_name"] = match.group(1)
                    symbols.append({"id": "yggdrasil:" + path + "::workflow::" + str(line),
                                    "file": path, "kind": "workflow", "name": match.group(1),
                                    "start_line": line, "end_line": line,
                                    "label": match.group(1), "evidence_basis": "lexical-only",
                                    "source_url": link + "#L" + str(line)})
                    break
        elif kind == "research-ice":
            file["research_header"] = {m.group(1).lower(): m.group(2)[:200]
                                       for text in lines[:30]
                                       if (m := re.match(r"^(TITLE|STATUS|TRACK|DATE):\s*(.+)$", text))}
        files.append(file)
    symbols.sort(key=lambda s: (s["file"], s["start_line"], s["id"]))
    imports.sort(key=lambda x: (x["file"], x["line"], x["literal"]))
    return {"schema": SCHEMA, "repository": REPO, "source_commit": source,
            "authority": "advisory-locators-only", "source_reviewed_labels": 0,
            "wingless_evidence_imported": False,
            "counts": {"files": len(files), "symbols": len(symbols), "imports": len(imports)},
            "files": files, "symbols": symbols, "imports": imports,
            "warnings": ["Do not interpret lexical edges as proven call paths",
                         "Existing research .ice records preserved unchanged"]}


def render(atlas):
    js = json.dumps(atlas, sort_keys=True, indent=2, ensure_ascii=True) + "\n"
    packed = json.dumps(atlas, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    packed = packed.replace("<", "\\u003c").replace(">", "\\u003e")
    html = """<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Yggdrasil Source Atlas</title>
<style>body{font:15px system-ui;background:#151f2b;color:#f1f3f7;padding:16px}
main{max-width:1300px;margin:auto;display:grid;grid-template-columns:40% 1fr;gap:16px}
section{padding:16px;background:#253346;border:1px solid #566678;border-radius:9px}
input,button{font:inherit;padding:8px}input{width:90%}button{display:block;
width:100%;text-align:left;background:#34475f;color:#fff;border:1px solid #61748a}
a{color:#9fe2ff}.warn{color:#ffd595}@media(max-width:700px){main{display:block}}
</style></head><body><main><section><h1>Yggdrasil source atlas</h1>
<p class="warn">Provisional locators only; no human-reviewed behavioral labels.</p>
<p id="counts"></p><input id="query" aria-label="Search code" placeholder="Search files or symbols">
<div id="matches"></div></section><section><h2>Source identity</h2><div id="details"></div></section></main>
<script id="atlas" type="application/json">""" + packed + """</script>
<script>(()=>{"use strict";const a=JSON.parse(document.getElementById("atlas").textContent);
const q=document.getElementById("query"),list=document.getElementById("matches"),
detail=document.getElementById("details");document.getElementById("counts").textContent=
a.counts.files+" files · "+a.counts.symbols+" locators · "+a.counts.imports+" lexical imports";
const items=[...a.files.map(x=>({name:x.path,obj:x})),...a.symbols.map(x=>({name:x.name+" | "+x.file,obj:x}))];
function text(tag,value,parent){const node=document.createElement(tag);node.textContent=value;parent.append(node);return node}
function show(x){detail.replaceChildren();text("h3",x.name,detail);text("p",x.obj.evidence_basis||"pinned Git file SHA",detail);
const anchor=text("a","Open pinned source",detail);anchor.href=x.obj.source_url;anchor.target="_blank";anchor.rel="noopener noreferrer";
text("p",a.source_commit,detail);if(x.obj.research_header)text("pre",JSON.stringify(x.obj.research_header,null,2),detail)}
function filter(){list.replaceChildren();let matches=items.filter(x=>x.name.toLowerCase().includes(q.value.toLowerCase())).slice(0,200);
text("p",matches.length+" shown",list);for(const x of matches){const b=text("button",x.name,list);b.onclick=()=>show(x)}}
q.oninput=filter;filter();if(items.length)show(items[0]);})();</script></body></html>"""
    ice = ("TITLE: Yggdrasil Source Atlas\nSTATUS: ADVISORY NAVIGATION ONLY\n"
           "SOURCE_REPOSITORY: " + REPO + "\nSOURCE_COMMIT: " + atlas["source_commit"] +
           "\nSCHEMA: " + SCHEMA + "\nFILES: " + str(atlas["counts"]["files"]) +
           "\nSYMBOLS: " + str(atlas["counts"]["symbols"]) +
           "\nLEXICAL_IMPORTS: " + str(atlas["counts"]["imports"]) +
           "\nSOURCE_REVIEWED_LABELS: 0\nWINGLESS_PROVENANCE_IMPORTED: FALSE\n"
           "Original Yggdrasil research .ice documents are not modified.\n")
    return dict(zip(OUT, (js, html, ice)))


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--root", type=Path, default=Path("."))
    p.add_argument("--source-commit")
    p.add_argument("--write", action="store_true")
    p.add_argument("--check", action="store_true")
    p.add_argument("--check-if-present", action="store_true")
    p.add_argument("--emit-base64", action="store_true")
    x = p.parse_args()
    root = x.root.resolve()
    source = x.source_commit or (json.loads((root / OUT[0]).read_text("utf-8"))["source_commit"]
                                 if (root / OUT[0]).exists() else
                                 git(root, "rev-parse", "HEAD").decode("ascii").strip())
    artifacts = render(snapshot(root, source))
    found = [path for path in OUT if (root / path).exists()]
    if x.check or (x.check_if_present and found):
        require(len(found) == len(OUT), "partial atlas")
        for path, want in artifacts.items():
            committed = git(root, "show", "HEAD:" + path)
            require(committed == want.encode("utf-8"), "stale committed blob: " + path)
            require((root / path).read_bytes().replace(b"\r\n", b"\n") ==
                    committed.replace(b"\r\n", b"\n"), "checkout drift: " + path)
        print("YGG_G29_PINNED_ATLAS_PASS", source)
    elif x.check_if_present:
        print("YGG_G29_SNAPSHOT_PENDING")
    if x.write:
        for path, want in artifacts.items():
            dest = root / path
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(want.encode("utf-8"))
    if x.emit_base64:
        payload = json.dumps(artifacts, sort_keys=True, ensure_ascii=True).encode("ascii")
        print("YGG_ATLAS_BUNDLE_B64:" + base64.b64encode(payload).decode("ascii"))
    print("YGG_G29_SOURCE_PASS", source)


if __name__ == "__main__":
    try:
        main()
    except (RuntimeError, OSError, SyntaxError, UnicodeError, ValueError) as err:
        print(str(err), file=sys.stderr)
        sys.exit(1)
