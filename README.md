# Protect

An experimental chunk-based backup program. This is a proof-of-concept
implementation to explore concepts which may not be addressed fully in
currently available backup programs.

The concepts to be tested include:

- Mandatory use of asymmetric (public key) cryptography
- Backup and tracking to multiple destinations before reporting a file as
  "protected"
- Distributed peer-to-peer backup with friends and family

Protect stands on the shoulders of and is motivated by the many pioneers in the
chunk-based backup space, including borg, duplicacy, hashbackup, restic, and
kopia.
