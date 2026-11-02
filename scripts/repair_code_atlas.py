#!/usr/bin/env python3
"""Exact-source atlas companions. Never update a proposal or accepted ref."""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import urllib.error
import urllib.request

REPOSITORY = "spoonman136668-ai/Yggdrasil"
OWNER = "spoonman136668-ai"
OUTPUTS = (".ice/code-atlas.json", ".ice/code-atlas.html", ".ice/code-atlas.ice")
GUARDS = ("scripts/build_code_atlas.py", "tests/test_code_atlas.py")
SCHEMA = "yggdrasil.atlas-companion.v1"
GIT = shutil.which("git")
sys.dont_write_bytecode = True


def require(ok, message):
    if not ok:
        raise RuntimeError("YGG_ATLAS_REPAIR_REFUSED: " + message)


def git(root, *args, data=None, env=None):
    result = subprocess.run([GIT, *args], cwd=root, input=data, capture_output=True,
                            env=env, check=False)
    require(result.returncode == 0, "git " + args[0] + ": " +
            result.stderr.decode("utf-8", "replace")[-300:])
    return result.stdout


def text(root, *args):
    return git(root, *args).decode("ascii").strip()


def sha(value):
    require(isinstance(value, str) and re.fullmatch(r"[0-9a-f]{40}", value), "invalid SHA")
    return value


def builder(control):
    spec = importlib.util.spec_from_file_location("trusted_atlas", control / GUARDS[0])
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    # Pin the executable even when the candidate contains a file named git.exe.
    module.git = git
    return module


def validate_source(root, control, source):
    sha(source)
    require(text(root, "rev-parse", "HEAD") == source, "checkout is not exact source")
    require(not git(root, "status", "--porcelain", "--untracked-files=all"), "dirty source")
    control_sha = text(control, "rev-parse", "HEAD")
    require(not git(control, "status", "--porcelain", "--untracked-files=all"), "dirty control")
    for path in GUARDS:
        require(git(root, "show", source + ":" + path) ==
                git(control, "show", control_sha + ":" + path), "changed guard: " + path)
    for entry in git(root, "ls-tree", "-rz", source).split(b"\0"):
        if not entry:
            continue
        mode, kind, rest = entry.split(b" ", 2)
        _, path = rest.split(b"\t", 1)
        name = path.decode("utf-8")
        require(mode in (b"100644", b"100755") and kind == b"blob", "nonregular Git entry")
        require(not name.startswith("/") and ".." not in name.split("/") and
                "\\" not in name and ":" not in name, "unsafe path")
    return control_sha


def prepare(root, control, source, checkout=True):
    """Use only the control builder; candidate Python is parsed, never imported."""
    control_sha = validate_source(root, control, source)
    atlas = builder(control)
    # Already valid metadata is a no-op, including an artifact-only companion.
    current = False
    try:
        pinned = json.loads(git(root, "show", source + ":" + OUTPUTS[0]))["source_commit"]
        expected = atlas.render(atlas.snapshot(root, pinned))
        current = all(git(root, "show", source + ":" + p) == value.encode("utf-8")
                      for p, value in expected.items())
    except (RuntimeError, KeyError, ValueError, OSError):
        pass
    changed = []
    companion = source
    if not current:
        rendered = atlas.render(atlas.snapshot(root, source))
        # An isolated index bypasses candidate attributes, filters and hooks.
        with tempfile.TemporaryDirectory(prefix="ygg-atlas-index-") as temp:
            env = dict(os.environ, GIT_INDEX_FILE=str(Path(temp) / "index"))
            git(root, "read-tree", source, env=env)
            for path in OUTPUTS:
                raw = rendered[path].encode("utf-8")
                blob = git(root, "hash-object", "--no-filters", "-w", "--stdin", data=raw).strip()
                git(root, "update-index", "--add", "--cacheinfo", "100644",
                    blob.decode("ascii"), path, env=env)
            tree = text_with_env(root, env, "write-tree")
        epoch = text(root, "show", "-s", "--format=%ct", source)
        require(epoch.isdecimal(), "invalid source timestamp")
        identity = "Yggdrasil Atlas <atlas@users.noreply.github.com> " + epoch + " +0000"
        commit = ("tree " + tree + "\nparent " + source + "\nauthor " + identity +
                  "\ncommitter " + identity + "\n\nAtlas companion for " + source + "\n").encode("ascii")
        companion = git(root, "hash-object", "-t", "commit", "-w", "--stdin", data=commit).decode().strip()
        changed = git(root, "diff-tree", "--no-commit-id", "--name-only", "-r", "-z",
                      source, companion).decode("utf-8").strip("\0").split("\0")
        require(bool(changed) and set(changed) <= set(OUTPUTS), "non-atlas delta")
        if checkout:
            git(root, "checkout", "--detach", companion)
    pinned = json.loads(git(root, "show", companion + ":" + OUTPUTS[0]))["source_commit"]
    expected = atlas.render(atlas.snapshot(root, pinned))
    require(all(git(root, "show", companion + ":" + path) == value.encode("utf-8")
                for path, value in expected.items()), "companion is not canonical")
    return {"schema": SCHEMA, "source": source, "control": control_sha,
            "source_tree": text(root, "rev-parse", source + "^{tree}"),
            "companion": companion, "tree": text(root, "rev-parse", companion + "^{tree}"),
            "changed": sorted(changed), "atlas_source": pinned,
            "guards": {p: text(control, "rev-parse", control_sha + ":" + p) for p in GUARDS},
            "artifacts": {p: hashlib.sha256(git(root, "show", companion + ":" + p)).hexdigest()
                          for p in OUTPUTS}}


def text_with_env(root, env, *args):
    return git(root, *args, env=env).decode("ascii").strip()


def verify(root, receipt):
    require(receipt["schema"] == SCHEMA, "receipt schema")
    require(text(root, "rev-parse", "HEAD") == receipt["companion"], "qualification HEAD changed")
    require(text(root, "rev-parse", "HEAD^{tree}") == receipt["tree"], "qualification tree changed")
    require(not git(root, "status", "--porcelain", "--untracked-files=all"), "qualification drift")
    require(set(receipt["artifacts"]) == set(OUTPUTS), "partial artifact receipt")
    for path, digest in receipt["artifacts"].items():
        require(path in OUTPUTS and hashlib.sha256((root / path).read_bytes().replace(
            b"\r\n", b"\n")).hexdigest() == digest, "artifact drift")


def api(path, method="GET", body=None):
    require(path.startswith("/repos/" + REPOSITORY + "/"), "API scope")
    request = urllib.request.Request("https://api.github.com" + path, method=method,
        data=None if body is None else json.dumps(body).encode("utf-8"),
        headers={"Authorization": "Bearer " + os.environ["GH_TOKEN"],
                 "Accept": "application/vnd.github+json", "Content-Type": "application/json",
                 "X-GitHub-Api-Version": "2022-11-28"})
    with urllib.request.urlopen(request, timeout=45) as response:
        raw = response.read(4_000_001)
    require(len(raw) <= 4_000_000, "oversized API response")
    return json.loads(raw) if raw else None


def lease(pr_number, source):
    pr = api("/repos/" + REPOSITORY + "/pulls/" + str(pr_number))
    require(pr["state"] == "open" and pr["user"]["login"] == OWNER and
            pr["author_association"] == "OWNER" and
            pr["head"]["repo"]["full_name"] == REPOSITORY and
            pr["base"]["repo"]["full_name"] == REPOSITORY and
            pr["head"]["sha"] == sha(source), "PR lease changed or not owner source")
    require(not pr["head"]["ref"].startswith("atlas/automatic/"), "companion recursion")
    return pr


def resolve(event):
    require(os.environ["GITHUB_REPOSITORY"] == REPOSITORY, "repository")
    run = event.get("workflow_run")
    if run:
        require(run["event"] == "pull_request" and run["status"] == "completed" and
                run["path"] == ".github/workflows/yggdrasil-g29-atlas.yml" and
                run["head_repository"]["full_name"] == REPOSITORY, "not a G29 PR run")
        source = sha(run["head_sha"])
        prs = run["pull_requests"]
        if not prs:
            prs = api("/repos/" + REPOSITORY + "/commits/" + source + "/pulls")
        numbers = [p["number"] for p in prs if p["head"]["sha"] == source]
        require(len(numbers) == 1, "ambiguous PR run")
        number = numbers[0]
    else:
        require(os.environ["GITHUB_EVENT_NAME"] in ("pull_request", "pull_request_target"), "event")
        number = event["pull_request"]["number"]
        source = sha(event["pull_request"]["head"]["sha"])
    lease(number, source)
    return {"source": source, "pr": str(number)}


def publish(root, control, source, number, receipts):
    # Recompute from Git objects using trusted control code, never execute a
    # candidate test, builder, action or artifact with this write token.
    lease(number, source)
    want = prepare(root, control, source, checkout=False)
    found = sorted(receipts.glob("*/receipt.json"))
    require(len(found) == 2 and {p.parent.name for p in found} ==
            {"atlas-qualification-linux", "atlas-qualification-windows"}, "both OS receipts required")
    for file in found:
        require(file.stat().st_size < 16384 and json.loads(file.read_text("utf-8")) == want,
                "qualification does not match independent reconstruction")
    run_id = int(os.environ["GITHUB_RUN_ID"])
    jobs = api("/repos/" + REPOSITORY + "/actions/runs/" + str(run_id) + "/jobs?per_page=100")["jobs"]
    for platform in ("linux", "windows"):
        matches = [j for j in jobs if j["name"] == "atlas-qualification (" + platform + ")"]
        require(len(matches) == 1 and matches[0]["status"] == "completed" and
                matches[0]["conclusion"] == "success", "OS qualification not successful")
    if not want["changed"]:
        print("YGG_ATLAS_REPAIR_ALREADY_VALID=" + source)
        return
    branch = "atlas/automatic/" + source
    # Git transports only the independently rebuilt object to an unreferenced
    # object store. The API creates a new branch; no force/update/delete exists.
    require(text(root, "rev-parse", "HEAD") == source and
            text(root, "rev-parse", want["companion"] + "^{tree}") == want["tree"], "publish tree drift")
    lease(number, source)
    try:
        existing = api("/repos/" + REPOSITORY + "/git/ref/heads/" + branch)
    except urllib.error.HTTPError as err:
        if err.code != 404:
            raise
        existing = None
    if existing:
        require(existing["object"]["sha"] == want["companion"], "existing companion differs")
    else:
        # A one-use askpass avoids storing the token in Git config or a URL.
        with tempfile.TemporaryDirectory(prefix="ygg-atlas-auth-") as temp:
            askpass = Path(temp) / "askpass.py"
            askpass.write_text("#!/usr/bin/env python3\nimport os,sys\nprint('x-access-token' if 'Username' in sys.argv[1] else os.environ['GH_TOKEN'])\n", encoding="utf-8")
            askpass.chmod(0o700)
            env = dict(os.environ, GIT_ASKPASS=str(askpass), GIT_TERMINAL_PROMPT="0")
            # An absent-ref lease makes concurrent/repeated publication safe.
            git(root, "-c", "core.hooksPath=/dev/null", "push",
                "--force-with-lease=refs/heads/" + branch + ":",
                "https://github.com/" + REPOSITORY + ".git",
                want["companion"] + ":refs/heads/" + branch, env=env)
    # GITHUB_TOKEN pushes do not start ordinary CI. Explicit dispatch runs the
    # unchanged, committed-blob G29 checks at the companion instead.
    runs = api("/repos/" + REPOSITORY + "/actions/runs?head_sha=" + want["companion"] +
               "&event=workflow_dispatch&per_page=100")["workflow_runs"]
    if not any(run["path"] == ".github/workflows/yggdrasil-g29-atlas.yml" and
               run["head_sha"] == want["companion"] and run.get("conclusion") != "cancelled" for run in runs):
        api("/repos/" + REPOSITORY + "/actions/workflows/yggdrasil-g29-atlas.yml/dispatches",
            "POST", {"ref": branch})
    url = "https://github.com/" + REPOSITORY + "/commit/" + want["companion"]
    print("YGG_ATLAS_COMPANION_PUBLISHED=" + url)
    summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary:
        with open(summary, "a", encoding="utf-8") as file:
            file.write("Atlas repaired for PR #" + str(number) + ": [companion](" + url +
                       "). Source `" + source + "` unchanged. Linux and Windows qualification passed; "
                       "strict G29 dispatched. No accepted-ref update or scientific promotion.\n")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("resolve", "prepare", "verify", "publish"))
    parser.add_argument("--root", type=Path)
    parser.add_argument("--control", type=Path)
    parser.add_argument("--source")
    parser.add_argument("--receipt", type=Path)
    parser.add_argument("--receipts", type=Path)
    parser.add_argument("--pr", type=int)
    args = parser.parse_args()
    if args.command == "resolve":
        result = resolve(json.loads(Path(os.environ["GITHUB_EVENT_PATH"]).read_text("utf-8")))
        with open(os.environ["GITHUB_OUTPUT"], "a", encoding="utf-8") as output:
            for key, value in result.items():
                output.write(key + "=" + value + "\n")
    elif args.command == "prepare":
        result = prepare(args.root.resolve(), args.control.resolve(), args.source)
        args.receipt.parent.mkdir(parents=True, exist_ok=True)
        args.receipt.write_text(json.dumps(result, sort_keys=True) + "\n", encoding="utf-8")
        print("YGG_ATLAS_COMPANION_PREPARED=" + result["companion"])
    elif args.command == "verify":
        verify(args.root.resolve(), json.loads(args.receipt.read_text("utf-8")))
        print("YGG_ATLAS_COMPANION_QUALIFIED")
    else:
        publish(args.root.resolve(), args.control.resolve(), args.source, args.pr, args.receipts)


if __name__ == "__main__":
    main()
