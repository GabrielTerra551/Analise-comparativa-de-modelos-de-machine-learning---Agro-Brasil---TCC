const state = {
    metadata: null,
    chartSelections: {},
};

const metricFormat = new Intl.NumberFormat('pt-BR', {
    minimumFractionDigits: 4,
    maximumFractionDigits: 4,
});

const controls = {
    modelos: document.getElementById('modelos'),
    datasets: document.getElementById('datasets'),
    tickers: document.getElementById('tickers'),
    horizontes: document.getElementById('horizontes'),
    metricaOrdenar: document.getElementById('metrica_ordenar'),
    ordemDesc: document.getElementById('ordem_desc'),
    topN: document.getElementById('top_n'),
    topNValue: document.getElementById('top_n_value'),
    heatmapMetric: document.getElementById('heatmap_metric'),
    heatmapHorizon: document.getElementById('heatmap_horizon'),
    evolutionMetric: document.getElementById('evolution_metric'),
    evolutionTicker: document.getElementById('evolution_ticker'),
    boxMetric: document.getElementById('box_metric'),
};

function getTipoSelecionado() {
    return document.querySelector('input[name="tipo"]:checked')?.value || 'Regressão';
}

function setAlert(message = '', kind = 'warning') {
    const alertBox = document.getElementById('alert-box');
    if (!message) {
        alertBox.classList.add('hidden');
        alertBox.textContent = '';
        alertBox.classList.remove('alert-error');
        return;
    }
    alertBox.textContent = message;
    alertBox.classList.remove('hidden');
    alertBox.classList.toggle('alert-error', kind === 'error');
}

function fillSelect(container, options, selectedValues = []) {
    const selected = new Set(selectedValues.length ? selectedValues : options);
    container.innerHTML = '';
    options.forEach((optionValue) => {
        const label = document.createElement('label');
        label.className = 'checkbox-item' + (selected.has(optionValue) ? ' is-checked' : '');

        const input = document.createElement('input');
        input.type = 'checkbox';
        input.value = optionValue;
        input.checked = selected.has(optionValue);

        input.addEventListener('change', () => {
            label.classList.toggle('is-checked', input.checked);
        });

        const span = document.createElement('span');
        span.textContent = optionValue;

        label.appendChild(input);
        label.appendChild(span);
        container.appendChild(label);
    });
}

function fillSingleSelect(select, options, selectedValue) {
    select.innerHTML = '';
    options.forEach((optionValue) => {
        const option = document.createElement('option');
        option.value = optionValue;
        option.textContent = optionValue;
        option.selected = optionValue === selectedValue;
        select.appendChild(option);
    });
}

function getMultiSelectValues(container) {
    return Array.from(container.querySelectorAll('input[type="checkbox"]:checked')).map((cb) => cb.value);
}

function formatValue(value) {
    return typeof value === 'number' ? metricFormat.format(value) : (value ?? '-');
}

function sanitizeText(value) {
    return value ?? '-';
}

function updateTopNDisplay() {
    controls.topNValue.textContent = controls.topN.value;
}

async function fetchMetadata(tipo) {
    const response = await fetch(`/api/metadata?tipo=${encodeURIComponent(tipo)}`);
    if (!response.ok) {
        throw new Error('Não foi possível carregar os metadados do dashboard.');
    }
    return response.json();
}

function applyMetadata(metadata, { resetCharts = true } = {}) {
    state.metadata = metadata;
    const { options, defaults } = metadata;

    fillSelect(controls.modelos, options.modelos, defaults.modelos);
    fillSelect(controls.datasets, options.datasets, defaults.datasets);
    fillSelect(controls.tickers, options.tickers, defaults.tickers);
    fillSelect(controls.horizontes, options.horizontes, defaults.horizontes);
    fillSingleSelect(controls.metricaOrdenar, options.metricas, defaults.metrica_ordenar);

    controls.ordemDesc.checked = defaults.ordem_desc;
    controls.topN.min = options.top_n_min || 1;
    controls.topN.max = Math.max(1, options.top_n_max || 1);
    controls.topN.value = defaults.top_n;
    updateTopNDisplay();

    if (resetCharts) {
        state.chartSelections = {};
    }
}

function buildPayload() {
    return {
        tipo: getTipoSelecionado(),
        modelos: getMultiSelectValues(controls.modelos),
        datasets: getMultiSelectValues(controls.datasets),
        tickers: getMultiSelectValues(controls.tickers),
        horizontes: getMultiSelectValues(controls.horizontes),
        metrica_ordenar: controls.metricaOrdenar.value,
        ordem_desc: controls.ordemDesc.checked,
        top_n: Number(controls.topN.value),
        heatmap_metric: controls.heatmapMetric.value || state.chartSelections.heatmap_metric,
        heatmap_horizon: controls.heatmapHorizon.value || state.chartSelections.heatmap_horizon,
        evolution_metric: controls.evolutionMetric.value || state.chartSelections.evolution_metric,
        evolution_ticker: controls.evolutionTicker.value || state.chartSelections.evolution_ticker,
        box_metric: controls.boxMetric.value || state.chartSelections.box_metric,
    };
}

async function fetchDashboardData() {
    const response = await fetch('/api/dashboard-data', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(buildPayload()),
    });

    if (!response.ok) {
        throw new Error('Não foi possível carregar os dados do dashboard.');
    }

    return response.json();
}

function renderCards(cards) {
    document.getElementById('card-results').textContent = cards.results_count;
    document.getElementById('card-metric').textContent = cards.metric;
    document.getElementById('card-order').textContent = cards.order;
}

function renderTable(tableId, columns, rows, { numericColumns = [], highlightMetric = null, higherIsBetter = true } = {}) {
    const table = document.getElementById(tableId);
    table.innerHTML = '';

    const thead = document.createElement('thead');
    const headRow = document.createElement('tr');
    const rankHeader = document.createElement('th');
    rankHeader.textContent = 'Rank';
    headRow.appendChild(rankHeader);
    columns.forEach((column) => {
        const th = document.createElement('th');
        th.textContent = column;
        headRow.appendChild(th);
    });
    thead.appendChild(headRow);
    table.appendChild(thead);

    const tbody = document.createElement('tbody');
    const valuesForScale = rows.map((row) => row[highlightMetric]).filter((value) => typeof value === 'number');
    const minValue = valuesForScale.length ? Math.min(...valuesForScale) : 0;
    const maxValue = valuesForScale.length ? Math.max(...valuesForScale) : 0;

    rows.forEach((row, index) => {
        const tr = document.createElement('tr');
        const rankCell = document.createElement('td');
        rankCell.textContent = index + 1;
        tr.appendChild(rankCell);

        columns.forEach((column) => {
            const td = document.createElement('td');
            const value = row[column];
            const isNumeric = numericColumns.includes(column);
            td.textContent = isNumeric ? formatValue(value) : sanitizeText(value);
            if (isNumeric) {
                td.classList.add('number-cell');
            }

            if (highlightMetric && column === highlightMetric && typeof value === 'number' && maxValue !== minValue) {
                const ratio = (value - minValue) / (maxValue - minValue);
                const adjusted = higherIsBetter ? ratio : 1 - ratio;
                const hue = adjusted * 120;
                td.style.background = `hsla(${hue}, 75%, 45%, 0.25)`;
            }
            tr.appendChild(td);
        });
        tbody.appendChild(tr);
    });

    if (!rows.length) {
        const emptyRow = document.createElement('tr');
        const emptyCell = document.createElement('td');
        emptyCell.colSpan = columns.length + 1;
        emptyCell.innerHTML = '<div class="no-data">Nenhum resultado encontrado com os filtros selecionados.</div>';
        emptyRow.appendChild(emptyCell);
        tbody.appendChild(emptyRow);
    }

    table.appendChild(tbody);
}

function updateChartControls(chartControls) {
    const available = chartControls.available;
    const selected = chartControls.selected;
    state.chartSelections = selected;

    fillSingleSelect(controls.heatmapMetric, available.heatmap_metrics, selected.heatmap_metric);
    fillSingleSelect(controls.heatmapHorizon, available.heatmap_horizons, selected.heatmap_horizon);
    fillSingleSelect(controls.evolutionMetric, available.evolution_metrics, selected.evolution_metric);
    fillSingleSelect(controls.evolutionTicker, available.evolution_tickers, selected.evolution_ticker);
    fillSingleSelect(controls.boxMetric, available.box_metrics, selected.box_metric);
}

function renderRankingChart(data) {
    const container = document.getElementById('ranking-chart');
    if (!data.records.length) {
        container.innerHTML = '<div class="no-data">Sem dados para o gráfico.</div>';
        return;
    }

    const fullLabels = data.records.map((item) => item.Label);
    const shortLabels = fullLabels.map((label) => (label.length > 58 ? `${label.slice(0, 55)}...` : label));

    Plotly.newPlot(container, [{
        type: 'bar',
        orientation: 'h',
        x: data.records.map((item) => item[data.metric]),
        y: shortLabels,
        customdata: fullLabels,
        marker: {
            color: data.records.map((item) => item[data.metric]),
            colorscale: data.higher_is_better ? 'Greens' : 'Reds',
        },
        hovertemplate: `%{customdata}<br>${data.metric}: %{x:.4f}<extra></extra>`,
    }], {
        paper_bgcolor: 'transparent',
        plot_bgcolor: 'transparent',
        margin: { t: 10, r: 20, b: 40, l: 300 },
        font: { color: '#eef4ff' },
        yaxis: {
            autorange: data.descending ? 'reversed' : true,
            automargin: true,
            tickfont: { size: 11 },
        },
        xaxis: { title: data.metric, gridcolor: 'rgba(255,255,255,0.08)' },
        height: Math.min(720, Math.max(360, data.records.length * 30)),
        bargap: 0.2,
    }, { responsive: true, displayModeBar: false });
}

function renderHeatmapChart(data) {
    const container = document.getElementById('heatmap-chart');
    if (!data.x.length || !data.y.length) {
        container.innerHTML = '<div class="no-data">Sem dados para o horizonte selecionado.</div>';
        return;
    }

    Plotly.newPlot(container, [{
        type: 'heatmap',
        x: data.x,
        y: data.y,
        z: data.z,
        colorscale: data.higher_is_better ? 'RdYlGn' : 'RdYlGn_r',
        hovertemplate: 'Modelo: %{y}<br>Dataset | Ticker: %{x}<br>Valor: %{z:.4f}<extra></extra>',
    }], {
        paper_bgcolor: 'transparent',
        plot_bgcolor: 'transparent',
        margin: { t: 10, r: 20, b: 80, l: 120 },
        font: { color: '#eef4ff' },
        xaxis: { tickangle: -25 },
        yaxis: { automargin: true },
        height: Math.min(500, Math.max(280, data.y.length * 60)),
    }, { responsive: true, displayModeBar: false });
}

function renderEvolutionChart(data) {
    const container = document.getElementById('evolution-chart');
    if (!data.records.length) {
        container.innerHTML = '<div class="no-data">Sem dados para o ativo selecionado.</div>';
        return;
    }

    const grouped = data.records.reduce((acc, item) => {
        if (!acc[item.Grupo]) {
            acc[item.Grupo] = [];
        }
        acc[item.Grupo].push(item);
        return acc;
    }, {});

    const traces = Object.entries(grouped).map(([group, records]) => ({
        type: 'scatter',
        mode: 'lines+markers',
        name: group,
        x: records.map((item) => item.Horizonte),
        y: records.map((item) => item[data.metric]),
        hovertemplate: `${group}<br>Horizonte: %{x}<br>${data.metric}: %{y:.4f}<extra></extra>`,
    }));

    Plotly.newPlot(container, traces, {
        paper_bgcolor: 'transparent',
        plot_bgcolor: 'transparent',
        margin: { t: 10, r: 20, b: 60, l: 60 },
        font: { color: '#eef4ff' },
        xaxis: { title: 'Horizonte de Previsão' },
        yaxis: { title: data.metric, gridcolor: 'rgba(255,255,255,0.08)' },
        height: 360,
    }, { responsive: true, displayModeBar: false });
}

function renderBoxChart(data) {
    const container = document.getElementById('box-chart');
    if (!data.records.length) {
        container.innerHTML = '<div class="no-data">Sem dados para o box plot.</div>';
        return;
    }

    const grouped = data.records.reduce((acc, item) => {
        const groupKey = `${item.modelo_nome} | ${item.dataset_nome}`;
        if (!acc[groupKey]) {
            acc[groupKey] = [];
        }
        acc[groupKey].push(item[data.metric]);
        return acc;
    }, {});

    const traces = Object.entries(grouped).map(([group, values]) => ({
        type: 'box',
        name: group,
        y: values,
        boxpoints: 'all',
        jitter: 0.35,
        pointpos: 0,
    }));

    Plotly.newPlot(container, traces, {
        paper_bgcolor: 'transparent',
        plot_bgcolor: 'transparent',
        margin: { t: 10, r: 20, b: 80, l: 60 },
        font: { color: '#eef4ff' },
        yaxis: { title: data.metric, gridcolor: 'rgba(255,255,255,0.08)' },
        height: 360,
    }, { responsive: true, displayModeBar: false });
}

function renderAllCharts(charts) {
    updateChartControls(charts.controls);
    renderRankingChart(charts.ranking);
    renderHeatmapChart(charts.heatmap);
    renderEvolutionChart(charts.evolution);
    renderBoxChart(charts.box);
}

function renderSummary(summary) {
    renderTable('summary-table', summary.columns, summary.rows, {
        numericColumns: summary.columns.filter((column) => column !== 'modelo_nome'),
    });
}

function renderBest(bestByScenario) {
    document.getElementById('best-title').textContent = `🏆 Melhor Modelo por Cenário (${bestByScenario.metric})`;
    const columns = ['Ticker', 'Horizonte', 'Modelo', 'Dataset', bestByScenario.metric];
    renderTable('best-table', columns, bestByScenario.rows, {
        numericColumns: [bestByScenario.metric],
    });
}

function renderFeatureSummary(featureSummary) {
    renderTable('feature-summary-table', featureSummary.columns, featureSummary.rows, {
        numericColumns: featureSummary.columns.filter((column) => column !== 'dataset_nome'),
    });
}

async function refreshDashboard() {
    try {
        setAlert('');
        const data = await fetchDashboardData();
        renderCards(data.cards);
        renderTable('results-table', data.table.columns, data.table.rows, {
            numericColumns: data.table.metricas,
            highlightMetric: data.table.sort_metric,
            higherIsBetter: data.table.higher_is_better,
        });
        renderTable('details-table', data.details.columns, data.details.rows, {
            numericColumns: data.table.metricas,
        });
        renderAllCharts(data.charts);
        renderSummary(data.summary);
        renderBest(data.best_by_scenario);
        renderFeatureSummary(data.feature_summary);

        if (!data.table.rows.length) {
            setAlert('Nenhum resultado encontrado com os filtros selecionados.');
        }
    } catch (error) {
        setAlert(error.message, 'error');
    }
}

async function initializeDashboard(tipo = 'Regressão') {
    try {
        const metadata = await fetchMetadata(tipo);
        applyMetadata(metadata);
        await refreshDashboard();
    } catch (error) {
        setAlert(error.message, 'error');
    }
}

function handleMetricOrderChange() {
    const selectedMetric = controls.metricaOrdenar.value;
    const higherIsBetter = ['R2', 'Accuracy', 'Precision', 'Recall', 'F1-Score', 'AUC-ROC'].includes(selectedMetric);
    controls.ordemDesc.checked = higherIsBetter;
}

function configureTabs() {
    const buttons = document.querySelectorAll('.tab-button');
    const panels = document.querySelectorAll('.tab-panel');

    buttons.forEach((button) => {
        button.addEventListener('click', () => {
            buttons.forEach((btn) => btn.classList.remove('active'));
            panels.forEach((panel) => panel.classList.remove('active'));
            button.classList.add('active');
            document.querySelector(`[data-content="${button.dataset.tab}"]`)?.classList.add('active');
        });
    });
}

function bindEvents() {
    document.getElementById('apply-filters').addEventListener('click', refreshDashboard);
    document.getElementById('reset-filters').addEventListener('click', () => initializeDashboard(getTipoSelecionado()));
    controls.topN.addEventListener('input', updateTopNDisplay);
    controls.metricaOrdenar.addEventListener('change', handleMetricOrderChange);

    document.querySelectorAll('.btn-toggle-all').forEach((btn) => {
        btn.addEventListener('click', () => {
            const container = document.getElementById(btn.dataset.target);
            const checkboxes = Array.from(container.querySelectorAll('input[type="checkbox"]'));
            const allChecked = checkboxes.every((cb) => cb.checked);
            checkboxes.forEach((cb) => {
                cb.checked = !allChecked;
                cb.closest('.checkbox-item').classList.toggle('is-checked', !allChecked);
            });
        });
    });

    document.querySelectorAll('input[name="tipo"]').forEach((radio) => {
        radio.addEventListener('change', async (event) => {
            await initializeDashboard(event.target.value);
        });
    });

    [
        controls.heatmapMetric,
        controls.heatmapHorizon,
        controls.evolutionMetric,
        controls.evolutionTicker,
        controls.boxMetric,
    ].forEach((control) => {
        control.addEventListener('change', refreshDashboard);
    });
}

document.addEventListener('DOMContentLoaded', async () => {
    configureTabs();
    bindEvents();
    await initializeDashboard();
});
