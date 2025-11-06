# TW1X GitHub Repository Setup

**Repository URL**: https://github.com/thoracle/tw1x
**Access**: Private repository

---

## Step 1: Create GitHub Repository

1. Go to: https://github.com/new
2. Configure:
   - **Owner**: thoracle
   - **Repository name**: `tw1x`
   - **Description**: "TW1X - Unified Twee 1.0 Parser for Interactive Fiction"
   - **Visibility**: ✅ **Private**
   - **Initialize**: ❌ Do NOT initialize with README, .gitignore, or license
3. Click **"Create repository"**

---

## Step 2: Push Local Repository

```bash
cd /Users/retroverse/Desktop/LLM/tw1x
git push -u origin master
```

This will push:
- ✅ 2 commits (Initial commit + Documentation)
- ✅ 22 files (6,620 lines of code)
- ✅ All tests, docs, and examples

---

## Step 3: Verify GitHub Repository

Visit: https://github.com/thoracle/tw1x

You should see:
- ✅ README.md with full documentation
- ✅ tw1x/ package directory
- ✅ tests/ directory
- ✅ docs/ directory
- ✅ examples/ directory
- ✅ setup.py, requirements.txt, LICENSE

---

## Step 4: Update Projects to Use GitHub URL

### Option A: Keep Using Local (Recommended for Development)

**No changes needed!** Continue using:

**branched/requirements.txt**:
```txt
-e ../../tw1x
```

**engine/requirements.txt**:
```txt
-e ../../tw1x
```

**Benefits**:
- ✅ Changes immediately reflected
- ✅ No git operations needed
- ✅ Faster development

---

### Option B: Install from GitHub (For Production/Other Machines)

**branched/requirements.txt**:
```txt
# TW1X Parser (for Twee file parsing)
# Installed from private GitHub repository
-e git+ssh://git@github.com/thoracle/tw1x.git#egg=tw1x
```

**engine/requirements.txt**:
```txt
# TW1X Parser (for Twee file parsing)
# Installed from private GitHub repository
-e git+ssh://git@github.com/thoracle/tw1x.git#egg=tw1x
```

**Install command**:
```bash
pip3 install -r requirements.txt
```

**Note**: Requires SSH key configured with GitHub access to private repo.

---

## Repository Information

### URLs

- **GitHub**: https://github.com/thoracle/tw1x
- **SSH Clone**: git@github.com:thoracle/tw1x.git
- **HTTPS Clone**: https://github.com/thoracle/tw1x.git

### Access

- **Visibility**: Private
- **Owner**: thoracle
- **Collaborators**: Add as needed in repo settings

---

## Cloning on Other Machines

```bash
# SSH (recommended for private repos)
git clone git@github.com:thoracle/tw1x.git

# HTTPS (will prompt for credentials)
git clone https://github.com/thoracle/tw1x.git

# Install in editable mode
cd tw1x
pip3 install -e .
```

---

## Making Changes

### Workflow

1. **Make changes** in `/Users/retroverse/Desktop/LLM/tw1x/`
2. **Test locally** with branched and engine
3. **Commit changes**:
   ```bash
   git add .
   git commit -m "Description of changes"
   ```
4. **Push to GitHub**:
   ```bash
   git push origin master
   ```

---

## Version Updates

When releasing a new version:

1. **Update version** in `setup.py` and `tw1x/__init__.py`:
   ```python
   __version__ = "0.4.0"  # Increment version
   ```

2. **Commit and tag**:
   ```bash
   git commit -am "Bump version to 0.4.0"
   git tag -a v0.4.0 -m "Release v0.4.0"
   git push origin master --tags
   ```

3. **View releases** on GitHub:
   - https://github.com/thoracle/tw1x/releases

---

## Sharing with Others

### Give Access to Private Repo

1. Go to: https://github.com/thoracle/tw1x/settings/access
2. Click **"Add people"**
3. Enter GitHub username
4. Select permission level (Read, Write, Admin)

### For Read-Only Access

If others only need to use the package:
- Add them as **Read** collaborators
- They can clone and install but not push changes

---

## Backup Strategy

The GitHub repository serves as:
- ✅ **Remote backup** of tw1x code
- ✅ **Version history** with all commits
- ✅ **Collaboration platform** for team members
- ✅ **Distribution method** for other projects

Local repository at `/Users/retroverse/Desktop/LLM/tw1x/` remains the development location.

---

## Quick Reference

### Push Changes
```bash
cd /Users/retroverse/Desktop/LLM/tw1x
git add .
git commit -m "Your commit message"
git push origin master
```

### Pull Changes (if working on multiple machines)
```bash
git pull origin master
```

### Check Status
```bash
git status
git remote -v
git log --oneline
```

### Repository Stats
- **Commits**: 2 (will grow)
- **Files**: 22
- **Lines**: 6,620
- **Version**: 0.3.0

---

**Setup Date**: 2025-11-05
**Owner**: thoracle
**Repository**: tw1x
