#!/usr/bin/env python3
"""Fetch ARMv7 bundles selected by a conservative upstream license-metadata allowlist."""
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
ARMV7_EXCLUDED = {
    "amiberry", "armsx2", "azahar", "cemu", "citra", "citra2018",
    "irogb", "mamemess", "panda3ds", "pcee2", "pcsx2", "ymir",
}
ALLOWED_LICENSES = {
    "MIT", "BSD-3-Clause", "zlib", "Zlib", "Public Domain", "ISC",
    "The Unlicense", "2-clause BSD", "3-clause BSD",
}
EXPECTED_IDS = {
    "ardens", "chailove", "crocods", "dingooemu", "dirksimple", "doukutsu_rs",
    "fixgb", "fixnes", "galaksija", "gw", "handy", "jaxe", "lowresnx", "lutro",
    "mojozork", "native32emu", "nekop2", "nicaiemu", "np2kai", "oberon",
    "openlara", "pd777", "play", "potator", "sameboy", "sameduck", "skyemu",
    "spmp8000emu", "tic80", "uw8", "uzem", "vaporspec", "vircon32", "wasm4",
}
EXPECTED_TOTAL = 34
EXPECTED_LIBRETRO = 23
EXPECTED_ENGINE = 11


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
    ids = [core.get("id") for core in all_cores]
    if len(set(ids)) != 190:
        fail("Source catalog IDs are not unique.")
    actual_excluded = {core["id"] for core in all_cores if core["id"] in ARMV7_EXCLUDED}
    if actual_excluded != ARMV7_EXCLUDED:
        fail(f"ARMv7 exclusions differ from the reviewed list: {sorted(actual_excluded ^ ARMV7_EXCLUDED)}")
    cores = [
        copy.deepcopy(core) for core in all_cores
        if core["id"] not in ARMV7_EXCLUDED and core.get("license") in ALLOWED_LICENSES
    ]
    selected_ids = {core["id"] for core in cores}
    if selected_ids != EXPECTED_IDS:
        fail(f"Selected IDs differ from the reviewed allowlist; missing={sorted(EXPECTED_IDS-selected_ids)}, extra={sorted(selected_ids-EXPECTED_IDS)}")
    if len(cores) != EXPECTED_TOTAL:
        fail(f"Expected {EXPECTED_TOTAL} ARMv7 entries with declared allowlisted licenses, found {len(cores)}.")
    if sum(core.get("catalogType") == "libretro" for core in cores) != EXPECTED_LIBRETRO:
        fail(f"Expected {EXPECTED_LIBRETRO} Libretro entries.")
    if sum(core.get("catalogType") == "engine-virtual" for core in cores) != EXPECTED_ENGINE:
        fail(f"Expected {EXPECTED_ENGINE} engine/virtual entries.")
    for core in cores:
        lic = str(core.get("license", ""))
        lowered = lic.lower()
        if not core.get("name") or not core.get("system") or not core.get("coreInfoUrl"):
            fail(f"Missing source or license metadata for {core.get('id')}")
        if lic not in ALLOWED_LICENSES:
            fail(f"Non-allowlisted license appeared for {core['id']}: {lic}")
        if any(term in lowered for term in ("gpl", "agpl", "lgpl", "mame", "non-commercial", "noncommercial", "non commercial", "unknown", " or ", "/")):
            fail(f"Restricted or ambiguous license appeared for {core['id']}: {lic}")
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
            url = BUILD_BASE + core["sourceArchive"]
            archive_bytes, archive_sha = download(url, source_zip)
            total_payload += archive_bytes
            if total_payload >= MAX_SOURCE_PAYLOAD:
                fail(f"ARMv7 source ZIP payload exceeded 1 GiB at {ident}.")
            try:
                with zipfile.ZipFile(source_zip) as archive:
                    corrupt = archive.testzip()
                    if corrupt is not None:
                        fail(f"ZIP CRC validation failed for {ident}: {corrupt}")
                    files = [member for member in archive.infolist() if not member.is_dir()]
                    so_members = [member for member in files if member.filename.lower().endswith(".so")]
                    if len(so_members) != 1:
                        fail(f"Expected exactly one .so for {ident}; found {[member.filename for member in so_members]}")
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
    print(f"Prepared {len(cores)} ARMv7 core packages ({total_payload} source ZIP bytes); filtered by exact allowlist and permissive upstream license metadata.")


if __name__ == "__main__":
    main()
