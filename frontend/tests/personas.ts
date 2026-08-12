export const personas = {
    A: {
        name: "Traditional Tara",
        description: "Values family, duty, stability, and marriage.",
        keywords: ["family", "duty", "marriage", "stable", "dependable", "tradition", "elders", "respect", "peace", "comfort"],
        scaleBias: "high", // leans toward 4-5 on traditional scales
        shortAnswer: "I am looking for a traditional family-oriented partner."
    },
    B: {
        name: "Modern Rohan",
        description: "Values independence, growth, ambition, and freedom.",
        keywords: ["career", "independence", "growth", "freedom", "exciting", "equal", "modern", "ambition", "partnership", "opportunity"],
        scaleBias: "low",
        shortAnswer: "I am looking for a modern, independent partner to build a life with."
    },
    C: {
        name: "Emotional Priya",
        description: "Values deep emotional connection, chemistry, and expressiveness.",
        keywords: ["emotional connection", "chemistry", "warm", "expressive", "passionate", "understands", "comfort first", "intense"],
        scaleBias: "high",
        shortAnswer: "I want deep emotional connection and someone who understands me."
    },
    D: {
        name: "Practical Amit",
        description: "Values logic, financial stability, practicality, and peace.",
        keywords: ["practical", "calm", "private", "logical", "financial", "reserved", "firm", "practicality", "savings"],
        scaleBias: "mid",
        shortAnswer: "Looking for practical stability and a peaceful life."
    }
};

export async function answerQuestion(page: any, persona: any, logTest: Function) {
    let questionCount = 0;
    
    while (true) {
        await page.waitForSelector('.interaction-area');
        
        const nextBtn = page.locator('button.action-btn-gold');
        
        const format = await page.evaluate(() => {
            if (document.querySelector('.scale-expert')) return 'scale';
            if (document.querySelector('.ranking-hint')) return 'ranking';
            if (document.querySelector('textarea')) return 'textarea';
            if (document.querySelector('input[type="text"].single')) return 'text_input';
            return 'options';
        });

        // Add realistic delay for reading (100 - 300ms for fast testing, usually would be longer)
        await page.waitForTimeout(Math.random() * 200 + 100);

        if (format === 'scale') {
            const dots = page.locator('.scale-dot-btn');
            const count = await dots.count();
            if (count > 0) {
                let pick = Math.floor(count / 2); // default mid
                if (persona.scaleBias === 'high') pick = Math.min(count - 1, pick + 2);
                if (persona.scaleBias === 'low') pick = Math.max(0, pick - 2);
                await dots.nth(pick).click({ force: true });
            }
        } else if (format === 'ranking' || format === 'options') {
            const btns = page.locator('.options-list button');
            const count = await btns.count();
            
            // Score each option
            let bestIndex = 0;
            let bestScore = -1;
            
            for (let i = 0; i < count; i++) {
                const text = (await btns.nth(i).textContent()) || "";
                let score = 0;
                for (const kw of persona.keywords) {
                    if (text.toLowerCase().includes(kw.toLowerCase())) score += 5;
                }
                
                // Add a deterministic hash element to break ties so they don't all pick index 0
                const hash = text.length % 3;
                score += hash;
                
                if (score > bestScore) {
                    bestScore = score;
                    bestIndex = i;
                }
            }
            
            if (format === 'ranking') {
                // Click all but prioritize best index first
                await btns.nth(bestIndex).click({ force: true });
                await page.waitForTimeout(50);
                for (let i = 0; i < count; i++) {
                    if (i !== bestIndex) {
                        await btns.nth(i).click({ force: true });
                        await page.waitForTimeout(50);
                    }
                }
            } else {
                await btns.nth(bestIndex).click({ force: true });
            }
        } else if (format === 'textarea' || format === 'text_input') {
            const questionText = await page.locator('.accent-title').first().textContent() || "";
            let answerText = persona.shortAnswer;
            const q = questionText.toLowerCase();

            if (q.includes("kind of person")) {
                if (persona.name.includes("Tara")) answerText = "I want a grounded, responsible man who respects my family and values a peaceful, structured life.";
                else if (persona.name.includes("Rohan")) answerText = "An independent equal who has her own ambitions and doesn't rely on me for her entire identity.";
                else if (persona.name.includes("Priya")) answerText = "Someone who isn't afraid to be vulnerable with me and prioritize our emotional connection above everything.";
                else answerText = "A rational, calm partner who handles finances well and doesn't bring unnecessary drama into my life.";
            } else if (q.includes("unspoken rule")) {
                if (persona.name.includes("Tara")) answerText = "Elders are always right, and you never talk back to them in front of others.";
                else if (persona.name.includes("Rohan")) answerText = "You have to figure out your own problems; no one is going to hand you success.";
                else if (persona.name.includes("Priya")) answerText = "We don't go to bed angry. Silence was treated as a punishment in my house.";
                else answerText = "Don't waste money and don't make a scene.";
            } else if (q.includes("respected")) {
                if (persona.name.includes("Tara")) answerText = "When my partner consults me before making a decision that affects our family.";
                else if (persona.name.includes("Rohan")) answerText = "When they respect my need for space and support my career without being needy.";
                else if (persona.name.includes("Priya")) answerText = "When they actually listen to how I feel instead of just trying to 'fix' my problems logically.";
                else answerText = "When my practical advice is taken seriously and my boundaries are honored.";
            } else if (q.includes("spouse should never do")) {
                if (persona.name.includes("Tara")) answerText = "Disrespect my parents or air our dirty laundry to outsiders.";
                else if (persona.name.includes("Rohan")) answerText = "Try to control who I am or hold me back from my goals.";
                else if (persona.name.includes("Priya")) answerText = "Shut me out emotionally or refuse to communicate when things get hard.";
                else answerText = "Lie about finances or make reckless decisions that jeopardize our stability.";
            } else if (q.includes("distance from family")) {
                if (persona.name.includes("Tara")) answerText = "We shouldn't have distance. Family is everything, we should be deeply involved.";
                else if (persona.name.includes("Rohan")) answerText = "Living separately and only visiting on holidays or when convenient. Our unit comes first.";
                else if (persona.name.includes("Priya")) answerText = "Being close enough to care, but having strict boundaries so they don't interfere in our marriage.";
                else answerText = "Maintaining a polite relationship but strictly keeping our finances and household separate.";
            } else if (q.includes("taken for granted")) {
                if (persona.name.includes("Tara")) answerText = "When I cook and clean and nobody even acknowledges the effort it takes to keep the house running.";
                else if (persona.name.includes("Rohan")) answerText = "When it's assumed I'll just pay for everything without it being a discussion.";
                else if (persona.name.includes("Priya")) answerText = "When I constantly check in on their feelings, but they never ask how my day was.";
                else answerText = "When people expect me to just handle all the logistics and paperwork without helping.";
            } else if (q.includes("spending")) {
                if (persona.name.includes("Tara")) answerText = "Making a massive purchase or giving away a lot of money without asking me.";
                else if (persona.name.includes("Rohan")) answerText = "I don't care what they spend their own money on, but they shouldn't spend from our joint savings.";
                else if (persona.name.includes("Priya")) answerText = "Spending money on a luxury for themselves when we haven't had a date night in months.";
                else answerText = "Any frivolous spending that puts us into debt or jeopardizes our emergency fund.";
            } else if (q.includes("genuine apology")) {
                if (persona.name.includes("Tara")) answerText = "Admitting they were wrong and showing they've changed their behavior.";
                else if (persona.name.includes("Rohan")) answerText = "A quick 'my bad' and moving on. I don't need a huge emotional display.";
                else if (persona.name.includes("Priya")) answerText = "Looking me in the eye, validating why I was hurt, and holding me.";
                else answerText = "Explaining logically why it happened and exactly what steps they will take to prevent it.";
            } else if (q.includes("emotionally safest")) {
                if (persona.name.includes("Tara")) answerText = "When I know they will never leave, no matter what happens.";
                else if (persona.name.includes("Rohan")) answerText = "When I feel I can be fully myself without being judged or tied down.";
                else if (persona.name.includes("Priya")) answerText = "When I'm crying or upset and they don't pull away, but lean in closer.";
                else answerText = "When the bills are paid, the house is quiet, and there is no chaos.";
            } else if (q.includes("lifestyle difference")) {
                if (persona.name.includes("Tara")) answerText = "If they wanted to go out partying every weekend while I want to be home with family.";
                else if (persona.name.includes("Rohan")) answerText = "If they expected me to be home at 5 PM every day and resented my work hours.";
                else if (persona.name.includes("Priya")) answerText = "If they wanted to spend all their free time playing video games instead of connecting.";
                else answerText = "If they were messy and disorganized while I need a clean, structured environment.";
            } else if (q.includes("parenting belief")) {
                if (persona.name.includes("Tara")) answerText = "Children must respect their elders and know their culture.";
                else if (persona.name.includes("Rohan")) answerText = "We will not force our kids into a specific career path; they must be independent.";
                else if (persona.name.includes("Priya")) answerText = "We will never use the silent treatment or emotional manipulation on our kids.";
                else answerText = "We will teach them financial literacy from a young age.";
            } else if (q.includes("permanently damage trust")) {
                if (persona.name.includes("Tara")) answerText = "Cheating or humiliating me in front of my community.";
                else if (persona.name.includes("Rohan")) answerText = "Snooping through my phone or trying to trap me.";
                else if (persona.name.includes("Priya")) answerText = "Lying to me about something important, or having an emotional affair.";
                else answerText = "Hiding massive amounts of debt.";
            } else if (q.includes("repeated pattern")) {
                if (persona.name.includes("Tara")) answerText = "Constantly putting their friends above our family responsibilities.";
                else if (persona.name.includes("Rohan")) answerText = "Clinginess and constantly needing me to reassure them.";
                else if (persona.name.includes("Priya")) answerText = "Dismissing my feelings as 'dramatic' every time I bring up an issue.";
                else answerText = "Repeatedly breaking promises or failing to do chores they said they would do.";
            } else if (q.includes("unsupported")) {
                if (persona.name.includes("Tara")) answerText = "When my in-laws criticized me and my partner just sat there silently.";
                else if (persona.name.includes("Rohan")) answerText = "When I wanted to take a risk on a new business and everyone told me to play it safe.";
                else if (persona.name.includes("Priya")) answerText = "When I was going through a depressive episode and they just told me to cheer up.";
                else answerText = "When I was overwhelmed with logistics for a move and they offered zero practical help.";
            } else if (q.includes("hygiene")) {
                if (persona.name.includes("Tara")) answerText = "Not showering every day before doing puja.";
                else if (persona.name.includes("Rohan")) answerText = "Leaving wet towels on the bed.";
                else if (persona.name.includes("Priya")) answerText = "Bad breath or not taking care of their physical health.";
                else answerText = "Leaving the kitchen a mess after cooking.";
            } else if (q.includes("ritual")) {
                if (persona.name.includes("Tara")) answerText = "Not having dinner together as a family.";
                else if (persona.name.includes("Rohan")) answerText = "Someone interrupting my morning gym or deep-work routine.";
                else if (persona.name.includes("Priya")) answerText = "Skipping our goodnight kiss or morning coffee chat.";
                else answerText = "Moving my organized things or changing the schedule last minute.";
            } else {
                // Generic fallback that uses their core identity
                answerText = persona.shortAnswer;
            }

            if (format === 'textarea') {
                await page.fill('textarea', answerText);
            } else {
                await page.fill('input[type="text"].single', answerText);
            }
        }

        const nextBtnText = await nextBtn.textContent();
        
        // Wait for next button to become enabled
        let retries = 0;
        while (retries < 10) {
            const isEnabled = await nextBtn.isEnabled();
            if (isEnabled) break;
            await page.waitForTimeout(100);
            retries++;
        }
        
        await nextBtn.click({ force: true });
        questionCount++;
        
        // Let Svelte transition (500ms delay in component)
        await page.waitForTimeout(600); 
        
        if (nextBtnText?.includes('Complete Simulation')) {
            break;
        }
    }
}
