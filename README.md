# Protect

Experimental chunk-based backup program. This is a proof-of-concept
implementation.

The main concept to be tested include:

- Mandatory use of asymmetric (public key) cryptography
- Backup and tracking to multiple destinations before reporting a file as
  "protected"

Protect is motivated by the many pioneers in the chunk-based backup space,
including borg, duplicacy, hashbackup, restic, and kopia.
