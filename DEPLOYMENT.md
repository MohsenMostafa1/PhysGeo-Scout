# Deployment Guide — Step by Step

## Option A: Hugging Face Spaces (Recommended — Free, Runs Your Agent as a Web App)

### Step 1: Create a Hugging Face Account
1. Go to https://huggingface.co/join
2. Sign up (free) with GitHub, Google, or email
3. Verify your email

### Step 2: Create a New Space
1. Go to https://huggingface.co/new-space
2. Fill in:
   - **Owner:** your username (e.g. `mohsenmostafa`)
   - **Space name:** `ai-research-agent` (or any name you like)
   - **Visibility:** Public (free) or Private
   - **SDK:** Gradio
   - **Hardware:** CPU basic (free)
3. Click **Create Space**

### Step 3: Upload Files to Your Space

Only upload these 3 files (flat in root, no folders):

```
your-space/
├── app.py
├── hf_tools.py
├── requirements.txt
└── README.md
```

#### Via Git (Recommended):
```bash
cd hf_space
git init
git add app.py hf_tools.py requirements.txt README.md
git commit -m "Deploy AI Research Agent"
git branch -M main
git remote add origin https://huggingface.co/spaces/YOUR_USERNAME/ai-research-agent
git push -u origin main
```
When prompted: Username = your HF username, Password = your HF access token (create at https://huggingface.co/settings/tokens)

#### Via Web Upload:
1. Go to your space URL
2. Click **Files** tab → **Upload files**
3. Upload `app.py`, `hf_tools.py`, `requirements.txt`
4. Replace the existing `README.md`

### Step 4: Wait for Build (~2-3 minutes)
Your app goes live at: `https://YOUR_USERNAME-ai-research-agent.hf.space`

### Step 5: (Optional) Add Secrets for Extra APIs
Go to your Space → Settings → Repository secrets → add `GITHUB_TOKEN` and `SEMANTIC_SCHOLAR_API_KEY`

---

## Option B: GitHub (Code Hosting + Scheduled Runs)

### Step 1: Create GitHub Repository
```bash
cd mohsen_research_agent
git init && git add . && git commit -m "v1.0"
git remote add origin https://github.com/YOUR_USERNAME/ai-research-agent.git
git push -u origin main
```

### Step 2: Configure GitHub Secrets
Repo → Settings → Secrets and variables → Actions → add:
- `OPENAI_API_KEY`
- `REDDIT_CLIENT_ID`, `REDDIT_CLIENT_SECRET`
- `DISCORD_WEBHOOK_URL`
- `SEMANTIC_SCHOLAR_API_KEY`

### Step 3: GitHub Actions Auto-Run
The `.github/workflows/research_agent.yml` runs every 6 hours automatically.
To trigger manually: Actions tab → Run Research Agent → Run workflow

---

## Recommended: Deploy on BOTH

| Platform | Purpose | Why |
|----------|---------|-----|
| **Hugging Face Spaces** | Live web app | Anyone can use it via browser |
| **GitHub** | Code + scheduled runs | Auto-runs every 6h, stores history |