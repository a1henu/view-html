#!/usr/bin/env python3
"""扫描 reports/ 下的每个报告文件夹，生成根目录导航首页 index.html。

约定：
- 每个报告是 reports/<slug>/ 文件夹，入口为 index.html。
- 标题优先级：reports/<slug>/meta.json 的 "title" > index.html 的 <title> > 文件夹名。
- meta.json 可选字段：title, description, date(YYYY-MM-DD)。
  若无 date，则用文件夹的 git 最后提交时间，再退化为文件系统 mtime。
"""
import os
import re
import json
import html
import subprocess
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.abspath(__file__))
REPORTS_DIR = os.path.join(ROOT, "reports")

TITLE_RE = re.compile(r"<title[^>]*>(.*?)</title>", re.IGNORECASE | re.DOTALL)


def git_last_date(path):
    try:
        out = subprocess.run(
            ["git", "log", "-1", "--format=%cI", "--", path],
            cwd=ROOT, capture_output=True, text=True, timeout=10,
        ).stdout.strip()
        if out:
            return out[:10]
    except Exception:
        pass
    return None


def extract_title(report_dir):
    idx = os.path.join(report_dir, "index.html")
    if not os.path.isfile(idx):
        return None
    try:
        with open(idx, encoding="utf-8", errors="ignore") as f:
            head = f.read(8192)
        m = TITLE_RE.search(head)
        if m:
            t = re.sub(r"\s+", " ", m.group(1)).strip()
            return html.unescape(t) or None
    except Exception:
        pass
    return None


def collect():
    reports = []
    if not os.path.isdir(REPORTS_DIR):
        return reports
    for slug in sorted(os.listdir(REPORTS_DIR)):
        d = os.path.join(REPORTS_DIR, slug)
        if not os.path.isdir(d) or slug.startswith("."):
            continue
        if not os.path.isfile(os.path.join(d, "index.html")):
            continue  # 没有入口的跳过
        meta = {}
        mp = os.path.join(d, "meta.json")
        if os.path.isfile(mp):
            try:
                with open(mp, encoding="utf-8") as f:
                    meta = json.load(f)
            except Exception:
                meta = {}
        title = meta.get("title") or extract_title(d) or slug
        date = meta.get("date") or git_last_date(f"reports/{slug}") or \
            datetime.fromtimestamp(os.path.getmtime(d), timezone.utc).strftime("%Y-%m-%d")
        reports.append({
            "slug": slug,
            "title": title,
            "desc": meta.get("description", ""),
            "date": date,
        })
    # 按日期倒序，新报告在前
    reports.sort(key=lambda r: r["date"], reverse=True)
    return reports


PAGE = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>阅读报告</title>
<style>
  :root {{ color-scheme: light dark; }}
  * {{ box-sizing: border-box; }}
  body {{
    margin: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI",
    "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", sans-serif;
    background: #f6f7f9; color: #1a1a1a; line-height: 1.6;
  }}
  @media (prefers-color-scheme: dark) {{
    body {{ background: #16181d; color: #e6e6e6; }}
    .card {{ background: #1f2229 !important; border-color: #2c3038 !important; }}
    .card:hover {{ border-color: #4a90d9 !important; }}
    a {{ color: #6ab0f3 !important; }}
    .meta {{ color: #8a909a !important; }}
  }}
  .wrap {{ max-width: 860px; margin: 0 auto; padding: 48px 20px 80px; }}
  h1 {{ font-size: 28px; margin: 0 0 4px; }}
  .sub {{ color: #888; margin: 0 0 32px; font-size: 14px; }}
  .grid {{ display: flex; flex-direction: column; gap: 14px; }}
  .card {{
    display: block; padding: 18px 20px; background: #fff;
    border: 1px solid #e3e6ea; border-radius: 12px; text-decoration: none;
    color: inherit; transition: border-color .15s, transform .15s;
  }}
  .card:hover {{ border-color: #4a90d9; transform: translateY(-1px); }}
  .card h2 {{ font-size: 17px; margin: 0 0 6px; }}
  .card .desc {{ font-size: 14px; color: #666; margin: 0 0 8px; }}
  .meta {{ font-size: 12px; color: #999; font-variant-numeric: tabular-nums; }}
  .empty {{ color: #999; text-align: center; padding: 60px 0; }}
  a.card {{ color: inherit; }}
</style>
</head>
<body>
<div class="wrap">
  <h1>📄 阅读报告</h1>
  <p class="sub">共 {count} 份 · 更新于 {now}</p>
  <div class="grid">
{cards}
  </div>
</div>
</body>
</html>
"""

CARD = """    <a class="card" href="reports/{slug}/">
      <h2>{title}</h2>
      {desc}
      <div class="meta">{date} · {slug}</div>
    </a>"""


def main():
    reports = collect()
    cards = []
    for r in reports:
        desc = f'<p class="desc">{html.escape(r["desc"])}</p>' if r["desc"] else ""
        cards.append(CARD.format(
            slug=html.escape(r["slug"]),
            title=html.escape(r["title"]),
            desc=desc,
            date=html.escape(r["date"]),
        ))
    body = "\n".join(cards) if cards else '    <p class="empty">还没有报告。</p>'
    now = git_last_date(".") or datetime.now(timezone.utc).strftime("%Y-%m-%d")
    out = PAGE.format(count=len(reports), now=now, cards=body)
    with open(os.path.join(ROOT, "index.html"), "w", encoding="utf-8") as f:
        f.write(out)
    print(f"index.html rebuilt: {len(reports)} report(s)")


if __name__ == "__main__":
    main()
