# Private Odoo Fork Setup for Safee

This guide shows how to create a **private fork** of Odoo that stays in sync with public Odoo updates.

## Why Private Fork?

- **Keep your customizations private** (api_rest module, configurations)
- **Still get upstream updates** from public Odoo
- **No public exposure** of your business logic
- **Easy to sync** with `git pull public 19.0`

---

## Quick Setup (Automated)

### Step 1: Create Private Repository on GitHub

1. Go to GitHub: https://github.com/new
2. **Owner:** `safee-analytics` (or your account)
3. **Repository name:** `odoo`
4. **Visibility:** ⭐ **Private** ⭐
5. **Do NOT initialize** (no README, .gitignore, license)
6. Click **Create repository**

Copy the URL: `https://github.com/safee-analytics/odoo.git`

### Step 2: Run Setup Script

```bash
cd ~/github/safee
./scripts/setup-odoo-private.sh https://github.com/safee-analytics/odoo.git
```

**This will:**
1. ✅ Clone bare Odoo from public repo (mirror)
2. ✅ Push to your private repo
3. ✅ Clone your private repo to `safee/odoo/`
4. ✅ Add public Odoo as "public" remote
5. ✅ Checkout 19.0 branch
6. ✅ Copy Docker files (Dockerfile, odoo.conf, entrypoint.sh)
7. ✅ Copy api_rest module
8. ✅ Copy documentation
9. ✅ Commit everything
10. ✅ Push to private repo
11. ✅ Clean up temp files

**Time:** 5-10 minutes (depending on network speed)

### Step 3: Build and Start

```bash
cd ~/github/safee
docker-compose build odoo
docker-compose up odoo
```

### Step 4: Access Odoo

- **Web UI:** http://localhost:8069
- **API Docs:** http://localhost:8069/api/docs
- **Health:** http://localhost:8069/web/health

**Credentials:**
- Database: `odoo`
- Username: `admin`
- Password: `admin`

---

## Manual Setup (Alternative)

If you prefer to do it manually:

### 1. Create Private Repo (same as above)

### 2. Mirror Public Odoo to Private Repo

```bash
cd ~/github/safee

# Clone bare repo
git clone --bare https://github.com/odoo/odoo.git odoo-temp
cd odoo-temp

# Push to your private repo
git push --mirror https://github.com/safee-analytics/odoo.git

# Cleanup
cd ..
rm -rf odoo-temp
```

### 3. Clone Your Private Repo

```bash
cd ~/github/safee
git clone https://github.com/safee-analytics/odoo.git odoo
cd odoo
```

### 4. Add Public Odoo as Upstream

```bash
git remote add public https://github.com/odoo/odoo.git
git remote -v

# Output:
# origin    https://github.com/safee-analytics/odoo.git (fetch)
# origin    https://github.com/safee-analytics/odoo.git (push)
# public    https://github.com/odoo/odoo.git (fetch)
# public    https://github.com/odoo/odoo.git (push)
```

### 5. Checkout 19.0 Branch

```bash
git checkout 19.0
```

### 6. Add Customizations

```bash
# Copy Docker files
cp ~/github/safee/odoo-config-temp/Dockerfile .
cp ~/github/safee/odoo-config-temp/odoo.conf .
cp ~/github/safee/odoo-config-temp/entrypoint.sh .
cp ~/github/safee/odoo-config-temp/.dockerignore .
chmod +x entrypoint.sh

# Copy api_rest module
cp -r ~/odoo/addons/api_rest addons/

# Copy documentation
mkdir -p docs
cp ~/odoo/ACCOUNTING_APP_GUIDE.md docs/
cp ~/odoo/NEXTJS_QUICKSTART.md docs/
cp ~/odoo/API_OVERVIEW.md docs/
cp ~/github/safee/odoo-config-temp/SETUP.md .
```

### 7. Commit and Push

```bash
git add .
git commit -m "[ADD] Safee customizations: Docker + api_rest module"
git push origin 19.0
```

---

## Keeping Up to Date with Public Odoo

### Pull Latest Changes from Public Odoo

```bash
cd ~/github/safee/odoo

# Fetch and merge from public Odoo
git pull public 19.0

# This creates a merge commit with upstream changes
# Resolve any conflicts if they occur

# Push to your private repo
git push origin 19.0
```

### Update Docker Image

```bash
cd ~/github/safee
docker-compose build odoo
docker-compose restart odoo
```

---

## Git Remote Structure

```
Your Local Clone (~/github/safee/odoo)
│
├─ origin (private) ────────> https://github.com/safee-analytics/odoo.git
│                              ├─ Your customizations
│                              ├─ api_rest module
│                              ├─ Docker files
│                              └─ Odoo source code
│
└─ public (upstream) ───────> https://github.com/odoo/odoo.git
                               └─ Official Odoo releases
```

**Normal workflow:**
```bash
# Make changes
vim addons/api_rest/controllers/api_controller.py
git add .
git commit -m "Improved API"
git push origin 19.0

# Pull Odoo updates
git pull public 19.0
git push origin 19.0
```

---

## Advantages

✅ **Private:** Your code is not publicly visible
✅ **Synced:** Easy to pull upstream Odoo updates
✅ **Safe:** Your customizations are preserved during updates
✅ **Isolated:** Changes don't affect public Odoo
✅ **Trackable:** Full git history of your changes
✅ **Collaborative:** Team can access via GitHub permissions

---

## Common Operations

### View Remotes

```bash
git remote -v
```

### Check Current Branch

```bash
git branch
```

### See What's Different from Public Odoo

```bash
git log public/19.0..HEAD
```

### Create Feature Branch

```bash
git checkout -b feature/new-api-endpoint
# make changes
git commit -m "Add new endpoint"
git push origin feature/new-api-endpoint
```

### Merge Feature Branch

```bash
git checkout 19.0
git merge feature/new-api-endpoint
git push origin 19.0
```

---

## Troubleshooting

### Merge Conflicts When Pulling from Public

```bash
git pull public 19.0
# CONFLICT in some file

# Fix conflicts manually
vim conflicted_file.py

# Mark as resolved
git add conflicted_file.py
git commit
git push origin 19.0
```

### Reset to Public Odoo State (Dangerous!)

```bash
# This removes ALL your customizations!
git fetch public
git reset --hard public/19.0
git push --force origin 19.0
```

### See Your Custom Changes

```bash
# List files you've modified
git diff public/19.0 --name-only

# Show diff of your changes
git diff public/19.0
```

---

## Security Notes

- ✅ Repository is **private** - only team members can access
- ✅ GitHub permissions control who can read/write
- ✅ api_rest module code is protected
- ✅ Configuration secrets should use `.env` (not committed)
- ⚠️ Never commit passwords or API keys
- ⚠️ Use GitHub Secrets for CI/CD credentials

---

## Next Steps

1. ✅ Complete the setup (automated or manual)
2. ✅ Build and start Odoo: `docker-compose up odoo`
3. ✅ Test the API: http://localhost:8069/api/docs
4. ✅ Build Next.js frontend (see guides in docs/)
5. ✅ Set up CI/CD pipeline (optional)
6. ✅ Configure production deployment

---

## Resources

- **This Guide:** Understanding private fork
- **SETUP.md:** Complete Odoo setup and usage
- **SAFEE_README.md:** Quick start for developers
- **ODOO_INTEGRATION.md:** Architecture overview
- **GitHub Docs:** [Duplicating a repository](https://docs.github.com/en/repositories/creating-and-managing-repositories/duplicating-a-repository)

---

**Ready?** Run the script:

```bash
cd ~/github/safee
./scripts/setup-odoo-private.sh https://github.com/safee-analytics/odoo.git
```
