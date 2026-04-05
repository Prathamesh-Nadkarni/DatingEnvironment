<script lang="ts">
  import { onMount } from 'svelte';
  import Dashboard from './Dashboard.svelte';

  let sections: any[] = [];
  let currentSectionIndex = 0;
  let currentQuestionIndex = 0;
  let answers: Record<string, any> = {};
  let submitted = false;
  let loading = true;
  let isTransitioning = false;

  const CORE_DIMENSIONS = [
    "family_deference", "couple_first_orientation", "boundary_strength", "egalitarianism",
    "tradition_compliance", "public_harmony_preference", "partner_advocacy", "financial_mutuality",
    "risk_tolerance", "security_need", "co_regulation_capacity", "distress_tolerance",
    "conflict_dominance", "withdrawal_tendency", "repair_skill", "shame_sensitivity",
    "guilt_susceptibility", "autonomy_need", "caregiving_flexibility", "parenting_alignment",
    "jealousy_threshold", "privacy_need", "career_priority", "resentment_accumulation_rate",
    "forgiveness_rate", "moral_reasoning_style", "burnout_vulnerability", "identity_rigidity",
    "household_order_preference", "social_image_sensitivity"
  ];

  onMount(async () => {
    try {
      const response = await fetch('http://localhost:8000/api/onboarding/questions');
      if (response.ok) {
        const data = await response.json();
        sections = data.sections;
      }
    } catch(e) {
      console.error("Backend connection failed, using fallback...");
      // Fallback logic if needed
    } finally {
      loading = false;
    }
  });

  $: currentSection = sections[currentSectionIndex];
  $: currentQuestion = currentSection?.questions[currentQuestionIndex];
  $: totalQuestionsInSection = currentSection?.questions.length || 0;

  let introSlide = true;

  function selectOption(qId: string, value: any) {
    if ("vibrate" in navigator) navigator.vibrate(10);
    if (currentQuestion.format === 'ranking') {
        const currentRanking = answers[qId] || [];
        if (currentRanking.includes(value)) {
            answers[qId] = currentRanking.filter((i: any) => i !== value);
        } else {
            answers[qId] = [...currentRanking, value];
        }
    } else {
        answers[qId] = value;
    }
  }

  async function handleNext() {
    if ("vibrate" in navigator) navigator.vibrate(20);
    isTransitioning = true;
    setTimeout(async () => {
        if (introSlide) {
          introSlide = false;
        } else if (currentQuestionIndex < totalQuestionsInSection - 1) {
          currentQuestionIndex++;
        } else if (currentSectionIndex < sections.length - 1) {
          currentSectionIndex++;
          currentQuestionIndex = 0;
        } else {
          await submitSurvey();
        }
        isTransitioning = false;
    }, 500); 
  }

  async function submitSurvey() {
    loading = true;
    try {
      await fetch('http://localhost:8000/api/onboarding/submit', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_id: 1, answers })
      });
    } catch(e) {
       console.error(e);
    }
    submitted = true;
    loading = false;
  }

  function getScaleConfig(q: any) {
    if (q.format === 'importance_scale') {
        return { length: 6, labels: ["Not important", "Slightly", "Somewhat", "Important", "Very", "Extremely"] };
    } else if (q.format === 'scale_6') {
        return { length: 6, labels: ["1", "2", "3", "4", "5", "6"] };
    } else if (q.format === 'comfort_scale') {
        return { length: 7, labels: ["V. Uncomfy", "Uncomfy", "Slightly", "Neutral", "Slightly", "Comfy", "V. Comfy"] };
    } else {
        return { length: 7, labels: ["Strongly Disagree", "Disagree", "Slightly", "Neutral", "Slightly", "Agree", "Strongly Agree"] };
    }
  }
</script>

<svelte:head>
  <link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,400;0,600;1,400&family=Plus+Jakarta+Sans:wght@300;400;500;600&display=swap" rel="stylesheet">
</svelte:head>

<main class="app-root">
  {#if loading}
    <div class="loader-overlay">
        <div class="luxury-spinner"></div>
        <p class="accent-text">Synthesizing {CORE_DIMENSIONS.length} Dimensions of You</p>
    </div>
  {:else if submitted}
    <div class="fade-in">
        <Dashboard userId={1} />
    </div>
  {:else if introSlide}
    <div class="luxury-container {isTransitioning ? 'transitioning' : ''}">
        <div class="card glass intro-card">
            <header>
                <span class="section-tag">Welcome to MiroFish</span>
                <h1 class="accent-title larger">Mirroring the Future of Your Relationships</h1>
            </header>
            <div class="intro-body">
                <p>MiroFish is not a matching algorithm. It is a <strong>High-Fidelity Behavioral Simulation Engine</strong>.</p>
                <p>We are about to build your digital twin—a persona built from your instincts, boundaries, and family conditioning.</p>
                <p>Through 30 clinical-grade stress tests, we will simulate years of real-world friction in minutes to find your most resilient match.</p>
            </div>
            <footer>
                <button class="action-btn-gold" on:click={handleNext}>
                    <span class="btn-text">Begin The Mirroring</span>
                </button>
            </footer>
        </div>
    </div>
  {:else if currentQuestion}
    <div class="progress-bar">
        <div class="fill" style="width: {((currentSectionIndex * 10 + currentQuestionIndex) / (sections.length * 10)) * 100}%"></div>
    </div>

    <div class="luxury-container {isTransitioning ? 'transitioning' : ''}">
      <div class="card glass">
        <header>
            <span class="section-tag">Assessment // Section {currentSectionIndex + 1}: {currentSection.section}</span>
            <h1 class="accent-title">{currentQuestion.text}</h1>
        </header>
        
        <div class="interaction-area">
          {#if currentQuestion.format === 'multiple_choice' || currentQuestion.format === 'forced_choice' || currentQuestion.format === 'sjt'}
              <div class="options-list">
                  {#each currentQuestion.options as opt}
                      <button 
                          class="luxury-btn {answers[currentQuestion.id] === (opt.id || opt) ? 'selected' : ''}"
                          on:click={() => selectOption(currentQuestion.id, opt.id || opt)}>
                          <span class="btn-inner">{opt.text || opt}</span>
                      </button>
                  {/each}
              </div>

          {:else if currentQuestion.format.startsWith('scale') || currentQuestion.format.includes('scale')}
              {@const config = getScaleConfig(currentQuestion)}
              <div class="scale-expert">
                  <div class="scale-labels">
                      <span>{config.labels[0]}</span>
                      <span>{config.labels[config.length - 1]}</span>
                  </div>
                  <div class="scale-row">
                      {#each Array(config.length) as _, i}
                          <button 
                              class="scale-dot-btn {answers[currentQuestion.id] === (i + 1) ? 'selected' : ''}"
                              on:click={() => selectOption(currentQuestion.id, i + 1)}>
                              <span class="val">{i + 1}</span>
                              <span class="dot-label">{config.labels[i] || ''}</span>
                          </button>
                      {/each}
                  </div>
              </div>

          {:else if currentQuestion.format === 'short_answer'}
              <textarea 
                  class="luxury-input"
                  placeholder="Share your thoughts gently..."
                  bind:value={answers[currentQuestion.id]}
              ></textarea>

          {:else if currentQuestion.format === 'text_input'}
              <input 
                  type="text" 
                  class="luxury-input single"
                  placeholder="Your response..."
                  bind:value={answers[currentQuestion.id]}
              />

          {:else if currentQuestion.format === 'ranking'}
              <div class="ranking-hint">Select in order of importance:</div>
              <div class="options-list">
                  {#each currentQuestion.options as opt}
                      <button 
                          class="luxury-btn { (answers[currentQuestion.id] || []).includes(opt) ? 'selected' : '' }"
                          on:click={() => selectOption(currentQuestion.id, opt)}>
                          {#if (answers[currentQuestion.id] || []).includes(opt)}
                              <span class="rank-badge">{(answers[currentQuestion.id] || []).indexOf(opt) + 1}</span>
                          {/if}
                          <span class="btn-inner">{opt}</span>
                      </button>
                  {/each}
              </div>
          {/if}
        </div>

        <footer>
            <button class="action-btn-gold" on:click={handleNext} disabled={!answers[currentQuestion.id]}>
              <span class="btn-text">
                { (currentSectionIndex === sections.length - 1 && currentQuestionIndex === totalQuestionsInSection - 1) ? 'Synthesize My Persona' : 'Calmly Proceed' }
              </span>
              <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14"/><path d="m12 5 7 7-7 7"/></svg>
            </button>
        </footer>
      </div>
    </div>
  {/if}
</main>

<style>
    :global(body) {
        margin: 0;
        background-color: #0f172a;
        background: radial-gradient(circle at center, #1e1b4b 0%, #0f172a 100%);
        color: #f8fafc;
        font-family: 'Plus Jakarta Sans', sans-serif;
        min-height: 100vh;
        -webkit-font-smoothing: antialiased;
    }

    .app-root {
        display: flex;
        align-items: center;
        justify-content: center;
        min-height: 100vh;
        padding: 2rem;
    }

    .glass {
        background: rgba(30, 27, 75, 0.4);
        backdrop-filter: blur(40px);
        -webkit-backdrop-filter: blur(40px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        box-shadow: 0 40px 100px -20px rgba(0, 0, 0, 0.6);
        border-radius: 32px;
    }

    .luxury-container {
        width: 100%;
        max-width: 720px;
        transition: transform 0.6s cubic-bezier(0.2, 1, 0.2, 1), opacity 0.5s ease;
    }

    .luxury-container.transitioning {
        opacity: 0;
        transform: translateY(10px) scale(0.98);
    }

    .card {
        padding: 4rem;
        display: flex;
        flex-direction: column;
        gap: 3rem;
    }

    .section-tag {
        display: block;
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 0.2em;
        color: rgba(251, 191, 36, 0.6);
        margin-bottom: 1rem;
        font-weight: 500;
    }

    .accent-title {
        font-family: 'Cormorant Garamond', serif;
        font-size: 2.75rem;
        line-height: 1.1;
        font-weight: 400;
        color: #fbbf24;
        margin: 0;
    }

    .accent-title.larger {
        font-size: 3.5rem;
    }

    .intro-body {
        margin: 2rem 0;
        font-size: 1.1rem;
        line-height: 1.8;
        color: #cbd5e1;
    }

    .intro-body p {
        margin-bottom: 1.5rem;
    }

    .intro-body strong {
        color: #fbbf24;
        font-weight: 600;
    }

    .options-list {
        display: flex;
        flex-direction: column;
        gap: 0.75rem;
    }

    .luxury-btn {
        background: rgba(255, 255, 255, 0.02);
        border: 1px solid rgba(255, 255, 255, 0.08);
        padding: 1.25rem 1.75rem;
        border-radius: 16px;
        color: #e2e8f0;
        text-align: left;
        cursor: pointer;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        display: flex;
        align-items: center;
        width: 100%;
    }

    .luxury-btn:hover {
        background: rgba(255, 255, 255, 0.05);
        border-color: rgba(251, 191, 36, 0.3);
        transform: translateX(4px);
    }

    .luxury-btn.selected {
        background: #fbbf24;
        border-color: #fbbf24;
        color: #1e1b4b;
        font-weight: 600;
        box-shadow: 0 10px 30px -5px rgba(251, 191, 36, 0.2);
    }

    .scale-expert {
        display: flex;
        flex-direction: column;
        gap: 1.5rem;
    }

    .scale-labels {
        display: flex;
        justify-content: space-between;
        font-size: 0.8rem;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        color: #64748b;
    }

    .scale-row {
        display: flex;
        gap: 0.5rem;
    }

    .scale-dot-btn {
        flex: 1;
        height: 80px;
        background: rgba(255, 255, 255, 0.02);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 12px;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        gap: 4px;
        cursor: pointer;
        transition: all 0.25s ease;
        color: #94a3b8;
    }

    .scale-dot-btn.selected {
        background: #fbbf24;
        color: #1e1b4b;
        border-color: #fbbf24;
    }

    .dot-label {
        font-size: 0.6rem;
        text-transform: uppercase;
        opacity: 0.6;
        text-align: center;
    }

    .val {
        font-weight: 600;
        font-size: 1.1rem;
    }

    .luxury-input {
        width: 100%;
        background: rgba(255, 255, 255, 0.02);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 1.5rem;
        color: white;
        font-family: inherit;
        font-size: 1.1rem;
        resize: none;
        box-sizing: border-box;
    }

    .luxury-input:focus {
        outline: none;
        border-color: #fbbf24;
        background: rgba(255, 255, 255, 0.05);
    }

    .luxury-input.single {
        padding: 1.25rem 1.5rem;
    }

    .action-btn-gold {
        width: 100%;
        background: #fbbf24;
        border: none;
        padding: 1.5rem;
        border-radius: 100px;
        color: #1e1b4b;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.15em;
        font-size: 0.9rem;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 12px;
        cursor: pointer;
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    }

    .action-btn-gold:hover:not(:disabled) {
        transform: translateY(-4px) scale(1.02);
        box-shadow: 0 20px 40px -10px rgba(251, 191, 36, 0.4);
    }

    .action-btn-gold:disabled {
        background: rgba(255, 255, 255, 0.05);
        color: rgba(148, 163, 184, 0.3);
        cursor: not-allowed;
    }

    .progress-bar {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 4px;
        background: rgba(255, 255, 255, 0.03);
    }

    .fill {
        height: 100%;
        background: #fbbf24;
        transition: width 0.8s cubic-bezier(0.65, 0, 0.35, 1);
        box-shadow: 0 0 20px rgba(251, 191, 36, 0.4);
    }

    .loader-overlay {
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 2rem;
    }

    .luxury-spinner {
        width: 60px;
        height: 60px;
        border: 2px solid rgba(251, 191, 36, 0.1);
        border-top-color: #fbbf24;
        border-radius: 50%;
        animation: spin 1.5s linear infinite;
    }

    @keyframes spin {
        to { transform: rotate(360deg); }
    }

    .accent-text {
        font-family: 'Cormorant Garamond', serif;
        font-size: 1.5rem;
        color: #fbbf24;
        font-style: italic;
    }

    .rank-badge {
        background: #fbbf24;
        color: #1e1b4b;
        width: 24px;
        height: 24px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 0.75rem;
        font-weight: 800;
        margin-right: 1rem;
    }

    .ranking-hint {
        color: rgba(148, 163, 184, 0.6);
        font-size: 0.8rem;
        margin-bottom: 1rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }

    .fade-in {
        animation: fadeIn 1s ease forwards;
    }

    @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
    }
</style>
