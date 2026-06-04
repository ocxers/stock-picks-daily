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
                        <div class="price">Entry: $${stock.entry_price.toFixed(2)}</div>
                        
                        ${stock.target_price ? `<div class="target">Target: $${stock.target_price.toFixed(2)}</div>` : ''}
                        
                        <div class="reason-text">${stock.reason}</div>

                        <div class="sources">
                            <strong>Sources:</strong><br>
                            ${stock.sources.map(url => `<a href="${url}" target="_blank">${new URL(url).hostname.replace('www.', '')}</a>`).join('')}
                        </div>
                    </div>
                `).join('');
            } else {
                picksContainer.innerHTML = '<p>No picks available for today.</p>';
            }

            // Render All History Records
            if (data.history && data.history.length > 0) {
                historyContainer.innerHTML = data.history.map(day => `
                    <div class="stock-card">
                        <span class="ticker">${day.date}</span>
                        ${day.picks.map(pick => {
                            const pnlClass = pick.pnl_pct.startsWith('+') ? 'pnl-positive' : 'pnl-negative';
                            return `
                                <div style="margin-top: 10px; display: flex; justify-content: space-between;">
                                    <span>${pick.ticker} (Entry: $${pick.entry_price.toFixed(2)})</span>
                                    <span class="${pnlClass}">${pick.pnl_pct}</span>
                                </div>
                            `;
                        }).join('')}
                    </div>
                `).join('');
            } else {
                historyContainer.innerHTML = '<p>No history available yet.</p>';
            }
        })
        .catch(error => {
            console.error('Error loading data:', error);
            picksContainer.innerHTML = '<p>Error loading stock data. Please try again later.</p>';
        });
});
