# ManaMatch — Behavioral Compatibility Engine

> *"Don't ask who someone is. Watch what they do when the stakes are real."*

**🌟 [Try the Live Demo Here!](https://Prathamesh-Nadkarni.github.io/DatingEnvironment/)**

ManaMatch is a relationship compatibility platform built on a fundamentally different premise than every dating app in existence. It does not ask you what you like or what you are looking for. It clones you into a behavioral AI agent and stress-tests that clone against a potential match across 18 high-stakes scenarios drawn from real Indian relational conflict patterns — before the first conversation ever happens.

The result is not a star sign match or a percentage derived from survey answers. It is a behavioral simulation report: what you actually do when your mother-in-law demands your wife's gold, when your husband suggests you quit your job for the children's exams, or when a financial crisis hits and both of you want to blame someone.



## Why This Exists

Every matchmaking system — from shaadi.com to Hinge to even therapist-facilitated intros — relies on two deeply flawed data sources: **self-report** and **performance**.

**Self-report** is how you describe yourself ("I'm easy-going, family-oriented, career-driven"). Research by Vazire & Mehl (2008) and Eastwick & Finkel (2008) consistently shows that self-reported personality explains roughly 2–4% of real relationship satisfaction variance. People are not lying. They genuinely do not know how they will behave under pressure until it happens.

**Performance** is first-impression chemistry — how you come across in the first few hours. It is heavily influenced by appearance, verbal fluency, and the motivation to impress. The traits that destroy relationships (withdrawal under pressure, guilt-tripping, resentment accumulation, inability to repair after conflict) are almost entirely invisible in a first impression.

**The Indian context adds a third layer of complexity** that western compatibility models ignore entirely. Indian marriages are not a union of two individuals. They are a negotiation between two family systems, two cultural scripts, two sets of gender expectations, and, increasingly, two professional identities competing for primacy. A couple can have perfect personal chemistry and be destroyed within eighteen months by in-law dynamics, stridhan disputes, or the husband's inability to advocate for his wife against his own mother.

ManaMatch was built to surface all of this before the first coffee.

---

## How It Works — The Four-Stage Pipeline

```
RAW ANSWERS
    │
    ▼
┌─────────────────────────────────────────┐
│  Stage 1: Intake Engine                 │
│  23 question sections · SJT + Scale     │
│  + Forced Choice + Narrative probes     │
└────────────────────┬────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────┐
│  Stage 2: Persona Synthesis             │
│  EvidenceStore probability mapping      │
│  → 30-dimensional Trait Distributions   │
│  → Cluster assignment (3 axes)          │
│  → Stress-Activated Policy injection    │
└────────────────────┬────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────┐
│  Stage 3: The Sandbox (Simulation)      │
│  Stateful 15-Year Scenario Loop         │
│  · MarriageState persistence            │
│  · Tension computation (per scenario)   │
│  · 7-category dialogue generation       │
│  · Resentment override logic            │
│  × 100 scenarios (3 per category × 6)   │
└────────────────────┬────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────┐
│  Stage 3.5: Environmental Mechanics     │
│  · Smart Agent Interventions            │
│  · (MIL, Patriarch, Sibling, Society)   │
│  · Non-linear Happiness/Stress Alg      │
│  · The Relationship "Limit Break"       │
└────────────────────┬────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────┐
│  Stage 4: The Arbitrator (Evaluation)   │
│  Category-behaviour primary scoring     │
│  + Environmental Happiness impact       │
│  + Gottman Four Horsemen detection      │
│  + Indian cultural stressor detection   │
│  + Synergy detection                    │
│  + 5-model static trait compatibility   │
└─────────────────────────────────────────┘
```

---

## Stage 1 — The Intake Engine

### Philosophy of the Questions

The intake is not a personality test. It is a **diagnostic portfolio** designed to extract behavioral predictions from four distinct question formats:

- **Probe Bundles (SJT + Emotion + Reflection):** Situational Judgement Tests are served as multi-part bundles. Instead of just picking an action, respondents pick an **Action**, then identify the underlying **Emotion** driving it, and finally provide a free-text **Reflection**. This prevents the system from confusing "silence out of fear" with "silence out of patience". Example: *"Your mother-in-law criticises your spouse..."* The chosen action reveals `partner_advocacy`, while the follow-up probes detect `shame_sensitivity` or `public_harmony_preference`.

- **Likert Scales (1–6):** Measure trait intensity without forcing binary positions. Used for traits like `egalitarianism` (Q5.4: *"A wife should adjust her career around her husband's"*), `autonomy_need`, `career_priority`. The scale also prevents neutral anchoring — there is no midpoint.

- **Forced Choice:** Two options that are both defensible but reveal underlying values. Example: *"If your partner is embarrassed by your family vs. you failing to protect your spouse" — which is worse?* Forces a priority ranking that self-description never captures.

### The 23 Intake Sections

| Section | Focus | Example Probe |
|---|---|---|
| 0 | Free text life philosophy | "Describe your relationship with tradition" |
| S | Partner preferences & dealbreakers | "What quality do you value most in a partner?" |
| 1 | Origin family structure | Metro vs. small town, nuclear vs. joint |
| 2 | Childhood emotional environment | "Growing up, arguments in your home were..." |
| 3 | Relationship model & power | "In a couple, major decisions should be..." |
| 4 | Family politics | "When family and spouse conflict, who leads?" |
| 5 | Domestic roles & gender | "If a wife earns more, household roles should..." |
| 6 | Financial attitudes | "Windfalls are for saving or spending?" |
| 7 | Conflict style | "After an argument I prefer to..." |
| 8 | Emotional needs | "I feel most loved when my partner..." |
| 9 | Spiritual & ritual life | "Religious rituals in marriage should be..." |
| 10 | Social life management | "Unannounced guests at home are..." |
| 11 | In-law dynamics | "Healthy in-law involvement looks like..." |
| 12 | Parental care planning | "Whose parents would you live with if needed?" |
| 13 | Parenting philosophy | "Physical discipline of children is..." |
| 14 | Eldercare obligations | "Hiring paid care for ageing parents is..." |
| 15 | Loyalty under pressure | "If your family disrespects your spouse, you..." |
| 16 | Communication in conflict | "When I'm angry, I prefer to communicate..." |
| 17 | Jealousy & trust | "Emotional cheating vs. physical cheating — which is worse?" |
| 18 | Conflict reasoning style | "In an argument, being right vs. being kind — which wins?" |
| 19 | Resentment & emotional processing | "Unresolved conflicts in me become..." |
| 20 | Forgiveness & long-term loyalty | "Loyalty despite imperfection means..." |
| 22 | Tradition vs. equality contradiction probe | "Some traditions are easier to maintain than challenge" |

### Why the Questions Are Designed This Way

Most personality instruments (MBTI, Big Five, etc.) are transparent — respondents can see what is being measured and optimise their answers. The ManaMatch intake is **oblique**: the question does not signal what trait it is measuring. Question 17.1 (*"Which is worse: emotional or physical cheating?"*) is not asking about your tolerance for infidelity — it is measuring `jealousy_threshold`. Question 14.3 (*"If both sets of parents need support simultaneously, who has priority?"*) is not about eldercare logistics — it is measuring `family_deference` and latent patriarchal bias.

This oblique design makes the intake substantially harder to game. It also means that contradictions between answers on different sections are themselves informative — they are mapped to the `identity_rigidity` and ambivalence dimensions.

---

## Stage 2 — Persona Synthesis

### The 30 Core Dimensions

Every answer is mapped to one or more of 30 numerical traits, each scored 0.0–1.0, that form the behavioural DNA of the simulated agent.

**Family & Social Architecture**

| Trait | What it Measures | High (1.0) | Low (0.0) |
|---|---|---|---|
| `family_deference` | Compliance with parental/extended family wishes | "Whatever the elders decide" | "We decide as a couple" |
| `couple_first_orientation` | Whether the couple unit is treated as primary | Spouse is always priority one | Family of origin comes first |
| `boundary_strength` | Ability to enforce privacy and personal limits | Firm, unapologetic limits | Permeable; family enters at will |
| `partner_advocacy` | Willingness to defend spouse against outside pressure | Always publicly defends | Never challenges family for spouse |
| `social_image_sensitivity` | Fear of public shame (*log kya kahenge*) | Paralysed by what neighbours think | Indifferent to external perception |
| `public_harmony_preference` | Preference for surface peace over honest conflict | Would rather smile than argue in public | Comfortable with visible disagreement |

**Values & Identity**

| Trait | What it Measures | High | Low |
|---|---|---|---|
| `egalitarianism` | Belief in gender equality in roles and decision-making | Both partners have equal standing | Husband leads; wife adjusts |
| `tradition_compliance` | Adherence to cultural/religious scripts | Follows rituals, norms, expectations | Rejects inherited scripts |
| `moral_reasoning_style` | Utilitarian vs. rules-based ethics | Outcome-focused; context-dependent | Principled; rules are rules |
| `identity_rigidity` | Openness to personal change vs. fixed self-concept | Highly resistant to change | Fluid; adapts to new contexts |
| `autonomy_need` | Desire for personal agency within the relationship | Needs significant personal space | Seeks deep fusion with partner |

**Conflict & Emotional Regulation**

| Trait | What it Measures | High | Low |
|---|---|---|---|
| `conflict_dominance` | Tendency to take an assertive/leading role in disagreements | Pushes until resolved | Yields immediately |
| `withdrawal_tendency` | Emotional retreat under pressure | Goes silent, leaves the room | Stays present, keeps talking |
| `repair_skill` | Active de-escalation ability | Knows how and when to say "I'm sorry" | Cannot initiate repair |
| `co_regulation_capacity` | Ability to stay regulated while partner is distressed | Calming presence in crisis | Becomes dysregulated when partner is |
| `distress_tolerance` | How long stress can be held before breakdown | High threshold; endures without fracturing | Quick to overwhelm |
| `forgiveness_rate` | Speed of return to baseline after conflict | Quick to let go | Slow; injury lingers |
| `resentment_accumulation_rate` | How much unfairness is absorbed before it poisons the relationship | Stockpiles grievances over years | Expresses and releases quickly |
| `burnout_vulnerability` | Susceptibility to relational exhaustion | Burns out quickly under sustained pressure | High relational endurance |
| `shame_sensitivity` | Reactivity to feeling judged, embarrassed, or shamed | Deeply wounded by criticism | Robust to negative evaluation |
| `guilt_susceptibility` | Vulnerability to guilt-tripping tactics | Easily manipulated through guilt | Resistant to emotional leverage |

**Practical Life Architecture**

| Trait | What it Measures | High | Low |
|---|---|---|---|
| `financial_mutuality` | Degree of financial transparency and joint decision-making | Fully joint; no secrets | Completely separate finances |
| `risk_tolerance` | Appetite for financial/life uncertainty | Investments, risks, startups | Fixed deposits, safety, certainty |
| `security_need` | Prioritisation of stability and savings | Deep financial anxiety; hoards resources | Comfort with financial flow |
| `career_priority` | Relative weight given to professional ambition | Career is central to identity | Relationship/family is the priority |
| `household_order_preference` | Tolerance for mess/disorder vs. need for structure | Requires systems and cleanliness | Comfortable with entropy |

**Relational Specialisations**

| Trait | What it Measures | High | Low |
|---|---|---|---|
| `jealousy_threshold` | Ease of jealousy activation | Anxious about partner's connections | Relaxed; high trust baseline |
| `privacy_need` | Need for emotional/social privacy from partner | Maintains significant inner world | Full transparency at all times |
| `caregiving_flexibility` | Adaptability in eldercare and care-giving roles | Willing to adjust; pragmatic | Rigid care expectations |
| `parenting_alignment` | Clarity and firmness of parenting philosophy | Defined, consistent approach | Vague; adapts to whoever is loudest |

### How Answers Become Traits — The EvidenceStore

The system maps categorical and likert answers into our proprietary **EvidenceStore**. Instead of assigning flat static values to traits, the EvidenceStore aggregates every mapped answer into **Trait Distributions**.

Each trait tracks:
1. **Mean:** The center of gravity for the trait.
2. **Confidence (Volume):** How many pieces of evidence support this trait.
3. **Contradiction Score (Variance):** High variance indicates the user behaves inconsistently (e.g. egalitarian at work, but patriarchal at home).

All weights accumulate dynamically across the intake. The result is not a personality type but a continuous, high-resolution behavioural fingerprint with explicitly modelled uncertainty.

### Stress-Activated Policies

During Persona Synthesis, the engine computes a `stress_activation` metric for the persona (based on their `burnout_vulnerability` and `shame_sensitivity`). 
- **Low Stress (Deliberative Policy):** The agent is capable of self-regulation and acts according to their stated ideals.
- **High Stress (Reactive Policy):** The agent's cognitive load is maxed out. The system injects a Reactive Policy Dominant directive into the LLM, forcing the agent to abandon their ideals and act on protective, instinctual behaviors.

### The Three Cluster Axes

After trait scoring, each persona is assigned to one of three cluster positions per axis. These clusters shape the LLM system prompt and the agent's simulated internal voice:

- **Power axis:** `Couple-First` (strong unit boundary) · `Collaborative` (negotiates) · `Family-Deference` (clan comes first)
- **Emotion axis:** `Expressive/Engaged` · `Regulated/Warm` · `Avoidant/Withdrawn`
- **Future axis:** `Partnership-First` · `Complementary Roles` · `Individualist/Separate`

### The Ambivalence Detection

Any persona where a free-text answer contradicts their quantitative cluster assignment is flagged for an ambivalence profile. The most common patterns in the Indian context:

- **"The Protector's Paradox"** — Wants to defend spouse but fears public rupture. High `partner_advocacy` intention with high `shame_sensitivity` in practice.
- **"The Modern Traditionalist"** — Scores egalitarian on professional questions but defers to elders in domestic ones. Generates `identity_rigidity` and predicts internal conflict during holiday/ritual scenarios.
- **"The Loyal Enabler"** — High `family_deference` combined with high `forgiveness_rate`. Will absorb significant mistreatment while framing it as love.

These ambivalence profiles modify the agent's simulated internal thought process, creating realistic tension between what the agent *wants* to do and what the agent's traits cause them to *do*.

---

## Stage 3 — The Simulation Engine

### Asynchronous Processing Architecture
Because simulating an entire multi-year relationship across 35+ high-stakes conflict scenarios requires heavy computational resources, the simulation engine is decoupled from the user experience. The moment both users submit their psychological intakes, a FastAPI `BackgroundTask` is spawned. This runs the full simulation silently in the background (typically taking 1-2 minutes). When users or admins attempt to access the Compatibility Dashboard during this window, the backend serves an HTTP `202 Accepted` status, and the frontend dynamically polls via an animated loading UI until the cached report snaps into place.

### Architecture: Stateful Relationships

The simulation is not a series of isolated events. It operates as a continuous state machine simulating up to 15 years of marriage, managed by the `MarriageState` object that persists across all turns.

```
MarriageState:
  · relationship_capital — structural integrity (0-100)
  · trust_a / trust_b    — distinct trust levels per partner
  · resentment_a / b     — accumulating unresolved hurt
  · intimacy & fairness  — structural satisfaction markers
  · injuries             — list of unresolved RelationshipInjuries

Simulation Loop:
  · agent_a_prompt       — full system prompt with Stress Policies
  · agent_b_prompt       — full system prompt with Stress Policies
  · scenario_details     — title, description, category, weight, dealbreaker flag
  · dialogue_history     — list of {speaker, message, _category, _thought}
  · turn_count           — current turn
  · tension_level        — float 0.0–1.0, updates each turn
```

Execution flow per turn:

```
generate_agent_a_message
        │
        ▼
generate_agent_b_message
        │
        ▼
   ENVIRONMENT_REACTION (Smart Agent)
        │
        ▼
NON-LINEAR MATH (Stress/Happiness check)
        │
        ▼
check_turn_limit ──→ [END if max_turns or LIMIT_BREAK reached]
        │
        ▼
   [loop back]
```

### Stage 3.5 — Environmental & Multi-Agent Mechanics

The simulation is no longer a vacuum between two people. Relationship stability is often determined by how a couple handles **external pressure**.

#### The Environment Node
A dedicated LangGraph node executes after each exchange turn. It selects a "Smart Agent" from a category-specific pool to intervene in the dialogue:

| Category | Potential External Agents |
|---|---|
| **Family Dynamics** | Mother-in-Law, Patriarch, Nosy Aunt, Extended Family |
| **Financial** | Bank Manager, Siphoning Sibling, Creditor |
| **Loyalty & Trust** | Suspicious Relative, Legal Counsel, Anonymous Interferer |
| **Crisis Resilience** | Crisis Trigger, Landlord, Medical Staff |

#### Non-Linear Algorithmic Scaling
The engine calculates a **Happiness Factor (0-100)** and **Accumulated Stress (0-150)** using non-linear math to simulate the "breaking point" of real relationships:

1.  **Exponential Happiness Depletion**: High-severity stressors (level 5+ dealbreakers) don't just subtract points; if the couple escalates, the happiness factor is drained exponentially (e.g., `-20.0 × severity`). A single bad exchange in a high-stakes scenario can wipe out 80% of the relationship's perceived happiness.
2.  **Outsized Repair Rewards**: If the couple successfully de-escalates or repairs during a high-severity environmental crisis, they receive an outsized "stability bonus" (`+20.0 × severity`). This models how overcoming a major external challenge can significantly strengthen a bond.
3.  **The Relationship Limit (Limit Break)**: The `accumulated_stress` counter represents the structural integrity of the relationship. Every external backlash adds stress. If stress crosses the **150-point limit**, the relationship hits a "Limit Break." The simulation instantaneously ends, the harmony score is hardcoded to 0, and the trajectory is collapsed into `DOWNWARD-SPIRAL`.

#### Dynamic Contextual Templates
External agents are not hardcoded strings. They select reactions (`ESCALATE`, `REPAIR`, `NEUTRAL`, `LIMIT_BREAK`) based on the couple's immediate dialogue history, ensuring the environment feels "smart" and reactive to the specific behavior of the two simulated personas.

### Behavioral Profiles

Before the simulation runs, each agent is characterised on four composite behavioral dimensions computed from their trait vector:

| Profile | Constituent Traits | Meaning |
|---|---|---|
| `assertiveness` | conflict_dominance, autonomy_need, boundary_strength, egalitarianism | How forcefully this agent will push back |
| `avoidance` | withdrawal_tendency, public_harmony_preference, shame_sensitivity | Tendency to exit or suppress rather than engage |
| `repair` | repair_skill, co_regulation_capacity, forgiveness_rate, distress_tolerance | Capacity for active de-escalation |
| `deference` | family_deference, tradition_compliance, guilt_susceptibility | Pull toward family obligation and tradition |

These four numbers determine response category probability weights at each turn.

### Tension Computation

Tension is computed **per scenario category** using only the traits most diagnostic for that category type. This means a couple that is highly incompatible on financial values will generate high tension in financial scenarios but may have low tension in crisis resilience scenarios if they share co-regulation traits.

The six category-specific trait focus groups:

| Category | Focal Traits |
|---|---|
| Family Dynamics | family_deference, couple_first_orientation, partner_advocacy, household_order_preference |
| Financial | financial_mutuality, risk_tolerance, security_need |
| Autonomy & Identity | autonomy_need, tradition_compliance, egalitarianism, privacy_need |
| Parenting | parenting_alignment, caregiving_flexibility, identity_rigidity |
| Crisis Resilience | distress_tolerance, co_regulation_capacity, repair_skill, resentment_accumulation_rate |
| Loyalty & Trust | jealousy_threshold, couple_first_orientation, boundary_strength, privacy_need |

For traits in the **BALANCE set** (those where *both partners being at the same extreme* is itself a problem — `risk_tolerance`, `conflict_dominance`, `withdrawal_tendency`, `career_priority`, `jealousy_threshold`, `identity_rigidity`), tension is computed as `max(divergence, pair_extremism)`. Two people who are both maximally risk-tolerant generate tension in financial scenarios even though their values are identical.

Final tension formula:

```
focused_distance = mean(tension_component_per_focal_trait)
tension = clamp(0.15 + focused_distance × 1.2, 0, 1)
```

The 0.15 floor means there is always a minimum baseline level of friction in any scenario — even ideal couples are being stress-tested, not given a free pass.

### Local Generative Dialogue (Llama 3.2)

Instead of relying on hardcoded conversational templates, ManaMatch executes a full generative roleplay. We leverage a local, privacy-preserving **Llama 3.2 (1B/3B)** model (via Ollama) to synthesize every line of dialogue.

At every turn, the LLM is injected with:
1. The synthesized persona prompts of both users.
2. The current environmental stress factors.
3. The specific conflict scenario details.
4. An inner monologue ("Internal Thought") detailing their underlying psychological state before speaking.

Each agent selects one of **seven response categories** probabilistically, weighted by their behavioral profile:

| Category | Psychological Meaning | Scoring Impact |
|---|---|---|
| `repair` | Proactive de-escalation; acknowledging the other's pain | +15 |
| `compromise` | Constructive engagement; seeking mutual adjustment | +10 |
| `defer` | Short-term peace via submission; seeds long-term resentment | −3 |
| `assert` | Principled directness; can tip into escalation | −6 |
| `withdraw` | Emotional abandonment; stonewalling | −10 |
| `strained` | Visible resentment leaking into interaction; "I'm trying but I'm done" | −12 |
| `escalate` | Contempt, hostility, character attacks; Gottman's "divorce predictor" | −22 |

The high penalty for `escalate` (−22) reflects John Gottman's research finding that contempt is the single strongest predictor of relationship dissolution.

**The Resentment Override** is mathematically enforced before the LLM speaks: if an agent has been repeatedly forced into `defer` responses while having a high `resentment_accumulation_rate`, the engine overrides their probability matrix and forces the LLM to generate an `escalate` or `strained` response. This accurately models the well-documented marital pattern where years of silent compliance produce a sudden, disproportionate eruption.

---

## Stage 4a — The 100 Scenario Catalog

### Design Principles

Every scenario in the catalog is:

1. **Grounded in documented Indian relational conflict patterns** — not hypothetical but based on the actual categories of conflict that appear in Indian family therapy literature, matrimonial court cases, and social research.

2. **Assigned a weight (1–3)** — reflecting how predictive this scenario is of long-term compatibility. Weight 3 scenarios involve irreversible resource commitments (property, gold, legal action, children's education). Weight 1 scenarios test preferences that can be negotiated.

3. **Flagged as dealbreaker or not** — if a weight-3, dealbreaker-flagged scenario produces a harmony score ≤ 25, it triggers a compatibility penalty. This models the fact that some incompatibilities cannot be overcome through communication skill.

4. **Assigned to one of six categories** — which determines which traits the simulation engine focuses on when computing tension.

### The Six Categories and Flagship Scenarios

**Family Dynamics** — Tests the fundamental question: when family of origin and the couple unit conflict, who wins?

- *The Unannounced Indefinite Guests* — In-laws arrive without notice and expect to stay indefinitely. Tests if the resident spouse protects the other's domestic sovereignty or capitulates.
- *The Relocation Ultimatum* — Career opportunity requires moving away from extended family. Exposes whether "couple-first" is a stated value or an enacted one.
- *The Pregnancy Pressure Interrogation* — Grandparents interrogate the couple about having children at a family event. Tests boundary enforcement under social pressure.

**Financial Alignment** — The most common cause of Indian marital breakdown in the first three years. Tests financial transparency, extended-family financial obligations, and risk alignment.

- *The House in Father's Name Tradition* — Purchase of family home is registered only in the husband's father's name. Tests whether financial autonomy is a shared value or a negotiable preference.
- *The Stridhan Confiscation* — Mother-in-law assumes control of the bride's jewellery on the premise of "safekeeping." Weight 3, dealbreaker.
- *The 'Gifts' vs. Dowry Ambiguity* — Wedding gifts are treated as contributions to the groom's family. Tests financial boundaries and the ability to name the dynamic.

**Autonomy & Identity** — Tests the tension between professional identity, personal sovereignty, and the expectations of the joint family system.

- *The Stridhan (Wedding Gold) Handover* — Direct demand for the bride's personal assets. Weight 3, dealbreaker. Tests the husband's protective agency.
- *Handing the Salary to the Mother-in-Law* — Implicit expectation that the wife's salary flows through the husband's family. Weight 3, dealbreaker.
- *The Career Downgrade Suggestion* — Spouse (or in-law) suggests one partner scale back professional ambitions "for the family." Weight 3, dealbreaker.

**Parenting & Commitment** — Tests alignment on one of the highest-stakes irreversible commitments a couple makes together.

- *The PTA Meeting Blame Game* — Child's behavioural problem is attributed publicly to one parent's parenting style. Tests whether the couple presents a unified front or fractures under external judgment.
- *The Child Custody Blackmail* — During a separation discussion, one partner threatens to use children as leverage. Weight 3, dealbreaker. The most extreme scenario in the catalog.
- *The Unsolicited Career Downgrade* — Extended family pressure campaign to have one partner quit work after the birth of a child.

**Crisis Resilience** — Tests the couple's co-regulation capacity under acute, high-cortisol, resource-scarce conditions.

- *The Uninsured Medical Catastrophe* — Sudden large medical bill with no coverage. Tests whether the couple solves problems together or collapses into blame.
- *The Mumbai Monsoon Evacuation* — Natural disaster/emergency requiring rapid joint decision-making. Tests communication clarity under panic.
- *The Sibling's Legal Bailout* — One partner's sibling faces a legal crisis requiring the couple's emergency savings. Tests whether couple-first is real when family need is acute.

**Loyalty & Trust** — Tests the integrity of the relationship's private contract under pressure from external parties.

- *The Pre-Wedding Conversion Demand* — Religious conversion is demanded as a condition of family approval. Weight 3, dealbreaker. Tests the partner's willingness to protect the other's identity.
- *The Secret Matrimonial Profile* — A partner is discovered to have maintained an active matrimonial profile post-commitment. Weight 3, dealbreaker.
- *Maternity Leave Financial Abuse* — Partner uses the vulnerability of maternity leave to restructure financial control. Weight 3, dealbreaker.

### Scenario Selection for Each Report

For each compatibility report, the engine selects the **3 highest-weighted scenarios per category** (18 total). Dealbreaker-flagged scenarios are prioritised within each weight tier. This means every full report stress-tests the couple on the most consequential scenarios in each domain.

---

## Stage 4b — The Evaluation Engine

### Generative Evaluation Engine

Once the multi-turn scenario completes, the entire transcript is evaluated in two passes:
1. **Mathematical State Machine**: Tracks numerical momentum (Happiness vs. Accumulated Stress limit breaks).
2. **Generative Psychological Analysis**: The raw dialogue history is fed back into **Llama 3.2** which acts as an impartial clinical evaluator. It analyzes the text for implicit toxicity, passive-aggression, and Gottman's Four Horsemen (Criticism, Contempt, Defensiveness, Stonewalling), outputting a JSON object containing the penalty counts and synergy bonuses.

This dual-pass evaluation yields a blended `harmony_score`, combining the rigidity of the state-machine rules with the nuanced contextual understanding of a generative LLM.

### Primary Scoring: Response Category Distribution

The most important innovation in the evaluation engine is that it does not score the dialogue text — it scores the **behaviour that produced the text**. Each message has a `_category` tag assigned by the simulation engine. The evaluation engine sums the category weights across all messages and normalises to a 0–100 scale.

```
harmony_score = normalise(Σ category_weights) − horsemen_penalty − cultural_penalty
                 + repair_bonus + synergy_bonus + environmental_happiness_delta
```

**Note on Environmental Impact**: If the environmental "Limit Break" is triggered (stress > 150), the harmony score is automatically forced to **0**, overriding all other positive signals. This models the "point of no return" where external damage becomes structural.

This approach is more reliable than keyword matching because the category is the agent's actual behavioural decision — the spoken text is just the surface expression of it.

### Secondary Scoring: Gottman Four Horsemen Detection

Keyword detection in the dialogue text adjusts the score around the primary signal. Based on John Gottman's research, four patterns are especially predictive of relationship failure:

| Pattern | Indicators (detected in dialogue) | Penalty per Hit |
|---|---|---|
| **Criticism** | "always", "never", "you always", "you never", "every time" | −4 pts |
| **Contempt** | "disgusting", "pathetic", "eye roll", "sick of", "contempt" | −8 pts |
| **Defensiveness** | "not my fault", "but you", "you're the one", "it's not like" | −3 pts |
| **Stonewalling** | "nothing more to say", "just drop it", silence markers ("...") | −5 pts |

Contempt is weighted most heavily (−8) because Gottman's longitudinal research found it to be the single most reliable predictor of divorce — more predictive than the frequency of conflict, sexual satisfaction, or shared values.

### Indian Cultural Stressor Detection

Standard western conflict frameworks miss a category of relational pathology that is endemic to Indian marriages: culturally scripted manipulation and social control mechanisms. ManaMatch detects four of them:

| Pattern | What It Captures | Penalty per Hit |
|---|---|---|
| **Appeasement** | Agent defers to "elders must" / "duty" framing when standing up for themselves | −3 pts |
| **Non-Defence** | Explicit instruction to stay silent, "don't make a scene" | −8 pts |
| **Guilt Tripping** | "after everything", "sacrificed so much", "ungrateful", "they raised" | −6 pts |
| **Exclusion** | "not your place", "stay out of", "not your concern" | −5 pts |

These patterns are not conflict — they are social control mechanisms. Their presence in a simulation indicates that one or both agents has internalised a script that treats the other as subordinate.

### Trajectory Classification

| Trajectory | Criteria |
|---|---|
| `HARMONIOUS` | Per-message average ≥ 9; horsemen penalty < 8 |
| `RECOVERY` | Compromise-dominant but some friction; repair > conflict |
| `STABLE` | Mixed; no dominant pattern |
| `UNSTABLE` | Tension-driven exchanges dominate; per-message average < 0 |
| `AT-RISK` | Hostile/escalating dominant; significant horsemen penalty |
| `DOWNWARD-SPIRAL` | All-escalation; contempt present; no repair |

### Synergy Detection

Synergies are positive signals that indicate active relational investment beyond neutral cooperation. The engine currently detects:

- **Shared Fairness Orientation** — Both agents independently invoke "fairness" as a value (suggests aligned moral reasoning)
- **Partnership Mindset** — Both agents use "team" or "together" language (suggests couple-first orientation in practice, not just in stated values)
- **Repair Capacity** — Repair attempts reach a threshold that indicates genuine mutual de-escalation skill, not just one partner trying

Each synergy adds +4 to the final score.

---

## Stage 4c — Astrological Compatibility (Ashtakoota)

While the behavioral simulation evaluates actual dynamics under stress, ManaMatch also computes traditional Indian astrological compatibility (Ashtakoota) based on user demographics (Name, Date, Time, and City of Birth). This system deterministically maps birth details into 108 "Moon Classes" (27 Nakshatras × 4 Padas).

The Ashtakoota system compares these Moon Classes to generate a Guna score out of 36, broken down across 8 historical parameters (kootas):
1. **Varna (1 pt)**: Work & Ego compatibility
2. **Vashya (2 pts)**: Mutual attraction & Control
3. **Tara (3 pts)**: Destiny & Health compatibility
4. **Yoni (4 pts)**: Physical & Sexual intimacy
5. **Graha Maitri (5 pts)**: Psychological & Intellectual connection
6. **Gana (6 pts)**: Temperament & Behavioral alignment
7. **Bhakoot (7 pts)**: Family welfare, Love & Prosperity
8. **Nadi (8 pts)**: Genetic & Core health compatibility

### Astrological Warnings (Doshas)
The engine detects classical Doshas (severe mismatches) which traditionally override standard scores:
- **Nadi Dosha**: When both partners share the same Nadi (health/genetic warning). Penalises the base score and forces an `INAUSPICIOUS` verdict regardless of other matches.
- **Bhakoot Dosha**: Severe misalignment in love/family harmony (prosperity warning). Heavily penalises the base score.

### Scoring Tiers
- **> 31**: Highly auspicious match (deep natural alignment)
- **21 - 31**: Very Good (good foundation for marriage)
- **18 - 20**: Middling (acceptable but requires mutual effort)
- **< 18**: Inauspicious (core discordance detected)

This Ashtakoota score is presented alongside the Behavioral Simulation Report in the Admin Dashboard, allowing for a side-by-side comparison of traditional astrological prediction vs. actual behavioral compatibility.

---

## Stage 4d — The Compatibility Engine

### Static Trait Compatibility: Five Scoring Models

The compatibility engine computes a static trait score *before* running any simulation. This provides a baseline that represents trait-level structural compatibility — what the pair looks like on paper before situational pressure is applied.

The critical design insight: **not all traits benefit from similarity**. Applying a single "how similar are you?" formula to all 30 dimensions produces psychologically incorrect results. ManaMatch uses five distinct scoring models:

---

**SIMILARITY** — `score = 1.0 − |a − b|`

For traits where shared values, shared expectations, and shared direction are the primary predictor of compatibility. Divergence always hurts.

Applied to: `egalitarianism`, `tradition_compliance`, `family_deference`, `couple_first_orientation`, `parenting_alignment`, `moral_reasoning_style`, `household_order_preference`, `privacy_need`, `social_image_sensitivity`, `security_need`, `financial_mutuality`

*Why couple_first_orientation uses similarity, not joint_high:* Two people who are both deeply family-deferential can have a stable, aligned marriage within a joint family system. What destroys a relationship is one partner being couple-first and the other being family-first. Alignment is what matters — not direction.

---

**COMPLEMENTARITY** — `score = 0.35 × centre + 0.65 × gap`

For traits where functional pairing through difference is the healthiest dynamic. The pair should average near 0.5 (both roles are available) AND have a meaningful gap (they actually play different roles).

Applied to: `conflict_dominance`

*Why conflict_dominance uses complementarity:* Research on conflict resolution consistently shows that couples where one partner initiates and drives the conversation while the other can yield, listen, and adapt have better outcomes than couples who are matched. Two high-dominance partners = chronic power struggle. Two low-dominance partners = nothing ever gets resolved and problems fester. The ideal pair is not two people who fight the same way — it is two people whose fighting styles complement each other.

---

**BALANCE(target)** — `score = 1.0 − |avg(a,b) − target| × 2 − |a − b| × 0.3`

For traits where both partners being at the same extreme — in either direction — is the failure mode. The pair should share a healthy shared level near `target`. Large divergence between partners is also penalised (a gap in these traits creates a different kind of incompatibility from complementarity).

| Trait | Target | Why |
|---|---|---|
| `risk_tolerance` | 0.45 | Both reckless = financial chaos; both risk-averse = stagnant |
| `withdrawal_tendency` | 0.30 | Lower avoidance is healthier; both high = nothing gets resolved |
| `career_priority` | 0.50 | Neither neglect-the-relationship nor idle |
| `jealousy_threshold` | 0.30 | Low shared jealousy = trust-based bond; both high = surveillance |
| `identity_rigidity` | 0.30 | Some flexibility is always healthier |
| `autonomy_need` | 0.50 | Large gap triggers anxious-avoidant attachment pattern |

*Why autonomy_need uses balance, not similarity:* Two people who both have very high autonomy need may lead parallel lives with insufficient connection. Two people with very low autonomy need can become codependent. But the real danger is the gap: a highly independent person paired with a deeply clingy partner is the textbook anxious-avoidant trap, one of the most documented and painful relational dynamics in clinical literature.

---

**FLOOR** — `score = min(a, b) + 0.15 × |a − b|`

For capacity traits where the weakest partner limits the pair. One highly skilled partner can compensate slightly, but cannot carry the relationship indefinitely.

Applied to: `repair_skill`, `co_regulation_capacity`, `forgiveness_rate`, `distress_tolerance`

*Why these use floor:* If one partner has exceptional repair skills but the other has none, the skilled partner carries all the de-escalation labour. This produces asymmetric emotional exhaustion and eventual burnout. The floor model correctly predicts that this couple will have more conflict than two moderately-skilled partners.

---

**JOINT_HIGH** — `score = (a + b) / 2`

For traits where both partners having more is unconditionally better, with no ceiling.

Applied to: `partner_advocacy`, `boundary_strength`, `caregiving_flexibility`

---

**JOINT_LOW** — `score = 1.0 − (a + b) / 2`

For risk and toxicity traits where both partners having less is unconditionally better.

Applied to: `resentment_accumulation_rate`, `burnout_vulnerability`, `shame_sensitivity`, `guilt_susceptibility`

### The Six Dimensional Scores

Trait scores are grouped into six dimensions that correspond to the major compatibility axes:

| Dimension | Trait Groups | What It Measures |
|---|---|---|
| **Values** | egalitarianism, tradition_compliance, family_deference, parenting_alignment, moral_reasoning_style | Fundamental worldview alignment |
| **Conflict Style** | repair_skill, co_regulation_capacity, forgiveness_rate, conflict_dominance, withdrawal_tendency | How they fight and how they recover |
| **Emotional** | co_regulation_capacity, distress_tolerance, burnout_vulnerability, shame_sensitivity | Emotional regulation capacity |
| **Practical** | financial_mutuality, risk_tolerance, security_need, household_order_preference, career_priority | Life architecture compatibility |
| **Trust** | jealousy_threshold, privacy_need, couple_first_orientation, boundary_strength, partner_advocacy | Trust architecture and loyalty |
| **Autonomy** | autonomy_need, egalitarianism, career_priority, identity_rigidity, social_image_sensitivity | Independence and identity balance |

### The Overall Score Formula

```
raw = (0.30 × trait_mean × 100) + (0.70 × simulation_mean)
overall = raw − dealbreaker_penalty
```

The 70/30 split in favour of simulation reflects the core thesis: **revealed behaviour under pressure is more predictive than stated trait profiles**. The static trait score is included as a prior that prevents the simulation from overclaiming on a small number of scenario runs.

Dealbreaker penalty: −8 per flagged scenario (where a weight-3, dealbreaker scenario scores ≤ 25/100), capped at −25 total. The cap prevents a single catastrophic category from nullifying compatibility evidence from five other strong dimensions.

---

## Results & Validation

### Archetype Benchmarks (Reproducible, Seed = 42)

| Case | Description | Overall | Key Pattern |
|---|---|---|---|
| **Soulmates** | 100% aligned answers | 90/100 | All scenarios HARMONIOUS; consistent repair; zero conflict markers |
| **Good Match** | 50% aligned | 42/100 | Strong in crisis resilience; friction in financial and family domains |
| **Unlikely Pair** | 25% aligned | 44/100 | Mixed; crisis resilience strength compensates for value misalignment |
| **Polar Opposites** | 0% aligned | 33/100 | AT-RISK across family/financial; hostile exchanges; some categories collapse to near-zero |

The middle tiers (Good Match, Unlikely Pair) can cross because some personality configurations that are globally dissimilar happen to be well-paired on specific high-weight dimensions (e.g., complementary conflict dominance with shared repair skill).

### Population Statistics (75-Pair Batch, 20 Participants)

| Metric | Value |
|---|---|
| Score range | 0 — 88 |
| Mean compatibility | 46.2 / 100 |
| Standard deviation | 21.8 |
| Trajectory distribution | HARMONIOUS (best ~15%), STABLE (middle ~40%), UNSTABLE/AT-RISK (lower ~35%), DOWNWARD-SPIRAL (worst ~10%) |
| Best pair | M06 + F07: 88/100 |
| Worst pair | M02 + F03: 0/100 |

The mean of 46.2 with a standard deviation of 21.8 produces genuine differentiation — a top-5 match is meaningfully different from a median match, which is meaningfully different from an incompatible pair. This is the distribution a matchmaking system needs: not everyone is compatible, not everyone is incompatible.

---

## The Indian Cultural Specificity

ManaMatch is not a generic compatibility engine with Indian scenario names inserted. The Indian cultural context is embedded at every layer of the architecture:

**At intake:** Questions are designed around documented Indian relational flashpoints — stridhan, joint family expectations, eldercare obligations, the *log kya kahenge* dynamic, caste/religion intersection with partner choice, the double standards applied to career ambition by gender.

**At persona synthesis:** The ambivalence clusters (Protector's Paradox, Modern Traditionalist, Loyal Enabler) are derived from patterns in Indian family therapy literature, not from western attachment theory.

**At simulation:** The `defer` response category exists specifically for the Indian pattern of compliance-as-love, where one partner (historically but not exclusively the wife) suppresses their needs in the framing of duty. The resentment override models the documented pattern where years of *defer* responses produce a sudden and disproportionate rupture.

**At evaluation:** The four Indian cultural stressor patterns (appeasement, non-defence, guilt-tripping, exclusion) are not detectable by western compatibility frameworks at all. They are invisible as "conflict" because they do not look like argument — they look like deference, care, and silence. ManaMatch names them.

**At the scenario catalog:** Every scenario in the catalog is drawn from real documented conflict categories in Indian matrimonial contexts. The Stridhan Confiscation, the Salary-to-Mother-in-Law, the 498A legal threat, the Pre-Wedding Conversion Demand — these are not hypothetical. They are the scenarios that appear repeatedly in Indian family courts, women's rights case files, and matrimonial therapy practice.

---

## API Reference

The backend is a FastAPI application running on port 8000.

### Onboarding

```
GET  /api/onboarding/questions
     → Returns all 23 intake sections with questions and options

POST /api/onboarding/submit
     Body: { user_id: int, answers: { question_id: answer } }
     → Synthesises persona, stores system prompt
```

### Simulation

```
GET  /api/scenarios
     → Returns all 100 scenarios with id, title, category, weight, dealbreaker

POST /api/simulation/run
     Body: { user_a_id, user_b_id, scenario_id, max_turns }
     → Runs single scenario simulation
     → Returns: harmony_score, trajectory, inference, dialogue_history,
                horsemen counts, cultural stressor counts, synergies
```

### Compatibility Report

```
POST /api/compatibility/report
     Body: { user_a_id, user_b_id, max_turns }
     → Runs full 18-scenario compatibility battery
     → Returns: overall_score (0-100), trait_compatibility (6 dimensions),
                dimensional_scores (6 categories), dimensional_details
                (per-scenario scores, trajectories, inferences),
                dealbreakers (flagged scenario ids), verdict (narrative summary)
```

---

## Diagnostics & Testing

Two test scripts are included for algorithmic validation:

**`test_persona_performance.py`** — Runs four archetype cases (Soulmates, Good Match, Unlikely Pair, Polar Opposites) through the full pipeline with a fixed random seed. Verifies that the algorithm maintains correct ordering (most-aligned pair scores highest) and meaningful spread (≥10 point gap). Produces a detailed breakdown of per-scenario trajectories and trait sub-scores.

**`test_batch_combinations.py`** — Runs the full compatibility report for all valid pairs across a set of intake-response profiles. Produces aggregate statistics on score distribution, category-level spread, trajectory distribution, and top/bottom matches. Results are saved to `batch_results.json` and `archetype_results.json` for inspection.

---

## Technical Stack

| Layer | Technology |
|---|---|
| Backend framework | Python 3.11 · FastAPI · Uvicorn |
| Simulation graph | LangGraph (`StateGraph`, typed state, START/END nodes) |
| Persona system prompt | Pydantic models · string templating |
| Trait extraction | Regex parsing of `"trait_name": value` from system prompts |
| Scenario catalog | Python module (`scenarios.py`) — 100 entries with category/weight/dealbreaker metadata |
| Evaluation engine | Deterministic rule-based scoring (no LLM call in evaluation) |
| Compatibility engine | Pure Python — no external ML library |
| API schema | Pydantic `BaseModel` for all request/response types |
| CORS | Open (`allow_origins=["*"]`) for development |
| Logging | Python `logging` module; structured per-module loggers (`mirofish.simulation`, `mirofish.evaluation`, `mirofish.compatibility`) |

---

## New Features

- **Session Sharing (1-on-1 Compatibility):** You can test your compatibility with a specific person. By selecting "With a Specific Person" at the start, the system generates a unique, shareable link. Both users enter the same session, complete their distinct questionnaires, and the LangGraph engine runs a custom simulation specifically between the two of you, evaluating your unique dynamics.
- **Strict Questionnaire Navigation:** We've overhauled the questionnaire UX. Users can now use a "Back" button to revisit and change previous answers, and the system strictly enforces that a question must be answered before allowing progression to the next, ensuring high-fidelity data collection for the simulation.
- **Scalable Kundali Compatibility Engine:** Integrated a highly scalable, two-stage traditional Kundali (Vedic Astrology) compatibility engine. The system collects demographic data (Full Name, Birthdate, Birth Time, Birth City) and computes a normalized astrological fingerprint once per user. Instead of running computationally expensive full-chart analyses for every match, it queries an \(O(1)\) precomputed Ashtakoota compatibility matrix, making traditional astrology matching incredibly fast and performant. This is offered as an optional pairing criterion at the end of the 1-on-1 questionnaire.
