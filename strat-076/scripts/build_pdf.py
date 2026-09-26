"""Build the two-page A4 recruiter brief for STRAT-032 v0.7.6."""

from __future__ import annotations

import json
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen.canvas import Canvas
from reportlab.platypus import Paragraph

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "reports" / "STRAT-032-v0.7.6-project-brief.pdf"
FONT_PATH = Path("C:/Windows/Fonts/msyh.ttc")


def register_font() -> str:
    if not FONT_PATH.is_file():
        raise FileNotFoundError("A Chinese font is required for this PDF")
    pdfmetrics.registerFont(TTFont("PortfolioCN", str(FONT_PATH), subfontIndex=0))
    return "PortfolioCN"


def draw_paragraph(canvas: Canvas, text: str, x: float, y: float, width: float, style: ParagraphStyle) -> float:
    paragraph = Paragraph(text, style)
    _, height = paragraph.wrap(width, 1000 * mm)
    paragraph.drawOn(canvas, x, y - height)
    return y - height


def metric_card(canvas: Canvas, font: str, x: float, y: float, label: str, value: str) -> None:
    width = 54 * mm
    canvas.setFillColor(colors.white)
    canvas.setStrokeColor(colors.HexColor("#CBD9E6"))
    canvas.roundRect(x, y, width, 24 * mm, 2 * mm, fill=1, stroke=1)
    canvas.setFillColor(colors.HexColor("#526173"))
    canvas.setFont(font, 8)
    canvas.drawString(x + 4 * mm, y + 17 * mm, label)
    canvas.setFillColor(colors.HexColor("#07111F"))
    canvas.setFont(font, 15.4)
    canvas.drawString(x + 4 * mm, y + 6.8 * mm, value)


def footer(canvas: Canvas, font: str, page: int) -> None:
    canvas.setStrokeColor(colors.HexColor("#CBD9E6"))
    canvas.line(18 * mm, 13 * mm, 192 * mm, 13 * mm)
    canvas.setFillColor(colors.HexColor("#667588"))
    canvas.setFont(font, 7)
    canvas.drawString(18 * mm, 8.5 * mm, "STRAT-032 v0.7.6 · Historical research backtest · Not investment advice")
    canvas.drawRightString(192 * mm, 8.5 * mm, str(page))


def main() -> None:
    data = json.loads((ROOT / "data" / "public-metrics.json").read_text(encoding="utf-8"))
    if data["source_run"] != "STRAT032-FULL-MAIN-20260926":
        raise ValueError("unexpected source run")
    font = register_font()
    canvas = Canvas(str(OUTPUT), pagesize=A4, pageCompression=1)
    canvas.setTitle("STRAT-032 v0.7.6 商品期货连续换月策略")
    canvas.setAuthor("羊振雪")
    canvas.setSubject("招聘项目成果：估值筛选、风险控制、同手数换月和独立审计")
    width, height = A4
    heading = ParagraphStyle("heading", fontName=font, fontSize=14, leading=20, textColor=colors.HexColor("#07111F"))
    body = ParagraphStyle("body", fontName=font, fontSize=9.2, leading=15, textColor=colors.HexColor("#344255"))

    canvas.setFillColor(colors.HexColor("#07111F"))
    canvas.rect(0, height - 54 * mm, width, 54 * mm, fill=1, stroke=0)
    canvas.setFillColor(colors.HexColor("#83C7F8"))
    canvas.setFont(font, 8)
    canvas.drawString(18 * mm, height - 15 * mm, "AUDITED RESEARCH PROJECT · STRAT-032 · v0.7.6")
    canvas.setFillColor(colors.white)
    canvas.setFont(font, 26)
    canvas.drawString(18 * mm, height - 33 * mm, "商品期货估值与连续换月策略")
    canvas.setFillColor(colors.HexColor("#B6C4D4"))
    canvas.setFont(font, 8)
    canvas.drawString(18 * mm, height - 47 * mm, "羊振雪 · 2019-01-02至2026-09-24 · 正式运行 STRAT032-FULL-MAIN-20260926")

    x0, gap = 18 * mm, 6 * mm
    for index, (label, value) in enumerate((
        ("累计收益", f"{data['total_return'] * 100:,.2f}%"),
        ("年化收益", f"{data['annualized_return'] * 100:.2f}%"),
        ("最大平仓回撤", f"{data['max_closed_drawdown'] * 100:.2f}%"),
    )):
        metric_card(canvas, font, x0 + index * (54 * mm + gap), height - 88 * mm, label, value)
    for index, (label, value) in enumerate((
        ("期末权益", f"{data['ending_equity'] / 10000:,.2f}万元"),
        ("闭环周期 / 换月", f"{data['closed_trades']} / {data['rollovers_filled']}"),
        ("Sharpe / 胜率", f"{data['sharpe']:.2f} / {data['win_rate'] * 100:.2f}%"),
    )):
        metric_card(canvas, font, x0 + index * (54 * mm + gap), height - 118 * mm, label, value)

    y = height - 132 * mm
    y = draw_paragraph(canvas, "项目概述", x0, y, 174 * mm, heading) - 3 * mm
    y = draw_paragraph(canvas,
        "系统将估值偏离、动态保证金、公告提保、交割月成交量、固定代码排畸和同手数换月纳入可审计的事件状态机。普通开仓先筛选后执行；换月保留原周期策略状态，并按新合约实际成交价记账。",
        x0, y, 174 * mm, body) - 7 * mm
    y = draw_paragraph(canvas, "主要工程环节", x0, y, 174 * mm, heading) - 3 * mm
    y = draw_paragraph(canvas,
        "① 冻结行情与参考数据　② 交割估值和成交量筛选　③ 动态保证金与提保减仓　④ 到期前强退及五日限价换月　⑤ 策略阈值平移与真实会计成本分离　⑥ 逐笔逐日独立复算",
        x0, y, 174 * mm, body) - 7 * mm
    y = draw_paragraph(canvas, "风险与年度口径", x0, y, 174 * mm, heading) - 3 * mm
    year = data["annual_account_change"]["2026"]
    draw_paragraph(canvas,
        f"普通最大回撤{data['max_drawdown'] * 100:.2f}%，最大日终总毛保证金风险度{data['max_portfolio_risk'] * 100:.2f}%。2026年截至9月24日，账户权益较2025年末增加{year['change'] / 10000:,.2f}万元（{year['return'] * 100:.2f}%）；按最终退出年归属的周期净盈亏使用另一统计口径。",
        x0, y, 174 * mm, body)
    footer(canvas, font, 1)
    canvas.showPage()

    canvas.setFillColor(colors.HexColor("#07111F"))
    canvas.rect(0, height - 28 * mm, width, 28 * mm, fill=1, stroke=0)
    canvas.setFillColor(colors.white)
    canvas.setFont(font, 18)
    canvas.drawString(x0, height - 18 * mm, "验证证据与研究边界")

    y = height - 40 * mm
    y = draw_paragraph(canvas, "审计证据", x0, y, 174 * mm, heading) - 3 * mm
    audit = data["audit"]
    y = draw_paragraph(canvas,
        f"本轮{audit['targeted_tests']}项专项测试通过；{audit['independent_assertions']:,}条独立审计断言通过；{audit['trades']}个周期全部平仓；{audit['equity_days']:,}个交易日账户权益复算一致；{audit['fills']}条成交记录核验；正式输出审计状态为PASS。",
        x0, y, 174 * mm, body) - 7 * mm
    y = draw_paragraph(canvas, "结果解释限制", x0, y, 174 * mm, heading) - 3 * mm
    limitations = (
        f"未来锚：{data['research_flags']['future_anchor_cycles']}/{data['closed_trades']}个周期带未来锚标记，部分历史月价的当时可知性未逐月独立证明。",
        "数据：正式输入质量标记为PARTIAL，已声明的缺失与推定政策在运行中留痕。",
        "成本：手续费和滑点均为零；未检验真实成交冲击与市场容量。",
        "撮合：日线无法还原跨合约盘中事件先后，阈值触价不保证真实成交。",
        "资金：同一开盘批次采用统一权益快照，未成交预算不作当日反复分配。",
        "用途：这是按冻结假设执行的历史模拟，不是实盘业绩或收益承诺。",
    )
    for item in limitations:
        y = draw_paragraph(canvas, "• " + item, x0 + 3 * mm, y, 169 * mm, body) - 2.2 * mm
    y -= 4 * mm
    y = draw_paragraph(canvas, "公开范围", x0, y, 174 * mm, heading) - 3 * mm
    draw_paragraph(canvas,
        "公开站点提供项目说明、完整区间曲线、结构化指标、方法说明及两份来自正式运行快照的Python增量模块。前序完整引擎、私人数据库和输入快照未公开。",
        x0, y, 174 * mm, body)

    canvas.setFillColor(colors.HexColor("#F0F7FC"))
    canvas.setStrokeColor(colors.HexColor("#83C7F8"))
    canvas.roundRect(x0, 37 * mm, 174 * mm, 29 * mm, 2 * mm, fill=1, stroke=1)
    canvas.setFillColor(colors.HexColor("#07111F"))
    canvas.setFont(font, 10)
    canvas.drawString(x0 + 5 * mm, 55 * mm, "项目链接")
    canvas.setFont(font, 9)
    canvas.drawString(x0 + 5 * mm, 47 * mm, "https://yanzhen-cpu.github.io/Yangzhenxue/strat-076/")
    canvas.setFillColor(colors.HexColor("#667588"))
    canvas.setFont(font, 7.4)
    canvas.drawString(x0 + 5 * mm, 41 * mm, "Source run: STRAT032-FULL-MAIN-20260926 · Independent audit: PASS")
    footer(canvas, font, 2)
    canvas.save()


if __name__ == "__main__":
    main()
