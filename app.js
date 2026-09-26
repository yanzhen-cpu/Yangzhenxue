async function renderYearlyResults() {
  const container = document.querySelector('#year-grid');
  if (!container) return;
  try {
    const response = await fetch('data/public-metrics.json');
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    const data = await response.json();
    container.innerHTML = Object.entries(data.yearly_realized_pnl).map(([year, pnl]) => {
      const signClass = pnl < 0 ? 'negative' : '';
      const value = `${pnl >= 0 ? '+' : ''}${(pnl / 10000).toLocaleString('zh-CN', { maximumFractionDigits: 1 })}万`;
      return `<article><span>${year}</span><strong class="${signClass}">${value}</strong></article>`;
    }).join('');
  } catch (error) {
    container.innerHTML = '<p class="data-error">年度数据加载失败，请查看结构化指标文件。</p>';
  }
}

renderYearlyResults();
