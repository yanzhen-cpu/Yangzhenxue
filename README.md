# 商品期货估值与风险控制系统

这是策略0.6.2的公开招聘展示版。项目覆盖策略形式化、历史数据治理、日频事件驱动回测、组合风险控制、逐笔审计和结果呈现。

[在线项目页](https://yanzhen-cpu.github.io/Yangzhenxue/) · [网页阅读代码](https://yanzhen-cpu.github.io/Yangzhenxue/code.html) · [GitHub源码节选](src/strategy_pipeline.py) · [招聘版PDF](reports/STRAT-026-v0.6.2-project-brief.pdf)

## 核心结果

| 指标 | 结果 |
|---|---:|
| 回测区间 | 2021-01-04至2026-08-07 |
| 初始权益 | 100万元 |
| 期末权益 | 5030.22万元 |
| 累计收益 | 4930.22% |
| 年化收益 | 101.61% |
| 最大平仓回撤 | 19.63% |
| Sharpe | 1.52 |
| 闭环交易 | 32笔 |
| 胜率 | 46.88% |
| 平均盈亏比 | 4.33 |

## 项目工作

- 将自然语言策略拆分为筛选、择优、委托、持仓、退出和组合风控六类状态规则。
- 建立34个非农商品品种的行情、动态保证金、合约周期、交割标准、主力身份和资讯可得性数据链。
- 实现逐日权益、保证金占用、方向风险、账户风险和三类回撤的同源计算。
- 对32笔完整交易执行逐笔回放，对1356个交易日执行账户会计复算。
- 通过693项测试、95686项独立审计断言和正式输出完整性审计。

## 阅读边界

这是研究型历史回测，不是实盘业绩或投资建议。主结果采用零手续费、零滑点和日频阈值成交口径；开盘批次权益为近似值，部分交割锚采用经确认的研究口径。公开仓库展示系统结构、关键不变式和审计证据，不提供私人数据库或完整专有参数组合。

分年度数字为按平仓年度归属的已实现盈亏。2026年截至8月7日共有3笔交易，均在成本价退出，因此已实现盈亏为0；持仓期间日终权益在2743.53万至6276.41万元之间波动。

## 目录

```text
assets/   verified charts
data/     compact public result data
docs/     methodology and build records
reports/  recruiter-facing PDF
scripts/  deterministic build and checks
src/      reviewable strategy architecture excerpt
```

Source run: `STRAT026-FULL-MAIN-20260912`<br>
Strategy version: `0.6.2`<br>
Formal audit: `pass`
