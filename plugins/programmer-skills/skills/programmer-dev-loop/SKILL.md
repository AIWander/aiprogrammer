---
name: programmer-dev-loop
description: The edit-build-test-commit loop with Programmer-Wander tools, including Rust/cargo specifics on Windows, locked-binary swaps, and long builds in persistent sessions. Surface when editing source code, building a project, running tests, committing, or releasing using programmer tools.
---

# Programmer Dev Loop

## The core loop

```
read_file (grep first if large)
  -> edit_block            (surgical, atomic; one logical change per call)
  -> cmd "cargo build"    (or the project's build command)
  -> cmd "cargo test"
  -> cmd "git diff"       (review what actually changed)
  -> cmd "git commit"
```

Git left the dev shell in the v2.0 rebuild. Drive it through `cmd`, or use the
`gitplus` add-on server's `git_*` tools when that server is registered.

## Rust on Windows - the rules that bite

- **cargo goes through `cmd`, never `powershell`.** PowerShell pipes corrupt
  cargo output and mangle ANSI on multi-line commits.
- **Locked binary:** a running .exe cannot be overwritten. Build with an
  alternate target dir and swap by rename:
  ```
  cmd "set CARGO_TARGET_DIR=C:\\temp\\alt-target&& cargo build --release"
  move_file  old exe -> old.exe.bak
  copy_file  new exe -> destination
  ```
  Never kill the running process to free the lock if it is an MCP server the
  host is using - stage the swap and let the user restart at their boundary.
- **Cross-arch:** on ARM64 hosts build x64 with
  `cargo build --release --target x86_64-pc-windows-msvc`.

## Long builds

Blocking `cmd` calls time out on big builds. Use a state-carrying session:

```
shell_session  action=create
shell_session  action=run     "cargo build --release 2>&1 | tail -20"
shell_session  action=read     (poll until done)
shell_session  action=history  (audit what ran)
shell_session  action=destroy
```

## Review before commit

`git diff --stat` for the shape, `git diff` for content, then `git commit`
with a message that says why, not just what. Push is a separate decision -
`git push` publishes; confirm intent before pushing to shared branches.

## Clone-modify-push-back

```
git clone -> edit_block (x N) -> git status -> git diff -> git commit -> git push
```

## Scaffolding

`transform_scaffold` for new project skeletons; `transform_sync_dir` to mirror
a template directory into place.
