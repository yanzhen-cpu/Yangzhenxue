async function renderAnnualAccountChange() {
  const grid = document.querySelector('#annual-grid');
  const context = document.querySelector('#annual-context');
  if (!grid || !context) return;
  try {
    const response = await fetch('data/public-metrics.json');
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    const data = await response.json();
    const formatWan = value => (value / 10000).toLocaleString('zh-CN', {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    });
    grid.innerHTML = Object.entries(data.annual_account_change).map(([year, entry]) => {
      const amount = `${entry.change > 0 ? '+' : ''}${formatWan(entry.change)}万`;
      const percent = `${entry.return > 0 ? '+' : ''}${(entry.return * 100).toFixed(2)}%`;
      return `<article><span>${year}</span><strong class="${entry.change < 0 ? 'negative' : ''}">${amount}</strong><small>${percent}</small></article>`;
    }).join('');
    const y = data.year_2026;
    const account = data.annual_account_change['2026'];
    context.textContent =
      `2026年截至${account.end_date}：相对2025年末，账户权益增加${formatWan(account.change)}万元` +
      `（${(account.return * 100).toFixed(2)}%）。${y.closed_cycles}个在2026年完成的周期合计净盈亏` +
      `${formatWan(y.completed_cycle_pnl)}万元，按最终退出年归属；两者不同，是因为跨年持仓和换月分腿的盈亏确认时点不同。`;
  } catch (error) {
    grid.innerHTML = '<p class="data-error">年度账户数据加载失败，请查看结构化指标。</p>';
    context.textContent = '';
  }
}

renderAnnualAccountChange();
