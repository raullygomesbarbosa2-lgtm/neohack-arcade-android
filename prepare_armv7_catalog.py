#!/usr/bin/env python3
"""Fetch official ARMv7 Libretro bundles, verify ELF32/ARM, and normalize 178 cores."""
from __future__ import annotations

import copy
import hashlib
import json
import os
import re
import struct
import tempfile
import time
import urllib.request
import zipfile
from pathlib import Path, PurePosixPath

ASSETS = Path("app/src/main/assets")
CATALOG_PATH = ASSETS / "core_catalog.json"
BUILD_BASE = "https://buildbot.libretro.com/nightly/android/latest/armeabi-v7a/"
MAX_SOURCE_PAYLOAD = 1024 ** 3
EXCLUDED = {
    "amiberry", "armsx2", "azahar", "cemu", "citra", "citra2018",
    "irogb", "mamemess", "panda3ds", "pcee2", "pcsx2", "ymir",
}
EXPECTED_TOTAL = 178
EXPECTED_LIBRETRO = 153
EXPECTED_ENGINE = 25


def fail(message: str) -> None:
    raise SystemExit(message)


def armv7_elf(header: bytes) -> bool:
    return (
        len(header) >= 20 and header[:4] == b"\x7fELF"
        and header[4] == 1 and header[5] == 1
        and struct.unpack_from("<H", header, 18)[0] == 40
    )


def download(url: str, target: Path, attempts: int = 4) -> tuple[int, str]:
    last_error: Exception | None = None
    for attempt in range(1, attempts + 1):
        target.unlink(missing_ok=True)
        digest = hashlib.sha256()
        total = 0
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Vortix-Pro-ARMv7-catalog/1.0"})
            with urllib.request.urlopen(req, timeout=180) as response, target.open("wb") as out:
                if response.status != 200:
                    raise RuntimeError(f"Buildbot returned HTTP {response.status}")
                declared = response.headers.get("Content-Length")
                for chunk in iter(lambda: response.read(1024 * 1024), b""):
                    total += len(chunk)
                    if total > MAX_SOURCE_PAYLOAD:
                        raise ValueError("single source archive exceeded 1 GiB")
                    out.write(chunk)
                    digest.update(chunk)
                if declared is not None and int(declared) != total:
                    raise ValueError(f"HTTP Content-Length was {declared}; received {total}")
            if total <= 0:
                raise ValueError("empty source archive")
            return total, digest.hexdigest()
        except Exception as error:
            last_error = error
            target.unlink(missing_ok=True)
            if attempt == attempts:
                break
            delay = min(2 ** (attempt - 1), 8)
            print(f"Retry {attempt}/{attempts - 1} after {type(error).__name__}: {error}; waiting {delay}s", flush=True)
            time.sleep(delay)
    fail(f"Could not download {url} after {attempts} attempts: {last_error}")
    raise AssertionError("unreachable")


def main() -> None:
    catalog = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
    all_cores = catalog.get("cores", [])
    if catalog.get("version") != 1 or len(all_cores) != 190:
        fail("Expected the checked-in version-1 190-entry source catalog.")
    ids = [c.get("id") for c in all_cores]
    if len(set(ids)) != 190:
        fail("Source catalog IDs are not unique.")
    actual_excluded = {c["id"] for c in all_cores if c["id"] in EXCLUDED}
    if actual_excluded != EXCLUDED:
        fail(f"ARMv7 exclusions differ from the reviewed list: {sorted(actual_excluded ^ EXCLUDED)}")
    cores = [copy.deepcopy(c) for c in all_cores if c["id"] not in EXCLUDED]
    if len(cores) != EXPECTED_TOTAL:
        fail(f"Expected {EXPECTED_TOTAL} ARMv7 entries, found {len(cores)}.")
    if sum(c.get("catalogType") == "libretro" for c in cores) != EXPECTED_LIBRETRO:
        fail("Expected 153 Libretro entries in the ARMv7 catalog.")
    if sum(c.get("catalogType") == "engine-virtual" for c in cores) != EXPECTED_ENGINE:
        fail("Expected 25 engine/virtual entries in the ARMv7 catalog.")
    for core in cores:
        license_name = str(core.get("license", "")).lower()
        if not core.get("name") or not core.get("system") or not core.get("coreInfoUrl"):
            fail(f"Missing source metadata for {core.get('id')}")
        if any(x in license_name for x in ("non-commercial", "noncommercial", "non commercial", "unknown")):
            fail(f"Screened-out license appeared for {core['id']}: {core.get('license')}")
        if not re.fullmatch(r"[A-Za-z0-9._-]+\.zip", str(core.get("sourceArchive", ""))):
            fail(f"Unsafe source archive name for {core['id']}")
        if not re.fullmatch(r"corepacks/[A-Za-z0-9._-]+\.zip", str(core.get("coreZip", ""))):
            fail(f"Unsafe normalized package path for {core['id']}")

    pack_dir = ASSETS / "corepacks"
    pack_dir.mkdir(parents=True, exist_ok=True)
    for old in pack_dir.glob("*.zip"):
        old.unlink()
    runner_temp = Path(os.environ.get("RUNNER_TEMP", tempfile.gettempdir()))
    runner_temp.mkdir(parents=True, exist_ok=True)
    total_payload = 0
    with tempfile.TemporaryDirectory(prefix="vortix-armv7-", dir=runner_temp) as temp:
        source_zip = Path(temp) / "source.zip"
        for index, core in enumerate(cores, 1):
            ident = core["id"]
            filename = core["sourceArchive"]
            url = BUILD_BASE + filename
            archive_bytes, archive_sha = download(url, source_zip)
            total_payload += archive_bytes
            if total_payload >= MAX_SOURCE_PAYLOAD:
                fail(f"ARMv7 source ZIP payload exceeded 1 GiB at {ident}.")
            try:
                with zipfile.ZipFile(source_zip) as archive:
                    corrupt = archive.testzip()
                    if corrupt is not None:
                        fail(f"ZIP CRC validation failed for {ident}: {corrupt}")
                    files = [m for m in archive.infolist() if not m.is_dir()]
                    so_members = [m for m in files if m.filename.lower().endswith(".so")]
                    if len(so_members) != 1:
                        fail(f"Expected exactly one .so for {ident}; found {[m.filename for m in so_members]}")
                    info = so_members[0]
                    if PurePosixPath(info.filename).name != core["coreFile"]:
                        fail(f"Unexpected ARMv7 member name for {ident}: {info.filename}")
                    output_path = ASSETS / core["coreZip"]
                    output_path.parent.mkdir(parents=True, exist_ok=True)
                    temp_path = output_path.with_suffix(".zip.tmp")
                    digest = hashlib.sha256()
                    header = bytearray()
                    count = 0
                    with archive.open(info) as src, zipfile.ZipFile(
                        temp_path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=6
                    ) as normalized:
                        with normalized.open(core["coreFile"], "w", force_zip64=True) as dst:
                            while True:
                                chunk = src.read(1024 * 1024)
                                if not chunk:
                                    break
                                if len(header) < 20:
                                    header.extend(chunk[:20 - len(header)])
                                count += len(chunk)
                                digest.update(chunk)
                                dst.write(chunk)
                    if not armv7_elf(bytes(header)):
                        temp_path.unlink(missing_ok=True)
                        fail(f"{ident} is not a little-endian ARMv7 ELF32 shared object.")
                    with zipfile.ZipFile(temp_path) as normalized:
                        if normalized.namelist() != [core["coreFile"]] or normalized.testzip() is not None:
                            temp_path.unlink(missing_ok=True)
                            fail(f"Invalid normalized package for {ident}.")
                    core.update({
                        "abi": "armeabi-v7a",
                        "sourceArchiveUrl": url,
                        "sourceArchiveBytes": archive_bytes,
                        "sourceArchiveSha256": archive_sha,
                        "sourceMember": info.filename,
                        "coreBytes": count,
                        "sha256": digest.hexdigest(),
                    })
                    temp_path.replace(output_path)
            except zipfile.BadZipFile as error:
                fail(f"Invalid official Buildbot ZIP for {ident}: {error}")
            source_zip.unlink(missing_ok=True)
            print(f"[{index}/{len(cores)}] verified ARMv7 {ident}: {count} bytes; source SHA-256 {archive_sha}", flush=True)

    catalog["cores"] = cores
    catalog["sourceArchivePayloadBytes"] = total_payload
    CATALOG_PATH.write_text(json.dumps(catalog, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Prepared {len(cores)} ARMv7 core packages ({total_payload} source ZIP bytes); excluded {len(EXCLUDED)} unavailable cores.")


if __name__ == "__main__":
    main()
