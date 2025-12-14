import requests
from collections import defaultdict
import os

USERNAME = os.getenv("GITHUB_USERNAME")
TOKEN = os.getenv("GITHUB_TOKEN")

if not USERNAME:
    raise ValueError("GITHUB_USERNAME environment variable is required.")

session = requests.Session()
if TOKEN:
    session.headers.update({"Authorization": f"token {TOKEN}"})

def fetch_repos(username):
    url = f"https://api.github.com/users/{username}/repos?per_page=100"
    repos = []

    while url:
        r = session.get(url)
        r.raise_for_status()
        repos.extend(r.json())
        url = r.links.get("next", {}).get("url")

    return repos

def fetch_languages(repo_full_name):
    url = f"https://api.github.com/repos/{repo_full_name}/languages"
    r = session.get(url)
    r.raise_for_status()
    return r.json()

def main():
    repos = fetch_repos(USERNAME)
    language_stats = defaultdict(int)
    total_bytes = 0

    for repo in repos:
        if repo.get("fork"):
            continue

        langs = fetch_languages(repo["full_name"])
        for lang, size in langs.items():
            language_stats[lang] += size
            total_bytes += size

    lines = [
        "## 📊 Language Stats\n\n",
        "| Language | Percentage |\n",
        "|----------|------------|\n",
    ]

    for lang, size in sorted(language_stats.items(), key=lambda x: x[1], reverse=True):
        percent = (size / total_bytes) * 100
        lines.append(f"| {lang} | {percent:.2f}% |\n")

    with open("LANG_STATS.md", "w", encoding="utf-8") as f:
        f.writelines(lines)

    print("✅ Language stats generated.")

if __name__ == "__main__":
    main()
