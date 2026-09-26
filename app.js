async function renderYearlyResults() {
  const container = document.querySelector('#year-grid');
  if (!container) return;
  try {
    const response = await fetch('data/public-metrics.json');
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    const data = await response.json();
    container.innerHTML = Object.entries(data.yearly_realized_pnl).map(([year, pnl]) => {
      const signClass = pnl < 0 ? 'negative' : '';
      const value = `${pnl > 0 ? '+' : ''}${(pnl / 10000).toLocaleString('zh-CN', { maximumFractionDigits: 1 })}万`;
      return `<article><span>${year}</span><strong class="${signClass}">${value}</strong></article>`;
    }).join('');
    const year = data.year_2026;
    const amount = value => (value / 10000).toLocaleString('zh-CN', {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    });
    document.querySelector('#year-context').textContent =
      `2026年截至${data.period.end}，${year.closed_trades}笔交易均以成本价退出，已实现盈亏为0；` +
      `但持仓期间权益并非不变：日终最高${amount(year.high_equity)}万元（${year.high_date}），` +
      `最低${amount(year.low_equity)}万元（${year.low_date}），样本末回到${amount(year.end_equity)}万元。`;
  } catch (error) {
    container.innerHTML = '<p class="data-error">年度数据加载失败，请查看结构化指标文件。</p>';
    document.querySelector('#year-context').textContent = '';
  }
}

renderYearlyResults();
