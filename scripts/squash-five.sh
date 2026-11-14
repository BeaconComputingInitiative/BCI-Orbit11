#!/usr/bin/env bash
# BEACON COMPUTING INITIATIVE | Developer Seal: CJB-DEV-2026
# SHA-256 recorded in root SHA256SUMS.
# Execute if and only if five unpublished linear commits satisfy all safety gates.
set -euo pipefail
deny(){ printf 'HOLD: %s\n' "$*" >&2; exit 1; }
[[ "$#" == 1 && -n "$1" && "$1" != *$'\n'* ]] || deny 'Provide one nonempty logical commit subject'
subject="$1"
git rev-parse --is-inside-work-tree >/dev/null 2>&1 || deny 'Not a Git checkout'
cd "$(git rev-parse --show-toplevel)"
branch="$(git symbolic-ref -q --short HEAD)" || deny 'Detached HEAD'
[[ "$branch" != main && "$branch" != master ]] || deny 'Never rewrite main/master'
[[ -z "$(git status --porcelain)" ]] || deny 'Working tree not clean'
git rev-parse -q --verify 'origin/main^{commit}' >/dev/null || deny 'Fetch origin/main first'
base="$(git rev-parse origin/main)"
head="$(git rev-parse HEAD)"
[[ "$(git merge-base "$base" "$head")" == "$base" ]] || deny 'Diverged from origin/main'
[[ "$(git rev-parse HEAD~5 2>/dev/null || true)" == "$base" ]] || deny 'Exactly five linear commits from base required'
[[ "$(git rev-list --count "$base..$head")" == 5 ]] || deny 'Wrong commit count'
[[ "$(git rev-list --count --merges "$base..$head")" == 0 ]] || deny 'Merge commits forbidden'
while IFS= read -r sha; do
  [[ -z "$(git branch -r --contains "$sha")" ]] || deny 'Commit is already visible in a local remote-tracking branch'
done < <(git rev-list "$base..$head")
printf 'ORBIT11 | CJB-DEV-2026\nFive development commits:\n'
git log --reverse --format='  %h %s' "$base..$head"
printf 'Type SQUASH-5 to confirm local-history rewrite: '
IFS= read -r answer || deny 'No confirmation'
[[ "$answer" == SQUASH-5 ]] || deny 'Operator denied'
slug="$(printf '%s' "$branch" | tr -c 'A-Za-z0-9._-' '-')"
backup="refs/bci-backups/$slug/$(date -u +%Y%m%dT%H%M%SZ)"
git update-ref "$backup" "$head" || deny 'Could not preserve original HEAD'
tree="$(git rev-parse 'HEAD^{tree}')"
new="$( { printf 'ORBIT11: %s\n\nBEACON COMPUTING INITIATIVE\nDeveloper Seal: CJB-DEV-2026\nOriginal five commits:\n' "$subject"; git log --reverse --format='- %h %s' "$base..$head"; } | git commit-tree "$tree" -p "$base" )" || deny 'Commit creation failed'
[[ "$(git rev-parse "$new^{tree}")" == "$tree" ]] || deny 'Content tree mismatch'
git update-ref "refs/heads/$branch" "$new" "$head" || deny 'Concurrent branch update'
printf 'PASS: new commit %s\nBackup ref: %s\n' "$new" "$backup"
git status --short --branch
