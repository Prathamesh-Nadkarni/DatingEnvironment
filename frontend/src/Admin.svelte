<script lang="ts">
  import { onMount } from 'svelte';
  import SimulationLoader from './SimulationLoader.svelte';
  import Chart from 'chart.js/auto';

  const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

  let sessions = {};
  let telemetryEvents = [];
  let loading = true;
  let activeSessionId: string | null = null;
  let activeRole: string | null = null;
  let activeResults: any = null;
  let fetchingResults = false;
  let activeSyntheticReport: any = null;
  let selectedMonth: any = null;
  let timelineChartCanvas: HTMLCanvasElement;
  let timelineChartInstance: any = null;

  function buildTimelineChart(node: HTMLCanvasElement, trajectory: any[]) {
    if (!trajectory || trajectory.length === 0) return;
    if (timelineChartInstance) timelineChartInstance.destroy();
    timelineChartCanvas = node;

    const labels = trajectory.map(e => `M${e.month}`);
    const happyA = trajectory.map(e => Math.round((e.happiness_a || 0) * 100));
    const happyB = trajectory.map(e => Math.round((e.happiness_b || 0) * 100));
    const capital = trajectory.map(e => Math.round(e.capital || 0));
    const harmony = trajectory.map(e => e.harmony_score || 0);

    timelineChartInstance = new Chart(timelineChartCanvas, {
      type: 'line',
      data: {
        labels,
        datasets: [
          {
            label: 'Happiness A (%)',
            data: happyA,
            borderColor: '#d4af37',
            backgroundColor: 'rgba(212,175,55,0.08)',
            tension: 0.4,
            pointRadius: 3,
            fill: false,
          },
          {
            label: 'Happiness B (%)',
            data: happyB,
            borderColor: '#818cf8',
            backgroundColor: 'rgba(129,140,248,0.08)',
            tension: 0.4,
            pointRadius: 3,
            fill: false,
          },
          {
            label: 'Harmony Score',
            data: harmony,
            borderColor: '#4ade80',
            backgroundColor: 'rgba(74,222,128,0.08)',
            tension: 0.4,
            pointRadius: 3,
            borderDash: [4, 3],
            fill: false,
          },
          {
            label: 'Relationship Capital',
            data: capital,
            borderColor: '#f87171',
            backgroundColor: 'rgba(248,113,113,0.08)',
            tension: 0.4,
            pointRadius: 3,
            borderDash: [2, 4],
            fill: false,
          },
        ]
      },
      options: {
        responsive: true,
        interaction: { mode: 'index', intersect: false },
        plugins: {
          legend: { labels: { color: '#fff', font: { size: 11 } } },
          tooltip: {
            backgroundColor: 'rgba(0,0,0,0.85)',
            titleColor: '#d4af37',
            bodyColor: '#fff',
            callbacks: {
              title: (items: any) => {
                const idx = items[0].dataIndex;
                return `Month ${trajectory[idx].month}: ${trajectory[idx].scenario}`;
              }
            }
          }
        },
        scales: {
          x: { ticks: { color: '#94a3b8', maxTicksLimit: 20 }, grid: { color: 'rgba(255,255,255,0.05)' } },
          y: { ticks: { color: '#94a3b8' }, grid: { color: 'rgba(255,255,255,0.05)' }, min: 0, max: 120 }
        }
      }
    });
    return { destroy() { if (timelineChartInstance) { timelineChartInstance.destroy(); timelineChartInstance = null; } } };
  }

  let timeChartCanvas: HTMLCanvasElement;
  let timeChartInstance: Chart | null = null;

  let eventChartCanvas: HTMLCanvasElement;
  let eventChartInstance: Chart | null = null;

  let syntheticReports = [];

  onMount(async () => {
    try {
      const [sessRes, telRes, synthRes] = await Promise.all([
        fetch(`${API_URL}/api/admin/sessions`),
        fetch(`${API_URL}/api/admin/telemetry`),
        fetch(`${API_URL}/api/admin/synthetic-reports`)
      ]);
      const sessData = await sessRes.json();
      const telData = await telRes.json();
      const synthData = await synthRes.json();
      
      sessions = sessData.sessions || {};
      telemetryEvents = telData.events || [];
      syntheticReports = synthData.reports || [];
      
      loading = false;
      setTimeout(renderCharts, 100);
    } catch (e) {
      console.error("Failed to load admin data:", e);
      loading = false;
    }
  });

  function renderCharts() {
    if (!timeChartCanvas || !eventChartCanvas) return;

    // 1. Time Spent per Question
    const questionEvents = telemetryEvents.filter(e => e.event === 'question_answered' && e.time_ms);
    // Average time by question index/element
    const timeByElement = {};
    questionEvents.forEach(e => {
        if (!timeByElement[e.element]) timeByElement[e.element] = [];
        timeByElement[e.element].push(parseInt(e.time_ms));
    });

    const elements = Object.keys(timeByElement).sort();
    const avgTimes = elements.map(el => {
        const times = timeByElement[el];
        return times.reduce((a, b) => a + b, 0) / times.length;
    });

    timeChartInstance = new Chart(timeChartCanvas, {
        type: 'bar',
        data: {
            labels: elements,
            datasets: [{
                label: 'Avg Time (ms) per Question',
                data: avgTimes,
                backgroundColor: 'rgba(212, 175, 55, 0.6)',
                borderColor: 'rgba(212, 175, 55, 1)',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            plugins: { legend: { labels: { color: '#fff' } } },
            scales: {
                y: { ticks: { color: '#fff' }, grid: { color: 'rgba(255,255,255,0.1)' } },
                x: { ticks: { color: '#fff' }, grid: { color: 'rgba(255,255,255,0.1)' } }
            }
        }
    });

    // 2. Event Frequency
    const eventCounts = {};
    telemetryEvents.forEach(e => {
        eventCounts[e.event] = (eventCounts[e.event] || 0) + 1;
    });

    eventChartInstance = new Chart(eventChartCanvas, {
        type: 'doughnut',
        data: {
            labels: Object.keys(eventCounts),
            datasets: [{
                data: Object.values(eventCounts),
                backgroundColor: [
                    'rgba(212, 175, 55, 0.8)',
                    'rgba(180, 180, 180, 0.8)',
                    'rgba(100, 150, 255, 0.8)',
                    'rgba(255, 100, 150, 0.8)'
                ],
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            plugins: { legend: { labels: { color: '#fff' } } }
        }
    });
  }

  function viewAnswers(sessionId: string, role: string) {
      activeSessionId = sessionId;
      activeRole = role;
      activeResults = null;
  }

  let pollingInterval: any = null;

  async function viewResults(sessionId: string) {
      if (pollingInterval) {
          clearInterval(pollingInterval);
          pollingInterval = null;
      }
      activeSessionId = sessionId;
      activeRole = null;
      activeResults = null;
      fetchingResults = true;
      
      const poll = async () => {
          try {
              const res = await fetch(`${API_URL}/api/compatibility/report`, {
                  method: 'POST',
                  headers: { 'Content-Type': 'application/json' },
                  body: JSON.stringify({ session_id: sessionId })
              });
              
              if (res.status === 202) {
                  // Still generating, wait and poll again
                  return;
              }
              
              if (res.ok) {
                  const data = await res.json();
                  activeResults = {
                      report: data,
                      astro_score: data.kundali
                  };
                  fetchingResults = false;
                  clearInterval(pollingInterval);
                  pollingInterval = null;
              } else {
                  activeResults = { error: "Results not ready or missing users." };
                  fetchingResults = false;
                  clearInterval(pollingInterval);
                  pollingInterval = null;
              }
          } catch(e) {
              activeResults = { error: "Failed to fetch results." };
              fetchingResults = false;
              clearInterval(pollingInterval);
              pollingInterval = null;
          }
      };
      
      // Initial poll
      await poll();
      if (fetchingResults) {
          pollingInterval = setInterval(poll, 3000);
      }
  }
</script>

<div class="admin-container">
    <header class="admin-header">
        <h1>System Observability Dashboard</h1>
        <p>Live metrics and simulation results.</p>
    </header>

    {#if loading}
        <div class="loading">Loading data...</div>
    {:else}
        <div class="admin-grid">
            <!-- Charts Section -->
            <div class="card glass">
                <h2>Telemetry: Average Time (ms)</h2>
                <div class="chart-container">
                    <canvas bind:this={timeChartCanvas}></canvas>
                </div>
            </div>
            
            <div class="card glass">
                <h2>Telemetry: Event Distribution</h2>
                <div class="chart-container" style="max-height: 300px; display: flex; justify-content: center;">
                    <canvas bind:this={eventChartCanvas}></canvas>
                </div>
            </div>

            <!-- Sessions Section -->
            <div class="card glass full-width">
                <h2>Captured Sessions ({Object.keys(sessions).length})</h2>
                <div class="sessions-list">
                    {#each Object.keys(sessions) as sessionId}
                        <div class="session-card">
                            <h3>Session: {sessionId}</h3>
                            <div class="roles">
                                {#each Object.keys(sessions[sessionId]) as role}
                                    <button class="action-btn-ghost" on:click={() => viewAnswers(sessionId, role)}>
                                        View {role}
                                    </button>
                                {/each}
                                {#if Object.keys(sessions[sessionId]).length >= 2}
                                    <button class="action-btn-gold" style="padding: 0.5rem 1rem; border: none; border-radius: 8px;" on:click={() => viewResults(sessionId)}>
                                        View Results
                                    </button>
                                {/if}
                            </div>
                        </div>
                    {/each}
                </div>
            </div>

            <!-- Synthetic Reports Section -->
            <div class="card glass full-width">
                <h2>Synthetic Persona Tests ({syntheticReports.length})</h2>
                <div class="sessions-list">
                    {#each syntheticReports as report}
                        <div class="session-card">
                            <div>
                                <h3>Test: {report.run_id} ({report.mode})</h3>
                                <p style="font-size: 0.8rem; color: #aaa; margin: 0; margin-top: 0.25rem;">Pair: {report.person_a.id} &amp; {report.person_b.id}</p>
                                <p style="font-size: 0.8rem; color: #aaa; margin: 0;">Status: <span style="color: {report.status === 'PASS' ? 'lightgreen' : 'coral'}">{report.status}</span></p>
                            </div>
                            <div class="roles">
                                <button class="action-btn-ghost" on:click={() => {
                                    activeSyntheticReport = report;
                                    setTimeout(() => document.getElementById('synthetic-results')?.scrollIntoView({ behavior: 'smooth' }), 100);
                                }}>
                                    View Report Details
                                </button>
                            </div>
                        </div>
                    {/each}
                </div>
            </div>

            <!-- Synthetic Results Panel -->
            {#if activeSyntheticReport}
                {@const compat = activeSyntheticReport.relationship_behavior.compatibility}
                {@const sim = activeSyntheticReport.relationship_behavior.simulation}
                {@const astro = activeSyntheticReport.relationship_behavior.astro_score}
                <div class="card glass full-width" id="synthetic-results">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.5rem;">
                        <div>
                            <h2 style="margin:0;">Synthetic Test Report</h2>
                            <p style="color:#aaa; font-size:0.85rem; margin:0.25rem 0 0;">
                                {activeSyntheticReport.person_a.id} &amp; {activeSyntheticReport.person_b.id}
                                &nbsp;·&nbsp; Run ID: {activeSyntheticReport.run_id}
                                &nbsp;·&nbsp; Seed: {activeSyntheticReport.seed}
                            </p>
                        </div>
                        <button class="action-btn-ghost" on:click={() => activeSyntheticReport = null}>Close</button>
                    </div>

                    <!-- Persona Fidelity badges -->
                    <div style="display:flex; gap:1rem; margin-bottom:1.5rem;">
                        <div style="background:rgba(212,175,55,0.1); border:1px solid rgba(212,175,55,0.3); border-radius:8px; padding:0.6rem 1.2rem;">
                            <strong style="color:var(--accent);">Persona A Fidelity</strong>
                            <p style="margin:0; font-size:1.4rem; font-weight:700;">{activeSyntheticReport.persona_fidelity?.A ?? '—'}%</p>
                        </div>
                        <div style="background:rgba(212,175,55,0.1); border:1px solid rgba(212,175,55,0.3); border-radius:8px; padding:0.6rem 1.2rem;">
                            <strong style="color:var(--accent);">Persona B Fidelity</strong>
                            <p style="margin:0; font-size:1.4rem; font-weight:700;">{activeSyntheticReport.persona_fidelity?.B ?? '—'}%</p>
                        </div>
                        <div style="background:{activeSyntheticReport.status === 'PASS' ? 'rgba(74,222,128,0.1)' : 'rgba(239,68,68,0.1)'}; border:1px solid {activeSyntheticReport.status === 'PASS' ? 'rgba(74,222,128,0.4)' : 'rgba(239,68,68,0.4)'}; border-radius:8px; padding:0.6rem 1.2rem;">
                            <strong style="color:{activeSyntheticReport.status === 'PASS' ? '#4ade80' : '#ef4444'};">Status</strong>
                            <p style="margin:0; font-size:1.4rem; font-weight:700;">{activeSyntheticReport.status}</p>
                        </div>
                    </div>

                    <!-- Ashtakoota Section -->
                    {#if astro}
                        <div class="astro-card" style="border-color: var(--accent); border: 1px solid var(--accent); padding: 1.5rem; border-radius: 12px; margin-bottom: 2rem;">
                            <h3>Astrological Compatibility (Ashtakoota)</h3>
                            <div style="display: flex; align-items: baseline; gap: 1rem;">
                                <p style="font-size: 2.5rem; color: var(--accent); margin: 0.5rem 0; font-weight: bold;">
                                    {astro.guna} <span style="font-size: 1.2rem; color: #94a3b8;">/ 36</span>
                                </p>
                                <span class="score-badge {astro.guna >= 18 ? 'good' : 'bad'}">{astro.classification?.replace('_', ' ')}</span>
                            </div>
                            <p style="font-style: italic; color: #cbd5e1; margin-bottom: 1.5rem;">{astro.verdict_text}</p>
                            {#if astro.nadi_dosha || astro.bhakoot_dosha}
                                <div style="background: rgba(239,68,68,0.1); border-left: 4px solid #ef4444; padding: 1rem; margin-bottom: 1.5rem;">
                                    <strong style="color: #ef4444;">Astrological Warnings:</strong>
                                    <ul style="margin-top: 0.5rem; color: #f8fafc;">
                                        {#if astro.nadi_dosha}<li>Nadi Dosha detected (affects health/genetics)</li>{/if}
                                        {#if astro.bhakoot_dosha}<li>Bhakoot Dosha detected (affects prosperity/harmony)</li>{/if}
                                    </ul>
                                </div>
                            {/if}
                            {#if astro.breakdown}
                                <h4>Koota Breakdown</h4>
                                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 1rem; margin-top: 1rem;">
                                    {#each Object.entries(astro.breakdown) as [koota, details]}
                                        <div style="background: rgba(255,255,255,0.05); padding: 1rem; border-radius: 8px;">
                                            <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
                                                <strong style="text-transform: capitalize; color: var(--accent);">{koota.replace('_', ' ')}</strong>
                                                <span>{details.score} / {details.max}</span>
                                            </div>
                                            <p style="font-size: 0.8rem; color: #94a3b8; margin: 0;">{details.desc}</p>
                                        </div>
                                    {/each}
                                </div>
                            {/if}
                        </div>
                    {/if}

                    <!-- Compatibility Summary -->
                    <h3>Behavioral Compatibility Report</h3>
                    <div class="report-summary" style="margin-bottom:2rem;">
                        <strong>Overall Harmony:</strong>
                        <span style="color: var(--accent); font-size: 1.5rem; margin-left:0.5rem;">
                            {compat.overall_compatibility_score || compat.overall_score || 0}/100
                        </span><br/>
                        <strong>Breakdown Probability:</strong>
                        <span style="color: #ff4444;"> {((compat.breakdown_probability || 0) * 100).toFixed(0)}%</span><br/>
                        <strong>Mean Happiness A:</strong> {((compat.mean_happiness_a || 0) * 100).toFixed(0)}%
                        &nbsp;|&nbsp;
                        <strong>Mean Happiness B:</strong> {((compat.mean_happiness_b || 0) * 100).toFixed(0)}%<br/>
                        <strong>Inference:</strong> {compat.inference || compat.verdict || "No inference generated."}
                    </div>

                    <!-- 15-year simulation timeline chart -->
                    {#if compat.median_trajectory && compat.median_trajectory.length > 0}
                        <div class="category-block" style="margin-bottom: 2rem;">
                            <h4 class="category-title">15-YEAR RELATIONSHIP TIMELINE</h4>
                            <p style="font-size:0.8rem; color:#94a3b8; margin-bottom:1rem;">
                                {compat.median_trajectory.length} months simulated across {Math.round(compat.median_trajectory.length / 12)} Monte Carlo rollouts · hover for scenario details
                            </p>
                            <div style="background: rgba(0,0,0,0.3); border-radius: 12px; padding: 1.5rem;">
                                <canvas bind:this={timelineChartCanvas} use:buildTimelineChart={compat.median_trajectory}></canvas>
                            </div>

                            <!-- Breakdown events as a horizontal strip -->
                            <div style="margin-top:1.5rem;">
                                <h5 style="color:#94a3b8; font-size:0.8rem; text-transform:uppercase; letter-spacing:0.1em; margin-bottom:0.75rem;">Month-by-Month Scenarios</h5>
                                <div style="display:flex; flex-wrap:wrap; gap:0.4rem;">
                                    {#each compat.median_trajectory as event}
                                        <button
                                            style="background: {event.harmony_score >= 70 ? 'rgba(74,222,128,0.15)' : event.harmony_score >= 40 ? 'rgba(212,175,55,0.15)' : 'rgba(248,113,113,0.15)'};
                                                   border: 1px solid {event.harmony_score >= 70 ? 'rgba(74,222,128,0.4)' : event.harmony_score >= 40 ? 'rgba(212,175,55,0.4)' : 'rgba(248,113,113,0.4)'};
                                                   border-radius:6px; padding:0.25rem 0.5rem; font-size:0.72rem; color:#fff; cursor:pointer;"
                                            title="{event.scenario} — Harmony: {event.harmony_score}, Capital: {event.capital?.toFixed(1)}"
                                            on:click={() => selectedMonth = selectedMonth?.month === event.month ? null : event}
                                        >
                                            M{event.month}
                                        </button>
                                    {/each}
                                </div>
                            </div>

                            <!-- Expanded month detail -->
                            {#if selectedMonth}
                                <div style="margin-top:1rem; background:rgba(0,0,0,0.3); border-radius:12px; padding:1.5rem; border:1px solid rgba(212,175,55,0.2);">
                                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:1rem;">
                                        <div>
                                            <h5 style="margin:0; color:var(--accent);">Month {selectedMonth.month}: {selectedMonth.scenario}</h5>
                                            <p style="margin:0.25rem 0 0; font-size:0.8rem; color:#94a3b8;">
                                                Happiness A: {Math.round((selectedMonth.happiness_a||0)*100)}% ·
                                                Happiness B: {Math.round((selectedMonth.happiness_b||0)*100)}% ·
                                                Capital: {selectedMonth.capital?.toFixed(1)} ·
                                                Harmony: {selectedMonth.harmony_score}
                                            </p>
                                        </div>
                                        <button class="action-btn-ghost" style="font-size:0.75rem; padding:0.3rem 0.75rem;" on:click={() => selectedMonth = null}>✕</button>
                                    </div>
                                    {#if selectedMonth.dialogue_history && selectedMonth.dialogue_history.length > 0}
                                        <div class="dialogue-box">
                                            <h6>Dialogue Transcript</h6>
                                            {#each selectedMonth.dialogue_history as msg}
                                                <div class="msg {msg.speaker === 'Scene Master' ? 'sys' : msg.speaker?.startsWith('Environment') ? 'env' : 'user'}">
                                                    <strong>{msg.speaker}:</strong> {msg.message || msg.text || ''}
                                                </div>
                                            {/each}
                                        </div>
                                    {/if}
                                </div>
                            {/if}
                        </div>

                    <!-- Per-dimension scenario breakdown -->
                    {:else if compat.dimensional_details}
                        {#each Object.entries(compat.dimensional_details) as [category, scenarios]}
                            <div class="category-block">
                                <h4 class="category-title">{category.replace('_', ' ').toUpperCase()}</h4>
                                {#each scenarios as scenario}
                                    <div class="scenario-card">
                                        <h5>{scenario.scenario_title}
                                            <span class="score-badge {scenario.harmony_score > 60 ? 'good' : 'bad'}">{scenario.harmony_score}/100</span>
                                        </h5>
                                        <p><strong>Inference:</strong> {scenario.inference}</p>
                                        {#if scenario.dialogue_history && scenario.dialogue_history.length > 0}
                                            <div class="dialogue-box">
                                                <h6>Simulation Transcript</h6>
                                                {#each scenario.dialogue_history as msg}
                                                    <div class="msg {msg.speaker === 'Scene Master' ? 'sys' : 'user'}">
                                                        <strong>{msg.speaker}:</strong> {msg.message || msg.text}
                                                    </div>
                                                {/each}
                                            </div>
                                        {/if}
                                    </div>
                                {/each}
                            </div>
                        {/each}

                    <!-- Simulation events from sim engine -->
                    {:else if sim?.events && sim.events.length > 0}
                        <div class="category-block">
                            <h4 class="category-title">SCENARIO SIMULATION TRANSCRIPT</h4>
                            {#each sim.events as event}
                                <div class="scenario-card" style="border-left: 4px solid rgba(212,175,55,0.5);">
                                    <h5>{event.scenario || event.name || "Scenario"}
                                        {#if event.category}<span style="font-size:0.75rem; color:#94a3b8; margin-left:0.5rem;">({event.category})</span>{/if}
                                        {#if event.tension_level !== undefined}
                                            <span class="score-badge {event.tension_level < 0.5 ? 'good' : 'bad'}" style="margin-left:0.5rem;">
                                                Tension: {(event.tension_level * 100).toFixed(0)}%
                                            </span>
                                        {/if}
                                    </h5>
                                    {#if event.dialogue_history && event.dialogue_history.length > 0}
                                        <div class="dialogue-box">
                                            <h6>Transcript ({event.dialogue_history.length} turns)</h6>
                                            {#each event.dialogue_history as msg}
                                                <div class="msg {msg.speaker === 'Scene Master' ? 'sys' : 'user'}">
                                                    <strong>{msg.speaker}:</strong> {msg.message || msg.text || ''}
                                                </div>
                                            {/each}
                                        </div>
                                    {:else}
                                        <p style="color:#94a3b8; font-size:0.85rem;">No dialogue captured for this scenario.</p>
                                    {/if}
                                </div>
                            {/each}
                        </div>

                    {:else}
                        <div style="background:rgba(255,255,255,0.05); border-radius:8px; padding:1.5rem; color:#94a3b8; text-align:center;">
                            <p>No simulation events were generated for this run.</p>
                            <p style="font-size:0.85rem;">Run with a live Ollama model to get full scenario transcripts.</p>
                        </div>
                    {/if}
                </div>
            {/if}


            <!-- Answers Modal / View -->
            {#if activeSessionId && activeRole}
                <div class="card glass full-width">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <h2>Answers for {activeRole} in {activeSessionId}</h2>
                        <button class="action-btn-ghost" on:click={() => { activeSessionId = null; activeRole = null; }}>Close</button>
                    </div>
                    
                    <div class="answers-container">
                        {#if sessions[activeSessionId][activeRole].astro_fingerprint}
                            <div class="astro-card">
                                <h3>Astrological Fingerprint</h3>
                                <pre>{JSON.stringify(sessions[activeSessionId][activeRole].astro_fingerprint, null, 2)}</pre>
                            </div>
                        {/if}

                        <h3>Raw Answers</h3>
                        <pre class="json-viewer">{JSON.stringify(sessions[activeSessionId][activeRole].answers || {}, null, 2)}</pre>
                    </div>
                </div>
            {/if}

            <!-- Results View -->
            {#if activeSessionId && !activeRole}
                <div class="card glass full-width">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <h2>Compatibility Results for {activeSessionId}</h2>
                        <button class="action-btn-ghost" on:click={() => { activeSessionId = null; activeResults = null; }}>Close</button>
                    </div>
                    
                    <div class="answers-container">
                        {#if fetchingResults}
                            <SimulationLoader />
                        {:else if activeResults?.error}
                            <p style="color: #ff4444;">{activeResults.error}</p>
                        {:else if activeResults}
                            {#if activeResults.astro_score !== null}
                                <div class="astro-card" style="border-color: var(--accent); border: 1px solid var(--accent); padding: 1.5rem; border-radius: 12px; margin-bottom: 2rem;">
                                    <h3>Astrological Compatibility (Ashtakoota)</h3>
                                    <div style="display: flex; align-items: baseline; gap: 1rem;">
                                        <p style="font-size: 2.5rem; color: var(--accent); margin: 0.5rem 0; font-weight: bold;">
                                            {activeResults.astro_score.guna} <span style="font-size: 1.2rem; color: #94a3b8;">/ 36</span>
                                        </p>
                                        <span class="score-badge {activeResults.astro_score.guna >= 18 ? 'good' : 'bad'}">{activeResults.astro_score.classification.replace('_', ' ')}</span>
                                    </div>
                                    <p style="font-style: italic; color: #cbd5e1; margin-bottom: 1.5rem;">{activeResults.astro_score.verdict_text}</p>
                                    
                                    {#if activeResults.astro_score.nadi_dosha || activeResults.astro_score.bhakoot_dosha}
                                        <div style="background: rgba(239, 68, 68, 0.1); border-left: 4px solid #ef4444; padding: 1rem; margin-bottom: 1.5rem;">
                                            <strong style="color: #ef4444;">Astrological Warnings:</strong>
                                            <ul style="margin-top: 0.5rem; color: #f8fafc;">
                                                {#if activeResults.astro_score.nadi_dosha}<li>Nadi Dosha detected (affects health/genetics)</li>{/if}
                                                {#if activeResults.astro_score.bhakoot_dosha}<li>Bhakoot Dosha detected (affects prosperity/harmony)</li>{/if}
                                            </ul>
                                        </div>
                                    {/if}

                                    <h4>Koota Breakdown</h4>
                                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 1rem; margin-top: 1rem;">
                                        {#each Object.entries(activeResults.astro_score.breakdown) as [koota, details]}
                                            <div style="background: rgba(255, 255, 255, 0.05); padding: 1rem; border-radius: 8px;">
                                                <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
                                                    <strong style="text-transform: capitalize; color: var(--accent);">{koota.replace('_', ' ')}</strong>
                                                    <span>{details.score} / {details.max}</span>
                                                </div>
                                                <p style="font-size: 0.8rem; color: #94a3b8; margin: 0;">{details.desc}</p>
                                            </div>
                                        {/each}
                                    </div>
                                </div>
                            {/if}

                            <h3>Behavioral Compatibility Report (V2 Longitudinal)</h3>
                            <div class="report-summary">
                                <strong>Overall Harmony:</strong> <span style="color: var(--accent); font-size: 1.5rem;">{activeResults.report.overall_compatibility_score || activeResults.report.overall_score || 0}/100</span><br/>
                                <strong>Breakdown Probability:</strong> <span style="color: #ff4444;">{((activeResults.report.breakdown_probability || 0) * 100).toFixed(0)}%</span><br/>
                                <strong>Mean Happiness (A):</strong> {((activeResults.report.mean_happiness_a || 0) * 100).toFixed(0)}% | 
                                <strong>Mean Happiness (B):</strong> {((activeResults.report.mean_happiness_b || 0) * 100).toFixed(0)}%<br/>
                                <strong>Inference:</strong> {activeResults.report.inference || activeResults.report.verdict || "No inference generated."}
                            </div>

                            {#if activeResults.report.median_trajectory}
                                <div class="category-block">
                                    <h4 class="category-title">SIMULATED 15-YEAR TIMELINE (MEDIAN RUN)</h4>
                                    {#each activeResults.report.median_trajectory as event}
                                        <div class="scenario-card" style="border-left: 4px solid {event.capital > 0 ? '#4ade80' : '#ef4444'};">
                                            <h5>Month {event.month}: {event.scenario} <span class="score-badge {event.harmony_score > 60 ? 'good' : 'bad'}">{event.harmony_score} Harmony</span></h5>
                                            <p style="font-size: 0.9rem; color: #94a3b8; margin-top: 0.25rem;">
                                                Happiness A: {(event.happiness_a * 100).toFixed(0)}% | Happiness B: {(event.happiness_b * 100).toFixed(0)}% | Relationship Capital: {event.capital.toFixed(1)}
                                            </p>
                                            
                                            {#if event.dialogue_history && event.dialogue_history.length > 0}
                                                <div class="dialogue-box">
                                                    <h6>Event Transcript</h6>
                                                    {#each event.dialogue_history as msg}
                                                        <div class="msg {msg.speaker === 'Scene Master' ? 'sys' : 'user'}">
                                                            <strong>{msg.speaker}:</strong> {msg.message || msg.text}
                                                        </div>
                                                    {/each}
                                                </div>
                                            {/if}
                                        </div>
                                    {/each}
                                </div>
                            {:else if activeResults.report.dimensional_details}
                                {#each Object.entries(activeResults.report.dimensional_details) as [category, scenarios]}
                                    <div class="category-block">
                                        <h4 class="category-title">{category.replace('_', ' ').toUpperCase()}</h4>
                                        {#each scenarios as scenario}
                                            <div class="scenario-card">
                                                <h5>{scenario.scenario_title} <span class="score-badge {scenario.harmony_score > 60 ? 'good' : 'bad'}">{scenario.harmony_score}/100</span></h5>
                                                <p><strong>Inference:</strong> {scenario.inference}</p>
                                                
                                                {#if scenario.dialogue_history && scenario.dialogue_history.length > 0}
                                                    <div class="dialogue-box">
                                                        <h6>Simulation Transcript</h6>
                                                        {#each scenario.dialogue_history as msg}
                                                            <div class="msg {msg.speaker === 'Scene Master' ? 'sys' : 'user'}">
                                                                <strong>{msg.speaker}:</strong> {msg.message || msg.text}
                                                            </div>
                                                        {/each}
                                                    </div>
                                                {/if}
                                            </div>
                                        {/each}
                                    </div>
                                {/each}
                            {:else}
                                <pre class="json-viewer">{JSON.stringify(activeResults.report, null, 2)}</pre>
                            {/if}
                        {/if}
                    </div>
                </div>
            {/if}
        </div>
    {/if}
</div>

<style>
    .admin-container {
        padding: 2rem;
        min-height: 100vh;
        background: linear-gradient(135deg, #0a0a0a 0%, #1a1a1a 100%);
        color: #fff;
        font-family: 'Inter', sans-serif;
        overflow-y: auto;
    }
    .admin-header {
        margin-bottom: 2rem;
        text-align: center;
    }
    .admin-header h1 {
        font-family: 'Playfair Display', serif;
        color: #d4af37;
        margin-bottom: 0.5rem;
    }
    .admin-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 2rem;
        max-width: 1200px;
        margin: 0 auto;
    }
    .full-width {
        grid-column: 1 / -1;
    }
    .card {
        padding: 1.5rem;
        border-radius: 12px;
    }
    .glass {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        box-shadow: 0 4px 30px rgba(0, 0, 0, 0.1);
    }
    .chart-container {
        position: relative;
        width: 100%;
        margin-top: 1rem;
    }
    .sessions-list {
        display: flex;
        flex-direction: column;
        gap: 1rem;
        margin-top: 1rem;
    }
    .session-card {
        padding: 1rem;
        background: rgba(0,0,0,0.3);
        border-radius: 8px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .roles {
        display: flex;
        gap: 0.5rem;
    }
    .action-btn-ghost {
        background: transparent;
        color: #fff;
        border: 1px solid rgba(255, 255, 255, 0.3);
        padding: 0.5rem 1rem;
        border-radius: 8px;
        cursor: pointer;
        transition: all 0.3s ease;
    }
    .action-btn-ghost:hover {
        background: rgba(255, 255, 255, 0.1);
        border-color: #d4af37;
        color: #d4af37;
    }
    .answers-container {
        margin-top: 1rem;
        display: flex;
        flex-direction: column;
        gap: 1rem;
    }
    .astro-card, .json-viewer {
        background: #000;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid rgba(212, 175, 55, 0.3);
        overflow-x: auto;
    }
    pre {
        margin: 0;
        color: #a0d468;
        font-family: monospace;
    }
    .report-summary {
        background: rgba(212, 175, 55, 0.1);
        border: 1px solid rgba(212, 175, 55, 0.5);
        padding: 1rem;
        border-radius: 8px;
        margin-bottom: 1rem;
    }
    .category-block {
        margin-top: 2rem;
    }
    .category-title {
        color: #d4af37;
        border-bottom: 1px solid rgba(255,255,255,0.2);
        padding-bottom: 0.5rem;
    }
    .scenario-card {
        background: rgba(255,255,255,0.05);
        padding: 1rem;
        border-radius: 8px;
        margin-top: 1rem;
    }
    .scenario-card h5 {
        margin-top: 0;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .score-badge {
        padding: 0.2rem 0.5rem;
        border-radius: 4px;
        font-size: 0.9rem;
    }
    .score-badge.good { background: rgba(0, 200, 100, 0.2); color: #4ade80; }
    .score-badge.bad { background: rgba(255, 100, 100, 0.2); color: #f87171; }
    .dialogue-box {
        margin-top: 1rem;
        background: #000;
        padding: 1rem;
        border-radius: 8px;
        max-height: 400px;
        overflow-y: auto;
    }
    .msg {
        margin-bottom: 0.5rem;
        padding: 0.5rem;
        border-radius: 4px;
        font-size: 0.9rem;
    }
    .msg.env {
        background: rgba(129, 140, 248, 0.08);
        border-left: 3px solid #818cf8;
        padding: 0.4rem 0.75rem;
        margin: 0.25rem 0;
        border-radius: 4px;
        font-size: 0.82rem;
        color: #c7d2fe;
        font-style: italic;
    }
    .msg.sys {
        color: #94a3b8;
        font-style: italic;
    }
    .msg.user {
        background: rgba(255,255,255,0.1);
    }
</style>
