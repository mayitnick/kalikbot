import subprocess
import html

git_log = subprocess.check_output([
    "git", "log",
    "--pretty=format:%h|%ad|%s|%an",
    "--date=short"
], text=True)

commits = []
for line in git_log.strip().split("\n"):
    short_hash, date, message, author = line.split("|", 3)
    commits.append({
        "hash": short_hash,
        "date": date,
        "message": html.escape(message),
        "author": html.escape(author)
    })

html_content = """
<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>Таймлайн коммитов</title>
<style>
  html, body {
    margin: 0; padding: 0; height: 100%;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    background: #f5f7fa;
    color: #333;
  }
  body {
    display: flex;
    justify-content: center;
    align-items: center;
    padding: 10px;
    box-sizing: border-box;
  }
  .container {
    width: 95vw;
    height: 95vh;
    overflow-y: auto;
    background: #fff;
    border-radius: 12px;
    box-shadow: 0 8px 24px rgba(0,0,0,0.12);
    padding: 10px;
    display: grid;
    grid-template-columns: 100px 1fr 180px;
    gap: 8px 16px;
    align-items: center;
  }
  .commit {
    background: #e9f0ff;
    padding: 6px 12px;
    border-radius: 8px;
    transition: background-color 0.3s;
    cursor: default;
    font-size: clamp(10px, 1vw + 1vh, 14px);
    line-height: 1.3;
    overflow: hidden;
    white-space: nowrap;
    text-overflow: ellipsis;
  }
  .commit:hover {
    background: #c2d8ff;
  }
  .date {
    font-weight: 700;
    color: #1a73e8;
    text-align: right;
    font-size: clamp(10px, 1vw + 1vh, 14px);
    white-space: nowrap;
  }
  .message {
    font-weight: 600;
    color: #202124;
  }
  .author {
    font-style: italic;
    color: #5f6368;
    font-size: clamp(9px, 0.9vw + 0.8vh, 12px);
    white-space: nowrap;
  }
  @media (max-width: 700px) {
    .container {
      grid-template-columns: 1fr;
    }
    .date, .author {
      text-align: left;
      white-space: normal;
    }
    .commit {
      white-space: normal;
    }
  }
</style>
</head>
<body>
<div class="container">
"""

for commit in commits:
    html_content += f"""
    <div class="date">{commit['date']}</div>
    <div class="commit message" title="{commit['message']}">{commit['message']}</div>
    <div class="author" title="{commit['author']}">{commit['author']} (<code>{commit['hash']}</code>)</div>
    """

html_content += """
</div>
</body>
</html>
"""

with open("git_commits.html", "w", encoding="utf-8") as f:
    f.write(html_content)

print("✅ git_commits.html.")
