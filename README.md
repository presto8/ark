# Ark

<img src="assets/ark.svg" alt="Noah's Ark" align="right" style="width: 200px;" />

_Make yourself an ark of cypress wood; make rooms in it and coat it with
pitch inside and out. You are to bring into the ark two of all living
creatures, male and female, to keep them alive with you. Two of every kind
of bird, of every kind of animal and of every kind of creature that moves
along the ground will come to you to be kept alive._

An experimental chunk-based backup program. Ark is a proof-of-concept
implementation to explore concepts which may not be addressed fully in
currently available backup programs.

The concepts to be tested include:

- Backup and tracking to multiple destinations before reporting a file as
  "protected"
- Mandatory use of asymmetric (public key) cryptography
- Distributed peer-to-peer backup with friends and family
- Cloud-first storage design for backup files, taking into account the unique
  characteristics of cloud storage providers
- Optional use of hardware-based security keys like SoloKey or YubiKey

Ark stands on the shoulders of and is motivated by the many pioneers in the
chunk-based backup space, including borg, duplicacy, hashbackup, restic, and
kopia.

## Commands

Tentative list of major commands:

* ark backup
* ark restore
* ark verify
* ark list|ls
* ark find
* ark remote
* ark status

## Tech Stack
* Python (pytest, coverage)
* blake2b
* AES-GCM-256 (maybe: AES-SIV)
* MessagePack
* GPG/PGP (maybe: age)
