# Security Policy

## Reporting

Please use GitHub's private vulnerability reporting feature for this repository when available. Do not open a public issue containing a secret, exploit details, personal information, or a live provider credential. If private reporting is unavailable, open a minimal public issue asking the maintainer to establish a private channel, without including sensitive details.

If a credential is exposed, revoke or rotate it immediately. Removing it from a file or Git history does not make it safe.

## Scope and expectations

This is a legacy/reference project, not a production service. The offline core and current default branch are the supported security-review scope. Optional provider examples may require upstream API updates.

Safe defaults include loopback API binding, disabled publishing, environment-only provider secrets, validated identifiers, parameterized SQL, ignored generated content, and offline CI. Do not process untrusted media or expose the API to a network without an independent security review.
