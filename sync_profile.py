"""
Shallot Profile Auto-Synchronizer
=================================
Scans the workspace directory (C:\\Users\\strot\\Antigravity IDE), reconciles
active, published, and deleted projects, updates PROJECT_STATE.md and README.md,
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
    "cui-audio-vibe-node": ("Generative AI & ComfyUI Architecture", "Custom ComfyUI node analyzing song themes and mood via Gemini to guide visual generation."),
    "cui-ico-gen": ("Generative AI & ComfyUI Architecture", "High-precision Windows 11 icon generator node with glass and gloss overlays."),
    
    # 2. Audio & Web Synthesizers
    "ShallotWHAM": ("Interactive Audio & Web Synthesizers", "Cyber-styled dual-engine web synthesizer and performance station."),
    "ShallotBeats": ("Interactive Audio & Web Synthesizers", "18-kit acoustic drum step sequencer for guitar backing tracks via Web Audio API."),
    "audio-harmonica": ("Interactive Audio & Web Synthesizers", "Virtual instrument polyphony and harmonica synthesis engine."),
    
    # 3. The Shallot Suite (Local-First)
    "Shallot-Money": ("The Shallot Suite (Local-First Applications)", "Sleek mobile-first budgeting and expense tracker styled with the signature Shallot Plum theme."),
    "Shallot-Kitchen-Keeper": ("The Shallot Suite (Local-First Applications)", "Smart grocery inventory companion to eliminate food waste."),
    "shallot-kitchen-keeper": ("The Shallot Suite (Local-First Applications)", "Smart grocery inventory companion to eliminate food waste."),
    "ShallotPeel": ("The Shallot Suite (Local-First Applications)", "Telemetry and token usage analytics for AI coding interactions."),
    "Shallot-Media-Archive": ("The Shallot Suite (Local-First Applications)", "Local media indexing, tagging, and asset management."),
    
    # 4. Automation & Utilities
    "yt-short-bot-garden": ("Automation & Utilities", "Automated end-to-end YouTube Shorts video creation pipeline."),
    "util-exiftool-helper": ("Automation & Utilities", "Batch media metadata processing utility."),
    "DRAIN": ("Automation & Utilities", "Optimization dashboard for subscription AI workflows."),
    "The-Committee": ("Automation & Utilities", "Interactive module-chaining creative engine."),
    "util-joan-datacombinedrive": ("Automation & Utilities", "Zero-download indexer for cloud and local filesystems."),
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

def get_live_github_repos():
    live = set()
    print("Checking live repositories on GitHub...")
    for repo_name in CATEGORY_MAP.keys():
        url = f"https://github.com/{GITHUB_USER}/{repo_name}.git"
        try:
            res = subprocess.run(["git", "ls-remote", url], capture_output=True, text=True, timeout=5)
            if res.returncode == 0:
                live.add(repo_name)
        except Exception:
            pass
    return live

def get_existing_local_projects():
    projects = {}
    if not os.path.exists(WORKSPACE_ROOT):
        return projects
    for name in os.listdir(WORKSPACE_ROOT):
        full_path = os.path.join(WORKSPACE_ROOT, name)
        if not os.path.isdir(full_path) or name in [".git", "strothman"]:
            continue
        
        # Check description
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
    if os.path.exists(state_file):
        with open(state_file, "r", encoding="utf-8") as f:
            for line in f:
                match = re.search(r"\|\s*(?:\*\*\[?([a-zA-Z0-9_\-\s]+)\]?.*?|\`([a-zA-Z0-9_\-\s]+)\`)\s*\|", line)
                if match:
                    name = (match.group(1) or match.group(2)).strip()
                    if name and name != "Project Name":
                        tracked.add(name)
    return tracked

def generate_project_state(active_projects, live_repos):
    today = datetime.date.today().strftime("%Y-%m-%d")
    total = len(active_projects)
    pub_count = sum(1 for p in active_projects if p in live_repos)
    loc_count = total - pub_count
    
    out = []
    out.append("# 🧅 Shallot Profile — Project State & Ecosystem Matrix\n")
    out.append(f"> **Last Updated**: {today}  ")
    out.append(f"> **Workspace Root**: `C:\\Users\\strot\\Antigravity IDE`  ")
    out.append("> **Status Summary**: Actively tracking all local & published repositories in the Shallot ecosystem.\n")
    out.append("---\n")
    out.append("## 📊 Quick Statistics\n")
    out.append("| Total Projects Tracked | Published on GitHub | Local / Staged |")
    out.append("| :---: | :---: | :---: |")
    out.append(f"| **{total}** | **{pub_count}** | **{loc_count}** |\n")
    out.append("---\n")
    out.append("## 🗂️ Active Projects Matrix\n")

    for idx, cat_header in enumerate(CATEGORY_ORDER, 1):
        out.append(f"### {idx}. {cat_header}")
        out.append("| Project Name | Local Directory | GitHub Remote Status | Description |")
        out.append("| :--- | :--- | :--- | :--- |")
        
        cat_projects = [p for p in active_projects.values() if p["category"] == cat_header]
        for p in sorted(cat_projects, key=lambda x: (x["name"] not in live_repos, x["name"])):
            pname = p["name"]
            desc = p["description"]
            if pname in live_repos:
                link = f"**[{pname}](https://github.com/{GITHUB_USER}/{pname})**"
                status = "🟢 **Published**"
            else:
                link = f"**{pname}**"
                status = "🟡 *Local Only (Coming Soon)*"
            out.append(f"| {link} | `{pname}` | {status} | {desc} |")
        out.append("")
    
    out.append("---\n")
    out.append("## 🔄 Dynamic Sync Rules")
    out.append("1. **Deletion Policy**: If a project folder is deleted from `C:\\Users\\strot\\Antigravity IDE`, running `sync_profile.py` automatically removes its entry from `README.md` and `PROJECT_STATE.md`.")
    out.append("2. **Publish Policy**: When a local repo is pushed to GitHub, running `sync_profile.py` promotes it from *Coming Soon* to a live clickable hyperlink in `README.md`.")
    out.append("3. **Audit Trail**: Every modification, addition, or removal is automatically recorded in `CHANGELOG.md`.")
    return "\n".join(out) + "\n"

def generate_readme(active_projects, live_repos):
    out = []
    out.append("# Hi there, I'm Shallot (strothman) 👋\n")
    out.append('<p align="center">')
    out.append('  <img src="shallot_icon.png" width="130" height="130" alt="Shallot Logo" />')
    out.append("</p>\n")
    out.append('<p align="center">')
    out.append("  <em>Creative Technologist • Generative AI & ComfyUI • Audio Systems • Local-First Tooling</em>")
    out.append("</p>\n")
    out.append('<p align="center">')
    out.append('  <img src="https://img.shields.io/badge/Focus-Generative%20AI%20%26%20Audio-8A2BE2?style=flat-square" alt="Focus" />')
    out.append('  <img src="https://img.shields.io/badge/Architecture-Local--First-2ea44f?style=flat-square" alt="Local-First" />')
    out.append('  <img src="https://img.shields.io/badge/Ecosystem-Shallot%20Suite-purple?style=flat-square" alt="Shallot Suite" />')
    out.append("</p>\n")
    out.append("---\n")
    out.append("### 🧅 About Me")
    out.append("I'm a systems builder and creative technologist. I build bespoke software that sits at the intersection of **Generative AI pipelines**, **interactive audio DSP**, **automation bots**, and **self-sovereign local-first applications**.\n")
    out.append("---\n")
    out.append("### 🛠️ Featured Ecosystems & Projects\n")
    out.append("> [!NOTE]")
    out.append("> **Work in Progress**: I am currently in the process of cleaning up and gradually publishing my project repositories. Unlinked projects will go live soon!\n")

    for cat_header in CATEGORY_ORDER[:4]: # Featured top 4
        out.append(f"#### {cat_header}")
        cat_projects = [p for p in active_projects.values() if p["category"] == cat_header]
        for p in sorted(cat_projects, key=lambda x: (x["name"] not in live_repos, x["name"])):
            pname = p["name"]
            desc = p["description"]
            if pname in live_repos:
                out.append(f"* **[{pname}](https://github.com/{GITHUB_USER}/{pname})** — {desc}")
            else:
                out.append(f"* **{pname}** *(coming soon)* — {desc}")
        out.append("")

    out.append("---\n")
    out.append("### 💻 Tech Stack & Tooling\n")
    out.append("```")
    out.append("  Languages    :: Python, JavaScript, TypeScript, Luau, SQL")
    out.append("  AI / ML      :: ComfyUI, PyTorch, Stable Diffusion, LoRA Analysis, Gemini API")
    out.append("  Audio / Web  :: Web Audio API, DSP Synthesis, React, Vite, Tailwind")
    out.append("  Databases    :: SQLite, Local-First Sync, Google Sheets API")
    out.append("  DevOps / CLI :: Git, PowerShell, Bash, Custom Desktop Launchers")
    out.append("```\n")
    out.append("---\n")
    out.append('<p align="center">')
    out.append(f'  <img src="https://github-readme-stats.vercel.app/api?username={GITHUB_USER}&show_icons=true&theme=tokyonight&hide_border=true" alt="Shallot GitHub Stats" />')
    out.append("</p>")
    return "\n".join(out) + "\n"

def update_changelog(added_projects, removed_projects, newly_published):
    if not added_projects and not removed_projects and not newly_published:
        return
    
    today = datetime.date.today().strftime("%Y-%m-%d")
    changelog_path = os.path.join(PROFILE_REPO_DIR, "CHANGELOG.md")
    
    entry_lines = [f"\n### Auto-Sync Update ({today})"]
    if removed_projects:
        entry_lines.append("#### Removed (Deleted from Workspace)")
        for p in sorted(removed_projects):
            entry_lines.append(f"- Removed project reference `{p}` following local deletion.")
    if added_projects:
        entry_lines.append("#### Added (New Workspace Projects)")
        for p in sorted(added_projects):
            entry_lines.append(f"- Added tracking for new project `{p}`.")
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
    print(f"--- Shallot Profile Sync Engine ---")
    active_projects = get_existing_local_projects()
    previous_tracked = read_previous_project_state()
    live_repos = get_live_github_repos()
    
    current_names = set(active_projects.keys())
    removed_projects = previous_tracked - current_names if previous_tracked else set()
    added_projects = current_names - previous_tracked if previous_tracked else set()
    
    print(f"Active Projects Found : {len(active_projects)}")
    print(f"Published on GitHub   : {len([p for p in active_projects if p in live_repos])}")
    if removed_projects:
        print(f"Deleted / Removed     : {removed_projects}")
    if added_projects:
        print(f"Newly Added           : {added_projects}")
        
    # Write PROJECT_STATE.md
    state_content = generate_project_state(active_projects, live_repos)
    with open(os.path.join(PROFILE_REPO_DIR, "PROJECT_STATE.md"), "w", encoding="utf-8") as f:
        f.write(state_content)
    print("Updated PROJECT_STATE.md")

    # Write README.md
    readme_content = generate_readme(active_projects, live_repos)
    with open(os.path.join(PROFILE_REPO_DIR, "README.md"), "w", encoding="utf-8") as f:
        f.write(readme_content)
    print("Updated README.md")

    # Update CHANGELOG.md
    update_changelog(added_projects, removed_projects, set())
    
    if push_flag:
        print("Committing and pushing changes to GitHub...")
        subprocess.run(["git", "add", "."], cwd=PROFILE_REPO_DIR, check=True)
        commit_msg = "chore: sync project state and update changelog"
        if removed_projects:
            commit_msg = f"chore: prune deleted projects ({', '.join(sorted(removed_projects))})"
        res = subprocess.run(["git", "commit", "-m", commit_msg], cwd=PROFILE_REPO_DIR, capture_output=True, text=True)
        print(res.stdout)
        push_res = subprocess.run(["git", "push", "origin", "main"], cwd=PROFILE_REPO_DIR, capture_output=True, text=True)
        print(push_res.stdout or push_res.stderr)
        print("GitHub synchronization complete!")

if __name__ == "__main__":
    main()
