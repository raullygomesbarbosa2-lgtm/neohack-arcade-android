# ARM64 core-catalog technical POC: source and license notes

This is a technical catalog/build experiment, not legal clearance, a release approval, or a claim that every module may be commercially redistributed. The catalog contains 165 Libretro entries and 25 engine/virtual-platform entries. Every catalog row records the official Android ARM64 Buildbot ZIP URL and SHA-256, the normalized `.so` member and SHA-256, the `libretro-core-info` metadata file/URL, and the license string copied from that metadata. The build checks that each downloaded archive yields one little-endian ARM64 ELF `.so` and packages no ROMs, games, BIOS files, or other core-archive members.

## Important Opera license conflict

Opera (`opera`, 3DO) is included as the explicitly requested technical-POC candidate. The current `libretro-core-info` record (`opera_libretro.info`) says `LGPL/Non-commercial`. The FreeBSD ports record for `games/libretro-opera` says `GPLv2` ([FreshPorts record](https://www.freshports.org/games/libretro-opera/)); the upstream source repository is [libretro/opera-libretro](https://github.com/libretro/opera-libretro). These statements conflict; the catalog preserves the upstream metadata verbatim and records the FreeBSD GPLv2 statement separately rather than treating the conflict as settled. Do not regard Opera as approved for commercial redistribution until the rights holder/source licensing is reconciled.

## GPLv2 notices and source obligations

`GPL-2.0.txt` is included in the repository and copied into the built APK's license assets. In particular, Opera's GPLv2 record requires preserving the applicable license and notices and meeting the GPLv2 requirements for the exact distributed binary. Before distributing a binary, provide the complete corresponding source for that binary (or another source offer that actually satisfies GPLv2), keep the source available for the required period, and review whether distributing it with the app creates additional copyleft obligations. The catalog pins each ARM64 Buildbot source archive by URL, byte count, and SHA-256, and each extracted library by SHA-256, but a binary archive/checksum alone is not corresponding source code. The exact source revision/configuration and source offer have not been legally verified here.

Other modules have their own license terms as listed by `libretro-core-info`; their metadata URLs are in `app/src/main/assets/core_catalog.json`. Include and comply with the applicable license/notice and source obligations for every selected module before redistribution. This POC does not resolve third-party rights in game data or other content; none is packaged.

## Scope

This is a 190-entry intermediate POC, not the planned final 200-module catalog. The ten remaining planned custom modules still require separate implementation and review. No ROMs, games, BIOS, Pix key, or Pix email/key are included.
