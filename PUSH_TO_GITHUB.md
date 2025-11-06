# How to Push TW1X to GitHub

**Repository**: https://github.com/thoracle/tw1x (Private)

---

## Current Status

✅ Git remote configured: `git@github.com:thoracle/tw1x.git`
✅ 3 commits ready to push
⚠️ **Need to complete GitHub setup**

---

## Option 1: Use HTTPS (Easiest)

### Step 1: Update Remote to HTTPS

```bash
cd /Users/retroverse/Desktop/LLM/tw1x
git remote remove origin
git remote add origin https://github.com/thoracle/tw1x.git
```

### Step 2: Create GitHub Repository

1. Go to: https://github.com/new
2. Configure:
   - Owner: **thoracle**
   - Repository name: **tw1x**
   - Description: **TW1X - Unified Twee 1.0 Parser for Interactive Fiction**
   - Visibility: ✅ **Private**
   - ❌ Do NOT initialize with README, .gitignore, or license
3. Click **"Create repository"**

### Step 3: Push to GitHub

```bash
git push -u origin master
```

You'll be prompted for:
- **Username**: `thoracle`
- **Password**: Use a **Personal Access Token** (not your GitHub password)

#### Create Personal Access Token:
1. Go to: https://github.com/settings/tokens
2. Click **"Generate new token (classic)"**
3. Name: `tw1x-push`
4. Scopes: Check ✅ **repo** (all sub-items)
5. Click **"Generate token"**
6. **Copy the token** (you won't see it again)
7. Use this token as the password when pushing

---

## Option 2: Set Up SSH Keys (More Secure)

### Step 1: Generate SSH Key

```bash
ssh-keygen -t ed25519 -C "your_email@example.com"
# Press Enter to accept default location
# Enter passphrase (optional but recommended)
```

### Step 2: Add SSH Key to GitHub

```bash
# Copy the public key
cat ~/.ssh/id_ed25519.pub
# Copy the output
```

Then:
1. Go to: https://github.com/settings/ssh/new
2. Title: `Mac - TW1X Development`
3. Key: Paste the public key you copied
4. Click **"Add SSH key"**

### Step 3: Test SSH Connection

```bash
ssh -T git@github.com
# Should see: "Hi thoracle! You've successfully authenticated..."
```

### Step 4: Create GitHub Repository

1. Go to: https://github.com/new
2. Configure same as Option 1

### Step 5: Push to GitHub

```bash
cd /Users/retroverse/Desktop/LLM/tw1x
git push -u origin master
```

---

## Option 3: Keep Local Only (Current Setup Works!)

**No action needed!** The current setup works perfectly:

**Pros**:
- ✅ Already working with branched and engine
- ✅ No GitHub authentication needed
- ✅ Changes immediately reflected
- ✅ Fast development workflow

**Cons**:
- ❌ No remote backup
- ❌ Can't share with others
- ❌ Single machine only

**To keep local**: Just continue using `-e ../../tw1x` in requirements.txt

---

## After Pushing to GitHub

### Update Projects (Optional)

You can optionally update requirements.txt to use GitHub:

**branched/requirements.txt**:
```txt
# Option A: Keep using local (recommended for development)
-e ../../tw1x

# Option B: Use GitHub (for production/other machines)
-e git+https://github.com/thoracle/tw1x.git#egg=tw1x
```

**Note**: If using GitHub URL, requires authentication for private repos.

---

## Recommended Approach

**For Development** (Current Setup):
- ✅ Keep using local repository: `-e ../../tw1x`
- ✅ Push to GitHub for backup and sharing
- ✅ Best of both worlds!

**Workflow**:
1. Develop locally in `/Users/retroverse/Desktop/LLM/tw1x/`
2. Test with branched and engine (using local install)
3. Commit changes: `git commit -m "..."`
4. Push to GitHub for backup: `git push origin master`
5. Projects continue using local install (fast and easy)

---

## Quick Commands

### Check Status
```bash
cd /Users/retroverse/Desktop/LLM/tw1x
git status
git remote -v
```

### Commit and Push
```bash
git add .
git commit -m "Your changes"
git push origin master
```

### Pull Changes (if working on multiple machines)
```bash
git pull origin master
```

---

## Troubleshooting

### "Permission denied (publickey)"
- Use HTTPS instead of SSH (Option 1)
- Or set up SSH keys (Option 2)

### "Repository not found"
- Create the GitHub repository first at https://github.com/new
- Ensure it's named exactly: `tw1x`
- Ensure owner is: `thoracle`

### "Authentication failed"
- Use Personal Access Token, not password
- Generate token at: https://github.com/settings/tokens
- Token needs `repo` scope for private repos

---

**Current Config**:
- Remote: `git@github.com:thoracle/tw1x.git`
- Commits ready: 3
- Files: 23
- Status: Ready to push (after GitHub setup)
