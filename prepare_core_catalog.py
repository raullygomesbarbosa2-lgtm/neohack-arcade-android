#!/usr/bin/env python3
"""Download pinned official ARM64 Libretro archives and normalize each to one ELF core."""
from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import struct
import sys
import tempfile
import time
import urllib.request
import zipfile
from pathlib import Path, PurePosixPath

ASSETS = Path("app/src/main/assets")
CATALOG_PATH = ASSETS / "core_catalog.json"
BUILD_BASE = "https://buildbot.libretro.com/nightly/android/latest/arm64-v8a/"
MAX_SOURCE_PAYLOAD = 1024 ** 3
EXPECTED_TOTAL = 190
EXPECTED_LIBRETRO = 165
EXPECTED_ENGINE = 25


def fail(message: str) -> None:
    raise SystemExit(message)


def validate_manifest(catalog: dict) -> list[dict]:
    cores = catalog.get("cores")
    if catalog.get("version") != 1 or not isinstance(cores, list) or len(cores) != EXPECTED_TOTAL:
        fail(f"Expected exactly {EXPECTED_TOTAL} entries in version 1 of the catalog.")
    ids = [c.get("id") for c in cores]
    if len(set(ids)) != EXPECTED_TOTAL:
        fail("Catalog IDs must be unique.")
    if sum(c.get("catalogType") == "libretro" for c in cores) != EXPECTED_LIBRETRO:
        fail(f"Expected exactly {EXPECTED_LIBRETRO} Libretro entries.")
    if sum(c.get("catalogType") == "engine-virtual" for c in cores) != EXPECTED_ENGINE:
        fail(f"Expected exactly {EXPECTED_ENGINE} engine/virtual entries.")
    total = 0
    for c in cores:
        ident = c.get("id", "")
        if not re.fullmatch(r"[A-Za-z0-9_-]{1,48}", ident):
            fail(f"Invalid core ID: {ident!r}")
        if c.get("abi") != "arm64-v8a":
            fail(f"Non-ARM64 candidate in catalog: {ident}")
        if not re.fullmatch(r"corepacks/[A-Za-z0-9._-]+\.zip", c.get("coreZip", "")):
            fail(f"Invalid normalized asset path for {ident}.")
        if not re.fullmatch(r"[A-Za-z0-9._-]+\.so", c.get("coreFile", "")) or ".." in c["coreFile"]:
            fail(f"Invalid core member name for {ident}.")
        if not re.fullmatch(r"[a-f0-9]{64}", c.get("sha256", "")):
            fail(f"Invalid core SHA-256 for {ident}.")
        if not re.fullmatch(r"[a-f0-9]{64}", c.get("sourceArchiveSha256", "")):
            fail(f"Invalid source archive SHA-256 for {ident}.")
        if not re.fullmatch(r"[a-f0-9]{64}", c.get("coreInfoSha256", "")):
            fail(f"Invalid libretro-core-info metadata SHA-256 for {ident}.")
        if not c.get("name") or not c.get("system") or not c.get("license") or not c.get("coreInfoUrl"):
            fail(f"Missing source/license metadata for {ident}.")
        filename = c.get("sourceArchive", "")
        if not re.fullmatch(r"[A-Za-z0-9._-]+\.zip", filename):
            fail(f"Invalid source archive filename for {ident}.")
        if c.get("sourceArchiveUrl") != BUILD_BASE + filename:
            fail(f"Source URL is not the official pinned Android ARM64 Buildbot URL for {ident}.")
        if not c.get("sourceMember", "").endswith(".so") or PurePosixPath(c["sourceMember"]).name != c["sourceMember"]:
            fail(f"Unsafe/missing expected archive member for {ident}.")
        size = c.get("sourceArchiveBytes")
        if not isinstance(size, int) or size <= 0:
            fail(f"Missing source ZIP size for {ident}.")
        total += size
        lic = c.get("license", "").lower()
        if any(x in lic for x in ("non-commercial", "noncommercial", "non commercial", "unknown")):
            fail(f"Screened-out license status appeared for {ident}: {c.get('license')}")
    if total >= MAX_SOURCE_PAYLOAD:
        fail(f"Source ZIP payload is {total} bytes; expected less than 1 GiB.")
    if catalog.get("sourceArchivePayloadBytes") != total:
        fail("The catalog's recorded source ZIP payload total does not match its entries.")
    return cores


def elf_arm64_header(header: bytes) -> bool:
    return (len(header) >= 20 and header[:4] == b"\x7fELF" and header[4] == 2
            and header[5] == 1 and struct.unpack_from("<H", header, 18)[0] == 183)


def download(url: str, target: Path, expected_size: int) -> tuple[int, str]:
    request = urllib.request.Request(url, headers={"User-Agent": "Vortix-Pro-core-catalog/1.0"})
    digest = hashlib.sha256()
    total = 0
    with urllib.request.urlopen(request, timeout=180) as response, target.open("wb") as out:
        if response.status != 200:
            raise RuntimeError(f"Buildbot returned HTTP {response.status}")
        declared = response.headers.get("Content-Length")
        if declared is not None and int(declared) != expected_size:
            raise ValueError(f"HTTP Content-Length was {declared}; expected {expected_size} bytes")
        for chunk in iter(lambda: response.read(1024 * 1024), b""):
            total += len(chunk)
            if total > expected_size:
                raise ValueError(f"download exceeded expected size {expected_size}")
            out.write(chunk)
            digest.update(chunk)
    return total, digest.hexdigest()


def download_verified(core: dict, target: Path, attempts: int = 5) -> None:
    """Fetch a pinned archive from scratch and retry incomplete/corrupt transfers."""
    last_error: Exception | None = None
    for attempt in range(1, attempts + 1):
        # Never resume or append: every attempt starts with an empty destination.
        target.unlink(missing_ok=True)
        try:
            size, source_sha = download(
                core["sourceArchiveUrl"], target, core["sourceArchiveBytes"]
            )
            if size != core["sourceArchiveBytes"]:
                raise ValueError(
                    f"expected {core['sourceArchiveBytes']} bytes, received {size}"
                )
            if source_sha != core["sourceArchiveSha256"]:
                raise ValueError("SHA-256 does not match the pinned source archive")
            with zipfile.ZipFile(target) as archive:
                corrupt_member = archive.testzip()
                if corrupt_member is not None:
                    raise zipfile.BadZipFile(
                        f"CRC/integrity check failed for member {corrupt_member!r}"
                    )
            return
        except Exception as error:
            last_error = error
            target.unlink(missing_ok=True)
            if attempt == attempts:
                break
            delay = min(2 ** (attempt - 1), 16)
            print(
                f"Retry {attempt}/{attempts - 1} for {core['id']} after "
                f"{type(error).__name__}: {error}; waiting {delay}s.",
                flush=True,
            )
            time.sleep(delay)
    fail(
        f"Could not download a complete, pinned, valid ZIP for {core['id']} "
        f"after {attempts} clean attempts: {last_error}"
    )


def prepare(cores: list[dict]) -> None:
    pack_dir = ASSETS / "corepacks"
    pack_dir.mkdir(parents=True, exist_ok=True)
    for old in pack_dir.glob("*.zip"):
        old.unlink()
    runner_temp = Path(os.environ.get("RUNNER_TEMP", tempfile.gettempdir()))
    runner_temp.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="vortix-core-", dir=runner_temp) as td:
        tempdir = Path(td)
        for index, core in enumerate(cores, 1):
            ident = core["id"]
            source_zip = tempdir / "source.zip"
            download_verified(core, source_zip)
            try:
                source = zipfile.ZipFile(source_zip)
            except zipfile.BadZipFile as error:
                fail(f"Invalid official source ZIP for {ident}: {error}")
            with source:
                members = [i for i in source.infolist() if not i.is_dir()]
                so_members = [i for i in members if i.filename.lower().endswith(".so")]
                if len(so_members) != 1 or so_members[0].filename != core["sourceMember"]:
                    fail(f"Unexpected source archive member(s) for {ident}: {[i.filename for i in members]}")
                info = so_members[0]
                if PurePosixPath(info.filename).name != core["coreFile"]:
                    fail(f"Catalog coreFile does not match inspected archive member for {ident}.")
                out_path = ASSETS / core["coreZip"]
                out_path.parent.mkdir(parents=True, exist_ok=True)
                tmp_path = out_path.with_suffix(".zip.tmp")
                digest = hashlib.sha256()
                count = 0
                header = b""
                with source.open(info) as input_so, zipfile.ZipFile(
                        tmp_path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=6) as normalized:
                    with normalized.open(core["coreFile"], "w", force_zip64=True) as output_so:
                        while True:
                            chunk = input_so.read(1024 * 1024)
                            if not chunk:
                                break
                            if len(header) < 20:
                                header += chunk[:20 - len(header)]
                            count += len(chunk)
                            digest.update(chunk)
                            output_so.write(chunk)
                if not elf_arm64_header(header):
                    tmp_path.unlink(missing_ok=True)
                    fail(f"{ident} is not a little-endian ARM64 ELF shared object.")
                if digest.hexdigest() != core["sha256"]:
                    tmp_path.unlink(missing_ok=True)
                    fail(f"Core library SHA-256 mismatch for {ident}.")
                if count <= 0 or count != core["coreBytes"]:
                    tmp_path.unlink(missing_ok=True)
                    fail(f"Core library size mismatch for {ident}.")
                with zipfile.ZipFile(tmp_path) as normalized:
                    if normalized.namelist() != [core["coreFile"]]:
                        tmp_path.unlink(missing_ok=True)
                        fail(f"Normalized package for {ident} must contain exactly one .so member.")
                    corrupt_member = normalized.testzip()
                    if corrupt_member is not None:
                        tmp_path.unlink(missing_ok=True)
                        fail(f"Normalized package for {ident} failed ZIP CRC validation at {corrupt_member!r}.")
                tmp_path.replace(out_path)
            source_zip.unlink(missing_ok=True)
            print(f"[{index}/{len(cores)}] verified {ident}: {count} bytes, sha256 {core['sha256']}", flush=True)

    # The checked-in catalog is metadata; only normalized core libraries are put in the APK.
    for path in ASSETS.rglob("*"):
        if path.is_file() and path.suffix.lower() in {
            ".nes", ".sfc", ".smc", ".gba", ".gb", ".gbc", ".rom", ".bin", ".cue",
            ".iso", ".chd", ".bios", ".a26", ".a78", ".zip"
        } and path.parent != pack_dir:
            fail(f"Unexpected game/BIOS/content asset in APK assets: {path}")
    print(f"Prepared exactly {len(cores)} normalized ARM64 core packages; ROMs/BIOS/content absent.")


def main() -> None:
    catalog = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
    cores = validate_manifest(catalog)
    total = sum(c["sourceArchiveBytes"] for c in cores)
    print(f"Catalog check: {len(cores)} unique entries; {total} source ZIP bytes ({total / (1024 ** 2):.2f} MiB).")
    if "--validate-only" not in sys.argv:
        prepare(cores)


if __name__ == "__main__":
    main()
