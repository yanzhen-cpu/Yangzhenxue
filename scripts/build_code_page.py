"""Render the public Python excerpt as a readable static HTML page."""

from __future__ import annotations

from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "src" / "strategy_pipeline.py"
OUTPUT = ROOT / "code.html"


def main() -> None:
    code = escape(SOURCE.read_text(encoding="utf-8"))
    page = f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="description" content="STRAT-026 v0.6.2 公开Python架构节选。">
  <title>Python代码节选｜STRAT-026 v0.6.2</title>
  <link rel="stylesheet" href="styles.css">
</head>
<body>
  <header class="site-header">
    <a class="brand" href="index.html"><span class="brand-mark" aria-hidden="true">YZ</span><span>返回项目首页</span></a>
    <nav aria-label="代码页面导航"><a href="index.html#results">回测结果</a><a href="index.html#limits">研究边界</a></nav>
  </header>
  <main class="code-shell">
    <div class="code-intro">
      <p class="kicker">PUBLIC PYTHON EXCERPT · STRAT-026 v0.6.2</p>
      <h1>公开代码节选</h1>
      <p>以下代码展示偏离识别、合约择优、品种束风险门禁和账户保证金风险计算。它是可审阅的架构节选，完整回测引擎和私人数据适配器未公开。</p>
      <div class="code-links">
        <a href="https://github.com/yanzhen-cpu/Yangzhenxue/blob/main/src/strategy_pipeline.py">在GitHub查看源文件</a>
        <a href="index.html">返回项目首页</a>
      </div>
    </div>
    <pre class="code-view" aria-label="公开Python代码"><code>{code}</code></pre>
  </main>
</body>
</html>
"""
    OUTPUT.write_text(page, encoding="utf-8")


if __name__ == "__main__":
    main()
