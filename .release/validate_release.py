"""Standalone CI and hook validator for jhf-dev/wf3-kr-release."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
import zipfile
from datetime import datetime
from pathlib import Path, PurePosixPath
from typing import Any, Iterable, Mapping


STATE_SCHEMA = "wind3-release-repository-state-v1"
CANDIDATE_SCHEMA = "wind3-release-candidate-v1"
POLICY_SCHEMA = "wind3-release-policy-v1"
HEX40 = re.compile(r"^[0-9A-Fa-f]{40}$")
HEX64 = re.compile(r"^[0-9A-Fa-f]{64}$")
HANGUL = re.compile(r"[\uac00-\ud7a3]")
TRUSTED_CONTROL_PATHS = (
    ".gitattributes",
    ".gitignore",
    ".release/policy.json",
    ".release/github_settings.json",
    ".release/source_github_settings.json",
    ".release/validate_release.py",
    ".release/pre_push.py",
    ".release/audit_remote.py",
    ".release/install_hooks.ps1",
    ".githooks/commit-msg",
    ".githooks/pre-commit",
    ".githooks/pre-push",
    ".github/workflows/release-contract.yml",
    ".github/workflows/release-contract-base.yml",
    ".github/workflows/release-audit.yml",
    "VERSIONING.md",
)
TRUSTED_WORKFLOWS = {
    "release-contract.yml",
    "release-contract-base.yml",
    "release-audit.yml",
}
TRUSTED_HOOKS = {"commit-msg", "pre-commit", "pre-push"}


class ValidationError(ValueError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValidationError(message)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def load_json(path: Path) -> dict[str, Any]:
    try:
        result = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ValidationError(f"invalid JSON {path}: {exc}") from exc
    require(isinstance(result, dict), f"JSON root must be an object: {path}")
    return result


def normalize_lf(text: str) -> str:
    return text.replace("\r\n", "\n").replace("\r", "\n")


def validate_commit_message(message: str) -> dict[str, Any]:
    lines = normalize_lf(message).rstrip("\n").split("\n")
    require(len(lines) >= 4, "commit message requires a subject and 2-4 bullets")
    subject = lines[0]
    require(
        bool(subject) and subject == subject.strip(),
        "commit subject must be a non-empty trimmed line",
    )
    require(HANGUL.search(subject) is not None, "commit subject must contain Korean")
    require(lines[1] == "", "commit subject must be followed by one blank line")
    bullets = lines[2:]
    require(
        2 <= len(bullets) <= 4,
        "commit body must contain exactly 2-4 consecutive bullets",
    )
    for index, line in enumerate(bullets, start=1):
        require(
            line.startswith("- ") and len(line) > 2,
            f"commit bullet {index} must start with '- '",
        )
        require(
            HANGUL.search(line[2:]) is not None,
            f"commit bullet {index} must contain Korean",
        )
        require(
            not re.fullmatch(r"[A-Za-z0-9-]+:\s+.+", line[2:]),
            "commit attribution trailers are forbidden",
        )
    return {"subject": subject, "bullets": bullets}


def public_text(text: str, policy: Mapping[str, Any], label: str) -> None:
    folded = text.casefold()
    for term in policy["notes"]["forbidden_public_terms"]:
        require(
            str(term).casefold() not in folded,
            f"{label} contains forbidden development-only term: {term}",
        )


def channel(version: str, policy: Mapping[str, Any]) -> str:
    if re.fullmatch(policy["versioning"]["prerelease_pattern"], version):
        result = "prerelease"
    elif re.fullmatch(policy["versioning"]["stable_pattern"], version):
        result = "stable"
    else:
        raise ValidationError(f"invalid version: {version!r}")
    try:
        datetime.strptime(version[:8], "%Y%m%d")
    except ValueError as exc:
        raise ValidationError(
            f"release version contains an invalid calendar date: {version!r}"
        ) from exc
    return result


def artifact_version(version: str, policy: Mapping[str, Any]) -> str:
    release_channel = channel(version, policy)
    if release_channel == "prerelease":
        return version
    suffix = str(policy["versioning"]["stable_suffix"])
    base = version.removesuffix(suffix)
    require(
        channel(base, policy) == "prerelease" and base + suffix == version,
        "stable version does not map to a prerelease artifact",
    )
    return base


def clean_line(value: Any, label: str) -> str:
    result = str(value or "").strip()
    require(bool(result), f"{label} is empty")
    require("\n" not in result and "\r" not in result, f"{label} must be one line")
    require(not result.startswith("#"), f"{label} injects a Markdown heading")
    return result


def validate_control_inventory(root: Path) -> None:
    workflow_root = root / ".github" / "workflows"
    hook_root = root / ".githooks"
    attributes_path = root / ".gitattributes"
    require(workflow_root.is_dir(), "trusted workflow directory is missing")
    require(hook_root.is_dir(), "tracked hook directory is missing")
    require(attributes_path.is_file(), ".gitattributes is missing")
    attributes = set(attributes_path.read_text(encoding="utf-8").splitlines())
    require(
        ".release/*.json text eol=lf" in attributes,
        "release JSON must be checked out with LF for byte-stable policy hashes",
    )
    workflows = {
        path.name
        for path in workflow_root.iterdir()
        if path.is_file()
    }
    hooks = {
        path.name
        for path in hook_root.iterdir()
        if path.is_file()
    }
    require(
        workflows == TRUSTED_WORKFLOWS,
        f"trusted workflow inventory mismatch: {sorted(workflows)!r}",
    )
    require(
        hooks == TRUSTED_HOOKS,
        f"tracked hook inventory mismatch: {sorted(hooks)!r}",
    )


def change_lines(
    candidate: Mapping[str, Any],
    policy: Mapping[str, Any],
) -> list[str]:
    changes = candidate.get("changes")
    require(isinstance(changes, list) and changes, "candidate changes are required")
    lines: list[str] = []
    for index, section in enumerate(changes):
        require(isinstance(section, dict), f"changes[{index}] must be an object")
        require(
            set(section) == {"heading", "bullets"},
            f"changes[{index}] fields are not exact",
        )
        heading = clean_line(section.get("heading"), f"changes[{index}].heading")
        public_text(heading, policy, f"changes[{index}].heading")
        lines.extend(
            (
                f"### {heading}",
                "",
            )
        )
        bullets = section.get("bullets")
        require(
            isinstance(bullets, list) and bullets,
            f"changes[{index}].bullets are required",
        )
        for bullet_index, bullet in enumerate(bullets):
            cleaned = clean_line(
                bullet,
                f"changes[{index}].bullets[{bullet_index}]",
            )
            public_text(
                cleaned,
                policy,
                f"changes[{index}].bullets[{bullet_index}]",
            )
            lines.append(
                "- " + cleaned
            )
        lines.append("")
    return lines


def render_public_notes(
    candidate: Mapping[str, Any],
    policy: Mapping[str, Any],
) -> str:
    version = str(candidate["version"])
    baseline = str(candidate["baseline"]["tag_name"])
    asset = candidate["asset"]
    headings = [
        str(item).format(baseline_tag=baseline)
        for item in policy["notes"]["required_level2_headings"]
    ]
    lines = [
        str(policy["notes"]["title_template"]).format(version=version),
        "",
        f"## {headings[0]}",
        "",
        f"- 배포 파일: `{asset['name']}`",
        f"- SHA-256: `{str(asset['sha256']).upper()}`",
        f"- 파일 크기: `{asset['size']}` bytes",
        (
            "- 채널: pre-release"
            if candidate["channel"] == "prerelease"
            else "- 채널: release"
        ),
        "",
        f"## {headings[1]}",
        "",
        *change_lines(candidate, policy),
    ]
    result = "\n".join(lines).rstrip() + "\n"
    public_text(result, policy, "RELEASE_NOTES.md")
    return result


def render_package_notes(
    candidate: Mapping[str, Any],
    policy: Mapping[str, Any],
) -> str:
    version = artifact_version(str(candidate["version"]), policy)
    baseline = str(candidate["baseline"]["tag_name"])
    comparison = str(policy["notes"]["required_level2_headings"][1]).format(
        baseline_tag=baseline
    )
    lines = [
        str(policy["notes"]["package_title_template"]).format(version=version),
        "",
        f"## {comparison}",
        "",
        *change_lines(candidate, policy),
    ]
    result = "\n".join(lines).rstrip() + "\n"
    public_text(result, policy, "packaged RELEASE_NOTES.md")
    return result


def render_package_readme(candidate: Mapping[str, Any], policy: Mapping[str, Any]) -> str:
    version = artifact_version(str(candidate["version"]), policy)
    result = (
        "# Wind Fantasy 3 한국어 패치\n\n"
        f"버전: `{version}`\n\n"
        "`Wind3 Korean Patch Launcher.exe`를 실행해 패치 적용, 상태 확인, "
        "세이브 복구, 화면·입력 설정을 사용할 수 있습니다.\n"
        "패치 적용이 끝나면 패치 백엔드가 없는 `windconfig.exe` 경량 런처를 "
        "게임 폴더에 설치합니다. Steam에서 실행하면 화면·입력·자동 기능 설정과 "
        "게임 실행만 제공하며, 기존 `windconfig.exe`는 "
        "`windconfig_original.exe`로 보존합니다.\n"
        "배포 패키지는 개발 도구나 개발 폴더에 의존하지 않습니다.\n"
    )
    public_text(result, policy, "packaged README.md")
    return result


def render_repository_readme(
    candidate: Mapping[str, Any],
    policy: Mapping[str, Any],
) -> str:
    version = str(candidate["version"])
    release_channel = str(candidate["channel"])
    baseline = str(candidate["baseline"]["tag_name"])
    asset = candidate["asset"]
    label = (
        "검증 중인 pre-release"
        if release_channel == "prerelease"
        else "안정화 release"
    )
    lines = [
        "# Wind Fantasy 3 한국어 패치",
        "",
        "Wind Fantasy 3 한국어 패치 배포용 저장소입니다.",
        "",
        "이 저장소는 게임 본편이나 원본 게임 리소스를 포함하지 않습니다. "
        "사용자가 보유한 설치본에 차이 패치를 적용하고 원본 상태로 복원합니다.",
        "",
        "## 다운로드",
        "",
        f"- {label}: `{version}`",
        f"- 배포 파일: `{asset['name']}`",
        f"- SHA-256: `{str(asset['sha256']).upper()}`",
        f"- 파일 크기: `{asset['size']:,}` bytes",
        "- 체크섬 파일: `SHA256SUMS.txt`",
        "- 주요 변경사항: [RELEASE_NOTES.md](RELEASE_NOTES.md)",
        "- 버전명 정책: [VERSIONING.md](VERSIONING.md)",
        "",
        f"> 변경 비교 기준은 게시 시점의 직전 latest 안정판 `{baseline}`입니다.",
        "",
        "## 사용 방법",
        "",
        f"1. `{asset['name']}`을 다운로드합니다.",
        "2. 원하는 위치에 압축을 풉니다.",
        "3. `Wind3 Korean Patch Launcher.exe`를 실행합니다.",
        "4. `WIND3.EXE`가 있는 게임 폴더를 선택하고 `패치 적용`을 실행합니다.",
        "5. 문제가 생기면 같은 런처의 `원본 복원`으로 되돌립니다.",
        "",
        "저해상도 환경에서는 `Wind3 Korean Patch Lite Launcher.exe`를 사용할 수 "
        "있고, 화면·입력·자동 기능은 `windconfig.exe`에서 설정할 수 있습니다.",
        "",
        "## 사용 전 주의사항",
        "",
        "- 패치 적용 전에는 게임을 완전히 종료해 주세요.",
        "- 중요한 저장 데이터는 별도로 백업하는 것을 권장합니다.",
        "- 이 패치는 비공식 개인 한국어 패치이며 모든 PC 환경에서 동일한 동작을 보장하지 않습니다.",
        "",
        "## 포함하지 않는 것",
        "",
        "- Wind Fantasy 3 게임 실행 파일",
        "- 원본 게임 리소스 전체",
        "- 사용자의 저장 데이터",
        "- 로컬 테스트 로그와 개발 중간 산출물",
        "",
        "## 라이선스와 권리 고지",
        "",
        "오픈소스 구성요소 고지는 `THIRD_PARTY_NOTICES.txt`, `licenses/`, "
        "`LICENSES.md`를 확인하세요.",
        "",
    ]
    result = "\n".join(lines)
    public_text(result, policy, "README.md")
    return result


def render_checksums(candidate: Mapping[str, Any]) -> str:
    asset = candidate["asset"]
    return (
        "# SHA-256 checksums\n\n"
        f"{str(asset['sha256']).upper()}  {asset['name']}\n\n"
        f"Size bytes: {asset['size']}\n"
    )


def safe_zip_names(names: Iterable[str]) -> list[str]:
    result: list[str] = []
    folded: set[str] = set()
    for name in names:
        require("\\" not in name, f"ZIP path uses a backslash: {name}")
        path = PurePosixPath(name)
        require(
            not path.is_absolute()
            and ".." not in path.parts
            and not any(":" in part for part in path.parts),
            f"unsafe ZIP path: {name}",
        )
        require(name.casefold() not in folded, f"case-colliding ZIP path: {name}")
        folded.add(name.casefold())
        result.append(name)
    return result


def validate_zip(
    root: Path,
    candidate: Mapping[str, Any],
    policy: Mapping[str, Any],
) -> None:
    asset = candidate["asset"]
    asset_path = root / Path(str(asset["path"]))
    require(asset_path.is_file(), f"asset is missing: {asset_path}")
    require(asset_path.name == asset["name"], "asset path/name mismatch")
    require(asset_path.stat().st_size == asset["size"], "asset size mismatch")
    require(sha256_file(asset_path) == str(asset["sha256"]).upper(), "asset hash mismatch")
    package = policy["package"]
    prefix = str(package["root_prefix"])
    try:
        with zipfile.ZipFile(asset_path, "r") as archive:
            files = [
                name
                for name in safe_zip_names(
                    entry.filename for entry in archive.infolist()
                )
                if not name.endswith("/")
            ]
            require(files and all(name.startswith(prefix) for name in files), "ZIP root prefix mismatch")
            folded = [name.casefold() for name in files]
            for token in package["forbidden_developer_entries"]:
                require(
                    not any(str(token).casefold() in name for name in folded),
                    f"developer-only ZIP entry: {token}",
                )
            forbidden_extensions = {
                str(value).casefold()
                for value in package["forbidden_developer_extensions"]
            }
            for name in files:
                require(
                    PurePosixPath(name).suffix.casefold() not in forbidden_extensions,
                    f"developer-only ZIP file type: {name}",
                )
            version_path = str(package["launcher_version_path"])
            launcher_version = json.loads(archive.read(version_path).decode("utf-8"))
            require(
                launcher_version.get("version")
                == artifact_version(str(candidate["version"]), policy),
                "launcher_version version mismatch",
            )
            require(
                launcher_version.get("tag_name")
                == artifact_version(str(candidate["version"]), policy),
                "launcher_version tag mismatch",
            )
            require(
                launcher_version.get("repository") == policy["release_repository"],
                "launcher_version repository mismatch",
            )
            actual_executables = {
                name[len(prefix) :]
                for name in files
                if name.casefold().endswith(".exe")
            }
            expected_executables = {
                *map(str, package["public_launchers"]),
                *map(str, package["public_auxiliary_executables"]),
                *map(str, package["runtime_executables"]),
            }
            require(
                actual_executables == expected_executables,
                "ZIP executable inventory mismatch: "
                f"expected={sorted(expected_executables)!r}, "
                f"actual={sorted(actual_executables)!r}",
            )
            packaged_notes = archive.read(prefix + "RELEASE_NOTES.md").decode("utf-8")
            require(
                normalize_lf(packaged_notes) == render_package_notes(candidate, policy),
                "packaged release notes differ from candidate",
            )
            packaged_readme = archive.read(prefix + "README.md").decode("utf-8")
            require(
                normalize_lf(packaged_readme)
                == render_package_readme(candidate, policy),
                "packaged README.md differs from candidate",
            )
    except (OSError, KeyError, UnicodeError, json.JSONDecodeError, zipfile.BadZipFile) as exc:
        raise ValidationError(f"invalid release ZIP: {exc}") from exc


def validate_proof(
    root: Path,
    descriptor: Any,
    *,
    schema: str,
    asset_sha256: str,
    label: str,
) -> dict[str, Any]:
    require(isinstance(descriptor, dict), f"{label} descriptor is required")
    path = Path(str(descriptor.get("path") or ""))
    require(path.parts and not path.is_absolute() and ".." not in path.parts, f"unsafe {label} path")
    absolute = root / path
    expected = str(descriptor.get("sha256") or "").upper()
    require(bool(HEX64.fullmatch(expected)), f"invalid {label} descriptor hash")
    require(absolute.is_file(), f"{label} is missing")
    require(sha256_file(absolute) == expected, f"{label} file hash mismatch")
    proof = load_json(absolute)
    require(proof.get("schema") == schema, f"{label} schema mismatch")
    require(proof.get("ok") is True, f"{label} is not passing")
    require(
        str(proof.get("asset_sha256") or "").upper() == asset_sha256,
        f"{label} asset mismatch",
    )
    return proof


def validate_stage6_proof(
    root: Path,
    descriptor: Any,
    *,
    candidate: Mapping[str, Any],
    policy: Mapping[str, Any],
    asset_sha256: str,
) -> dict[str, Any]:
    proof = validate_proof(
        root,
        descriptor,
        schema="wind3-stage6-release-proof-v1",
        asset_sha256=asset_sha256,
        label="Stage 6 proof",
    )
    base_version = artifact_version(str(candidate["version"]), policy)
    expected = {
        "version": base_version,
        "baseline": candidate["baseline"],
        "source": candidate["source"],
        "release_plan_sha256": candidate["release_plan_sha256"],
        "asset_name": str(policy["versioning"]["asset_template"]).format(
            version=base_version
        ),
        "asset_size": int(candidate["asset"]["size"]),
    }
    actual = {
        key: proof.get(key)
        for key in (
            "version",
            "baseline",
            "source",
            "release_plan_sha256",
            "asset_name",
            "asset_size",
        )
    }
    require(actual == expected, f"Stage 6 identity mismatch: {actual!r}")
    require(bool(HEX64.fullmatch(str(proof.get("build_id") or ""))), "Stage 6 build_id invalid")
    require(bool(HEX64.fullmatch(str(proof.get("artifact_id") or ""))), "Stage 6 artifact_id invalid")
    gates = proof.get("gates")
    required = set(policy["proofs"]["stage6_required_gates"])
    require(isinstance(gates, dict) and set(gates) == required, "Stage 6 gate inventory mismatch")
    for gate in required:
        require(gates.get(gate) is True, f"Stage 6 gate did not pass: {gate}")
    return proof


def validate_candidate(
    root: Path,
    state: Mapping[str, Any],
    policy: Mapping[str, Any],
) -> dict[str, Any]:
    candidate_path = root / ".release" / "candidate.json"
    require(candidate_path.is_file(), "candidate mode requires .release/candidate.json")
    candidate = load_json(candidate_path)
    require(candidate.get("schema") == CANDIDATE_SCHEMA, "candidate schema mismatch")
    version = str(candidate.get("version") or "")
    release_channel = channel(version, policy)
    expected_fields = {
        "schema",
        "version",
        "channel",
        "baseline",
        "source",
        "release_plan_sha256",
        "asset",
        "changes",
        "proofs",
    }
    if release_channel == "stable":
        expected_fields.add("promotes_prerelease")
    require(set(candidate) == expected_fields, "candidate fields are not exact")
    require(candidate.get("channel") == release_channel, "candidate channel mismatch")
    require(
        bool(HEX64.fullmatch(str(candidate.get("release_plan_sha256") or ""))),
        "candidate release_plan_sha256 is invalid",
    )
    baseline = candidate.get("baseline")
    source = candidate.get("source")
    asset = candidate.get("asset")
    proofs = candidate.get("proofs")
    for value, label in (
        (baseline, "baseline"),
        (source, "source"),
        (asset, "asset"),
        (proofs, "proofs"),
    ):
        require(isinstance(value, dict), f"candidate {label} is required")
    require(channel(str(baseline.get("tag_name") or ""), policy) == "stable", "baseline must be stable")
    require(
        set(baseline) == {"release_id", "tag_name", "target_commit_sha"},
        "baseline fields are not exact",
    )
    require(
        isinstance(baseline.get("release_id"), int)
        and int(baseline["release_id"]) > 0,
        "baseline release_id must be positive",
    )
    require(bool(HEX40.fullmatch(str(baseline.get("target_commit_sha") or ""))), "baseline target SHA invalid")
    require(source.get("repository") == policy["source_repository"], "source repo mismatch")
    require(
        set(source) == {"repository", "commit_sha", "tag_name"},
        "source fields are not exact",
    )
    require(bool(HEX40.fullmatch(str(source.get("commit_sha") or ""))), "source SHA invalid")
    require(
        source.get("tag_name") == artifact_version(version, policy),
        "source tag differs from immutable artifact version",
    )
    expected_name = str(policy["versioning"]["asset_template"]).format(version=version)
    require(asset.get("name") == expected_name, "asset name mismatch")
    require(
        set(asset) == {"name", "path", "size", "sha256"},
        "asset fields are not exact",
    )
    require(bool(HEX64.fullmatch(str(asset.get("sha256") or ""))), "asset SHA invalid")
    require(isinstance(asset.get("size"), int) and asset["size"] > 0, "asset size invalid")
    relative_asset = Path(str(asset.get("path") or ""))
    require(
        relative_asset.parts
        and not relative_asset.is_absolute()
        and ".." not in relative_asset.parts
        and relative_asset.name == expected_name
        and str(relative_asset) == expected_name,
        "candidate asset.path must be the exact repository-root asset name",
    )
    require(
        normalize_lf((root / "RELEASE_NOTES.md").read_text(encoding="utf-8"))
        == render_public_notes(candidate, policy),
        "repository RELEASE_NOTES.md is not candidate-generated",
    )
    plan_path = root / ".release" / "proofs" / "release-plan.json"
    require(plan_path.is_file(), "sealed release plan is missing")
    require(
        sha256_file(plan_path)
        == str(candidate["release_plan_sha256"]).upper(),
        "sealed release plan hash mismatch",
    )
    plan = load_json(plan_path)
    require(plan.get("schema") == "wind3-release-plan-v1", "release plan schema mismatch")
    require(
        artifact_version(version, policy) == plan.get("version")
        and candidate["baseline"] == plan.get("baseline")
        and candidate["source"] == plan.get("source")
        and candidate["changes"] == plan.get("changes"),
        "candidate differs from sealed release plan",
    )
    require(
        normalize_lf((root / "README.md").read_text(encoding="utf-8"))
        == render_repository_readme(candidate, policy),
        "repository README.md is not candidate-generated",
    )
    require(
        normalize_lf((root / "SHA256SUMS.txt").read_text(encoding="utf-8"))
        == render_checksums(candidate),
        "repository SHA256SUMS.txt is not candidate-generated",
    )
    validate_zip(root, candidate, policy)
    asset_sha = str(asset["sha256"]).upper()
    stage6_proof = validate_stage6_proof(
        root,
        proofs.get("stage6"),
        candidate=candidate,
        policy=policy,
        asset_sha256=asset_sha,
    )
    expected_proofs = (
        {"stage6", "redownload"}
        if release_channel == "stable"
        else {"stage6"}
    )
    require(
        set(proofs) == expected_proofs,
        f"candidate proof inventory mismatch: expected={sorted(expected_proofs)!r}",
    )
    if release_channel == "stable":
        require(
            set(policy["publication"]["stable_required_proofs"])
            == {
                "github_redownload",
                "clean_temp_from_redownload",
                "runtime_user_pr_comment",
                "separate_user_approval_pr_comment",
            },
            "stable proof policy is unsupported or incomplete",
        )
        prerelease_version = artifact_version(version, policy)
        require(
            candidate.get("promotes_prerelease") == prerelease_version,
            "stable candidate promotes the wrong prerelease",
        )
        redownload = validate_proof(
            root,
            proofs.get("redownload"),
            schema="wind3-release-redownload-proof-v1",
            asset_sha256=asset_sha,
            label="redownload proof",
        )
        require(
            redownload.get("prerelease_version") == prerelease_version,
            "redownload proof prerelease mismatch",
        )
        require(
            isinstance(redownload.get("release_id"), int)
            and redownload["release_id"] > 0,
            "redownload proof release_id invalid",
        )
        require(
            isinstance(redownload.get("asset_id"), int)
            and redownload["asset_id"] > 0,
            "redownload proof asset_id invalid",
        )
        require(
            set(redownload)
            == {
                "schema",
                "ok",
                "prerelease_version",
                "release_id",
                "asset_id",
                "asset_name",
                "asset_size",
                "asset_sha256",
                "verified_at",
                "session_nonce",
                "clean_temp",
                "gates",
            },
            "redownload proof fields are not exact",
        )
        require(
            redownload.get("asset_name")
            == str(policy["versioning"]["asset_template"]).format(
                version=prerelease_version
            )
            and redownload.get("asset_size") == asset["size"],
            "redownload proof asset identity mismatch",
        )
        try:
            verified_at = datetime.fromisoformat(str(redownload["verified_at"]))
        except ValueError as exc:
            raise ValidationError("redownload proof verified_at invalid") from exc
        require(
            verified_at.tzinfo is not None,
            "redownload proof verified_at must include a timezone",
        )
        require(
            bool(re.fullmatch(r"[0-9a-f]{64}", str(redownload["session_nonce"]))),
            "redownload proof session_nonce invalid",
        )
        require(
            redownload.get("clean_temp")
            == {
                "artifact_id": str(stage6_proof["artifact_id"]),
                "package_backend_executed": True,
                "backend_preflight_verified": True,
                "xlsx_reads": 0,
                "build_steps": 0,
                "analysis_out_runtime_dependency": False,
                "restore_mismatch_count": 0,
                "temporary_remainder_count": 0,
                "release_zip_sha256": asset_sha,
            },
            "redownload clean/temp summary is not exact",
        )
        redownload_gates = redownload.get("gates")
        require(
            isinstance(redownload_gates, dict)
            and redownload_gates
            == {
                "github_redownload": True,
                "clean_temp_from_download": True,
            },
            "redownload proof gates are incomplete",
        )
    return {
        "mode": "candidate",
        "version": version,
        "channel": release_channel,
        "asset_sha256": asset_sha,
    }


def validate_grandfathered(
    root: Path,
    state: Mapping[str, Any],
    policy: Mapping[str, Any],
) -> dict[str, Any]:
    require(
        not (root / ".release" / "candidate.json").exists(),
        "grandfathered mode cannot contain a candidate",
    )
    grandfathered = state.get("grandfathered_release")
    require(isinstance(grandfathered, dict), "grandfathered release state is missing")
    pinned = grandfathered.get("pinned_files")
    require(isinstance(pinned, dict) and pinned, "grandfathered pinned files are missing")
    for relative, expected in pinned.items():
        path = root / str(relative)
        require(path.is_file(), f"grandfathered file is missing: {relative}")
        require(
            sha256_file(path) == str(expected).upper(),
            f"grandfathered file changed in place: {relative}; create a new candidate version",
        )
    zip_path = root / str(grandfathered["asset_name"])
    with zipfile.ZipFile(zip_path, "r") as archive:
        version_path = str(policy["package"]["launcher_version_path"])
        launcher_version = json.loads(archive.read(version_path).decode("utf-8"))
        require(
            launcher_version.get("version") == grandfathered["version"],
            "grandfathered ZIP version drift",
        )
        require(
            launcher_version.get("repository") == policy["release_repository"],
            "grandfathered ZIP repository drift",
        )
    return {
        "mode": "grandfathered-read-only",
        "version": grandfathered["version"],
        "asset_sha256": grandfathered["asset_sha256"],
        "warnings": list(grandfathered.get("known_noncompliance") or []),
    }


def validate(root: Path) -> dict[str, Any]:
    root = root.resolve()
    validate_control_inventory(root)
    policy_path = root / ".release" / "policy.json"
    state_path = root / ".release" / "state.json"
    policy = load_json(policy_path)
    state = load_json(state_path)
    require(policy.get("schema") == POLICY_SCHEMA, "policy schema mismatch")
    require(state.get("schema") == STATE_SCHEMA, "state schema mismatch")
    require(
        sha256_file(policy_path) == state.get("policy_sha256"),
        "policy changed without an explicit repository state transition",
    )
    settings_path = root / ".release" / "github_settings.json"
    require(
        settings_path.is_file()
        and sha256_file(settings_path) == state.get("github_settings_sha256"),
        "GitHub settings contract changed without an explicit repository state transition",
    )
    source_settings_path = root / ".release" / "source_github_settings.json"
    require(
        source_settings_path.is_file()
        and sha256_file(source_settings_path)
        == state.get("source_github_settings_sha256"),
        "source GitHub settings contract changed without a state transition",
    )
    require(policy["release_repository"] == "jhf-dev/wf3-kr-release", "wrong release repository policy")
    mode = state.get("mode")
    if mode == "grandfathered-read-only":
        detail = validate_grandfathered(root, state, policy)
    elif mode == "candidate":
        require(
            set(state)
            == {
                "schema",
                "mode",
                "policy_sha256",
                "github_settings_sha256",
                "source_github_settings_sha256",
                "candidate_version",
                "candidate_sha256",
            },
            "candidate repository state fields are not exact",
        )
        candidate_path = root / ".release" / "candidate.json"
        require(candidate_path.is_file(), "candidate state file is missing")
        candidate_state = load_json(candidate_path)
        require(
            state.get("candidate_version") == candidate_state.get("version"),
            "repository state candidate version mismatch",
        )
        require(
            state.get("candidate_sha256") == sha256_file(candidate_path),
            "repository state candidate hash mismatch",
        )
        detail = validate_candidate(root, state, policy)
    else:
        raise ValidationError(f"unknown repository state mode: {mode!r}")
    return {
        "schema": "wind3-release-repository-validation-v1",
        "ok": True,
        "policy_sha256": sha256_file(policy_path),
        "github_settings_sha256": sha256_file(settings_path),
        "source_github_settings_sha256": sha256_file(source_settings_path),
        **detail,
    }


def version_key(version: str, policy: Mapping[str, Any]) -> tuple[int, int]:
    base = artifact_version(version, policy)
    match = re.fullmatch(r"([0-9]{8})-v([1-9][0-9]*)", base)
    require(match is not None, f"invalid release version: {version}")
    return int(match.group(1)), int(match.group(2))


def validate_trusted_transition(root: Path, trusted_root: Path) -> None:
    root = root.resolve()
    trusted_root = trusted_root.resolve()
    for relative in TRUSTED_CONTROL_PATHS:
        candidate_path = root / relative
        trusted_path = trusted_root / relative
        require(
            candidate_path.is_file() and trusted_path.is_file(),
            f"trusted control file is missing: {relative}",
        )
        require(
            sha256_file(candidate_path) == sha256_file(trusted_path),
            f"normal PR cannot change trusted release control: {relative}",
        )
    trusted_state = load_json(trusted_root / ".release" / "state.json")
    candidate_state = load_json(root / ".release" / "state.json")
    if candidate_state.get("mode") == "grandfathered-read-only":
        require(
            candidate_state == trusted_state,
            "grandfathered state is immutable in normal pull requests",
        )
        return
    require(candidate_state.get("mode") == "candidate", "invalid state transition")
    candidate = load_json(root / ".release" / "candidate.json")
    policy = load_json(root / ".release" / "policy.json")
    if trusted_state.get("mode") == "grandfathered-read-only":
        minimum = str(
            trusted_state["next_candidate_requirements"]["minimum_replacement_version"]
        )
        require(
            version_key(str(candidate["version"]), policy)
            >= version_key(minimum, policy),
            "candidate version is below the grandfathered replacement minimum",
        )
        require(
            channel(str(candidate["version"]), policy) == "prerelease",
            "grandfathered state must transition to a new prerelease candidate",
        )
        return
    trusted_candidate = load_json(trusted_root / ".release" / "candidate.json")
    old_version = str(trusted_candidate["version"])
    new_version = str(candidate["version"])
    old_channel = channel(old_version, policy)
    new_channel = channel(new_version, policy)
    allowed_stable = (
        old_channel == "prerelease"
        and new_channel == "stable"
        and artifact_version(new_version, policy) == old_version
    )
    allowed_new_prerelease = (
        new_channel == "prerelease"
        and version_key(new_version, policy) > version_key(old_version, policy)
    )
    require(
        allowed_stable or allowed_new_prerelease,
        "candidate state must advance to same-byte stable or a higher prerelease",
    )
    if allowed_stable:
        for key in (
            "schema",
            "baseline",
            "source",
            "release_plan_sha256",
            "changes",
        ):
            require(
                candidate.get(key) == trusted_candidate.get(key),
                f"stable promotion changed sealed candidate field: {key}",
            )
        old_asset = trusted_candidate.get("asset")
        new_asset = candidate.get("asset")
        require(
            isinstance(old_asset, dict) and isinstance(new_asset, dict),
            "stable promotion asset metadata is invalid",
        )
        require(
            {
                "size": new_asset.get("size"),
                "sha256": str(new_asset.get("sha256") or "").upper(),
            }
            == {
                "size": old_asset.get("size"),
                "sha256": str(old_asset.get("sha256") or "").upper(),
            },
            "stable promotion changed the sealed asset bytes",
        )
        require(
            old_asset.get("name")
            == str(policy["versioning"]["asset_template"]).format(
                version=old_version
            )
            and old_asset.get("path") == old_asset.get("name")
            and new_asset.get("name")
            == str(policy["versioning"]["asset_template"]).format(
                version=new_version
            )
            and new_asset.get("path") == new_asset.get("name"),
            "stable promotion asset naming is not the exact channel projection",
        )
        old_proofs = trusted_candidate.get("proofs")
        new_proofs = candidate.get("proofs")
        require(
            isinstance(old_proofs, dict)
            and set(old_proofs) == {"stage6"}
            and isinstance(new_proofs, dict)
            and set(new_proofs) == {"stage6", "redownload"}
            and new_proofs.get("stage6") == old_proofs.get("stage6"),
            "stable promotion changed the sealed Stage 6 proof",
        )
        require(
            candidate.get("promotes_prerelease") == old_version
            and "promotes_prerelease" not in trusted_candidate,
            "stable promotion linkage is invalid",
        )


def git_output(root: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=root,
        text=True,
        encoding="utf-8",
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        raise ValidationError(f"git {' '.join(args)} failed: {result.stderr.strip()}")
    return result.stdout.strip()


def validate_git_identity(root: Path) -> None:
    policy = load_json(root / ".release" / "policy.json")
    identity = policy["identities"]
    expected_name = str(identity["release_author_name"])
    expected_email = str(identity["release_author_email"])
    require(git_output(root, "config", "--get", "user.name") == expected_name, "wrong git user.name")
    require(git_output(root, "config", "--get", "user.email") == expected_email, "wrong git user.email")
    remote = git_output(root, "remote", "get-url", "origin")
    require(
        remote == "https://jhf-dev@github.com/jhf-dev/wf3-kr-release.git",
        "wrong release origin or credential namespace",
    )
    require(
        git_output(
            root,
            "config",
            "--get",
            "credential.https://github.com.username",
        )
        == "jhf-dev",
        "wrong release Git credential namespace",
    )


def validate_commit_range(root: Path, base_ref: str) -> None:
    commits = [
        line
        for line in git_output(root, "rev-list", "HEAD", f"^{base_ref}").splitlines()
        if line
    ]
    require(bool(commits), "pull request contains no commits")
    expected = [
        "jhf-dev",
        "285839567+jhf-dev@users.noreply.github.com",
        "jhf-dev",
        "285839567+jhf-dev@users.noreply.github.com",
    ]
    for commit in commits:
        actual = git_output(
            root,
            "show",
            "-s",
            "--format=%an%n%ae%n%cn%n%ce",
            commit,
        ).splitlines()
        require(
            actual == expected,
            f"commit {commit} author/committer is not the dedicated jhf-dev identity",
        )
        validate_commit_message(
            git_output(root, "show", "-s", "--format=%B", commit)
        )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--check-git-identity", action="store_true")
    parser.add_argument("--trusted-root", type=Path)
    parser.add_argument("--base-ref")
    parser.add_argument("--commit-message-file", type=Path)
    parser.add_argument("--message-only", action="store_true")
    args = parser.parse_args(argv)
    try:
        if args.commit_message_file is not None:
            message_text = (
                sys.stdin.read()
                if str(args.commit_message_file) == "-"
                else args.commit_message_file.read_text(encoding="utf-8")
            )
            message_result = validate_commit_message(
                message_text
            )
            if args.message_only:
                print(
                    json.dumps(
                        {"ok": True, "commit_message": message_result},
                        ensure_ascii=False,
                        indent=2,
                        sort_keys=True,
                    )
                )
                return 0
        result = validate(args.root)
        if args.trusted_root is not None:
            validate_trusted_transition(args.root, args.trusted_root)
            result["trusted_transition_ok"] = True
        if args.check_git_identity:
            validate_git_identity(args.root.resolve())
            result["git_identity_ok"] = True
        if args.base_ref:
            validate_commit_range(args.root.resolve(), args.base_ref)
            result["commit_identity_ok"] = True
    except (OSError, UnicodeError, ValidationError, zipfile.BadZipFile) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False))
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
