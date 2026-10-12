# ARM64 core-catalog technical POC: source and license notes

This is a technical catalog/build experiment, not legal clearance, a release approval, or a claim that every module may be commercially redistributed. The catalog contains 165 Libretro entries and 25 engine/virtual-platform entries. Each catalog row records its official Android ARM64 Buildbot ZIP URL and SHA-256, normalized `.so` member and SHA-256, upstream metadata file/URL/hash, and license. The build verifies that each archive contains exactly one little-endian ARM64 ELF `.so`; it packages no ROMs, games, BIOS files, or unrelated archive members.

## Opera excluded; Rust-DOS replaces the catalog slot

The unresolved Opera licensing conflict has not been resolved. Opera and its core binary are excluded from this POC; the catalog does not retain or distribute that core. The same catalog slot is replaced by the official Rust-DOS Libretro core, preserving 190 unique entries.

## Rust-DOS attribution, source and GPL obligations

- Project/source: [dividebysandwich/rust-dos](https://github.com/dividebysandwich/rust-dos), with its Libretro wrapper under `libretro/`; upstream author attribution is `dividebysandwich`.
- Reviewed source revision: `7848bfdde026a795f068dbc5f98849cbd24c8770` (the upstream `main` tree observed during this change). This is a source reference, not proof that the Buildbot binary was compiled from that exact revision.
- Upstream Libretro metadata: [`libretro/rust_dos_libretro.info`](https://github.com/dividebysandwich/rust-dos/blob/main/libretro/rust_dos_libretro.info); it identifies version 1.7.0, license `GPLv2+`, `supports_no_game=true`, `firmware_count=0`, and `is_experimental=true`.
- Cargo manifest: [`libretro/Cargo.toml`](https://github.com/dividebysandwich/rust-dos/blob/main/libretro/Cargo.toml) declares `GPL-2.0-or-later` and `rust_dos_libretro` as a `cdylib`.
- Binary source archive: the official Android ARM64 Buildbot URL and exact archive/core SHA-256 values are pinned in `app/src/main/assets/core_catalog.json`. The ZIP was verified to contain exactly one member, `rust_dos_libretro_android.so`, an AArch64 little-endian ELF shared object.

The full upstream GPL-2.0 license is preserved as `RUST-DOS-LICENSE.txt` and copied into the APK's license assets. If distributing this binary, retain applicable copyright/license notices and meet GPLv2-or-later obligations for the exact distributed binary, including complete corresponding source, build scripts/instructions, and the source-offer/availability terms applicable under the license. A pinned binary ZIP and its checksums are not corresponding source. The exact Buildbot build revision/configuration and corresponding source have not been verified, and potential GPL linking/copyleft implications for the app have not been cleared. Thus Rust-DOS is a technical POC candidate only, not commercial approval; obtain legal review and prepare exact corresponding source before redistribution.

Rust-DOS is marked experimental upstream. The core reports no required firmware and can start without content, but this app does not bundle DOS programs, games, or disk images: users choose and supply their own content. No ROM, game, BIOS or user content is included in the APK.

## Other catalog license notices and scope

`GPL-2.0.txt` and `RUST-DOS-LICENSE.txt` are in the repository and copied to APK license assets. Other modules have their own license terms as listed in `app/src/main/assets/core_catalog.json`; include and comply with applicable licenses/notices and source obligations for every selected module before redistribution. This POC is not legal clearance for the complete catalog, any commercial distribution, or third-party game data.

This remains a 190-entry intermediate technical POC, not the planned 200-module catalog. Ten further modules and a whole-catalog licensing/source audit remain outstanding. No Pix key, Pix email/key, ROMs, games, BIOS or other user content are included.
