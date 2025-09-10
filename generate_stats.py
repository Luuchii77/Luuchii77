import requests
from collections import defaultdict
import os

USERNAME = os.getenv("GITHUB_USERNAME", "YOUR_GITHUB_USERNAME")  
TOKEN = os.getenv("GITHUB_TOKEN")  # GitHub Personal Access Token

def fetch_repos(username):
    url = f"https://api.github.com/users/{username}/repos?per_page=100"
    headers = {"Authorization": f"token {TOKEN}"} if TOKEN else {}
    repos = []
    while url:
        r = requests.get(url, headers=headers)
        r.raise_for_status()
        repos.extend(r.json())
        url = r.links.get("next", {}).get("url")
    return repos

def fetch_languages(repo_full_name):
    url = f"https://api.github.com/repos/{repo_full_name}/languages"
    headers = {"Authorization": f"token {TOKEN}"} if TOKEN else {}
    r = requests.get(url, headers=headers)
    r.raise_for_status()
    return r.json()

def main():
    repos = fetch_repos(USERNAME)
    language_stats = defaultdict(int)
    total_bytes = 0

    for repo in repos:
        langs = fetch_languages(repo["full_name"])
        for lang, size in langs.items():
            language_stats[lang] += size
            total_bytes += size

    # Generate Markdown Table
    lines = ["## 📊 Language Stats\n", "| Language | % |\n", "|----------|---|\n"]
    for lang, size in sorted(language_stats.items(), key=lambda x: x[1], reverse=True):
        percent = (size / total_bytes) * 100
        lines.append(f"| {lang} | {percent:.2f}% |\n")

    with open("LANG_STATS.md", "w", encoding="utf-8") as f:
        f.writelines(lines)

if __name__ == "__main__":
    main()

