<script lang="ts">
  import { onMount, tick } from 'svelte';
  import Dashboard from './Dashboard.svelte';
  import Admin from './Admin.svelte';

  let isAdmin = false;
  let sections: any[] = [];
  let currentSectionIndex = 0;
  let currentQuestionIndex = 0;
  let answers: Record<string, any> = {};
  let submitted = false;
  let loading = true;
  let isTransitioning = false;

  let modeSelectionSlide = false;
  let demographicsSlide = false;
  let shareLink = "";
  let sessionId = "local_demo";
  let role = "user_a";
  let isWaitingForPartner = false;
  
  // Telemetry variables
  let questionStartTime = Date.now();
  
  let demographics = {
      fullName: "",
      birthDate: "",
      birthTime: "",
      birthCity: ""
  };

  const CORE_DIMENSIONS = [
    "family_deference", "couple_first_orientation", "boundary_strength", "egalitarianism",
    "tradition_compliance", "public_harmony_preference", "partner_advocacy", "financial_mutuality",
    "risk_tolerance", "security_need", "co_regulation_capacity", "distress_tolerance",
    "conflict_dominance", "withdrawal_tendency", "repair_skill", "shame_sensitivity",
    "guilt_susceptibility", "autonomy_need", "caregiving_flexibility", "parenting_alignment",
    "jealousy_threshold", "privacy_need", "career_priority", "resentment_accumulation_rate",
    "forgiveness_rate", "moral_reasoning_style", "burnout_vulnerability", "identity_rigidity",
    "household_order_preference", "social_image_sensitivity",
    "hygiene_standard", "body_comfort", "sexual_openness", "libido_alignment",
    "intimacy_communication", "ritual_rigidity", "sleep_schedule_compatibility",
    "personal_space_need"
  ];

  const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

  // Telemetry helper
  async function logTelemetry(eventType: string, elementId: string | null = null, details: any = null) {
      let timeTaken = null;
      if (eventType === 'question_answered') {
          timeTaken = Date.now() - questionStartTime;
      }
      
      try {
          await fetch(`${API_URL}/api/telemetry`, {
              method: 'POST',
              headers: {'Content-Type': 'application/json'},
              body: JSON.stringify({
                  session_id: sessionId || 'anonymous',
                  role: role || 'N/A',
                  event_type: eventType,
                  element_id: elementId,
                  time_taken_ms: timeTaken,
                  details: details
              })
          });
      } catch (e) {
          console.error("Telemetry error:", e);
      }
  }

  onMount(async () => {
    const urlParams = new URLSearchParams(window.location.search);
    if (urlParams.get('admin') === 'true') {
        isAdmin = true;
        return;
    }
    if (urlParams.has('session')) {
        sessionId = urlParams.get('session') as string;
        role = urlParams.get('role') || 'user_b';
        introSlide = false;
        modeSelectionSlide = false;
        demographicsSlide = true;
    }

    try {
      const response = await fetch(`${API_URL}/api/onboarding/questions`);
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
  
  $: totalQuestions = sections.reduce((acc, sec) => acc + sec.questions.length, 0);
  $: absoluteQuestionIndex = sections.slice(0, currentSectionIndex).reduce((acc, sec) => acc + sec.questions.length, 0) + currentQuestionIndex;
  $: progressPercent = totalQuestions > 0 ? Math.round((absoluteQuestionIndex / totalQuestions) * 100) : 0;
  
  $: hasAnsweredCurrent = answers[currentQuestion?.id] !== undefined && 
                          (Array.isArray(answers[currentQuestion?.id]) ? answers[currentQuestion?.id].length > 0 : answers[currentQuestion?.id] !== '');

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

  async function handleBack() {
    if ("vibrate" in navigator) navigator.vibrate(20);
    isTransitioning = true;
    setTimeout(() => {
        if (currentQuestionIndex > 0) {
          currentQuestionIndex--;
        } else if (currentSectionIndex > 0) {
          currentSectionIndex--;
          currentQuestionIndex = sections[currentSectionIndex].questions.length - 1;
        } else {
          modeSelectionSlide = true;
          shareLink = "";
        }
        isTransitioning = false;
    }, 500); 
  }

  function handleRestart() {
      if ("vibrate" in navigator) navigator.vibrate(20);
      sessionId = "local_demo";
      role = "user_a";
      shareLink = "";
      answers = {};
      demographics = { fullName: "", birthDate: "", birthTime: "", birthCity: "" };
      currentSectionIndex = 0;
      currentQuestionIndex = 0;
      modeSelectionSlide = false;
      demographicsSlide = false;
      introSlide = true;
  }

  function selectSpecificMode() {
      logTelemetry('button_click', 'generate_1on1_link');
      sessionId = "session_" + Math.random().toString(36).substring(2, 8);
      role = "user_a";
      shareLink = `${window.location.origin}${window.location.pathname}?session=${sessionId}&role=user_b`;
  }

  async function handleNext() {
    if ("vibrate" in navigator) navigator.vibrate(20);
    isTransitioning = true;
    if (currentQuestion) {
        logTelemetry('question_answered', currentQuestion.id, { 
            section: currentSection.section,
            answer: answers[currentQuestion.id]
        });
    }
    
    setTimeout(async () => {
        if (introSlide) {
          logTelemetry('button_click', 'get_started');
          introSlide = false;
          if (!sessionId || sessionId === "local_demo") {
              modeSelectionSlide = true;
          } else {
              demographicsSlide = true;
          }
        } else if (demographicsSlide) {
          logTelemetry('button_click', 'submit_demographics');
          demographicsSlide = false;
        } else if (currentQuestionIndex < totalQuestionsInSection - 1) {
          currentQuestionIndex++;
        } else if (currentSectionIndex < sections.length - 1) {
          currentSectionIndex++;
          currentQuestionIndex = 0;
        } else {
          await submitSurvey();
        }
        questionStartTime = Date.now();
        isTransitioning = false;
    }, 500); 
  }

  async function submitSurvey() {
    loading = true;
    try {
      await fetch(`${API_URL}/api/onboarding/submit`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ session_id: sessionId, role: role, answers, demographics })
      });
    } catch(e) {
       console.error(e);
    }
    
    if (sessionId.startsWith("session_")) {
        isWaitingForPartner = true;
        pollSessionStatus();
    } else {
        submitted = true;
    }
    loading = false;
  }

  async function pollSessionStatus() {
      const interval = setInterval(async () => {
          try {
              const res = await fetch(`${API_URL}/api/session/status/${sessionId}`);
              const data = await res.json();
              if (data.ready) {
                  clearInterval(interval);
                  isWaitingForPartner = false;
                  submitted = true;
              }
          } catch(e) {}
      }, 3000);
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
  <div class="global-logo">
      <span class="logo-mana">Mana</span><span class="logo-match">Match</span>
  </div>
  {#if isAdmin}
    <Admin />
  {:else}
    {#if loading}
      <div class="loader-overlay">
          <div class="luxury-spinner"></div>
          <p class="accent-text">Synthesizing {CORE_DIMENSIONS.length} Dimensions of You</p>
      </div>
    {:else if isWaitingForPartner}
      <div class="loader-overlay">
          <div class="luxury-spinner"></div>
          <p class="accent-text">Waiting for your partner to finish...</p>
          <p class="dim" style="margin-top: 1rem; font-size: 0.9rem;">Keep this page open.</p>
      </div>
    {:else if submitted}
      <div class="fade-in">
          <Dashboard {sessionId} />
      </div>
    {:else if introSlide}
      <div class="luxury-container intro-layout {isTransitioning ? 'transitioning' : ''}">
          <div class="card glass intro-card">
              <header>
                  <div class="brand-badge">
                      <span class="pulse-dot"></span>
                      <span>AI Engine Online</span>
                  </div>
                  <h1 class="accent-title larger">Mirroring the Future of Your Relationships</h1>
              </header>
              <div class="intro-body">
                  <p>Compatibility Engine Co is a <strong>High-Fidelity Behavioral Simulation Engine</strong>.</p>
                  <p>We are about to build your digital twin—a persona generated from your deepest instincts, boundaries, and family conditioning.</p>
                  <p>Through advanced stress tests, we will simulate years of real-world friction in minutes to find your most resilient match.</p>
              </div>
              <footer>
                  <button class="action-btn-gold get-started" on:click={handleNext}>
                      <span class="btn-text">Get Started</span>
                      <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14"/><path d="m12 5 7 7-7 7"/></svg>
                  </button>
              </footer>
          </div>

          <div class="preview-column fade-in delay-1">
              <div class="avatars-container">
                  <img src="/DatingEnvironment/guy.png" class="avatar-img" alt="Guy Avatar" />
                  <div class="match-heart">
                      <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="#fbbf24" stroke="#fbbf24" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M19 14c1.49-1.46 3-3.21 3-5.5A5.5 5.5 0 0 0 16.5 3c-1.76 0-3 .5-4.5 2-1.5-1.5-2.74-2-4.5-2A5.5 5.5 0 0 0 2 8.5c0 2.3 1.5 4.05 3 5.5l7 7Z"/></svg>
                  </div>
                  <img src="/DatingEnvironment/girl.png" class="avatar-img" alt="Girl Avatar" />
              </div>

              <div class="terminal-preview glass">
                  <div class="mac-buttons">
                      <span class="mac-btn red"></span><span class="mac-btn yellow"></span><span class="mac-btn green"></span>
                      <span class="mac-title">test_persona_performance.py</span>
                  </div>
                  <pre class="terminal-text">
<span class="dim">===================================================</span>
<span class="gold">  CASE: Solid Match (74% Aligned)</span>
<span class="dim">===================================================</span>

OVERALL COMPATIBILITY  [################--] <span class="gold">74/100</span>

<span class="gold">-- Static trait compatibility --</span>
  Values           [###############---] 82%
  Conflict style   [############------] 68%
  Trust            [##############----] 76%

<span class="gold">Verdict:</span>
  Highly compatible. Disagreements detected in 
  financial scenarios, but de-escalation logic
  prevented dealbreakers. Long-term viable.
                  </pre>
              </div>
              
              <div class="dashboard-mock glass">
                  <div class="mock-score-card">
                      <span class="mock-label">Simulated Harmony Index</span>
                      <span class="mock-score gold-glow">74%</span>
                  </div>
                  <div class="mock-stats">
                      <div class="mock-stat">
                          <span class="mock-label">TRAJECTORY</span>
                          <span class="mock-val">STABLE</span>
                      </div>
                      <div class="mock-stat">
                          <span class="mock-label">TOP STRENGTH</span>
                          <span class="mock-val">Emotional Support</span>
                      </div>
                  </div>
              </div>
          </div>
      </div>
    {:else if modeSelectionSlide}
      <div class="luxury-container {isTransitioning ? 'transitioning' : ''}">
          <div class="card glass">
              <header>
                  <h1 class="accent-title" style="text-align: center;">Session Link</h1>
              </header>
              {#if !shareLink}
                  <div class="mode-buttons" style="display: flex; gap: 1rem; margin-top: 2rem;">
                      <button class="action-btn-gold" on:click={selectSpecificMode} style="flex: 1; padding: 1.5rem;">Generate 1-on-1 Match Link<br><small style="opacity: 0.8;">Test compatibility with a specific person</small></button>
                  </div>
                  <div style="margin-top: 1rem; text-align: center;">
                      <button class="action-btn-ghost" style="padding: 0.5rem 2rem; border: none;" on:click={() => { introSlide = true; modeSelectionSlide = false; }}>Back to Intro</button>
                  </div>
              {:else}
                  <div class="share-link-box" style="text-align: center; margin-top: 2rem;">
                      <p style="margin-bottom: 1rem;">Share this link with your partner:</p>
                      <input type="text" readonly value={shareLink} class="luxury-input" style="text-align: center; margin-bottom: 2rem;" on:focus={(e) => e.target.select()} />
                      <div style="display: flex; gap: 1rem;">
                          <button class="action-btn-ghost" style="flex: 0.5;" on:click={() => { shareLink = ""; }}>Back</button>
                          <button class="action-btn-gold" style="flex: 1;" on:click={() => { modeSelectionSlide = false; demographicsSlide = true; }}>Proceed to Questionnaire</button>
                      </div>
                  </div>
              {/if}
          </div>
      </div>
    {:else if demographicsSlide}
      <div class="luxury-container {isTransitioning ? 'transitioning' : ''}">
          <div class="card glass">
              <header>
                  <h1 class="accent-title" style="text-align: center;">Astrological Fingerprint</h1>
                  <p style="text-align: center; color: rgba(255,255,255,0.7); margin-top: 0.5rem;">Before we begin the behavioral simulation, we need your birth details to generate your Kundali (Ashtakoota) compatibility matrix.</p>
              </header>
              
              <div style="display: flex; flex-direction: column; gap: 1rem; margin-top: 2rem;">
                  <input type="text" class="luxury-input single" placeholder="Full Name" bind:value={demographics.fullName} />
                  <input type="date" class="luxury-input single" placeholder="Date of Birth" bind:value={demographics.birthDate} />
                  <input type="time" class="luxury-input single" placeholder="Time of Birth" bind:value={demographics.birthTime} />
                  <input type="text" class="luxury-input single" placeholder="City of Birth" bind:value={demographics.birthCity} />
              </div>

              <footer class="nav-footer" style="margin-top: 2rem;">
                  <button class="action-btn-gold" on:click={handleNext} disabled={!demographics.fullName || !demographics.birthDate || !demographics.birthTime || !demographics.birthCity}>
                    <span class="btn-text">Start Simulation</span>
                  </button>
              </footer>
          </div>
      </div>
    {:else if currentQuestion}
      <div class="progress-container">
          <div class="progress-bar">
              <div class="fill" style="width: {progressPercent}%"></div>
          </div>
          <div class="progress-text">
              <span>{progressPercent}% Completed</span>
              <span class="dim">({absoluteQuestionIndex} / {totalQuestions})</span>
          </div>
      </div>

      <div class="luxury-container {isTransitioning ? 'transitioning' : ''}">
        <div class="card glass">
          <header>
              <div style="display: flex; justify-content: space-between; align-items: center; width: 100%;">
                  <span class="section-tag">Assessment // Section {currentSectionIndex + 1}: {currentSection.section}</span>
                  <button class="action-btn-ghost" style="padding: 0.5rem 1rem; border: none; font-size: 0.8rem;" on:click={handleRestart}>Restart</button>
              </div>
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

          <footer class="nav-footer">
              <button class="action-btn-ghost" on:click={handleBack}>
                <span class="btn-text">Back</span>
              </button>
              <button class="action-btn-gold" on:click={handleNext} disabled={!hasAnsweredCurrent}>
                <span class="btn-text">
                    {#if currentSectionIndex === sections.length - 1 && currentQuestionIndex === totalQuestionsInSection - 1}
                        Complete Simulation
                    {:else}
                        Next Question
                    {/if}
                </span>
              </button>
          </footer>
        </div>
      </div>
    {/if}
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

    .luxury-container.intro-layout {
        max-width: 1200px;
        display: grid;
        grid-template-columns: 1.2fr 1fr;
        gap: 3rem;
        align-items: center;
    }

    @media (max-width: 900px) {
        .luxury-container.intro-layout {
            grid-template-columns: 1fr;
        }
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

    .brand-badge {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        background: rgba(251, 191, 36, 0.1);
        border: 1px solid rgba(251, 191, 36, 0.2);
        padding: 6px 12px;
        border-radius: 100px;
        font-size: 0.7rem;
        text-transform: uppercase;
        letter-spacing: 0.15em;
        color: #fbbf24;
        margin-bottom: 1.5rem;
    }

    .pulse-dot {
        width: 6px;
        height: 6px;
        background: #fbbf24;
        border-radius: 50%;
        box-shadow: 0 0 10px #fbbf24;
        animation: pulse 2s infinite;
    }

    @keyframes pulse {
        0% { opacity: 1; transform: scale(1); }
        50% { opacity: 0.5; transform: scale(1.5); }
        100% { opacity: 1; transform: scale(1); }
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

    .nav-footer {
        display: flex;
        gap: 1rem;
        margin-top: 1rem;
    }

    .action-btn-ghost {
        flex: 0.3;
        background: transparent;
        border: 1px solid rgba(255, 255, 255, 0.2);
        color: rgba(255, 255, 255, 0.7);
        border-radius: 12px;
        font-family: 'Plus Jakarta Sans', sans-serif;
        font-weight: 500;
        font-size: 0.85rem;
        cursor: pointer;
        transition: all 0.3s ease;
    }

    .action-btn-ghost:hover {
        background: rgba(255, 255, 255, 0.05);
        border-color: rgba(255, 255, 255, 0.4);
    }

    .action-btn-gold {
        flex: 1;
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

    .action-btn-gold.get-started {
        font-size: 1rem;
        padding: 1.75rem;
        box-shadow: 0 10px 30px -10px rgba(251, 191, 36, 0.3);
    }

    .progress-container {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        z-index: 50;
    }

    .progress-bar {
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

    .progress-text {
        position: absolute;
        top: 12px;
        right: 2rem;
        font-size: 0.75rem;
        font-weight: 600;
        color: #fbbf24;
        letter-spacing: 0.1em;
        text-transform: uppercase;
        display: flex;
        gap: 8px;
    }

    .progress-text .dim {
        color: rgba(255,255,255,0.4);
        font-weight: 400;
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
    
    .delay-1 {
        animation-delay: 0.3s;
        opacity: 0;
    }

    @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
    }

    .preview-column {
        display: flex;
        flex-direction: column;
        gap: 1.5rem;
    }

    .terminal-preview {
        padding: 1.5rem;
        border-radius: 20px;
        background: rgba(0, 0, 0, 0.4);
        border: 1px solid rgba(255, 255, 255, 0.05);
        font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace;
        font-size: 0.85rem;
    }

    .mac-buttons {
        display: flex;
        gap: 6px;
        margin-bottom: 1rem;
        align-items: center;
    }

    .mac-btn {
        width: 12px;
        height: 12px;
        border-radius: 50%;
    }
    .mac-btn.red { background: #ff5f56; }
    .mac-btn.yellow { background: #ffbd2e; }
    .mac-btn.green { background: #27c93f; }
    .mac-title {
        margin-left: 10px;
        color: rgba(255, 255, 255, 0.3);
        font-size: 0.75rem;
    }

    .terminal-text {
        color: #e2e8f0;
        margin: 0;
        line-height: 1.6;
        overflow-x: hidden;
    }

    .terminal-text .dim { color: rgba(255, 255, 255, 0.3); }
    .terminal-text .gold { color: #fbbf24; font-weight: bold; }
    .terminal-text .red { color: #ef4444; font-weight: bold; }

    .dashboard-mock {
        padding: 1.5rem;
        border-radius: 20px;
        display: flex;
        align-items: center;
        gap: 2rem;
    }

    .mock-score-card {
        text-align: center;
    }

    .mock-label {
        display: block;
        font-size: 0.65rem;
        letter-spacing: 0.15em;
        text-transform: uppercase;
        color: rgba(255, 255, 255, 0.5);
        margin-bottom: 0.5rem;
    }

    .mock-score {
        font-family: 'Cormorant Garamond', serif;
        font-size: 3rem;
        line-height: 1;
    }
    
    .mock-score.gold-glow {
        color: #fbbf24;
        text-shadow: 0 0 20px rgba(251, 191, 36, 0.4);
    }

    .mock-stats {
        display: flex;
        flex-direction: column;
        gap: 1rem;
        border-left: 1px solid rgba(255, 255, 255, 0.1);
        padding-left: 2rem;
    }

    .mock-val {
        color: #f8fafc;
        font-weight: 600;
        font-size: 0.9rem;
    }

    .avatars-container {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 1rem;
        margin-bottom: -1rem;
        position: relative;
        z-index: 10;
    }

    .avatar-img {
        width: 100px;
        height: 100px;
        border-radius: 50%;
        object-fit: cover;
        background: rgba(255, 255, 255, 0.1);
        border: 2px solid rgba(255, 255, 255, 0.2);
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.5);
    }

    .match-heart {
        display: flex;
        align-items: center;
        justify-content: center;
        width: 40px;
        height: 40px;
        background: rgba(0, 0, 0, 0.6);
        border-radius: 50%;
        border: 1px solid rgba(251, 191, 36, 0.3);
        box-shadow: 0 0 15px rgba(251, 191, 36, 0.2);
        animation: heartbeat 1.5s infinite;
    }

    @keyframes heartbeat {
        0% { transform: scale(1); }
        15% { transform: scale(1.15); }
        30% { transform: scale(1); }
        45% { transform: scale(1.15); }
        60% { transform: scale(1); }
        100% { transform: scale(1); }
    }

    .global-logo {
        position: absolute;
        top: 2rem;
        left: 2rem;
        font-family: 'Cormorant Garamond', serif;
        font-size: 2.2rem;
        font-weight: 600;
        letter-spacing: -0.02em;
        display: flex;
        align-items: center;
        z-index: 100;
        user-select: none;
    }

    .logo-mana {
        color: #f8fafc;
        text-shadow: 0 0 10px rgba(255, 255, 255, 0.2);
    }

    .logo-match {
        color: #fbbf24;
        font-style: italic;
        text-shadow: 0 0 15px rgba(251, 191, 36, 0.4);
        margin-left: 1px;
    }

    @media (max-width: 768px) {
        .global-logo {
            position: relative;
            top: 0;
            left: 0;
            justify-content: center;
            margin-bottom: 2rem;
            margin-top: 1rem;
        }
    }
</style>
