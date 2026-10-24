# Security policy

## Scope

Dev Journey Agent is a local, CLI-first planning tool. Its repository context
reader is read-only, and its generated artifacts are intended to be redacted
before they are shared.

## Reporting a concern

Please do not open a public issue containing credentials, private repository
content, or an exploitable detail. Use a private GitHub Security Advisory when
that feature is enabled for the repository, or contact the repository owner
through a private GitHub channel.

Include a short description, affected file or behavior, reproduction steps that
do not expose secrets, and the impact you observed.

## Handling credentials

Keep tokens in the local process environment. Do not put them in commands,
source files, checkpoints, telemetry, generated reports, or screenshots. If a
credential is exposed, revoke it immediately and replace it with a scoped,
read-only credential where possible.
