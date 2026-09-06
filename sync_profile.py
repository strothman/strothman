"""
Shallot Profile Auto-Synchronizer
=================================
Scans the workspace directory (C:\\Users\\strot\\Antigravity IDE), reconciles
active, published, private, and deleted projects, updates PROJECT_STATE.md and README.md,
and logs modifications to CHANGELOG.md.

Usage:
    python sync_profile.py          # Preview and update markdown files
    python sync_profile.py --push   # Update files, git commit, and push to GitHub
"""

import os
import sys
import subprocess
import datetime
import re

WORKSPACE_ROOT = r"C:\Users\strot\Antigravity IDE"
PROFILE_REPO_DIR = r"C:\Users\strot\Antigravity IDE\strothman"
GITHUB_USER = "strothman"

CATEGORY_MAP = {
    # 1. AI & ComfyUI
    "Shallot-Suite": ("Generative AI & ComfyUI Architecture", "Visual LoRA analyzer, epoch testing battery, and Windows 11 ICO generator."),
    "Shallot-cui-bot": ("Generative AI & ComfyUI Architecture", "Discord bot bridge for autonomous ComfyUI image generation."),
    
    # 2. Audio & Web Synthesizers
    "ShallotWHAM": ("Interactive Audio & Web Synthesizers", "Cyber-styled dual-engine web synthesizer and performance station."),
    "ShallotWHAM-mobile": ("Interactive Audio & Web Synthesizers", "Touch-optimized mobile dual-engine web synthesizer with ribbon controller and expressive performance pads."),
    "ShallotBeats": ("Interactive Audio & Web Synthesizers", "18-kit acoustic drum step sequencer for guitar backing tracks via Web Audio API."),
    "audio-harmonica": ("Interactive Audio & Web Synthesizers", "Virtual instrument polyphony and harmonica synthesis engine."),
    
    # 3. The Shallot Suite (Local-First)
    "Shallot-DECLUTTER": ("The Shallot Suite (Local-First Applications)", "Local-first AI document organizer & PWA for digitizing and structuring physical paperwork, receipts, and medical records."),
    "shallot-declutter": ("The Shallot Suite (Local-First Applications)", "Local-first AI document organizer & PWA for digitizing and structuring physical paperwork, receipts, and medical records."),
    "Shallot-Money": ("The Shallot Suite (Local-First Applications)", "Sleek mobile-first budgeting and expense tracker styled with the signature Shallot Plum theme."),
    "shallot-money": ("The Shallot Suite (Local-First Applications)", "Sleek mobile-first budgeting and expense tracker styled with the signature Shallot Plum theme."),
    "Shallot-Kitchen-Keeper": ("The Shallot Suite (Local-First Applications)", "Smart grocery inventory companion to eliminate food waste."),
    "shallot-kitchen-keeper": ("The Shallot Suite (Local-First Applications)", "Smart grocery inventory companion to eliminate food waste."),
    "ShallotPeel": ("The Shallot Suite (Local-First Applications)", "Telemetry and token usage analytics for AI coding interactions."),
    "Shallot-Media-Archive": ("The Shallot Suite (Local-First Applications)", "Local media indexing, tagging, and asset management."),
    
    # 4. Automation & Utilities
    "Google-Audit": ("Automation & Utilities", "Master Cloud Storage & Photos Migration Suite. Safe zero-download drive indexer, document isolation, duplicate/burst photo cleaner, and Google Photos migration engine with automated recovery manifests."),
    "Book Finder": ("Automation & Utilities", "Renaissance AR-aligned book discovery engine and Google Drive storage manager."),
    "Car Upgrade": ("Automation & Utilities", "Vehicle infotainment firmware stepping-stone update & hardware upgrade reference."),
    "yt-short-bot-garden": ("Automation & Utilities", "Automated end-to-end YouTube Shorts video creation pipeline."),
    "util-exiftool-helper": ("Automation & Utilities", "Batch media metadata processing utility."),
    "DRAIN": ("Automation & Utilities", "Optimization dashboard for subscription AI workflows."),
    "The-Committee": ("Automation & Utilities", "Interactive module-chaining creative engine."),
    "util-movie2vod-CO": ("Automation & Utilities", "Media ingestion and video-on-demand processing pipeline."),
    "utilapp-TokenPal": ("Automation & Utilities", "Discord alert bot monitoring game economy market rates."),
    "utilapp-PLEX Match Maker": ("Automation & Utilities", "Plex media library metadata matching assistant."),
    "utilapp-habits": ("Automation & Utilities", "Local-first personal habit and routine tracker."),
    "utilapp-Misery Detector": ("Automation & Utilities", "Sentiment and mood tracking utility."),

    # 5. Game Dev
    "game-palworld-eggscan": ("Game Development & Companion Tools", "Companion scanner and helper for Palworld."),
    "game-math-survivors-for-ipad": ("Game Development & Companion Tools", "Educational survivor-like action game for tablet."),
    "game-ROBLOX Midnight Menu": ("Game Development & Companion Tools", "Luau UI and custom game scripting module."),
    "game-DDOGS": ("Game Development & Companion Tools", "Experimental web game prototype."),
    "game-NTE": ("Game Development & Companion Tools", "Interactive canvas game prototype."),
}

CATEGORY_ORDER = [
    "🤖 Generative AI & ComfyUI Architecture",
    "🎛️ Interactive Audio & Web Synthesizers",
    "🧅 The Shallot Suite (Local-First Applications)",
    "⚡ Automation & Utilities",
    "🎮 Game Development & Companion Tools",
]

CAT_NORMALIZED = {
    "Generative AI & ComfyUI Architecture": "🤖 Generative AI & ComfyUI Architecture",
    "Interactive Audio & Web Synthesizers": "🎛️ Interactive Audio & Web Synthesizers",
    "The Shallot Suite (Local-First Applications)": "🧅 The Shallot Suite (Local-First Applications)",
    "Automation & Utilities": "⚡ Automation & Utilities",
    "Game Development & Companion Tools": "🎮 Game Development & Companion Tools",
}

# Explicit rich metadata for private repositories explaining program capabilities & privacy rationale
PRIVATE_REPOS_METADATA = {
    "Google-Audit": {
        "title": "Google-Audit: Master Cloud Storage & Photos Migration Suite",
        "category": "⚡ Automation & Utilities",
        "summary": "Master Cloud Storage & Photos Migration Suite. Safe zero-download drive indexer, document isolation, duplicate/burst photo cleaner, and Google Photos migration engine with automated recovery manifests and Discord status monitor.",
        "capabilities": [
            "**Zero-Download Cloud Audit**: Safely indexes and metadata-scans millions of cloud files without local disk exhaustion.",
            "**Document & Project Isolation**: Auto-detects and isolates documents (PDFs, Office files, CAD) away from photos into dedicated archival preservation folders before cleaning.",
            "**Burst & MD5 Deduplication**: Removes exact byte-for-byte duplicate photos and redundant high-speed camera bursts while preserving highest quality originals.",
            "**Multi-Stream Photos Migration**: High-throughput Google Photos streaming engine with configurable bandwidth throttle and multi-worker pools.",
            "**Flight-Recorder Safety Manifests**: 1-click restoration ledger tracking every file movement, allowing instant rollback of trashed files.",
            "**Discord Watchdog**: Background service posting live telemetry, progress bars, throughput metrics, and stall alerts.",
        ],
        "why_private": [
            "**Defense-in-Depth for Cloud Credentials**: While `.gitignore` strictly shields active OAuth tokens and keys, maintaining the repository as private provides a critical second layer of protection against accidental exposure of Google Cloud credentials or Discord bot webhooks.",
            "**Custom Family Infrastructure**: The system references specific household computer names, network paths (`\\\\joandesk\\Cloud\\...`), local drive letters (`W:\\My Drive`), and personal storage layouts designed for our specific family environment.",
            "**Live Family Data Operations**: The tool executes live file movement, deduplication, and Google Photos streaming for irreplaceable family memories spanning decades. Keeping the operations code in a private repository prevents unwanted external forks or unauthorized indexing.",
            "**Tailored Household Rules**: It includes custom bandwidth limiters designed around our home Wi-Fi and Plex media streaming needs rather than generic public software defaults.",
        ],
    }
}

def get_github_token():
    """Retrieve GitHub token using Git Credential Manager or environment."""
    try:
        p = subprocess.Popen(
            ['git', 'credential', 'fill'],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        stdout, _ = p.communicate('protocol=https\nhost=github.com\n\n', timeout=5)
        for line in stdout.splitlines():
            if line.startswith('password='):
                tok = line.split('password=', 1)[1].strip()
                if tok:
                    return tok
    except Exception:
        pass
    return os.environ.get("GITHUB_TOKEN")

def fetch_github_repos():
    """
    Fetch all GitHub repositories owned by GITHUB_USER.
    Returns (public_repos, private_repos) as sets of repository names.
    """
    token = get_github_token()
    headers = {
        'Accept': 'application/vnd.github.v3+json',
        'User-Agent': 'Shallot-Profile-Sync'
    }
    if token:
        headers['Authorization'] = f'Bearer {token}'
    
    public_repos = set()
    private_repos = set()
    
    # 1. Try authenticated /user/repos
    if token:
        try:
            import requests
            r = requests.get('https://api.github.com/user/repos?per_page=100&affiliation=owner', headers=headers, timeout=10)
            if r.status_code == 200:
                for repo in r.json():
                    name = repo.get('name', '')
                    if repo.get('private'):
                        private_repos.add(name)
                    else:
                        public_repos.add(name)
                return public_repos, private_repos
        except Exception as e:
            print(f"Notice: Authenticated query failed ({e}), falling back...")

    # 2. Try unauthenticated /users/{GITHUB_USER}/repos for public repos
    try:
        import requests
        r = requests.get(f'https://api.github.com/users/{GITHUB_USER}/repos?per_page=100', headers=headers, timeout=10)
        if r.status_code == 200:
            for repo in r.json():
                public_repos.add(repo.get('name', ''))
    except Exception:
        pass

    return public_repos, private_repos

def get_repo_visibility(repo_name, public_repos, private_repos, project_path=None):
    """
    Determines if a project is:
      'public'  -> Live public repository on GitHub
      'private' -> Live private repository on GitHub
      'staged'  -> Local project / not published to GitHub
    """
    name_lower = repo_name.lower()
    for pub in public_repos:
        if pub.lower() == name_lower:
            return 'public'
    for priv in private_repos:
        if priv.lower() == name_lower:
            return 'private'
            
    # Check remote url from local project if available
    if project_path and os.path.exists(os.path.join(project_path, ".git")):
        try:
            res = subprocess.run(["git", "-C", project_path, "remote", "get-url", "origin"], capture_output=True, text=True, timeout=3)
            if res.returncode == 0 and res.stdout.strip():
                remote_name = res.stdout.strip().rstrip("/").split("/")[-1].replace(".git", "").lower()
                for pub in public_repos:
                    if pub.lower() == remote_name:
                        return 'public'
                for priv in private_repos:
                    if priv.lower() == remote_name:
                        return 'private'
        except Exception:
            pass

    return 'staged'

def get_existing_local_projects():
    projects = {}
    if not os.path.exists(WORKSPACE_ROOT):
        return projects
    for name in os.listdir(WORKSPACE_ROOT):
        full_path = os.path.join(WORKSPACE_ROOT, name)
        if not os.path.isdir(full_path) or name in [".git", "strothman"]:
            continue
        
        cat, desc = CATEGORY_MAP.get(name, ("Automation & Utilities", "Custom utility project."))
        projects[name] = {
            "name": name,
            "category": CAT_NORMALIZED.get(cat, cat),
            "description": desc,
            "path": full_path,
        }
    return projects

def read_previous_project_state():
    state_file = os.path.join(PROFILE_REPO_DIR, "PROJECT_STATE.md")
    tracked = set()
    published = set()
    if os.path.exists(state_file):
        with open(state_file, "r", encoding="utf-8") as f:
            in_matrix = False
            for line in f:
                if "Active Projects Matrix" in line or "Active Applications Matrix" in line:
                    in_matrix = True
                    continue
                if not in_matrix:
                    continue
                match = re.search(r"^\|\s*.*?\s*\|\s*`([^`]+)`\s*\|\s*([^|]+)\s*\|", line)
                if match:
                    name = match.group(1).strip()
                    status_col = match.group(2).strip()
                    if name and name != "Local Directory":
                        tracked.add(name)
                        if "Published" in status_col or "Private" in status_col:
                            published.add(name)
    return tracked, published

def extract_private_metadata_from_readme(project_path, project_name):
    """
    Extracts 'Why Is This Repository Kept Private?' and capabilities from README.md if present.
    Falls back to PRIVATE_REPOS_METADATA.
    """
    fallback = PRIVATE_REPOS_METADATA.get(project_name, {
        "title": f"{project_name} (Private Internal Utility)",
        "capabilities": ["Internal operational automation and household utilities."],
        "why_private": ["Restricted to protect local credentials, infrastructure paths, and private data workflows."]
    })
    
    readme_path = os.path.join(project_path, "README.md")
    if not os.path.exists(readme_path):
        return fallback

    try:
        with open(readme_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()

        # Extract "Why Is This Repository Kept Private?"
        why_match = re.search(r"##\s*🔒?\s*Why Is This Repository Kept Private\??(.*?)(?=\n##|\Z)", content, re.DOTALL | re.IGNORECASE)
        reasons = []
        if why_match:
            lines = why_match.group(1).strip().splitlines()
            for line in lines:
                m = re.match(r"^\s*(?:\d+\.|\*|-)\s+(.*)", line)
                if m:
                    reasons.append(m.group(1).strip())
        
        if reasons:
            fallback["why_private"] = reasons
    except Exception:
        pass

    return fallback

def generate_project_state(active_projects, public_repos, private_repos):
    today = datetime.date.today().strftime("%Y-%m-%d")
    total = len(active_projects)
    
    visibility_map = {}
    for pname, p in active_projects.items():
        visibility_map[pname] = get_repo_visibility(pname, public_repos, private_repos, p["path"])
        
    pub_count = sum(1 for v in visibility_map.values() if v == 'public')
    priv_count = sum(1 for v in visibility_map.values() if v == 'private')
    loc_count = sum(1 for v in visibility_map.values() if v == 'staged')
    
    out = []
    out.append("# 🧅 Shallot Workspace — Systems State & Ecosystem Matrix\n")
    out.append(f"> **Last Updated**: {today}  ")
    out.append(f"> **Workspace Root**: `C:\\Users\\strot\\Antigravity IDE`  ")
    out.append("> **Status Summary**: Functional tracking matrix for all active tools, utilities, and applications in the Shallot ecosystem.\n")
    out.append("---\n")
    out.append("## 📊 Quick Statistics\n")
    out.append("| Total Applications Tracked | Published (Public) | Published (Private) | Local / Staged |")
    out.append("| :---: | :---: | :---: | :---: |")
    out.append(f"| **{total}** | **{pub_count}** | **{priv_count}** | **{loc_count}** |\n")
    out.append("---\n")
    out.append("## 🗂️ Active Applications Matrix\n")

    for idx, cat_header in enumerate(CATEGORY_ORDER, 1):
        out.append(f"### {idx}. {cat_header}")
        out.append("| Application | Local Directory | GitHub Remote Status | Capability & Function |")
        out.append("| :--- | :--- | :--- | :--- |")
        
        cat_projects = [p for p in active_projects.values() if p["category"] == cat_header]
        # Sort: Public first, then Private, then Staged
        sort_order = {'public': 0, 'private': 1, 'staged': 2}
        for p in sorted(cat_projects, key=lambda x: (sort_order.get(visibility_map[x["name"]], 3), x["name"])):
            pname = p["name"]
            desc = p["description"]
            vis = visibility_map[pname]
            if vis == 'public':
                link = f"**[{pname}](https://github.com/{GITHUB_USER}/{pname})**"
                status = "🟢 **Published**"
            elif vis == 'private':
                link = f"**[{pname}](https://github.com/{GITHUB_USER}/{pname})** 🔒"
                status = "🔒 **Private Repo**"
            else:
                link = f"**{pname}**"
                status = "🟡 *Staged (Local)*"
            out.append(f"| {link} | `{pname}` | {status} | {desc} |")
        out.append("")
    
    out.append("---\n")
    out.append("## 🔒 Private Repositories & Internal Utilities\n")
    out.append("Certain critical systems in the Shallot workspace are published to GitHub under **Private** visibility. These repositories are actively maintained, version-controlled, and deployed in production, but are restricted from public indexing to protect sensitive family infrastructure, credentials, and live data operations.\n")

    private_projs = [p for p in active_projects.values() if visibility_map[p["name"]] == 'private']
    for p in sorted(private_projs, key=lambda x: x["name"]):
        pname = p["name"]
        meta = extract_private_metadata_from_readme(p["path"], pname)
        out.append(f"### 🛡️ {pname} (`{pname}`)")
        out.append(f"* **Remote Status**: 🔒 **Private Repository** ([github.com/{GITHUB_USER}/{pname}](https://github.com/{GITHUB_USER}/{pname}))")
        out.append(f"* **Category**: {p['category']}")
        out.append(f"* **Operational Role**: {p['description']}\n")
        
        out.append("#### ⚙️ Key Capabilities & Architecture")
        for cap in meta.get("capabilities", []):
            out.append(f"- {cap}")
        out.append("")
        
        out.append("#### 🔐 Why This Repository Is Kept Private")
        for idx_r, reason in enumerate(meta.get("why_private", []), 1):
            out.append(f"{idx_r}. {reason}")
        out.append("")

    out.append("---\n")
    out.append("## 🔄 Dynamic Sync Rules")
    out.append("1. **Deletion Policy**: If an application directory is removed from `C:\\Users\\strot\\Antigravity IDE`, running `sync_profile.py` automatically prunes its entry from `README.md` and `PROJECT_STATE.md`.")
    out.append("2. **Publish Policy**: When a local repository is pushed to GitHub, running `sync_profile.py` automatically updates its status to a live repository link (`🟢 Published` for public, `🔒 Private Repo` for private) in `README.md` and `PROJECT_STATE.md`.")
    out.append("3. **Audit Trail**: Every modification, addition, or removal is automatically logged in `CHANGELOG.md`.")
    return "\n".join(out) + "\n"

def clean_table_cell(text):
    """Sanitizes text for safe inclusion inside markdown table cells."""
    return text.replace("|", "\\|").replace("\r\n", " ").replace("\n", " ").strip()

def generate_readme(active_projects, public_repos, private_repos):
    visibility_map = {}
    for pname, p in active_projects.items():
        visibility_map[pname] = get_repo_visibility(pname, public_repos, private_repos, p["path"])

    out = []
    out.append("# 🧅 Shallot Workspace — Systems & Applications Directory\n")
    out.append('<p align="center">')
    out.append('  <img src="shallot_icon.png" width="130" height="130" alt="Shallot Logo" />')
    out.append("</p>\n")
    out.append('<p align="center">')
    out.append("  <em>Vibe-Coded Software • Practical Local-First Tools • Interactive Web Audio • Generative Pipelines</em>")
    out.append("</p>\n")
    out.append('<p align="center">')
    out.append('  <img src="https://img.shields.io/badge/Methodology-Vibe%20Coded%20%26%20AI%20Assisted-8A2BE2?style=flat-square" alt="Methodology" />')
    out.append('  <img src="https://img.shields.io/badge/Architecture-Local--First-2ea44f?style=flat-square" alt="Architecture" />')
    out.append('  <img src="https://img.shields.io/badge/Design%20Goal-Results%20%26%20Utility-orange?style=flat-square" alt="Design Goal" />')
    out.append('  <img src="https://img.shields.io/badge/Ecosystem-Shallot%20Suite-purple?style=flat-square" alt="Shallot Suite" />')
    out.append("</p>\n")
    out.append("---\n")
    out.append("### ⚡ Ecosystem Overview")
    out.append("This catalog indexes functional software, experimental prototypes, and workflow utilities built through **vibe coding and human-AI collaboration**. The focus is placed entirely on **tangible results, usability, and rapid problem-solving** rather than authorship. Each project addresses a concrete need—ranging from browser-based Web Audio DSP synthesizers and autonomous ComfyUI image pipelines, to zero-telemetry local-first record organizers and desktop automation utilities.\n")
    out.append("---\n")
    out.append("### 🛠️ Featured Ecosystems & Projects\n")
    out.append("> [!NOTE]")
    out.append("> **Repository Index**: This directory reflects public open-source tools, private production systems, and local modules in development.")
    out.append("> * 🟢 **Public**: Clickable link to public GitHub repository.")
    out.append("> * 🔒 **Private**: Clickable link to private GitHub repository (authorized access only).")
    out.append("> * 🟡 **Staged**: Local module undergoing active development.\n")

    sort_order = {'public': 0, 'private': 1, 'staged': 2}
    for cat_header in CATEGORY_ORDER:
        cat_projects = [p for p in active_projects.values() if p["category"] == cat_header]
        if not cat_projects:
            continue
        out.append(f"#### {cat_header}")
        for p in sorted(cat_projects, key=lambda x: (sort_order.get(visibility_map[x["name"]], 3), x["name"])):
            pname = p["name"]
            desc = p["description"]
            vis = visibility_map[pname]
            if vis == 'public':
                out.append(f"* **[{pname}](https://github.com/{GITHUB_USER}/{pname})** — {desc}")
            elif vis == 'private':
                out.append(f"* **[{pname}](https://github.com/{GITHUB_USER}/{pname})** 🔒 *(Private)* — {desc}")
            else:
                out.append(f"* **{pname}** *(staged)* — {desc}")
        out.append("")

    out.append("---\n")
    out.append("### 🔒 Private Repositories & System Security\n")
    out.append("Certain specialized tools in the Shallot ecosystem are maintained as **Private** repositories on GitHub. These systems are production-ready and version-controlled, but are restricted from public indexing for specific security and infrastructure reasons:\n")
    out.append("| Repository | Focus & Architecture | Security & Privacy Rationale |")
    out.append("| :--- | :--- | :--- |")
    
    private_projs = [p for p in active_projects.values() if visibility_map[p["name"]] == 'private']
    for p in sorted(private_projs, key=lambda x: x["name"]):
        pname = p["name"]
        meta = extract_private_metadata_from_readme(p["path"], pname)
        reasons_list = meta.get("why_private", [])
        if reasons_list:
            reasons_summary = " ".join([r.split(":", 1)[1].strip() if ":" in r else r for r in reasons_list[:2]])
        else:
            reasons_summary = "Restricted to protect local credentials, infrastructure paths, and private data workflows."
        
        desc_clean = clean_table_cell(p['description'])
        reasons_clean = clean_table_cell(f"**Defense-in-Depth & Privacy**: {reasons_summary}")
        out.append(f"| **[{pname}](https://github.com/{GITHUB_USER}/{pname})** 🔒 | {desc_clean} | {reasons_clean} |")

    out.append("\n---\n")
    out.append("### 💻 Functional Domains & Tech Stack\n")
    out.append("```")
    out.append("  Domains        :: Local-first PWAs, Web Audio DSP, Discord bots, AI workflows, Media automation")
    out.append("  AI / Vision    :: ComfyUI pipelines, LoRA evaluation, Vision & OCR extraction, Gemini API")
    out.append("  Audio / Web    :: Web Audio API, real-time polyphonic synthesis, React, TypeScript, Tailwind")
    out.append("  Data / Storage :: Zero-telemetry local storage, IndexedDB, SQLite, Google Sheets API")
    out.append("  Platforms      :: Cross-platform Web, Desktop (Windows), PWA (iOS/Android), Headless CLI")
    out.append("```\n")
    out.append("---\n")
    out.append('<p align="center">')
    out.append('  <a href="PROJECT_STATE.md"><strong>View Full Dynamic Project State & Matrix →</strong></a>')
    out.append("</p>\n")
    out.append('<p align="center">')
    out.append(f'  <img src="https://github-readme-stats.vercel.app/api?username={GITHUB_USER}&show_icons=true&theme=tokyonight&hide_border=true" alt="GitHub Repository Activity" />')
    out.append("</p>")
    return "\n".join(out) + "\n"

def update_changelog(added_projects, removed_projects, newly_published, newly_private):
    if not added_projects and not removed_projects and not newly_published and not newly_private:
        return
    
    today = datetime.date.today().strftime("%Y-%m-%d")
    changelog_path = os.path.join(PROFILE_REPO_DIR, "CHANGELOG.md")
    
    entry_lines = [f"\n### Auto-Sync Update ({today})"]
    if removed_projects:
        entry_lines.append("#### Removed (Deleted / Migrated)")
        for p in sorted(removed_projects):
            entry_lines.append(f"- Removed obsolete project reference `{p}`.")
    if added_projects:
        entry_lines.append("#### Added (New Workspace Projects)")
        for p in sorted(added_projects):
            entry_lines.append(f"- Added tracking for new project `{p}`.")
    if newly_private:
        entry_lines.append("#### Private Repositories Documented")
        for p in sorted(newly_private):
            entry_lines.append(f"- Documented private repository `{p}` with full architecture details and privacy rationale.")
    if newly_published:
        entry_lines.append("#### Published to GitHub")
        for p in sorted(newly_published):
            entry_lines.append(f"- Updated `{p}` to live clickable GitHub repository link.")
    
    entry_text = "\n".join(entry_lines) + "\n"
    
    if os.path.exists(changelog_path):
        with open(changelog_path, "r", encoding="utf-8") as f:
            content = f.read()
        target = "## [Unreleased]\n"
        if target in content:
            new_content = content.replace(target, target + entry_text)
            with open(changelog_path, "w", encoding="utf-8") as f:
                f.write(new_content)
            print("Logged updates to CHANGELOG.md")

def main():
    push_flag = "--push" in sys.argv
    print("--- Shallot Profile Sync Engine ---")
    active_projects = get_existing_local_projects()
    previous_tracked, previous_published = read_previous_project_state()
    
    print("Fetching repository status from GitHub...")
    public_repos, private_repos = fetch_github_repos()
    print(f"Discovered GitHub Repos: {len(public_repos)} Public, {len(private_repos)} Private")
    
    current_names = set(active_projects.keys())
    removed_projects = previous_tracked - current_names if previous_tracked else set()
    added_projects = current_names - previous_tracked if previous_tracked else set()
    
    visibility_map = {pname: get_repo_visibility(pname, public_repos, private_repos, p["path"]) for pname, p in active_projects.items()}
    
    live_all = {pname for pname, v in visibility_map.items() if v in ('public', 'private')}
    newly_published = {pname for pname, v in visibility_map.items() if v == 'public' and pname not in previous_published}
    newly_private = {pname for pname, v in visibility_map.items() if v == 'private' and pname not in previous_published}
    
    pub_count = sum(1 for v in visibility_map.values() if v == 'public')
    priv_count = sum(1 for v in visibility_map.values() if v == 'private')
    staged_count = sum(1 for v in visibility_map.values() if v == 'staged')

    print(f"Active Projects Found : {len(active_projects)}")
    print(f"Published (Public)    : {pub_count}")
    print(f"Published (Private)   : {priv_count}")
    print(f"Local / Staged        : {staged_count}")
    if removed_projects:
        print(f"Deleted / Removed     : {removed_projects}")
    if added_projects:
        print(f"Newly Added           : {added_projects}")
    if newly_private:
        print(f"Newly Private         : {newly_private}")
    if newly_published:
        print(f"Newly Published       : {newly_published}")
        
    # Write PROJECT_STATE.md
    state_content = generate_project_state(active_projects, public_repos, private_repos)
    with open(os.path.join(PROFILE_REPO_DIR, "PROJECT_STATE.md"), "w", encoding="utf-8") as f:
        f.write(state_content)
    print("Updated PROJECT_STATE.md")

    # Write README.md
    readme_content = generate_readme(active_projects, public_repos, private_repos)
    with open(os.path.join(PROFILE_REPO_DIR, "README.md"), "w", encoding="utf-8") as f:
        f.write(readme_content)
    print("Updated README.md")

    # Update CHANGELOG.md
    update_changelog(added_projects, removed_projects, newly_published, newly_private)
    
    if push_flag:
        print("Committing and pushing changes to GitHub...")
        subprocess.run(["git", "add", "."], cwd=PROFILE_REPO_DIR, check=True)
        commit_msg = "chore: sync project matrix with private repositories and privacy rationale"
        if removed_projects:
            commit_msg = f"chore: sync projects and prune ({', '.join(sorted(removed_projects))})"
        res = subprocess.run(["git", "commit", "-m", commit_msg], cwd=PROFILE_REPO_DIR, capture_output=True, text=True)
        print(res.stdout)
        push_res = subprocess.run(["git", "push", "origin", "main"], cwd=PROFILE_REPO_DIR, capture_output=True, text=True)
        print(push_res.stdout or push_res.stderr)
        print("GitHub synchronization complete!")

if __name__ == "__main__":
    main()
