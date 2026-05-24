from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path
import shutil
import subprocess
import sys


@dataclass(frozen=True)
class LinkInfo:
    kind: str
    target: Path | None = None


@dataclass(frozen=True)
class LinkResult:
    kind: str
    message: str


class PlatformOps:
    def create_link(self, source: Path, target: Path) -> LinkResult:
        raise NotImplementedError

    def inspect_link(self, path: Path) -> LinkInfo:
        if path.is_symlink():
            return LinkInfo("symlink", normalize_path(Path(os.readlink(path))))
        if is_junction(path):
            return LinkInfo("junction", normalize_path(Path(os.readlink(path))))
        if not path.exists():
            return LinkInfo("missing")
        if path.is_dir():
            return LinkInfo("directory")
        if path.is_file():
            return LinkInfo("file")
        return LinkInfo("other")


class PosixOps(PlatformOps):
    def create_link(self, source: Path, target: Path) -> LinkResult:
        target.symlink_to(source, target_is_directory=source.is_dir())
        return LinkResult("symlink", "created symlink")


class WindowsOps(PlatformOps):
    def create_link(self, source: Path, target: Path) -> LinkResult:
        try:
            target.symlink_to(source, target_is_directory=source.is_dir())
            return LinkResult("symlink", "created symlink")
        except OSError as symlink_error:
            if not source.is_dir():
                raise symlink_error
            self._create_junction(source, target)
            return LinkResult("junction", "created junction")

    def _create_junction(self, source: Path, target: Path) -> None:
        cmd = ["cmd.exe", "/c", "mklink", "/J", str(target), str(source)]
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)
        if result.returncode != 0:
            stderr = result.stderr.strip() or result.stdout.strip()
            raise OSError(f"failed to create junction: {stderr}")


def get_platform_ops() -> PlatformOps:
    if sys.platform == "win32":
        return WindowsOps()
    return PosixOps()


def is_junction(path: Path) -> bool:
    checker = getattr(os.path, "isjunction", None)
    if checker is None:
        return False
    return bool(checker(path))


def normalize_path(path: Path) -> Path:
    text = str(path)
    if text.startswith("\\\\?\\"):
        text = text[4:]
    return Path(text).resolve(strict=False)


def remove_path(path: Path) -> None:
    if path.is_symlink() or is_junction(path):
        if path.is_dir():
            path.rmdir()
        else:
            path.unlink()
    elif path.is_dir():
        shutil.rmtree(path)
    else:
        path.unlink()
