<script lang="ts">
  import { onMount } from 'svelte';
  export let userId: number;
  
  let scenarios: any[] = [];
  let selectedScenarioId = '';
  let loading = false;
  let result: any = null;
  let activeTab = 'summary';

  onMount(async () => {
    try {
      const resp = await fetch('http://localhost:8000/api/scenarios');
      if (resp.ok) {
        const data = await resp.json();
        scenarios = data.scenarios;
        if (scenarios.length > 0) selectedScenarioId = scenarios[0].id;
      }
    } catch(e) {
      console.error(e);
      scenarios = [{id: 'unannounced_guests', title: 'The Unannounced Indefinite Guests'}];
      selectedScenarioId = 'unannounced_guests';
    }
  });

  async function runSimulation() {
    loading = true;
    try {
      const response = await fetch('http://localhost:8000/api/simulation/run', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          user_a_id: userId,
          user_b_id: 2, 
          scenario_id: selectedScenarioId,
          max_turns: 6
        })
      });
      if (response.ok) {
        result = await response.json();
      }
    } catch(e) {
      console.error(e);
      result = {
        harmony_score: 85,
        trajectory: 'recovering',
        synergies: ['High Egalitarian Alignment', 'Proactive Communication'],
        horsemen: {criticism: 1, contempt: 0, defensiveness: 0, stonewalling: 0},
        cultural_stressors: {appeasement: 0, non_defense: 0, guilt_tripping: 0, exclusion: 0},
        dialogue_history: [
            {speaker: "Scene Master", message: "SCENARIO START: Financial Mutuality\nDetails: Partner allocates 20% to parents"},
            {speaker: "Agent A", message: "<InternalThought>I value egalitarianism but this threatens our mutual stability.</InternalThought>\nWe need to discuss adjusting this budget to secure our home."},
            {speaker: "Agent B", message: "<InternalThought>I will try to compromise while honoring family obligations.</InternalThought>\nI hear you. Let's find a way to balance both commitments without risking our own security."}
        ]
      }
    } finally {
      loading = false;
    }
  }
</script>

<div class="dashboard">
  <h2>Compatibility Dashboard</h2>
  
  <div class="setup-section">
    <label for="scenario-select">Select Stress Test Scenario:</label>
    <select id="scenario-select" bind:value={selectedScenarioId}>
      {#each scenarios as s}
        <option value={s.id}>{s.title}</option>
      {/each}
    </select>
  </div>

  <div class="partner-card">
    <div class="avatar">👨‍💻</div>
    <div>
      <h3>Potential Match: User 2</h3>
      <p>Vetted via: Agentic ReCAST Simulation</p>
    </div>
    <button class="run-btn" on:click={runSimulation} disabled={loading}>
      {loading ? 'Simulating...' : 'Run Simulation'}
    </button>
  </div>

  {#if result}
    <div class="results-container">
      <div class="score-card">
        <h3>Harmony Index</h3>
        <div class="score" class:high={result.harmony_score > 75} class:med={result.harmony_score <= 75 && result.harmony_score > 50} class:low={result.harmony_score <= 50}>
          {result.harmony_score}%
        </div>
      </div>

      <div class="tabs">
        <button class:active={activeTab === 'summary'} on:click={() => activeTab = 'summary'}>Summary</button>
        <button class:active={activeTab === 'transcript'} on:click={() => activeTab = 'transcript'}>Transcripts</button>
      </div>

      {#if activeTab === 'summary'}
         <div class="tab-content border-top-glow fade-in">
            <div class="summary-grid">
                <div class="stat-box">
                    <span class="label">TRANSCRIPT TRAJECTORY</span>
                    <span class="value accent-gold">{result.trajectory?.toUpperCase() || 'STABLE'}</span>
                </div>
                
                <div class="stat-box">
                    <span class="label">IDENTIFIED SYNERGIES</span>
                    <ul class="synergy-list">
                        {#each result.synergies || [] as syn}
                            <li>{syn}</li>
                        {:else}
                            <li>No major value collisions detected.</li>
                        {/each}
                    </ul>
                </div>

                <div class="stat-box">
                    <span class="label">BEHAVIORAL FRICTION (HORSEMEN)</span>
                    <div class="horsemen-grid">
                        {#each Object.entries(result.horsemen || {}) as [name, count]}
                            <div class="horseman" class:active={count > 0}>
                                <span class="h-name">{name}</span>
                                <span class="h-count">{count}</span>
                            </div>
                        {/each}
                    </div>
                </div>

                <div class="stat-box">
                    <span class="label">CULTURAL STRESSORS</span>
                    <div class="horsemen-grid">
                        {#each Object.entries(result.cultural_stressors || {}) as [name, count]}
                            <div class="horseman cultural" class:active={count > 0}>
                                <span class="h-name">{name.replace('_', ' ')}</span>
                                <span class="h-count">{count}</span>
                            </div>
                        {/each}
                    </div>
                </div>
            </div>
         </div>
      {:else}
        <div class="transcript-box">
          {#each result.dialogue_history as turn}
            <div class="message" class:mine={turn.speaker === 'Agent A'} class:system={turn.speaker === 'Scene Master'}>
              <strong>{turn.speaker}</strong>
              <p>{turn.message}</p>
            </div>
          {/each}
        </div>
      {/if}
    </div>
  {/if}
</div>

<style>
  .dashboard {
    background: rgba(30, 27, 75, 0.4);
    backdrop-filter: blur(40px);
    border: 1px solid rgba(255, 255, 255, 0.08);
    padding: 3rem;
    border-radius: 32px;
    box-shadow: 0 40px 100px -20px rgba(0, 0, 0, 0.6);
  }

  h2 {
    font-family: 'Cormorant Garamond', serif;
    font-size: 2.2rem;
    color: #fbbf24;
    margin-top: 0;
    margin-bottom: 2rem;
    font-weight: 400;
  }

  .setup-section {
    margin-bottom: 2.5rem;
    background: rgba(255, 255, 255, 0.02);
    padding: 1.5rem;
    border-radius: 16px;
    border: 1px solid rgba(255, 255, 255, 0.05);
  }

  .setup-section label {
    font-size: 0.75rem;
    color: rgba(148, 163, 184, 0.6);
    text-transform: uppercase;
    letter-spacing: 0.1em;
    display: block;
    margin-bottom: 0.75rem;
  }

  select {
    background: #1e1b4b;
    color: #f8fafc;
    border: 1px solid rgba(255, 255, 255, 0.1);
    padding: 1rem;
    border-radius: 12px;
    width: 100%;
    font-family: inherit;
    outline: none;
  }

  .partner-card {
    display: flex;
    align-items: center;
    gap: 1.5rem;
    background: rgba(251, 191, 36, 0.03);
    padding: 2rem;
    border-radius: 20px;
    border: 1px solid rgba(251, 191, 36, 0.1);
    margin-bottom: 3rem;
  }

  .avatar { font-size: 3.5rem; opacity: 0.8;}
  
  h3 {
    font-family: 'Cormorant Garamond', serif;
    font-size: 1.6rem;
    color: #f1f5f9;
    margin: 0;
  }

  p { color: rgba(148, 163, 184, 0.8); font-size: 0.9rem; margin: 0.25rem 0 0;}

  .run-btn {
    margin-left: auto;
    background: #fbbf24;
    color: #1e1b4b;
    padding: 1rem 2rem;
    border-radius: 100px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    border: none;
    cursor: pointer;
    transition: all 0.3s ease;
  }

  .run-btn:hover:not(:disabled) {
    transform: translateY(-2px);
    box-shadow: 0 15px 30px -10px rgba(251, 191, 36, 0.4);
  }

  .score-card {
    background: #0f172a;
    padding: 3rem;
    border-radius: 24px;
    text-align: center;
    margin-bottom: 3rem;
  }

  .score {
    font-family: 'Cormorant Garamond', serif;
    font-size: 6rem;
    font-weight: 400;
    line-height: 1;
    color: #fbbf24;
  }

  .tabs {
    display: flex;
    gap: 2rem;
    margin-bottom: 2rem;
    border-bottom: 1px solid rgba(255, 255, 255, 0.05);
  }

  .tabs button {
    background: none;
    border: none;
    color: #64748b;
    padding: 1rem 0;
    cursor: pointer;
    font-size: 0.9rem;
    text-transform: uppercase;
    letter-spacing: 0.15em;
    transition: color 0.3s;
  }

  .tabs button.active {
    color: #fbbf24;
    border-bottom: 2px solid #fbbf24;
  }

  .transcript-box {
    background: rgba(0, 0, 0, 0.15);
    padding: 2rem;
    border-radius: 20px;
    max-height: 500px;
    overflow-y: auto;
    display: flex;
    flex-direction: column;
    gap: 1.5rem;
  }

  .message {
    padding: 1.5rem;
    border-radius: 16px;
    background: rgba(255, 255, 255, 0.02);
    border: 1px solid rgba(255, 255, 255, 0.05);
  }

  .message strong {
    display: block;
    font-size: 0.75rem;
    text-transform: uppercase;
    letter-spacing: 0.1rem;
    color: rgba(251, 191, 36, 0.6);
    margin-bottom: 0.75rem;
  }

  .message.mine {
    background: rgba(251, 191, 36, 0.03);
    border-color: rgba(251, 191, 36, 0.1);
  }

  .message.mine strong { color: #fbbf24; }

  .tab-content {
    line-height: 1.8;
    color: #cbd5e1;
    font-size: 1.05rem;
  }

  .summary-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 2rem;
  }

  .stat-box {
    background: rgba(255, 255, 255, 0.02);
    padding: 1.5rem;
    border-radius: 16px;
    border: 1px solid rgba(255, 255, 255, 0.05);
  }

  .label {
    display: block;
    font-size: 0.65rem;
    letter-spacing: 0.15em;
    color: rgba(148, 163, 184, 0.5);
    margin-bottom: 1rem;
    font-weight: 600;
  }

  .value.accent-gold {
    font-family: 'Cormorant Garamond', serif;
    font-size: 1.8rem;
    color: #fbbf24;
  }

  .synergy-list {
    list-style: none;
    padding: 0;
    margin: 0;
  }

  .synergy-list li {
    font-size: 0.95rem;
    color: #e2e8f0;
    margin-bottom: 0.75rem;
    padding-left: 1.5rem;
    position: relative;
  }

  .synergy-list li::before {
    content: '✧';
    position: absolute;
    left: 0;
    color: #fbbf24;
  }

  .horsemen-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 0.75rem;
  }

  .horseman {
    background: rgba(255, 255, 255, 0.03);
    padding: 0.75rem 1rem;
    border-radius: 10px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    opacity: 0.4;
    filter: grayscale(1);
    transition: all 0.3s;
  }

  .horseman.active {
    opacity: 1;
    filter: none;
    background: rgba(239, 68, 68, 0.1);
    border: 1px solid rgba(239, 68, 68, 0.3);
  }

  .horseman.cultural.active {
    background: rgba(251, 191, 36, 0.1);
    border: 1px solid rgba(251, 191, 36, 0.3);
  }

  .h-name { font-size: 0.7rem; text-transform: uppercase; color: #94a3b8;}
  .horseman.active .h-name { color: #f8fafc; }
  .h-count { font-weight: bold; font-family: 'Cormorant Garamond', serif; font-size: 1.2rem;}

  .fade-in {
    animation: fadeIn 0.8s cubic-bezier(0.2, 1, 0.2, 1);
  }

  @keyframes fadeIn {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
  }
</style>
