"""Reject public-history identity drift, force pushes, and direct main pushes."""
from __future__ import annotations

import json
import re
import subprocess
import sys
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ZERO = "0" * 40
PRE = re.compile(r"^[0-9]{8}-v[1-9][0-9]*$")
STABLE = re.compile(r"^[0-9]{8}-v[1-9][0-9]*-release$")


class PushError(ValueError):
    pass


def run(*args: str, check: bool = True) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=ROOT,
        text=True,
        encoding="utf-8",
        capture_output=True,
        check=False,
    )
    if check and result.returncode != 0:
        raise PushError(f"git {' '.join(args)} failed: {result.stderr.strip()}")
    return result.stdout.strip()


def commit_identity(commit: str) -> None:
    expected = [
        "jhf-dev",
        "285839567+jhf-dev@users.noreply.github.com",
        "jhf-dev",
        "285839567+jhf-dev@users.noreply.github.com",
    ]
    actual = run("show", "-s", "--format=%an%n%ae%n%cn%n%ce", commit).splitlines()
    if actual != expected:
        raise PushError(
            f"public release commit {commit} has wrong author/committer identity"
        )
    validator = subprocess.run(
        [
            sys.executable,
            str(ROOT / ".release" / "validate_release.py"),
            "--commit-message-file",
            "-",
            "--message-only",
        ],
        cwd=ROOT,
        input=run("show", "-s", "--format=%B", commit),
        text=True,
        encoding="utf-8",
        capture_output=True,
        check=False,
    )
    if validator.returncode != 0:
        raise PushError(
            "public release commit message violates policy: "
            + (validator.stdout.strip() or validator.stderr.strip())
        )


def outgoing_commits(local_sha: str, remote_sha: str) -> list[str]:
    if remote_sha != ZERO:
        result = subprocess.run(
            ["git", "merge-base", "--is-ancestor", remote_sha, local_sha],
            cwd=ROOT,
            check=False,
        )
        if result.returncode != 0:
            raise PushError("non-fast-forward branch update is forbidden")
    exclusion = remote_sha if remote_sha != ZERO else "refs/remotes/origin/main"
    result = run("rev-list", local_sha, f"^{exclusion}", check=False)
    return [line for line in result.splitlines() if line]


def authenticated_actor() -> str:
    query = "protocol=https\nhost=github.com\nusername=jhf-dev\n\n"
    credential = subprocess.run(
        ["git", "credential-manager", "get", "--no-ui"],
        input=query,
        text=True,
        encoding="utf-8",
        capture_output=True,
        check=False,
    )
    if credential.returncode != 0:
        raise PushError("dedicated jhf-dev credential is unavailable")
    fields = {
        line.split("=", 1)[0]: line.split("=", 1)[1]
        for line in credential.stdout.splitlines()
        if "=" in line
    }
    if str(fields.get("username") or "").casefold() != "jhf-dev":
        raise PushError("credential manager selected the wrong GitHub account")
    request = urllib.request.Request(
        "https://api.github.com/user",
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {fields.get('password', '')}",
            "User-Agent": "wind3-release-pre-push",
            "X-GitHub-Api-Version": "2026-03-10",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            actor = json.loads(response.read().decode("utf-8"))
    except Exception as exc:
        raise PushError(f"could not verify the GitHub push actor: {exc}") from exc
    login = str(actor.get("login") or "")
    if login.casefold() != "jhf-dev":
        raise PushError(f"GitHub push actor mismatch: {login!r}")
    return login


def main() -> int:
    try:
        remote_name = sys.argv[1] if len(sys.argv) > 1 else ""
        remote_url = sys.argv[2] if len(sys.argv) > 2 else ""
        expected_origin = "https://jhf-dev@github.com/jhf-dev/wf3-kr-release.git"
        if remote_name != "origin" or remote_url != expected_origin:
            raise PushError("release pushes are allowed only to the exact origin repository")
        authenticated_actor()
        validator = subprocess.run(
            [
                sys.executable,
                str(ROOT / ".release" / "validate_release.py"),
                "--root",
                str(ROOT),
                "--check-git-identity",
            ],
            cwd=ROOT,
            text=True,
            encoding="utf-8",
            capture_output=True,
            check=False,
        )
        if validator.returncode != 0:
            raise PushError(validator.stdout.strip() or validator.stderr.strip())

        lines = [line.split() for line in sys.stdin.read().splitlines() if line.strip()]
        for fields in lines:
            if len(fields) != 4:
                raise PushError("invalid pre-push ref input")
            local_ref, local_sha, remote_ref, remote_sha = fields
            if local_sha == ZERO:
                raise PushError(f"remote ref deletion is forbidden: {remote_ref}")
            if remote_ref == "refs/heads/main":
                raise PushError(
                    "direct main push is forbidden; use a pull request with release-contract CI"
                )
            if remote_ref.startswith("refs/tags/"):
                tag = remote_ref.removeprefix("refs/tags/")
                if remote_sha != ZERO:
                    raise PushError(f"published/release tag update is forbidden: {tag}")
                if not (PRE.fullmatch(tag) or STABLE.fullmatch(tag)):
                    raise PushError(f"invalid release tag format: {tag}")
                state = json.loads(
                    (ROOT / ".release" / "state.json").read_text(encoding="utf-8")
                )
                candidate_path = ROOT / ".release" / "candidate.json"
                if state.get("mode") != "candidate" or not candidate_path.is_file():
                    raise PushError("new release tags require candidate mode")
                candidate = json.loads(candidate_path.read_text(encoding="utf-8"))
                if candidate.get("version") != tag:
                    raise PushError("release tag differs from candidate version")
                commit_identity(run("rev-list", "-n", "1", local_sha))
                continue
            for commit in outgoing_commits(local_sha, remote_sha):
                commit_identity(commit)
    except (OSError, UnicodeError, json.JSONDecodeError, PushError) as exc:
        print(f"release pre-push rejected: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
