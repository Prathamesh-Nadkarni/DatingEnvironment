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

  let timeChartCanvas: HTMLCanvasElement;
  let timeChartInstance: Chart | null = null;

  let eventChartCanvas: HTMLCanvasElement;
  let eventChartInstance: Chart | null = null;

  onMount(async () => {
    try {
      const [sessRes, telRes] = await Promise.all([
        fetch(`${API_URL}/api/admin/sessions`),
        fetch(`${API_URL}/api/admin/telemetry`)
      ]);
      const sessData = await sessRes.json();
      const telData = await telRes.json();
      
      sessions = sessData.sessions || {};
      telemetryEvents = telData.events || [];
      
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
                                <div class="astro-card" style="border-color: #fbbf24; border: 1px solid #fbbf24; padding: 1.5rem; border-radius: 12px; margin-bottom: 2rem;">
                                    <h3>Astrological Compatibility (Ashtakoota)</h3>
                                    <div style="display: flex; align-items: baseline; gap: 1rem;">
                                        <p style="font-size: 2.5rem; color: #fbbf24; margin: 0.5rem 0; font-weight: bold;">
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
                                                    <strong style="text-transform: capitalize; color: #fbbf24;">{koota.replace('_', ' ')}</strong>
                                                    <span>{details.score} / {details.max}</span>
                                                </div>
                                                <p style="font-size: 0.8rem; color: #94a3b8; margin: 0;">{details.desc}</p>
                                            </div>
                                        {/each}
                                    </div>
                                </div>
                            {/if}

                            <h3>Behavioral Compatibility Report</h3>
                            <div class="report-summary">
                                <strong>Overall Score:</strong> <span style="color: #fbbf24; font-size: 1.5rem;">{activeResults.report.overall_score}/100</span><br/>
                                <strong>Verdict:</strong> {activeResults.report.verdict}
                            </div>

                            {#if activeResults.report.dimensional_details}
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
    .msg.sys {
        color: #94a3b8;
        font-style: italic;
    }
    .msg.user {
        background: rgba(255,255,255,0.1);
    }
</style>
