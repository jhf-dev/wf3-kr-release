"""Audit a GitHub release event against the committed candidate bytes."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import urllib.parse
import urllib.request
from datetime import datetime
from pathlib import Path
from typing import Any, Mapping


class AuditError(ValueError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AuditError(message)


def text_sha256(text: str) -> str:
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest().upper()


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def require_source_audit_token(environment: Mapping[str, str]) -> str:
    token = str(environment.get("WIND3_SOURCE_AUDIT_TOKEN") or "")
    require(
        bool(token),
        "private source tag audit token/App installation is not configured",
    )
    return token


def github_json(path: str, *, token: str | None = None) -> Any:
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "wind3-release-audit",
        "X-GitHub-Api-Version": "2026-03-10",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    request = urllib.request.Request(
        "https://api.github.com" + path,
        headers=headers,
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))


def resolve_tag(slug: str, tag: str, *, token: str | None = None) -> str:
    reference = github_json(
        f"/repos/{slug}/git/ref/tags/{urllib.parse.quote(tag, safe='')}",
        token=token,
    )
    target = reference["object"]
    seen: set[str] = set()
    while target["type"] == "tag":
        sha = str(target["sha"])
        require(sha not in seen, "annotated tag cycle detected")
        seen.add(sha)
        target = github_json(
            f"/repos/{slug}/git/tags/{sha}",
            token=token,
        )["object"]
    require(target["type"] == "commit", "release tag does not target a commit")
    return str(target["sha"]).upper()


def stable_approval_bodies(
    candidate: dict[str, Any],
    *,
    candidate_sha256: str,
    session_nonce: str,
) -> tuple[str, str]:
    version = str(candidate["version"])
    asset_sha = str(candidate["asset"]["sha256"]).upper()
    return (
        (
            f"WIND3 RUNTIME CONFIRM {version} {asset_sha} {session_nonce} "
            "REDOWNLOADED_ASSET_F3_VICTORY_VISIBLE"
        ),
        (
            f"WIND3 STABLE APPROVE {version} {asset_sha} {candidate_sha256} "
            f"{session_nonce} STABLE_LATEST_CONFIRMED"
        ),
    )


def audit_stable_prerelease(
    candidate: dict[str, Any],
    redownload: dict[str, Any],
    prerelease: dict[str, Any],
) -> dict[str, Any]:
    require(
        prerelease.get("id") == redownload.get("release_id")
        and prerelease.get("tag_name") == candidate["promotes_prerelease"]
        and prerelease.get("name") == candidate["promotes_prerelease"]
        and prerelease.get("draft") is False
        and prerelease.get("prerelease") is True
        and prerelease.get("immutable") is True
        and str((prerelease.get("author") or {}).get("login") or "").casefold()
        == "jhf-dev",
        "sealed prerelease identity/channel/actor is not exact",
    )
    prerelease_assets = prerelease.get("assets")
    require(
        isinstance(prerelease_assets, list) and len(prerelease_assets) == 1,
        "sealed prerelease asset inventory is not exact",
    )
    prerelease_asset = prerelease_assets[0]
    require(
        prerelease_asset.get("id") == redownload.get("asset_id")
        and prerelease_asset.get("name") == redownload.get("asset_name")
        and prerelease_asset.get("size") == redownload.get("asset_size")
        and str(prerelease_asset.get("digest") or "").casefold()
        == f"sha256:{redownload.get('asset_sha256')}".casefold(),
        "sealed prerelease asset differs from redownload proof",
    )
    return {
        "release_id": int(prerelease["id"]),
        "asset_id": int(prerelease_asset["id"]),
        "asset_sha256": str(redownload["asset_sha256"]).upper(),
    }


def audit_prerelease_baseline(
    candidate: dict[str, Any],
    latest: dict[str, Any],
    *,
    live_target: str,
) -> dict[str, Any]:
    baseline = candidate["baseline"]
    require(
        latest.get("id") == baseline.get("release_id")
        and latest.get("tag_name") == baseline.get("tag_name")
        and latest.get("draft") is False
        and latest.get("prerelease") is False
        and str((latest.get("author") or {}).get("login") or "").casefold()
        == "jhf-dev"
        and live_target.upper()
        == str(baseline.get("target_commit_sha") or "").upper(),
        "live latest stable differs from the sealed prerelease baseline",
    )
    return {
        "release_id": int(latest["id"]),
        "tag_name": str(latest["tag_name"]),
        "target_commit_sha": live_target.upper(),
    }


def audit_stable_comments(
    root: Path,
    candidate: dict[str, Any],
    trusted_head: str,
) -> dict[str, Any]:
    pulls = github_json(
        f"/repos/jhf-dev/wf3-kr-release/commits/{trusted_head}/pulls"
    )
    matches = [
        pull
        for pull in pulls
        if pull.get("merged_at")
        and str((pull.get("user") or {}).get("login") or "").casefold()
        == "jhf-dev"
        and str((pull.get("merged_by") or {}).get("login") or "").casefold()
        == "jhf-dev"
        and str((pull.get("base") or {}).get("ref") or "") == "main"
    ]
    require(bool(matches), "stable release commit lacks jhf-dev PR provenance")
    pull = matches[-1]
    comments = github_json(
        f"/repos/jhf-dev/wf3-kr-release/issues/{pull['number']}/comments?per_page=100"
    )
    redownload = json.loads(
        (
            root
            / str(candidate["proofs"]["redownload"]["path"])
        ).read_text(encoding="utf-8")
    )
    runtime_body, approval_body = stable_approval_bodies(
        candidate,
        candidate_sha256=file_sha256(root / ".release" / "candidate.json"),
        session_nonce=str(redownload["session_nonce"]),
    )
    prerelease = github_json(
        "/repos/jhf-dev/wf3-kr-release/releases/tags/"
        + urllib.parse.quote(str(candidate["promotes_prerelease"]), safe="")
    )
    published_at = datetime.fromisoformat(
        str(prerelease["published_at"]).replace("Z", "+00:00")
    )
    audit_stable_prerelease(candidate, redownload, prerelease)

    def exact(body: str) -> dict[str, Any]:
        found = [
            comment
            for comment in comments
            if str(comment.get("body") or "") == body
            and str((comment.get("user") or {}).get("login") or "").casefold()
            == "jhf-dev"
            and comment.get("created_at") == comment.get("updated_at")
        ]
        require(
            len(found) == 1,
            "stable release lacks one exact, unedited jhf-dev approval comment",
        )
        created = datetime.fromisoformat(
            str(found[0]["created_at"]).replace("Z", "+00:00")
        )
        require(
            created > published_at,
            "stable approval comment predates prerelease publication",
        )
        return found[0]

    runtime = exact(runtime_body)
    approval = exact(approval_body)
    require(runtime["id"] != approval["id"], "stable approval comments are not separate")
    return {
        "pull_number": int(pull["number"]),
        "runtime_comment_id": int(runtime["id"]),
        "approval_comment_id": int(approval["id"]),
        "session_nonce": str(redownload["session_nonce"]),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidate-root", type=Path, required=True)
    parser.add_argument("--trusted-root", type=Path, required=True)
    parser.add_argument(
        "--event",
        type=Path,
        default=Path(os.environ.get("GITHUB_EVENT_PATH", "")),
    )
    args = parser.parse_args(argv)
    try:
        event = json.loads(args.event.read_text(encoding="utf-8"))
        action = str(event.get("action") or "")
        require(action != "deleted", "deleting a published release is break-glass only")
        release = event.get("release")
        require(isinstance(release, dict), "release event payload is missing")
        root = args.candidate_root.resolve()
        trusted_root = args.trusted_root.resolve()
        candidate = json.loads(
            (root / ".release" / "candidate.json").read_text(encoding="utf-8")
        )
        notes = (root / "RELEASE_NOTES.md").read_text(encoding="utf-8")
        version = str(candidate["version"])
        channel = str(candidate["channel"])
        require(release.get("tag_name") == version, "remote release tag mismatch")
        require(release.get("name") == version, "remote release title mismatch")
        require(release.get("draft") is False, "published event still reports draft")
        require(
            release.get("prerelease") is (channel == "prerelease"),
            "remote release channel mismatch",
        )
        require(release.get("immutable") is True, "published release is not immutable")
        require(
            str((release.get("author") or {}).get("login") or "").casefold()
            == "jhf-dev",
            "remote release actor is not jhf-dev",
        )
        require(
            text_sha256(str(release.get("body") or "")) == text_sha256(notes),
            "remote release body differs from committed RELEASE_NOTES.md",
        )
        assets = release.get("assets")
        require(isinstance(assets, list) and len(assets) == 1, "remote asset count mismatch")
        remote_asset = assets[0]
        expected_asset = candidate["asset"]
        require(remote_asset.get("name") == expected_asset["name"], "remote asset name mismatch")
        require(remote_asset.get("size") == expected_asset["size"], "remote asset size mismatch")
        digest = str(remote_asset.get("digest") or "")
        require(
            digest.casefold() == f"sha256:{expected_asset['sha256']}".casefold(),
            "remote asset digest mismatch",
        )
        tag_target = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=root,
            text=True,
            encoding="utf-8",
            capture_output=True,
            check=True,
        ).stdout.strip()
        trusted_head = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=trusted_root,
            text=True,
            encoding="utf-8",
            capture_output=True,
            check=True,
        ).stdout.strip()
        require(
            tag_target.upper() == trusted_head.upper(),
            "released tag does not target the exact trusted main commit",
        )
        require(
            str(event.get("release", {}).get("target_commitish") or "")
            in {tag_target, tag_target.upper()},
            "release target_commitish is unexpected",
        )
        require(
            resolve_tag("jhf-dev/wf3-kr-release", version) == trusted_head.upper(),
            "live release tag target differs from trusted main",
        )
        source = candidate["source"]
        source_audit_token = require_source_audit_token(os.environ)
        require(
            resolve_tag(
                str(source["repository"]),
                str(source["tag_name"]),
                token=source_audit_token,
            )
            == str(source["commit_sha"]).upper(),
            "live source tag target differs from candidate source commit",
        )
        latest = github_json(
            "/repos/jhf-dev/wf3-kr-release/releases/latest"
        )
        approval: dict[str, Any] | None = None
        if channel == "stable":
            require(
                latest.get("id") == release.get("id")
                and latest.get("tag_name") == version,
                "stable release is not the exact latest release",
            )
            approval = audit_stable_comments(root, candidate, trusted_head.upper())
        else:
            audit_prerelease_baseline(
                candidate,
                latest,
                live_target=resolve_tag(
                    "jhf-dev/wf3-kr-release",
                    str(candidate["baseline"].get("tag_name") or ""),
                ),
            )
        result: dict[str, Any] = {
            "schema": "wind3-remote-release-audit-v1",
            "ok": True,
            "action": action,
            "release_id": release["id"],
            "version": version,
            "channel": channel,
            "tag_target": tag_target,
            "body_sha256": text_sha256(notes),
            "asset_sha256": str(expected_asset["sha256"]).upper(),
            "stable_approval": approval,
        }
    except (
        AuditError,
        OSError,
        UnicodeError,
        json.JSONDecodeError,
        subprocess.SubprocessError,
    ) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False))
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
