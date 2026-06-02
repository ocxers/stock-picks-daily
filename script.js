document.addEventListener('DOMContentLoaded', () => {
    const todayDateEl = document.getElementById('today-date');
    const picksContainer = document.getElementById('picks-container');
    const historyContainer = document.getElementById('history-container');

    fetch('data.json')
        .then(response => response.json())
        .then(data => {
            // Render Today's Picks
            todayDateEl.textContent = data.current_picks[0].date;
            
            if (data.current_picks.length > 0) {
                picksContainer.innerHTML = data.current_picks.map(stock => `
                    <div class="stock-card">
                        <span class="ticker">${stock.ticker}</span>
                        <span class="price">Entry: $${stock.entry_price.toFixed(2)}</span>
                    </div>
                `).join('');
            } else {
                picksContainer.innerHTML = '<p>No picks available for today.</p>';
            }

            // Render Yesterday's Review (History)
            if (data.history && data.history.length > 0) {
                const yesterday = data.history[0];
                historyContainer.innerHTML = `
                    <div class="stock-card">
                        <span class="ticker">${yesterday.date}</span>
                        ${yesterday.picks.map(pick => {
                            const pnlClass = pick.pnl_pct.startsWith('+') ? 'pnl-positive' : 'pnl-negative';
                            return `
                                <div style="margin-top: 10px; display: flex; justify-content: space-between;">
                                    <span>${pick.ticker} (Entry: $${pick.entry_price.toFixed(2)})</span>
                                    <span class="${pnlClass}">${pick.pnl_pct}</span>
                                </div>
                            `;
                        }).join('')}
                    </div>
                `;
            } else {
                historyContainer.innerHTML = '<p>No history available yet.</p>';
            }
        })
        .catch(error => {
            console.error('Error loading data:', error);
            picksContainer.innerHTML = '<p>Error loading stock data. Please try again later.</p>';
        });
});
