# Week 3 — Git Advanced

Working directory: ~/workspace/aws-learn/phase1/week3/

First, set up your practice repo:
```bash
bash scripts/setup_practice_repo.sh
cd /tmp/git-practice
```

---

## SECTION 1 — Branching Strategies

Study: `reference/branching_strategies.txt`

### 1.1 GitFlow Practice
```bash
cd /tmp/git-practice

# GitFlow: create develop branch from main
git checkout -b develop
git push -u origin develop 2>/dev/null || echo "(no remote — local practice only)"

# Start a feature
git checkout -b feature/user-search develop

# Do some work
echo "search()" >> src/main/java/com/example/UserService.java
git add .
git commit -m "feat(user): add search method stub"

# Finish feature — merge back to develop
git checkout develop
git merge --no-ff feature/user-search -m "feat(user): merge user-search feature"
git branch -d feature/user-search

# Create a release branch
git checkout -b release/1.0.0 develop
echo "version=1.0.0" > version.txt
git add .
git commit -m "chore(release): bump version to 1.0.0"

# Finish release — merge to main AND develop
git checkout main
git merge --no-ff release/1.0.0 -m "chore(release): release 1.0.0"
git tag -a v1.0.0 -m "Release 1.0.0"
git checkout develop
git merge --no-ff release/1.0.0 -m "chore(release): merge release back to develop"
git branch -d release/1.0.0

# Simulate hotfix
git checkout -b hotfix/null-fix main
sed -i 's/return null;/throw new IllegalArgumentException("negative id");/' \
    src/main/java/com/example/UserService.java
git add .
git commit -m "fix(user): throw exception instead of returning null for negative id"
git checkout main
git merge --no-ff hotfix/null-fix -m "fix(user): merge null-fix hotfix"
git checkout develop
git merge --no-ff hotfix/null-fix -m "fix(user): merge hotfix to develop"
git branch -d hotfix/null-fix
```

### 1.2 Trunk-Based Development Practice
```bash
# Main is always deployable. Feature branches live < 2 days.

git checkout main

# Short-lived feature branch
git checkout -b feature/add-caching
echo "// TODO: add Redis cache" >> src/main/java/com/example/UserService.java
git add .
git commit -m "feat(user): add caching placeholder"

# PR simulation: merge quickly back
git checkout main
git merge --squash feature/add-caching      # squash all commits into one
git commit -m "feat(user): add caching (squashed from feature/add-caching)"
git branch -d feature/add-caching

git log --oneline -5
```

**Challenge 1:** Look at `reference/branching_strategies.txt`. Based on the roadmap (CI/CD in Phase 2), which strategy will you use going forward and why?

---

## SECTION 2 — git rebase vs merge

```bash
cd /tmp/git-practice
```

### 2.1 Merge — preserves history
```bash
git checkout -b feature/logging
echo "logger.info('called');" >> src/main/java/com/example/OrderService.java
git add .
git commit -m "feat(order): add logging"

# Merge creates a merge commit
git checkout main
git merge feature/logging

# See the merge commit in log
git log --oneline --graph -8
```

### 2.2 Rebase — linear history (preferred for feature branches)
```bash
git checkout -b feature/metrics
echo "metrics.count++;" >> src/main/java/com/example/OrderService.java
git add .
git commit -m "feat(order): add metrics counter"

# Meanwhile, main got a new commit
git checkout main
echo "# updated" >> README.md
git add .
git commit -m "docs: update README"

# Rebase: replay feature commits on top of updated main
git checkout feature/metrics
git rebase main

# Now merge is a fast-forward (no merge commit, clean history)
git checkout main
git merge feature/metrics

git log --oneline --graph -8
```

**Rule:** 
- `merge` → keeps full history, use for completed feature branches going to main  
- `rebase` → clean linear history, use to update a feature branch with latest main

**Challenge 2:** Create a branch `feature/test-rebase`, add 2 commits on it, add 1 commit on main, then rebase the feature branch onto main.

---

## SECTION 3 — Interactive Rebase

```bash
cd /tmp/git-practice
git checkout -b feature/interactive-practice

# Make some messy commits (like real work)
echo "wip: start" >> src/main/java/com/example/ProductService.java
git add . && git commit -m "wip"

echo "wip: more" >> src/main/java/com/example/ProductService.java
git add . && git commit -m "wip 2"

echo "wip: done" >> src/main/java/com/example/ProductService.java
git add . && git commit -m "add product update"

echo "typo fix" >> src/main/java/com/example/ProductService.java
git add . && git commit -m "typo"

# View the last 4 commits
git log --oneline -4
```

### 3.1 squash — combine commits into one
```bash
# Squash last 4 commits into 1
git rebase -i HEAD~4
# In the editor:
#   pick  abc1234 wip
#   squash def5678 wip 2        ← change 'pick' to 'squash' (or 's')
#   squash ghi9012 add product update
#   squash jkl3456 typo
# Save. Then write the final commit message.
```

### 3.2 fixup — squash but discard the commit message
```bash
# Same as squash but auto-discards the squashed commit messages
git rebase -i HEAD~4
# Use 'f' or 'fixup' instead of 'squash'
```

### 3.3 reorder commits
```bash
# In the interactive rebase editor, just move lines up/down
# Order in the file = order of commits (oldest at top)
```

### 3.4 edit — amend a specific old commit
```bash
git rebase -i HEAD~3
# Change 'pick' to 'edit' on the commit you want to change
# Git pauses there. Make your changes, then:
git add .
git commit --amend
git rebase --continue
```

**Challenge 3:** Make 3 "wip" commits on a new branch, then squash them into one clean conventional commit.

---

## SECTION 4 — git stash, cherry-pick, bisect

### 4.1 git stash — save work without committing
```bash
cd /tmp/git-practice

# You're in the middle of work and need to switch branches
echo "half done" >> src/main/java/com/example/UserService.java

# Stash it
git stash
git stash list                        # see all stashes
git stash show -p                     # see what's in the stash

# Switch branch, do urgent work, come back
git checkout main
git checkout -                        # go back to previous branch

# Restore stash
git stash pop                         # apply + delete stash
# or:
git stash apply stash@{0}            # apply but KEEP stash
git stash drop stash@{0}             # delete a stash
git stash clear                      # delete ALL stashes

# Stash with a name
git stash push -m "half-done user search feature"
git stash list
```

### 4.2 git cherry-pick — apply a specific commit to another branch
```bash
# Get commit hash from feature/payment branch
git log --oneline feature/payment

# Apply just the PaymentService commit to main
COMMIT_HASH=$(git log --oneline feature/payment | head -1 | awk '{print $1}')
git checkout main
git cherry-pick $COMMIT_HASH

# Cherry-pick without committing (stage only)
git cherry-pick --no-commit $COMMIT_HASH

# Cherry-pick a range
git cherry-pick abc123..def456
```

### 4.3 git bisect — binary search for the commit that broke something
```bash
cd /tmp/git-practice

# You know:
#   HEAD = broken (getUser(-1) returns null instead of throwing)
#   First commit = working

FIRST_COMMIT=$(git log --oneline | tail -1 | awk '{print $1}')

git bisect start
git bisect bad HEAD                   # current commit is broken
git bisect good $FIRST_COMMIT         # this commit was fine

# Git will checkout the middle commit
# Test it — does the bug exist?
grep "return null" src/main/java/com/example/UserService.java && \
    git bisect bad || git bisect good

# Keep running 'bisect bad' or 'bisect good' until git finds the culprit
# Git will say: "XXXXXXX is the first bad commit"

# End bisect
git bisect reset

# Automate bisect with a test script
git bisect start
git bisect bad HEAD
git bisect good $FIRST_COMMIT
git bisect run bash -c 'grep -q "return null" src/main/java/com/example/UserService.java && exit 1 || exit 0'
git bisect reset
```

**Challenge 4:** Use `git bisect` to find which commit introduced the `return null` bug in the practice repo.

---

## SECTION 5 — Merge Conflict Resolution

```bash
cd /tmp/git-practice

# The practice repo already has a conflict ready:
# main and feature/payment both modified UserService.java

git checkout main
git merge feature/payment
# You'll see: CONFLICT (content): Merge conflict in UserService.java
```

### 5.1 Understanding conflict markers
```bash
cat src/main/java/com/example/UserService.java
# You'll see:
# <<<<<<< HEAD
#     return "u-" + id;  // your version (main)
# =======
#     return "USER-" + id;  // their version (feature/payment)
# >>>>>>> feature/payment
```

### 5.2 Resolve manually
```bash
# Edit the file — remove conflict markers, keep what you want
nano src/main/java/com/example/UserService.java

# After resolving
git add src/main/java/com/example/UserService.java
git commit -m "feat(payment): merge payment feature, keep uppercase user prefix"

# Abort a merge (go back to before you started)
# git merge --abort
```

### 5.3 Use a merge tool
```bash
# Install vimdiff or meld
sudo apt install -y meld

# Configure git to use meld
git config --global merge.tool meld
git mergetool                         # opens visual merge tool
```

**Challenge 5:** Resolve the merge conflict in the practice repo between `main` and `feature/payment`.

---

## SECTION 6 — git hooks

Study: `hooks/pre-commit` and `hooks/commit-msg`

### 6.1 Install hooks
```bash
cd /tmp/git-practice

# Copy hooks from this repo
cp ~/workspace/aws-learn/phase1/week3/hooks/pre-commit .git/hooks/
cp ~/workspace/aws-learn/phase1/week3/hooks/commit-msg .git/hooks/
chmod +x .git/hooks/pre-commit
chmod +x .git/hooks/commit-msg

# List installed hooks
ls -la .git/hooks/
```

### 6.2 Test pre-commit hook
```bash
# Try committing a System.out.println — should be BLOCKED
cat >> src/main/java/com/example/UserService.java << 'EOF'
    public void debug() { System.out.println("debug"); }
EOF
git add .
git commit -m "test"
# Should show: [pre-commit] FAIL: Found System.out.println...

# Fix it, then commit
sed -i '/System.out.println/d' src/main/java/com/example/UserService.java
git add .
git commit -m "test: clean commit"
```

### 6.3 Test commit-msg hook
```bash
# Bad message — should be BLOCKED
git commit --allow-empty -m "added stuff"
# Should show: [commit-msg] FAIL: does not follow Conventional Commits

# Good message — should PASS
git commit --allow-empty -m "feat(user): add debug utility method"
```

### 6.4 Bypass hooks (emergency only)
```bash
git commit --no-verify -m "emergency: bypass hooks"
# Use sparingly — defeats the purpose of hooks
```

---

## SECTION 7 — GitHub: PRs, Branch Protection, GPG

### 7.1 Branch Protection Rules (do this on GitHub UI)
```
GitHub → your repo → Settings → Branches → Add rule

Recommended rules for main:
  ✅ Require pull request reviews before merging (1 reviewer minimum)
  ✅ Require status checks to pass (CI must pass)
  ✅ Require branches to be up to date before merging
  ✅ Include administrators
  ✅ Restrict who can push to matching branches
```

### 7.2 GPG Signed Commits
Study: `scripts/gpg_setup.sh`
```bash
# Run the setup guide
bash ~/workspace/aws-learn/phase1/week3/scripts/gpg_setup.sh

# After setup, all commits are signed automatically
git log --show-signature -1
git verify-commit HEAD
```

### 7.3 Monorepo vs Polyrepo
```
POLYREPO: one git repo per service
  user-service/     → github.com/myorg/user-service
  order-service/    → github.com/myorg/order-service
  product-service/  → github.com/myorg/product-service

  Pros: independent deployments, clear ownership
  Cons: hard to make cross-service changes, duplicate CI config

MONOREPO: all services in one repo
  myapp/
    services/user-service/
    services/order-service/
    services/product-service/
    shared/common-lib/

  Pros: atomic cross-service changes, shared CI, easier refactoring
  Cons: large repo, need smart CI (only build changed services)

FOR PHASE 1 PROJECT: use polyrepo (one repo, one service)
Later phases use monorepo-style with path-based CI triggers.
```

### 7.4 Git Submodules
```bash
# Add a shared library as a submodule
git submodule add https://github.com/org/shared-lib libs/shared

# Clone a repo that has submodules
git clone --recurse-submodules https://github.com/org/myapp

# Update submodules
git submodule update --init --recursive
git submodule update --remote     # pull latest from submodule remote

# Remove a submodule
git submodule deinit libs/shared
git rm libs/shared
rm -rf .git/modules/libs/shared
```

---

## REAL-WORLD CHALLENGES

### Challenge A — Full GitFlow Cycle
Starting from the practice repo:
1. Create `feature/email-validation` from develop
2. Add an email regex check to UserService
3. Commit with a proper conventional commit message
4. Merge to develop (no-ff)
5. Create `release/1.1.0`, bump version
6. Merge to main and tag `v1.1.0`

### Challenge B — Bisect Automation
Write a one-liner `git bisect run` command that automatically finds which commit made `UserService.getUser(-1)` return null instead of throwing.
```bash
git bisect start && git bisect bad HEAD && \
git bisect good $(git log --oneline | tail -1 | awk '{print $1}') && \
git bisect run bash -c 'grep -q "return null" src/main/java/com/example/UserService.java && exit 1 || exit 0' && \
git bisect reset
```

### Challenge C — Interactive Rebase Cleanup
Look at `git log --oneline` in the practice repo. Squash all "wip" and "typo" style commits into clean conventional commits.

### Challenge D — Hook Installation Script
Write a script that installs both hooks from this repo into any git repository passed as an argument.
```bash
#!/bin/bash
REPO=${1:-.}
cp ~/workspace/aws-learn/phase1/week3/hooks/pre-commit "$REPO/.git/hooks/"
cp ~/workspace/aws-learn/phase1/week3/hooks/commit-msg "$REPO/.git/hooks/"
chmod +x "$REPO/.git/hooks/pre-commit" "$REPO/.git/hooks/commit-msg"
echo "Hooks installed in $REPO"
```

---

## QUICK REFERENCE CARD

| Command | What it does |
|---------|-------------|
| `git checkout -b feature/x develop` | Create feature branch from develop |
| `git merge --no-ff feature/x` | Merge with merge commit (GitFlow) |
| `git rebase main` | Replay commits on top of main |
| `git rebase -i HEAD~3` | Interactive rebase last 3 commits |
| `git stash` | Save dirty working tree |
| `git stash pop` | Restore stash + delete it |
| `git cherry-pick <hash>` | Apply specific commit to current branch |
| `git bisect start/bad/good` | Binary search for broken commit |
| `git bisect run <script>` | Automate bisect |
| `git bisect reset` | End bisect session |
| `git tag -a v1.0.0 -m "msg"` | Create annotated tag |
| `git log --oneline --graph` | Visual branch history |
| `git log --show-signature` | Show GPG signatures |
| `git verify-commit HEAD` | Verify signed commit |
| `git submodule add <url>` | Add submodule |
| `git commit --no-verify` | Bypass hooks (emergency) |

---

## DONE? Checklist

- [ ] I understand GitFlow, Trunk-Based, and GitHub Flow — and when to use each
- [ ] I can create feature/release/hotfix branches following GitFlow
- [ ] I know when to use rebase vs merge and can explain the difference
- [ ] I can use interactive rebase to squash, fixup, and reorder commits
- [ ] I can use git stash to save and restore work in progress
- [ ] I can cherry-pick a specific commit from one branch to another
- [ ] I can use git bisect (manual and automated) to find a bad commit
- [ ] I can resolve merge conflicts manually and with a merge tool
- [ ] I installed pre-commit and commit-msg hooks and tested them
- [ ] I understand conventional commits and can write them consistently
- [ ] I know the difference between monorepo and polyrepo
- [ ] I set up GPG signing for commits

Next: Week 4 — Docker
