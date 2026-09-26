"""Render the exact public STRAT-032 source excerpts as a readable HTML page."""

from __future__ import annotations

from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE_NAMES = ("strat_032_data.py", "strat_032_engine.py")


def main() -> None:
    sections = []
    for name in SOURCE_NAMES:
        source = ROOT / "src" / name
        code = escape(source.read_text(encoding="utf-8"))
        url = f"https://github.com/yanzhen-cpu/Yangzhenxue/blob/main/strat-076/src/{name}"
        sections.append(
            f'<section><h2 class="code-section-title">{name}</h2>'
            f'<p><a class="text-link" href="{url}">在GitHub查看该文件</a></p>'
            f'<pre class="code-view"><code>{code}</code></pre></section>'
        )
    page = """<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="description" content="STRAT-032 v0.7.6 冻结源码中的固定代码筛选和状态机增量模块。">
  <title>0.7.6 Python源码节选｜羊振雪</title>
  <link rel="stylesheet" href="../styles.css">
  <link rel="stylesheet" href="site.css">
</head>
<body>
  <header class="site-header">
    <a class="brand" href="index.html"><span class="brand-mark" aria-hidden="true">YZ</span><span>返回0.7.6项目页</span></a>
    <nav aria-label="代码页面导航"><a href="index.html#results">回测结果</a><a href="../index.html">0.6.2</a></nav>
  </header>
  <main class="code-shell">
    <div class="code-intro">
      <p class="kicker">FROZEN PYTHON EXCERPT · STRAT-032 v0.7.6</p>
      <h1>公开源码节选</h1>
      <p>以下两个文件直接来自正式运行冻结的源码快照，分别处理固定代码排畸与普通信号的状态机接入。它们依赖前序策略模块、保证金公告解析和数据适配器，不能单独复现完整回测。</p>
      <div class="code-links"><a href="index.html">返回项目页</a><a href="https://github.com/yanzhen-cpu/Yangzhenxue/tree/main/strat-076/src">在GitHub查看源码目录</a></div>
    </div>
    """ + "\n".join(sections) + """
  </main>
</body>
</html>
"""
    (ROOT / "code.html").write_text(page, encoding="utf-8")


if __name__ == "__main__":
    main()
