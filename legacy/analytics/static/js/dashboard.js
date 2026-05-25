// Vedic Analytics Dashboard JS

let lagnaChart = null;

// Zodiac sign order: Aries to Pisces
const ZODIAC_ORDER = [
    'Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo',
    'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces'
];

// Initialize on page load
document.addEventListener('DOMContentLoaded', async () => {
    console.log("📊 Initializing dashboard...");
    await loadSummary();
    await loadLagna();
    await loadYogas();
    await loadCombustion();
    await loadRetrograde();
    await loadExaltedDebilitated();
    await loadAfflicted();
    await loadSunMoonYogas();
    await loadCombos(2, 'combos2List');
    await loadCombos(3, 'combos3List');
    await loadCombos(4, 'combos4List');
    await loadCombos(5, 'combos5List');
    await loadCombos(6, 'combos6List');
    await loadHeatmap();
    await loadAvashaMatrix();
    await loadStrengths();
    console.log("✅ Dashboard loaded");
});

// Load summary statistics
async function loadSummary() {
    try {
        const response = await fetch('/api/stats/summary');
        const data = await response.json();
        
        document.getElementById('totalCharts').textContent = data.total_charts;
        document.getElementById('lagnaCount').textContent = data.lagna_count;
        document.getElementById('combos2Count').textContent = data.combos_2_count;
        document.getElementById('combos3Count').textContent = data.combos_3_count;
        document.getElementById('combos4Count').textContent = data.combos_4_count;
        document.getElementById('combos5Count').textContent = data.combos_5_count;
        document.getElementById('combos6Count').textContent = data.combos_6_count;
        document.getElementById('combustionCount').textContent = data.combustion_count;
        document.getElementById('retrogradeCount').textContent = data.retrograde_count;
        document.getElementById('exaltedCount').textContent = data.exalted_count;
        document.getElementById('debilitatedCount').textContent = data.debilitated_count;
        document.getElementById('afflictedCount').textContent = data.afflicted_count;
        document.getElementById('sunYogasCount').textContent = data.sun_yogas_count;
        document.getElementById('moonYogasCount').textContent = data.moon_yogas_count;
        document.getElementById('yogasCount').textContent = data.yogas_count;
    } catch (error) {
        console.error("Error loading summary:", error);
    }
}

// Load Lagna distribution
async function loadLagna() {
    try {
        const response = await fetch('/api/lagna');
        const data = await response.json();
        
        // Chart.js chart
        const ctx = document.getElementById('lagnaChart').getContext('2d');
        
        // Sort by zodiac order (Aries to Pisces)
        const labels = ZODIAC_ORDER.filter(sign => sign in data.data);
        const counts = labels.map(sign => data.data[sign].count);
        
        if (lagnaChart) lagnaChart.destroy();
        
        lagnaChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Count',
                    data: counts,
                    backgroundColor: [
                        '#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A',
                        '#98D8C8', '#F7DC6F', '#BB8FCE', '#85C1E2',
                        '#F8B88B', '#A8D8D8', '#F7C59F', '#FFAFCC'
                    ],
                    borderRadius: 5,
                    hoverBackgroundColor: '#667eea',
                    borderColor: '#333',
                    borderWidth: 1
                }]
            },
            options: {
                indexAxis: 'x',
                responsive: true,
                maintainAspectRatio: true,
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        callbacks: {
                            afterLabel: (context) => {
                                const sign = labels[context.dataIndex];
                                const count = data.data[sign].count;
                                return `Charts: ${count}`;
                            }
                        }
                    }
                },
                scales: {
                    y: { beginAtZero: true }
                },
                onClick: (event, elements) => {
                    if (elements.length > 0) {
                        const index = elements[0].index;
                        const sign = labels[index];
                        showChartsModal(`${sign} (${counts[index]} charts)`, `/api/charts/by-lagna/${sign}`);
                    }
                }
            }
        });
        
    } catch (error) {
        console.error("Error loading lagna:", error);
    }
}

// Load Combustion (Asta)
async function loadCombustion() {
    try {
        const response = await fetch('/api/combustion');
        const data = await response.json();
        
        const container = document.getElementById('combustionList');
        container.innerHTML = '';
        
        if (Object.keys(data.data).length === 0) {
            container.innerHTML = '<p class="text-muted">No combustion detected</p>';
            return;
        }
        
        Object.entries(data.data).forEach(([planet, details]) => {
            const div = document.createElement('div');
            div.className = 'combo-item';
            div.style.cursor = 'pointer';
            div.innerHTML = `
                <strong>${planet}</strong> <span class="badge bg-danger">Combust</span>
                <span class="combo-count">${details.count}</span>
                <div style="clear: both; font-size: 12px; color: #666; margin-top: 4px;">
                    ${details.charts.length} charts affected
                </div>
            `;
            div.addEventListener('click', () => showChartsModal(`${planet} Combustion (${details.count} charts)`, `/api/charts/by-combustion/${planet}`));
            container.appendChild(div);
        });
    } catch (error) {
        console.error("Error loading combustion:", error);
    }
}

// Load Retrograde (Vakra)
async function loadRetrograde() {
    try {
        const response = await fetch('/api/retrograde');
        const data = await response.json();
        
        const container = document.getElementById('retrogradeList');
        container.innerHTML = '';
        
        if (Object.keys(data.data).length === 0) {
            container.innerHTML = '<p class="text-muted">No retrograde planets detected</p>';
            return;
        }
        
        Object.entries(data.data).forEach(([planet, details]) => {
            const div = document.createElement('div');
            div.className = 'combo-item';
            div.style.cursor = 'pointer';
            div.innerHTML = `
                <strong>${planet}</strong> <span class="badge bg-warning">Retrograde</span>
                <span class="combo-count">${details.count}</span>
                <div style="clear: both; font-size: 12px; color: #666; margin-top: 4px;">
                    ${details.charts.length} charts affected
                </div>
            `;
            div.addEventListener('click', () => showChartsModal(`${planet} Retrograde (${details.count} charts)`, `/api/charts/by-retrograde/${planet}`));
            container.appendChild(div);
        });
    } catch (error) {
        console.error("Error loading retrograde:", error);
    }
}

// Load Exalted & Debilitated Planets
async function loadExaltedDebilitated() {
    try {
        const response = await fetch('/api/exalted-debilitated');
        const data = await response.json();
        
        // Load Exalted
        const exaltedContainer = document.getElementById('exaltedList');
        exaltedContainer.innerHTML = '';
        
        const exalted = data.exalted || {};
        if (Object.keys(exalted).length === 0) {
            exaltedContainer.innerHTML = '<p class="text-muted">No exalted planets detected</p>';
        } else {
            Object.entries(exalted).forEach(([planet, details]) => {
                const div = document.createElement('div');
                div.className = 'combo-item';
                div.style.cursor = 'pointer';
                div.innerHTML = `
                    <strong>${planet}</strong> <span class="badge bg-success">Exalted</span>
                    <span class="combo-count">${details.count}</span>
                    <div style="clear: both; font-size: 12px; color: #666; margin-top: 4px;">
                        ${details.charts.length} charts affected
                    </div>
                `;
                div.addEventListener('click', () => showChartsModal(`${planet} Exalted (${details.count} charts)`, `/api/charts/by-exalted/${planet}`));
                exaltedContainer.appendChild(div);
            });
        }
        
        // Load Debilitated
        const debilitatedContainer = document.getElementById('debilitatedList');
        debilitatedContainer.innerHTML = '';
        
        const debilitated = data.debilitated || {};
        if (Object.keys(debilitated).length === 0) {
            debilitatedContainer.innerHTML = '<p class="text-muted">No debilitated planets detected</p>';
        } else {
            Object.entries(debilitated).forEach(([planet, details]) => {
                const div = document.createElement('div');
                div.className = 'combo-item';
                div.style.cursor = 'pointer';
                div.innerHTML = `
                    <strong>${planet}</strong> <span class="badge bg-danger">Debilitated</span>
                    <span class="combo-count">${details.count}</span>
                    <div style="clear: both; font-size: 12px; color: #666; margin-top: 4px;">
                        ${details.charts.length} charts affected
                    </div>
                `;
                div.addEventListener('click', () => showChartsModal(`${planet} Debilitated (${details.count} charts)`, `/api/charts/by-debilitated/${planet}`));
                debilitatedContainer.appendChild(div);
            });
        }
    } catch (error) {
        console.error("Error loading exalted/debilitated:", error);
    }
}

// Load Afflicted Planets
async function loadAfflicted() {
    try {
        const response = await fetch('/api/afflicted');
        const data = await response.json();
        
        const container = document.getElementById('afflictedList');
        container.innerHTML = '';
        
        if (Object.keys(data.data).length === 0) {
            container.innerHTML = '<p class="text-muted">No afflicted planets detected</p>';
            return;
        }
        
        Object.entries(data.data).forEach(([planet, details]) => {
            const div = document.createElement('div');
            div.className = 'combo-item';
            div.style.cursor = 'pointer';
            div.innerHTML = `
                <strong>${planet}</strong> <span class="badge bg-warning">Afflicted</span>
                <span class="combo-count">${details.count}</span>
                <div style="clear: both; font-size: 12px; color: #666; margin-top: 4px;">
                    ${details.charts.length} charts affected
                </div>
            `;
            div.addEventListener('click', () => showChartsModal(`${planet} Afflicted (${details.count} charts)`, `/api/charts/by-afflicted/${planet}`));
            container.appendChild(div);
        });
    } catch (error) {
        console.error("Error loading afflicted:", error);
    }
}

// Load Sun & Moon Yogas
async function loadSunMoonYogas() {
    try {
        const response = await fetch('/api/sun-moon-yogas');
        const data = await response.json();
        
        // Load Sun Yogas
        const sunContainer = document.getElementById('sunYogasList');
        if (sunContainer) {
            sunContainer.innerHTML = '';
            
            const sunYogasData = data.sun_yogas || {};
            if (Object.keys(sunYogasData).length === 0) {
                sunContainer.innerHTML = '<p class="text-muted">No Sun yogas detected</p>';
            } else {
                Object.entries(sunYogasData).forEach(([yoga, count]) => {
                    const div = document.createElement('div');
                    div.className = 'combo-item';
                    div.style.cursor = 'pointer';
                    div.innerHTML = `
                        <strong>${yoga}</strong> <span class="badge bg-info">Sun Yoga</span>
                        <span class="combo-count">${count}</span>
                        <div style="clear: both;"></div>
                    `;
                    div.addEventListener('click', () => showChartsModal(`${yoga} (Sun Yoga - ${count} charts)`, `/api/charts/by-sun-yoga/${yoga}`));
                    sunContainer.appendChild(div);
                });
            }
        }
        
        // Load Moon Yogas
        const moonContainer = document.getElementById('moonYogasList');
        if (moonContainer) {
            moonContainer.innerHTML = '';
            
            const moonYogasData = data.moon_yogas || {};
            if (Object.keys(moonYogasData).length === 0) {
                moonContainer.innerHTML = '<p class="text-muted">No Moon yogas detected</p>';
            } else {
                Object.entries(moonYogasData).forEach(([yoga, count]) => {
                    const div = document.createElement('div');
                    div.className = 'combo-item';
                    div.style.cursor = 'pointer';
                    div.innerHTML = `
                        <strong>${yoga}</strong> <span class="badge bg-info">Moon Yoga</span>
                        <span class="combo-count">${count}</span>
                        <div style="clear: both;"></div>
                    `;
                    div.addEventListener('click', () => showChartsModal(`${yoga} (Moon Yoga - ${count} charts)`, `/api/charts/by-moon-yoga/${yoga}`));
                    moonContainer.appendChild(div);
                });
            }
        }
    } catch (error) {
        console.error("Error loading sun/moon yogas:", error);
    }
}

// Load Yogas
async function loadYogas() {
    try {
        const response = await fetch('/api/yogas');
        const data = await response.json();
        
        const container = document.getElementById('yogasList');
        container.innerHTML = '';
        
        Object.entries(data.data).slice(0, 10).forEach(([yoga, count]) => {
            const div = document.createElement('div');
            div.className = 'yoga-item';
            div.innerHTML = `
                <strong>${yoga}</strong>
                <span class="combo-count">${count}</span>
                <div style="clear: both;"></div>
            `;
            container.appendChild(div);
        });
    } catch (error) {
        console.error("Error loading yogas:", error);
    }
}

// Load N-planet combos
async function loadCombos(numPlanets, elementId) {
    try {
        const response = await fetch(`/api/combos/${numPlanets}`);
        const data = await response.json();
        
        const container = document.getElementById(elementId);
        container.innerHTML = '';
        
        Object.entries(data.data).forEach(([combo, details]) => {
            const div = document.createElement('div');
            div.className = 'combo-item';
            div.style.cursor = 'pointer';
            div.innerHTML = `
                <strong>${combo}</strong>
                <span class="combo-count">${details.count}</span>
                <div style="clear: both;"></div>
            `;
            div.addEventListener('click', () => showChartsModal(combo, `/api/charts/by-combo/${combo}`));
            container.appendChild(div);
        });
        
        if (Object.keys(data.data).length === 0) {
            container.innerHTML = '<p class="text-muted">No data</p>';
        }
    } catch (error) {
        console.error(`Error loading ${numPlanets}-planet combos:`, error);
    }
}

// Load Heatmap
async function loadHeatmap() {
    try {
        const response = await fetch('/api/planet-rashi-heatmap');
        const heatmap = await response.json();
        
        const container = document.getElementById('heatmapContainer');
        
        // Get all signs
        const signs = ['Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo', 
                       'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces'];
        
        let html = '<table class="heatmap-table"><tr><th>Planet</th>';
        signs.forEach(sign => html += `<th>${sign.slice(0, 3)}</th>`);
        html += '</tr>';
        
        Object.entries(heatmap).forEach(([planet, counts]) => {
            html += `<tr><th>${planet}</th>`;
            signs.forEach(sign => {
                const count = counts[sign] || 0;
                const heatClass = count === 0 ? 'heat-0' : count <= 1 ? 'heat-1' : count <= 2 ? 'heat-2' : count <= 3 ? 'heat-3' : count <= 4 ? 'heat-4' : count <= 5 ? 'heat-5' : 'heat-6';
                html += `<td class="heatmap-cell ${heatClass}" data-planet="${planet}" data-rashi="${sign}" style="cursor: pointer;">${count}</td>`;
            });
            html += '</tr>';
        });
        
        html += '</table>';
        container.innerHTML = html;
        
        // Add click handlers to cells
        document.querySelectorAll('.heatmap-cell').forEach(cell => {
            cell.addEventListener('click', async (e) => {
                const planet = e.target.dataset.planet;
                const rashi = e.target.dataset.rashi;
                const count = e.target.textContent;
                
                if (count === '0') {
                    alert(`No charts found with ${planet} in ${rashi}`);
                    return;
                }
                
                showChartsModal(`${planet} in ${rashi} (${count} charts)`, `/api/charts/by-planet-rashi/${planet}/${rashi}`);
            });
            
            cell.addEventListener('mouseenter', (e) => {
                e.target.style.opacity = '0.8';
                e.target.style.transform = 'scale(1.05)';
                e.target.style.transition = 'all 0.2s';
            });
            
            cell.addEventListener('mouseleave', (e) => {
                e.target.style.opacity = '1';
                e.target.style.transform = 'scale(1)';
            });
        });
    } catch (error) {
        console.error("Error loading heatmap:", error);
    }
}

// Load Avastha Matrix
async function loadAvashaMatrix() {
    try {
        const response = await fetch('/api/avastha-matrix');
        const matrix = await response.json();
        
        const container = document.getElementById('avashaMatrixContainer');
        
        // Define avastas in order
        const avastas = ['Garvita', 'Kshobhita', 'Kshudita', 'Lajjita', 'Mudita', 'Trashita'];
        
        // Build table header
        let html = '<table class="heatmap-table"><tr><th>Planet</th>';
        avastas.forEach(avasta => html += `<th>${avasta.slice(0, 6)}</th>`);
        html += '</tr>';
        
        // Build table rows for each planet
        Object.entries(matrix).forEach(([planet, avasthaCounts]) => {
            html += `<tr><th>${planet}</th>`;
            avastas.forEach(avasta => {
                const count = avasthaCounts[avasta] || 0;
                const heatClass = count === 0 ? 'heat-0' : count <= 1 ? 'heat-1' : count <= 2 ? 'heat-2' : count <= 3 ? 'heat-3' : count <= 4 ? 'heat-4' : count <= 5 ? 'heat-5' : 'heat-6';
                html += `<td class="avastha-cell ${heatClass}" data-planet="${planet}" data-avasta="${avasta}" style="cursor: pointer;">${count}</td>`;
            });
            html += '</tr>';
        });
        
        html += '</table>';
        container.innerHTML = html;
        
        // Add click handlers to cells
        document.querySelectorAll('.avastha-cell').forEach(cell => {
            cell.addEventListener('click', async (e) => {
                const planet = e.target.dataset.planet;
                const avasta = e.target.dataset.avasta;
                const count = e.target.textContent;
                
                if (count === '0') {
                    alert(`No charts found with ${planet} in ${avasta}`);
                    return;
                }
                
                showChartsModal(`${planet} in ${avasta} (${count} charts)`, `/api/charts/by-planet-avasta/${planet}/${avasta}`);
            });
            
            cell.addEventListener('mouseenter', (e) => {
                e.target.style.opacity = '0.8';
                e.target.style.transform = 'scale(1.05)';
                e.target.style.transition = 'all 0.2s';
            });
            
            cell.addEventListener('mouseleave', (e) => {
                e.target.style.opacity = '1';
                e.target.style.transform = 'scale(1)';
            });
        });
    } catch (error) {
        console.error("Error loading avastha matrix:", error);
    }
}

// Load Planetary Strengths
async function loadStrengths() {
    try {
        const response = await fetch('/api/strengths');
        const data = await response.json();
        
        renderStrengthList('strongPlanets', data.strong, '💪');
        renderStrengthList('moderatePlanets', data.moderate, '⚖️');
        renderStrengthList('weakPlanets', data.weak, '📉');
    } catch (error) {
        console.error("Error loading strengths:", error);
    }
}

function renderStrengthList(elementId, data, emoji) {
    const container = document.getElementById(elementId);
    container.innerHTML = '';
    
    Object.entries(data).sort((a, b) => b[1] - a[1]).forEach(([planet, count]) => {
        const div = document.createElement('div');
        div.className = 'strength-item';
        div.innerHTML = `${emoji} <strong>${planet}</strong> <span class="combo-count">${count}</span>`;
        container.appendChild(div);
    });
}

// Show Charts Modal
async function showChartsModal(title, apiUrl) {
    try {
        const response = await fetch(apiUrl);
        const data = await response.json();
        
        document.getElementById('modalTitle').textContent = title;
        
        const tbody = document.getElementById('chartsTable');
        tbody.innerHTML = '';
        
        if (data.charts && data.charts.length > 0) {
            data.charts.forEach(chart => {
                const row = document.createElement('tr');
                row.style.cursor = 'pointer';
                row.innerHTML = `
                    <td><a href="/chart/${chart.id}" style="text-decoration: none; color: inherit;">${chart.id}</a></td>
                    <td><a href="/chart/${chart.id}" style="text-decoration: none; color: inherit;">${chart.name}</a></td>
                    <td><a href="/chart/${chart.id}" style="text-decoration: none; color: inherit;">${chart.birth_time}</a></td>
                    <td><a href="/chart/${chart.id}" style="text-decoration: none; color: inherit;">${chart.location}</a></td>
                `;
                row.addEventListener('click', () => window.location.href = `/chart/${chart.id}`);
                tbody.appendChild(row);
            });
        } else {
            tbody.innerHTML = '<tr><td colspan="4" class="text-center text-muted">No charts found</td></tr>';
        }
        
        const modal = new bootstrap.Modal(document.getElementById('chartsModal'));
        modal.show();
    } catch (error) {
        console.error("Error showing charts:", error);
        alert("Error loading charts");
    }
}

// Refresh cache
async function refreshCache() {
    if (confirm('🔄 Regenerate analytics cache? This may take a moment...')) {
        try {
            const response = await fetch('/api/refresh-cache');
            const data = await response.json();
            alert('✅ Cache refreshed! ' + data.status);
            location.reload();
        } catch (error) {
            alert('❌ Error refreshing cache');
        }
    }
}
