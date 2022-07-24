# Store

<a href="https://commons.wikimedia.org/wiki/File:Wooden-pallets_stacked_8.jpg"><img src="assets/pallets128.jpg" alt="Image of wooden pallets" align="right" style="width: 128px;" /></a>

Store is a proof-of-concept backup program written to explore concepts which
may not be addressed fully in currently available backup programs. Store should
be considered highly experimental and is not suitable for primary backup
purposes.

The concepts to be tested include:

- Backup and tracking to multiple destinations before reporting a file as
  "store"
- Mandatory use of asymmetric (public key) cryptography
- Distributed peer-to-peer backup with friends and family
- Cloud-first storage design for backup files, taking into account the unique
  characteristics of cloud storage providers
- Optional use of hardware-based security keys like SoloKey or YubiKey
- Offline cold-storage with PAR blocks
- IPFS

Store stands on the shoulders of and is motivated by the many pioneers in the
chunk-based backup space, including borg, duplicacy, hashbackup, restic, and
kopia.

<img src="https://github.com/presto8/store/workflows/Ubuntu%2020.04/badge.svg"> <img src="https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/wiki/presto8/store/python-coverage-comment-action-badge.json">

## Commands

Tentative list of major commands:

* store [paths]: default operation is to backup the paths
* store add [paths]: add or check paths
* store restore [patterns] --to [path]
* store verify [patterns]
* store [list | ls] [patterns]
* store [find | grep] [patterns
* store remote
* store status [patterns]
* store info

## Tech Stack
* Python (pytest, coverage)
* blake2b
* AES-GCM-256 (maybe: AES-SIV)
* MessagePack
* GPG/PGP (maybe: age)
