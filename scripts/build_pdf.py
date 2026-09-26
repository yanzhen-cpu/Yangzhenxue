"""Generate the recruiter-facing two-page PDF from public metrics."""

from __future__ import annotations

import json
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen.canvas import Canvas
from reportlab.platypus import Paragraph

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "reports" / "STRAT-026-v0.6.2-project-brief.pdf"
FONT_PATH = Path("C:/Windows/Fonts/msyh.ttc")


def register_fonts() -> tuple[str, str]:
    if FONT_PATH.is_file():
        pdfmetrics.registerFont(TTFont("CN", str(FONT_PATH), subfontIndex=0))
        return "CN", "CN"
    return "Helvetica", "Helvetica-Bold"


def draw_paragraph(canvas: Canvas, text: str, x: float, y: float, width: float, style: ParagraphStyle) -> float:
    paragraph = Paragraph(text, style)
    _, height = paragraph.wrap(width, 1000 * mm)
    paragraph.drawOn(canvas, x, y - height)
    return y - height


def metric_card(canvas: Canvas, x: float, y: float, w: float, label: str, value: str, body_font: str, bold_font: str) -> None:
    canvas.setStrokeColor(colors.HexColor("#CCD5E1"))
    canvas.setFillColor(colors.white)
    canvas.roundRect(x, y, w, 24 * mm, 2 * mm, fill=1, stroke=1)
    canvas.setFillColor(colors.HexColor("#526173"))
    canvas.setFont(body_font, 8)
    canvas.drawString(x + 4 * mm, y + 17 * mm, label)
    canvas.setFillColor(colors.HexColor("#0A1422"))
    canvas.setFont(bold_font, 16)
    canvas.drawString(x + 4 * mm, y + 7 * mm, value)


def page_footer(canvas: Canvas, page: int, body_font: str) -> None:
    canvas.setStrokeColor(colors.HexColor("#CBD5E1"))
    canvas.line(18 * mm, 13 * mm, 192 * mm, 13 * mm)
    canvas.setFont(body_font, 7)
    canvas.setFillColor(colors.HexColor("#687789"))
    canvas.drawString(18 * mm, 8.5 * mm, "STRAT-026 v0.6.2 · Research backtest · Not investment advice")
    canvas.drawRightString(192 * mm, 8.5 * mm, str(page))


def main() -> None:
    data = json.loads((ROOT / "data" / "public-metrics.json").read_text(encoding="utf-8"))
    body_font, bold_font = register_fonts()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    canvas = Canvas(str(OUTPUT), pagesize=A4, pageCompression=1)
    canvas.setTitle("STRAT-026 v0.6.2 商品期货估值与风险控制系统")
    canvas.setAuthor("羊振雪")
    canvas.setSubject("招聘项目成果：策略形式化、数据治理、历史回测与独立审计")
    width, height = A4

    title = ParagraphStyle("title", fontName=bold_font, fontSize=27, leading=34, textColor=colors.HexColor("#07111F"), alignment=TA_LEFT)
    body = ParagraphStyle("body", fontName=body_font, fontSize=9.2, leading=15, textColor=colors.HexColor("#344255"))
    small = ParagraphStyle("small", fontName=body_font, fontSize=7.6, leading=12, textColor=colors.HexColor("#5E6B7A"))
    heading = ParagraphStyle("heading", fontName=bold_font, fontSize=14, leading=19, textColor=colors.HexColor("#07111F"))

    canvas.setFillColor(colors.HexColor("#07111F"))
    canvas.rect(0, height - 54 * mm, width, 54 * mm, fill=1, stroke=0)
    canvas.setFillColor(colors.HexColor("#58D3C0"))
    canvas.setFont(bold_font, 8)
    canvas.drawString(18 * mm, height - 15 * mm, "AUDITED RESEARCH PROJECT · STRAT-026 · v0.6.2")
    white_title = ParagraphStyle("white_title", parent=title, textColor=colors.white)
    draw_paragraph(canvas, "商品期货估值与风险控制系统", 18 * mm, height - 22 * mm, 145 * mm, white_title)
    canvas.setFont(body_font, 8)
    canvas.setFillColor(colors.HexColor("#B6C4D4"))
    canvas.drawString(18 * mm, height - 47 * mm, "羊振雪 · Strategy formalization / Data governance / Backtesting / Audit")

    card_w = 54 * mm
    gap = 6 * mm
    card_y1 = height - 88 * mm
    metric_card(canvas, 18 * mm, card_y1, card_w, "累计收益", "4,930.22%", body_font, bold_font)
    metric_card(canvas, 18 * mm + card_w + gap, card_y1, card_w, "年化收益", "101.61%", body_font, bold_font)
    metric_card(canvas, 18 * mm + 2 * (card_w + gap), card_y1, card_w, "最大平仓回撤", "19.63%", body_font, bold_font)
    card_y2 = height - 118 * mm
    metric_card(canvas, 18 * mm, card_y2, card_w, "期末权益", "5,030.22万元", body_font, bold_font)
    metric_card(canvas, 18 * mm + card_w + gap, card_y2, card_w, "闭环交易", "32笔", body_font, bold_font)
    metric_card(canvas, 18 * mm + 2 * (card_w + gap), card_y2, card_w, "Sharpe / 盈亏比", "1.52 / 4.33", body_font, bold_font)

    y = height - 132 * mm
    y = draw_paragraph(canvas, "项目概述", 18 * mm, y, 174 * mm, heading) - 3 * mm
    overview = "从自然语言策略到可审计的事件驱动回测，覆盖34个非农商品品种。系统联读行情、交割估值、动态保证金、合约生命周期、交割标准和资讯可得性，严格区分筛选层与执行层，并在账户层统一处理方向风险和总风险。"
    y = draw_paragraph(canvas, overview, 18 * mm, y, 174 * mm, body) - 6 * mm
    y = draw_paragraph(canvas, "工程链路", 18 * mm, y, 174 * mm, heading) - 3 * mm
    steps = "① 数据快照与质量门禁　② 品种筛选与偏离择优　③ 品种束与账户风险预算　④ 委托、加仓与分阶段退出　⑤ 逐笔成交与逐日账户复算　⑥ 独立审计与同源报告"
    y = draw_paragraph(canvas, steps, 18 * mm, y, 174 * mm, body) - 6 * mm
    y = draw_paragraph(canvas, "结果解释", 18 * mm, y, 174 * mm, heading) - 3 * mm
    draw_paragraph(canvas, "回测区间2021-01-04至2026-08-07，初始权益100万元，期末无未平仓。收益集中度较高，普通最大回撤56.29%，最大账户风险度92.74%，不能只看期末收益。", 18 * mm, y, 174 * mm, body)
    page_footer(canvas, 1, body_font)
    canvas.showPage()

    canvas.setFillColor(colors.HexColor("#07111F"))
    canvas.rect(0, height - 28 * mm, width, 28 * mm, fill=1, stroke=0)
    canvas.setFillColor(colors.white)
    canvas.setFont(bold_font, 18)
    canvas.drawString(18 * mm, height - 18 * mm, "验证证据与研究边界")

    y = height - 40 * mm
    y = draw_paragraph(canvas, "审计证据", 18 * mm, y, 174 * mm, heading) - 3 * mm
    audit_text = "693项自动化测试通过；95,686项独立审计断言通过；32笔交易周期逐笔复核；1,356个交易日从成交记录重新计算权益；69条成交检查价格范围、数量、成本和保证金；正式输出完整性审计状态为PASS。"
    y = draw_paragraph(canvas, audit_text, 18 * mm, y, 174 * mm, body) - 7 * mm

    y = draw_paragraph(canvas, "研究边界", 18 * mm, y, 174 * mm, heading) - 3 * mm
    limits = [
        "成本：手续费和滑点均为零，未测试成交冲击与市场容量。",
        "撮合：日线高低价仅证明阈值触达，不能恢复真实盘中先后顺序。",
        "资金：同一开盘批次使用统一权益快照，日内资金释放不重新分配。",
        "估值：部分交割锚采用经确认的研究算法，不标作官方最终交割价。",
        "数据：候选缺项时跳过，持仓关键数据缺失时终止，不制造成交价格。",
        "用途：这是研究型历史回测，不是实盘业绩、收益承诺或投资建议。",
    ]
    for item in limits:
        y = draw_paragraph(canvas, "• " + item, 21 * mm, y, 168 * mm, body) - 2.2 * mm

    y -= 4 * mm
    y = draw_paragraph(canvas, "公开内容", 18 * mm, y, 174 * mm, heading) - 3 * mm
    draw_paragraph(canvas, "GitHub仓库提供项目页、结构化指标、方法说明、正式曲线和可审阅的Python架构节选。私人数据库、完整输入快照、个人凭据以及完整专有参数组合不公开。", 18 * mm, y, 174 * mm, body)

    canvas.setStrokeColor(colors.HexColor("#58D3C0"))
    canvas.setFillColor(colors.HexColor("#F1F7F7"))
    canvas.roundRect(18 * mm, 37 * mm, 174 * mm, 29 * mm, 2 * mm, fill=1, stroke=1)
    canvas.setFillColor(colors.HexColor("#07111F"))
    canvas.setFont(bold_font, 10)
    canvas.drawString(23 * mm, 55 * mm, "项目链接")
    canvas.setFont(body_font, 9)
    canvas.drawString(23 * mm, 47 * mm, "https://yanzhen-cpu.github.io/Yangzhenxue/")
    canvas.setFont(body_font, 7.4)
    canvas.setFillColor(colors.HexColor("#5E6B7A"))
    canvas.drawString(23 * mm, 41 * mm, "Source run: STRAT026-FULL-MAIN-20260912 · Formal audit: PASS")
    page_footer(canvas, 2, body_font)
    canvas.save()


if __name__ == "__main__":
    main()
