#!/usr/bin/env bash
# Backup entire /home/z/my-project workspace to GitHub (ansaribilal14/workspace-backup)
# Token NEVER committed - only used via env var for push URL.
set -e
export GIT_TERMINAL_PROMPT=0
TOKEN="${GITHUB_TOKEN:?GITHUB_TOKEN env required}"
BASE=/home/z/my-project
BACKUP_DIR=/home/z/my-project/.backup-git
REPO=Bilal140202/workspace-backup

api() { curl -s -m 45 --retry 2 -H "Authorization: token $TOKEN" -H "Accept: application/vnd.github+json" "$@"; }

# 1) ensure repo exists
echo "[1] ensuring repo $REPO exists..."
code=$(api -o /dev/null -w "%{http_code}" https://api.github.com/repos/$REPO)
if [ "$code" = "404" ]; then
  api -X POST https://api.github.com/user/repos -d '{"name":"workspace-backup","description":"Full workspace backup: mega-shot engine, studio videos, scripts, docs, worklogs","private":false}' > /dev/null
  echo "  created."
else
  echo "  exists (http $code)."
fi

# 2) init clean git dir (separate from sandbox .git)
echo "[2] preparing git dir..."
mkdir -p "$BACKUP_DIR"
export GIT_DIR="$BACKUP_DIR" GIT_WORK_TREE="$BASE"
git init -q -b main 2>/dev/null || git init -q
git config user.name "ansaribilal14"
git config user.email "ansaribilal14@users.noreply.github.com"
git config core.autocrlf false
git config http.postBuffer 524288000

# stash nested .git so mega-shot is committed as plain files
if [ -d "$BASE/mega-shot/.git" ]; then rm -rf /tmp/megashot-git-stash; mv "$BASE/mega-shot/.git" /tmp/megashot-git-stash; fi
trap '[ -d /tmp/megashot-git-stash ] && mv /tmp/megashot-git-stash "$BASE/mega-shot/.git"' EXIT

# 3) excludes: only true junk/intermediates (GitHub hard-limits >100MB files)
mkdir -p "$BACKUP_DIR/info"
cat > "$BACKUP_DIR/info/exclude" <<'EOF'
__pycache__/
*.pyc
.git/
.backup-git/
node_modules/
build/layers/
build/v11_frames/
EOF
echo "[3] checking for >100MB files..."
find "$BASE" -path "$BACKUP_DIR" -prune -o -type f -size +99M -print | head -20 > /tmp/bigfiles.txt
wc -l < /tmp/bigfiles.txt | xargs echo "  files >99M:"

# 4) add + commit
echo "[4] staging all files..."
git add -A
git commit -q -m "workspace backup $(date -u +%Y-%m-%dT%H:%M:%SZ): full snapshot incl mega-shot, studio, scripts, docs" --allow-empty
echo "  objects staged: $(git ls-files | wc -l)"

# 5) push
echo "[5] pushing to GitHub..."
if git ls-remote https://Bilal140202:$TOKEN@github.com/$REPO.git refs/heads/main > /dev/null 2>&1; then
  git push -q -f https://Bilal140202:$TOKEN@github.com/$REPO.git main:main
else
  git push -q -u https://Bilal140202:$TOKEN@github.com/$REPO.git main:main
fi
echo "DONE backup push -> https://github.com/$REPO"
