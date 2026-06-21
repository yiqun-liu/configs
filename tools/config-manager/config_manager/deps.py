from __future__ import annotations

import json
import os
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Literal

from .model import ConfigError

Tier = Literal["required", "recommended", "optional"]
Status = Literal["ok", "missing", "blocked", "manual", "skip"]
Kind = Literal["tool", "env_var"]

_TIERS = {"required", "recommended", "optional"}
_PLATFORMS = {"windows", "linux", "macos", "unix"}


@dataclass(frozen=True)
class Dependency:
    id: str
    name: str
    description: str
    tier: Tier
    manual: bool = False
    install: dict[str, str] = field(default_factory=dict)
    check: tuple[str, ...] | None = None
    depend_on: tuple[str, ...] = ()
    platform: tuple[str, ...] | None = None


@dataclass(frozen=True)
class Manifest:
    schemaVersion: int
    dependencies: tuple[Dependency, ...]
    env_vars: tuple[str, ...]


@dataclass(frozen=True)
class CheckResult:
    kind: Kind
    id: str
    name: str
    tier: Tier
    status: Status
    blocked_by: tuple[str, ...] = ()


def load_manifest(path: Path) -> Manifest:
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ConfigError(f"manifest not found: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ConfigError(f"invalid JSON in {path}: {exc}") from exc

    if not isinstance(raw, dict):
        raise ConfigError("manifest root must be an object")

    schema_version = raw.get("schemaVersion")
    if schema_version != 1:
        raise ConfigError(f"unsupported schemaVersion: {schema_version!r}")

    deps_raw = raw.get("dependencies")
    if not isinstance(deps_raw, list):
        raise ConfigError("dependencies must be an array")

    seen: set[str] = set()
    deps: list[Dependency] = []
    for index, item in enumerate(deps_raw):
        deps.append(_parse_dependency(index, item, seen))

    env_vars_raw = raw.get("env_vars", [])
    if not isinstance(env_vars_raw, list):
        raise ConfigError("env_vars must be an array")
    env_vars: list[str] = []
    for index, item in enumerate(env_vars_raw):
        if not isinstance(item, str) or not item:
            raise ConfigError(f"env_vars[{index}] must be a non-empty string")
        env_vars.append(item)

    return Manifest(
        schemaVersion=schema_version,
        dependencies=tuple(deps),
        env_vars=tuple(env_vars),
    )


def _parse_dependency(index: int, item: Any, seen: set[str]) -> Dependency:
    if not isinstance(item, dict):
        raise ConfigError(f"dependencies[{index}] must be an object")

    dep_id = _required_string(item, "id", index)
    if dep_id in seen:
        raise ConfigError(f"duplicate dependency id: {dep_id}")
    seen.add(dep_id)

    name = _required_string(item, "name", index)

    description = item.get("description", "")
    if not isinstance(description, str):
        raise ConfigError(f"dependencies[{index}].description must be a string")

    tier = _required_string(item, "tier", index)
    if tier not in _TIERS:
        raise ConfigError(
            f"dependencies[{index}].tier must be 'required', 'recommended', or 'optional'"
        )

    manual = item.get("manual", False)
    if not isinstance(manual, bool):
        raise ConfigError(f"dependencies[{index}].manual must be a boolean")

    install_raw = item.get("install", {})
    if not isinstance(install_raw, dict):
        raise ConfigError(f"dependencies[{index}].install must be an object")
    install: dict[str, str] = {}
    for key, value in install_raw.items():
        if not isinstance(value, str):
            raise ConfigError(f"dependencies[{index}].install.{key} must be a string")
        install[key] = value

    check_raw = item.get("check")
    check: tuple[str, ...] | None
    if check_raw is None:
        check = None
    elif isinstance(check_raw, str):
        check = (check_raw,)
    elif isinstance(check_raw, list):
        check_cmds: list[str] = []
        for c_index, cmd in enumerate(check_raw):
            if not isinstance(cmd, str) or not cmd:
                raise ConfigError(
                    f"dependencies[{index}].check[{c_index}] must be a non-empty string"
                )
            check_cmds.append(cmd)
        check = tuple(check_cmds)
    else:
        raise ConfigError(f"dependencies[{index}].check must be a string or array")

    depend_on_raw = item.get("depend_on", [])
    if not isinstance(depend_on_raw, list):
        raise ConfigError(f"dependencies[{index}].depend_on must be an array")
    depend_on: list[str] = []
    for d_index, dep in enumerate(depend_on_raw):
        if not isinstance(dep, str) or not dep:
            raise ConfigError(
                f"dependencies[{index}].depend_on[{d_index}] must be a non-empty string"
            )
        depend_on.append(dep)

    platform = _parse_platform(item.get("platform"), index)

    return Dependency(
        id=dep_id,
        name=name,
        description=description,
        tier=tier,  # type: ignore[arg-type]
        manual=manual,
        install=install,
        check=check,
        depend_on=tuple(depend_on),
        platform=platform,
    )


def _parse_platform(raw: Any, index: int) -> tuple[str, ...] | None:
    if raw is None:
        return None
    allowed = ", ".join(sorted(_PLATFORMS))
    if isinstance(raw, str):
        if raw not in _PLATFORMS:
            raise ConfigError(f"dependencies[{index}].platform must be one of: {allowed}")
        return (raw,)
    if isinstance(raw, list):
        if not raw:
            raise ConfigError(f"dependencies[{index}].platform must not be empty")
        tokens: list[str] = []
        for p_index, token in enumerate(raw):
            if not isinstance(token, str) or token not in _PLATFORMS:
                raise ConfigError(
                    f"dependencies[{index}].platform[{p_index}] must be one of: {allowed}"
                )
            tokens.append(token)
        return tuple(tokens)
    raise ConfigError(f"dependencies[{index}].platform must be a string or array")


def _required_string(item: dict[str, Any], key: str, index: int) -> str:
    value = item.get(key)
    if not isinstance(value, str) or not value:
        raise ConfigError(f"dependencies[{index}].{key} must be a non-empty string")
    return value


def _platform_tokens() -> set[str]:
    if sys.platform == "win32":
        return {"windows"}
    if sys.platform == "linux":
        return {"linux", "unix"}
    if sys.platform == "darwin":
        return {"macos", "unix"}
    return set()


def _applies_here(platform: tuple[str, ...] | None, here: set[str]) -> bool:
    return platform is None or bool(set(platform) & here)


def verify(manifest: Manifest) -> list[CheckResult]:
    here = _platform_tokens()
    results: dict[str, CheckResult] = {}
    for dep in manifest.dependencies:
        if not _applies_here(dep.platform, here):
            status: Status = "skip"
        else:
            status = _base_status(dep)
        results[dep.id] = CheckResult(
            kind="tool",
            id=dep.id,
            name=dep.name,
            tier=dep.tier,
            status=status,
        )

    _propagate_blocked(manifest, results)

    ordered: list[CheckResult] = [results[dep.id] for dep in manifest.dependencies]
    for name in manifest.env_vars:
        ordered.append(
            CheckResult(
                kind="env_var",
                id=name,
                name=name,
                tier="required",
                status="ok" if os.environ.get(name, "").strip() else "missing",
            )
        )
    return ordered


def _base_status(dep: Dependency) -> Status:
    if dep.check is None:
        return "manual"
    return "ok" if _run_check(dep.check) else "missing"


def _run_check(commands: tuple[str, ...]) -> bool:
    for cmd in commands:
        result = subprocess.run(
            cmd,
            shell=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        if result.returncode == 0:
            return True
    return False


def _propagate_blocked(manifest: Manifest, results: dict[str, CheckResult]) -> None:
    changed = True
    while changed:
        changed = False
        for dep in manifest.dependencies:
            current = results[dep.id]
            if current.status in ("blocked", "skip"):
                continue
            blocking = tuple(
                d
                for d in dep.depend_on
                if d in results and results[d].status in ("missing", "blocked")
            )
            if blocking:
                results[dep.id] = CheckResult(
                    kind="tool",
                    id=dep.id,
                    name=dep.name,
                    tier=dep.tier,
                    status="blocked",
                    blocked_by=blocking,
                )
                changed = True


def exit_code(results: list[CheckResult]) -> int:
    for result in results:
        if result.tier == "required" and result.status in ("missing", "blocked"):
            return 1
    return 0
