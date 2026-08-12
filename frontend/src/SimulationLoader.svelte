<script>
    import { onMount, onDestroy } from 'svelte';
    
    const messages = [
        "Synthesizing behavioral profiles...",
        "Running conflict simulations...",
        "Evaluating structural tension...",
        "Analyzing communication patterns...",
        "Compiling psychological report...",
        "Almost done..."
    ];
    
    let currentMessageIndex = 0;
    let interval;
    
    onMount(() => {
        interval = setInterval(() => {
            currentMessageIndex = (currentMessageIndex + 1) % messages.length;
        }, 12000); // Change text every 12 seconds since it takes ~2 mins total
    });
    
    onDestroy(() => {
        clearInterval(interval);
    });
</script>

<div class="simulation-loader">
    <div class="radar-container">
        <div class="radar-circle"></div>
        <div class="radar-ping"></div>
        <div class="radar-center"></div>
    </div>
    <div class="loader-text-container">
        {#key currentMessageIndex}
            <p class="loader-message fade-in-up">{messages[currentMessageIndex]}</p>
        {/key}
    </div>
    <p class="loader-subtext">Agentic LLM Simulation in progress. This typically takes 1-2 minutes.</p>
</div>

<style>
    .simulation-loader {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        padding: 4rem 2rem;
        text-align: center;
        background: rgba(15, 23, 42, 0.4);
        border: 1px solid rgba(148, 163, 184, 0.1);
        border-radius: 16px;
        backdrop-filter: blur(12px);
        margin: 2rem 0;
    }

    .radar-container {
        position: relative;
        width: 80px;
        height: 80px;
        margin-bottom: 2rem;
    }

    .radar-circle, .radar-ping {
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        border-radius: 50%;
    }

    .radar-circle {
        border: 2px solid rgba(167, 139, 250, 0.3);
    }

    .radar-ping {
        background-color: rgba(167, 139, 250, 0.4);
        animation: ping 2s cubic-bezier(0, 0, 0.2, 1) infinite;
    }

    .radar-center {
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        width: 16px;
        height: 16px;
        background: #a78bfa;
        border-radius: 50%;
        box-shadow: 0 0 15px #a78bfa, 0 0 30px #a78bfa;
    }

    @keyframes ping {
        75%, 100% {
            transform: scale(2);
            opacity: 0;
        }
    }

    .loader-text-container {
        height: 28px;
        margin-bottom: 0.5rem;
    }

    .loader-message {
        font-family: 'Plus Jakarta Sans', sans-serif;
        font-size: 1.1rem;
        font-weight: 500;
        color: #f8fafc;
        margin: 0;
        letter-spacing: 0.5px;
    }

    .loader-subtext {
        font-family: 'Plus Jakarta Sans', sans-serif;
        font-size: 0.85rem;
        color: #94a3b8;
        margin: 0;
    }

    .fade-in-up {
        animation: fadeInUp 0.5s ease-out forwards;
    }

    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(10px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
</style>
