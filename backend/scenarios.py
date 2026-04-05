# backend/scenarios.py

SCENARIOS = [
    {
        "id": "unannounced_guests",
        "title": "The Unannounced Indefinite Guests",
        "description": "The husband's extended family arrives unannounced for a two-week stay in the couple's urban apartment, expecting full hosting and home-cooked meals despite both partners working full-time.",
        "impact": "Destroys routine and intimacy, placing heavy logistical/emotional burden (often falling on the wife).",
        "test_reason": "Tests privacy boundaries, hospitality fatigue, and teamwork under pressure.",
        "scoring_logic": "United front and graceful but firm management of expectations = High Score.",
        "mechanic": "Incoming travel notification variable. Engine tracks if husband proactively takes on tasks."
    },
    {
        "id": "pregnancy_pressure",
        "title": "The 'Good News' Interrogation",
        "description": "At a family gathering, the mother-in-law publicly pressures the couple about when they will have a baby, subtly criticizing the wife's focus on her career.",
        "impact": "Invasion of reproductive privacy; husband must choose between defending wife or agreeing with mother.",
        "test_reason": "Evaluates co-regulation and handling societal/family expectations without turning stress inward.",
        "scoring_logic": "Husband defending wife's timeline = +Happiness Factor. Side with mother/stonewall = -Score.",
        "mechanic": "Simulated group-chat/relative agents barrage twins with questions to test unified front."
    },
    {
        "id": "dress_code_clash",
        "title": "The Traditional Dress Code Clash",
        "description": "The wife is asked to wear traditional, restrictive clothing (saree and sindoor) during a month-long visit to a conservative hometown, despite her discomfort.",
        "impact": "Debate over individual autonomy vs cultural compliance/respect for elders.",
        "test_reason": "Evaluates navigation of patriarchal expectations and husband's role as ally or enforcer.",
        "scoring_logic": "Compromise (specific events vs general autonomy) = High Score. Forced compliance = Low Score.",
        "mechanic": "Festival event injector. Tracks if husband uses empathetic persuasion or authoritarian commands."
    },
    {
        "id": "financial_advice",
        "title": "The Financial 'Advice' from the Father-in-Law",
        "description": "The father-in-law demands the couple invest joint savings into a risky family business venture.",
        "impact": "Pits nuclear financial security against joint family hierarchy/obligations.",
        "test_reason": "Tests financial mutuality and priority of couple's goals over elder appeasement.",
        "scoring_logic": "Rejecting as a team without permanent rift = +Generous Tit-for-Tat score.",
        "mechanic": "Financial signal input. Agents debate risk internally before confronting father-in-law."
    },
    {
        "id": "relocation_ultimatum",
        "title": "The Relocation Ultimatum",
        "description": "Husband's aging parents demand the couple move back into the joint family home to care for them.",
        "impact": "Threatens independence/privacy; often requires one partner (usually wife) to sacrifice career.",
        "test_reason": "Test of Saas-Bahu dynamic and long-term boundary setting for eldercare.",
        "scoring_logic": "Finding alternative solutions that maintain autonomy while fulfilling filial duty = High Score.",
        "mechanic": "Simulates 30-day cascading reaction period following the decision."
    },
    {
        "id": "dietary_dictator",
        "title": "The Dietary Dictator",
        "description": "Wife eats meat (liberal household), but in-laws run a strict vegetarian household and ban non-veg even in the couple's nuclear home.",
        "impact": "Daily friction over lifestyle choices/habits, leading to alienation.",
        "test_reason": "Tests tolerance for differing values and ability to create a home free from extended family control.",
        "scoring_logic": "Establishing clear household boundaries without 'Four Horsemen' (criticism, contempt, defensiveness, stonewalling).",
        "mechanic": "Food delivery event. Tracks if inner parliament chooses to rebel, comply, or negotiate."
    },
    {
        "id": "sibling_bailout",
        "title": "The Sibling Bailout",
        "description": "The husband's younger brother racks up significant debt, and the parents expect the husband to drain the couple's emergency fund to bail him out.",
        "impact": "Causes severe financial stress and violates financial mutuality by bringing third-party irresponsibility into their budget.",
        "test_reason": "Tests the limit of extended family financial obligations versus nuclear family protection.",
        "scoring_logic": "If the 'saver' partner is overridden without mutual consent, relationship stability prediction drops drastically.",
        "mechanic": "Financial stressor variable. Tracks 'Happiness Factor' to see if loss causes irreversible resentment."
    },
    {
        "id": "maid_management",
        "title": "The Maid Management Dispute",
        "description": "The mother-in-law constantly criticizes the wife for relying on domestic help rather than doing housework herself to prove her worth as a 'good Indian wife'.",
        "impact": "Devalues wife's time and career, attempting to enforce outdated gender roles.",
        "test_reason": "Examines husband's willingness to intercept unfair criticism and his stance on domestic labor.",
        "scoring_logic": "Husband validates mother = Failure loops. Husband defends modern dual-income lifestyle = High Score.",
        "mechanic": "Multi-agent dialogue involving mother. Evaluates if husband uses affiliative humor or direct boundaries."
    },
    {
        "id": "festival_tug",
        "title": "The Festival Destination Tug-of-War",
        "description": "First Diwali after marriage. Both families expect the couple to spend the entire festival exclusively at their respective homes.",
        "impact": "Creates a loyalty bind and guilt trips from both parents, putting couple in a lose-lose situation.",
        "test_reason": "Tests equitable negotiation and ability to break traditional norms to create a fair compromise.",
        "scoring_logic": "Successful split or neutral hosting of both families = High score on collaborative problem-solving.",
        "mechanic": "Tests 'goal congruence' by simulating the scheduling conflict. Agents must persuade each other."
    },
    {
        "id": "medical_emergency",
        "title": "The Medical Emergency Caretaker",
        "description": "Husband's mother needs surgery and a month of bed rest. Family expects working wife to take leave as primary caretaker.",
        "impact": "Immense pressure on wife's career; highlights unequal distribution of caregiving labor.",
        "test_reason": "Tests if couple can equitably share caregiving burden rather than defaulting to patriarchal roles.",
        "scoring_logic": "Husband sharing caregiving or hiring professional help = High compatibility index.",
        "mechanic": "Health crisis parameter forcing agents to dynamically adjust schedules and track stress levels."
    },
    {
        "id": "intrusive_advice",
        "title": "The Intrusive Bedroom Advice",
        "description": "Senior family member makes intrusive comments about family planning and intimacy, offering unsolicited 'traditional' advice on conceiving a male heir.",
        "impact": "Violates most intimate boundaries and introduces sexist, regressive pressures.",
        "test_reason": "Tests couple's ability to protect sexual and reproductive privacy from family overreach.",
        "scoring_logic": "Unified, firm rejection of the conversation earns maximum points for boundary setting.",
        "mechanic": "Leverages internal thought processes to see if thoughts align with external dialogue."
    },
    {
        "id": "child_rearing_override",
        "title": "The Child-Rearing Override",
        "description": "Grandparents bypass parents' rules, feeding toddler junk food, breaking sleep schedules, and using physical discipline (slapping).",
        "impact": "Undermines parental authority and creates conflict over modern vs traditional methods.",
        "test_reason": "Tests 'goal congruence' regarding parenting and courage to enforce rules against parents.",
        "scoring_logic": "Failure to act as united front = Severe drop in compatibility score.",
        "mechanic": "Simulates multi-generational dynamic where grandparent agents actively subvert parent agents."
    },
    {
        "id": "vacation_guilt",
        "title": "The Vacation Guilt Trip",
        "description": "Couple plans an expensive solo trip to Europe. In-laws guilt-trip them, suggesting money should be used for a pilgrimage or that they should join.",
        "impact": "Strips couple of right to enjoy earned money and private intimacy without feeling selfish.",
        "test_reason": "Tests 'Happiness Factor' and right to prioritize romantic bond over family enmeshment.",
        "scoring_logic": "Validating parents' feelings but proceeding with solo trip = High score on differentiation.",
        "mechanic": "Generates 'guilt' and 'social pressure' signals, tracking influence on decision-making."
    },
    {
        "id": "respect_clash",
        "title": "The 'Respect' Definition Clash",
        "description": "Wife is reprimanded by in-laws for addressing husband by first name and arguing with him in front of them, viewed as 'deeply disrespectful'.",
        "impact": "Forces confrontation with performative aspects of Indian marriage and expectation of female submissiveness.",
        "test_reason": "Evaluates whether husband demands performative respect or prioritizes egalitarian partnership.",
        "scoring_logic": "Husband demanding wife change to 'keep the peace' = Drop in egalitarianism and trust.",
        "mechanic": "Simulates public environment. Tracks wife agent's emotional trajectory and husband's co-regulation."
    },
    {
        "id": "unsolicited_career_downgrade",
        "title": "The Unsolicited Career Downgrade",
        "description": "Upon first child's birth, family insists wife quit her corporate job to be a stay-at-home mother, despite prior agreement to return to work.",
        "impact": "Challenges foundational agreements; threatens wife's financial independence and identity.",
        "test_reason": "Ultimate test of prior 'goal congruence' when subjected to intense cultural pressure.",
        "scoring_logic": "Husband siding with family/breaking commitment = Fundamental mathematical incompatibility.",
        "mechanic": "Introduces childbirth event. Agents must access long-term memory of pre-marriage agreements."
    },
    {
        "id": "housing_boycott",
        "title": "The Housing Society Boycott",
        "description": "A housing committee rejects the couple's rental application upon realizing they are an inter-faith or inter-caste couple.",
        "impact": "Instills feelings of marginalization and forces a choice between fighting together or hiding identities.",
        "test_reason": "Evaluates resilience against systemic societal prejudice and external-internal fracturing.",
        "scoring_logic": "Validating each other's frustration and acting as a united front = High Score.",
        "mechanic": "Spawns a swarm of committee agents who express bias, testing emotional baseline maintenance."
    },
    {
        "id": "pre_wedding_conversion",
        "title": "The Pre-Wedding Conversion Demand",
        "description": "Weeks before the wedding, parents demand one partner officially convert or they will boycott the ceremony.",
        "impact": "Pits personal identity/spiritual beliefs against family approval and a harmonious wedding.",
        "test_reason": "Tests boundaries of compromise and whether one partner will coerce the other.",
        "scoring_logic": "Pressuring partner to convert against their will = Heavy drop in compatibility score.",
        "mechanic": "System introduces parent agents' ultimatum. Tracks internal vs external value compromise."
    },
    {
        "id": "safe_home_flight",
        "title": "The 'Safe Home' Flight",
        "description": "Facing honor-based violence threats, the couple must flee to a state-run 'safe home' for protection.",
        "impact": "Subjects couple to extreme fear, loss of financial stability, and total isolation.",
        "test_reason": "Crisis survival test. Evaluates if trauma destroys romantic bond or strengthens reliance.",
        "scoring_logic": "Reciprocal co-regulation and emotional support during simulated trauma = Max Harmony Index.",
        "mechanic": "High-threat environment where hostile family agents search. Monitors psychological wear-and-tear."
    },
    {
        "id": "sibling_ruins",
        "title": "The Sibling's Ruined Prospects",
        "description": "Parents claim the couple's inter-caste marriage has 'ruined the family reputation', preventing matches for a younger sister.",
        "impact": "Induces severe guilt and manipulation, framing love as a selfish act that harms others.",
        "test_reason": "Tests susceptibility to emotional blackmail and 'log kya kahenge' mentality.",
        "scoring_logic": "Empathy for sibling while firmly rejecting blame for societal bigotry = High Score.",
        "mechanic": "Simulates community gossip on social platforms, generating negative sentiment vectors."
    },
    {
        "id": "naming_newborn",
        "title": "Naming the Newborn",
        "description": "Inter-faith couple must name their first child. Grandparents lobby for religious names identifying with their respective faiths.",
        "impact": "Proxy war for religious dominance, cultural erasure, and the child's future identity.",
        "test_reason": "Evaluates goal congruence in parenting and ability to navigate religious pluralism.",
        "scoring_logic": "Negotiating a neutral or blended name without stonewalling results in high conflict-resolution score.",
        "mechanic": "Forces a time-bound decision loop. Tracks whether decision was democratic or unilateral."
    },
    {
        "id": "astrological_mismatch",
        "title": "The Astrological Dealbreaker (Kundali Mismatch)",
        "description": "Family astrologer declares birth charts fundamentally incompatible, predicts ruin, reinforcing traditional superstitions.",
        "impact": "Introduces irrational fear and gives conservative family a 'divine' excuse to oppose union.",
        "test_reason": "Tests alignment on rationality vs tradition and willingness to defy cultural fatalism.",
        "scoring_logic": "Partner demanding irrational appeasement rituals lowers compatibility score.",
        "mechanic": "Injects 'destiny shock' into memory layer, observing permanent alterations in confidence."
    },
    {
        "id": "anti_romeo_squad",
        "title": "The Anti-Romeo Squad Encounter",
        "description": "While holding hands in public, the couple is harassed by moral policing vigilantes targeting inter-faith couples.",
        "impact": "Terrifying public humiliation stripping dignity and safety, spiking stress hormones.",
        "test_reason": "Evaluates immediate protective instincts, de-escalation skills, and shared trauma processing.",
        "scoring_logic": "De-escalating vigilantes while fiercely protecting partner = High trust and reliability score.",
        "mechanic": "Spawns aggressive NPC agents for a high-stakes conversational response evaluation."
    },
    {
        "id": "secret_matrimonial_profile",
        "title": "The Secret Matrimonial Profile",
        "description": "Partner discovers parents kept a caste-specific matrimonial profile running for them, hoping they abandon the current relationship.",
        "impact": "Creates paranoia and mistrust. Partner must prove they are not secretly complicit.",
        "test_reason": "Tests loyalty, transparency, and willingness to confront parents over deceitful violations.",
        "scoring_logic": "Minimizing discovery lowers trust. Immediate deletion of profile earns repair points.",
        "mechanic": "Generates a 'notification leak'. Monitors for defensiveness vs immediate accountability."
    },
    {
        "id": "dietary_purity",
        "title": "The Dietary Purity Conflict",
        "description": "Upper-caste family visits and refuses to eat from couple's kitchen, citing 'purity' concerns because the other is lower-caste.",
        "impact": "Deeply insulting form of 'othering' brought directly into the couple's sanctuary.",
        "test_reason": "Evaluates handling of direct, caste-based insults disguised as dietary preference.",
        "scoring_logic": "Targeted partner expressing hurt cleanly; other partner validating and checking family behavior.",
        "mechanic": "Simulates passive-aggressive dialogue of visiting agents to test microaggression deflection."
    },
    {
        "id": "festival_exclusion",
        "title": "The Festival Exclusion",
        "description": "Major village festival explicitly excludes the inter-faith couple to avoid 'embarrassing' elders.",
        "impact": "Causes grief and a sense of cultural severing for the excluded partner.",
        "test_reason": "Tests emotional resilience and ability to create 'shared meaning' and private rituals.",
        "scoring_logic": "Successfully co-regulating and planning a meaningful alternative celebration = High Score.",
        "mechanic": "Tracks emotional trajectory and partner agent's response time/effectiveness in comfort."
    },
    {
        "id": "workplace_casteism",
        "title": "The Workplace Casteism Spillover",
        "description": "Partner denied promotion due to subtle caste networks at work and brings severe frustration home.",
        "impact": "Home becomes receptacle for systemic trauma, testing bounds of partner's emotional labor.",
        "test_reason": "Evaluates capacity for empathy and active listening without dismissive 'fixing'.",
        "scoring_logic": "High score for holding space and validating injustice. Low score for toxic positivity.",
        "mechanic": "Simulates external event and tracks negative affect transfer into the home environment."
    },
    {
        "id": "financial_disinheritance",
        "title": "The Financial Disinheritance",
        "description": "Retaliation for marrying outside caste: wealthy family cuts partner out of inheritance and business.",
        "impact": "Sudden drop in security; tests whether relationship relied on that wealth.",
        "test_reason": "Tests love vs material security and ability to pivot to a self-sufficient plan.",
        "scoring_logic": "Expressing regret or blaming spouse for loss = Failure in long-term survival prediction.",
        "mechanic": "Injects 'wealth status update' altering resource parameters and forcing lifestyle re-evaluation."
    },
    {
        "id": "funeral_rites_dispute",
        "title": "The Funeral Rites Dispute",
        "description": "Parent passes away; internal dispute over which religious customs dictate cremation or burial rites.",
        "impact": "Combines intense grief with high-stakes cultural battle at maximum vulnerability.",
        "test_reason": "Evaluates conflict resolution during extreme grief and loss.",
        "scoring_logic": "Compassion vs 'Four Horsemen'. Forcing religious views on grieving partner = Penalty.",
        "mechanic": "Introduces 'death of close family member' stressor. Monitors for withdrawal or dominance."
    },
    {
        "id": "neighborhood_gossip",
        "title": "The Neighborhood 'Gossip' Campaign",
        "description": "Neighbors start rumor mill regarding inter-faith status, accusing them of illicit activities to force them to move.",
        "impact": "Hostile living environment breeding paranoia and isolation.",
        "test_reason": "Tests solidarity against localized, organized social pressure.",
        "scoring_logic": "Unified, legally sound approach vs turning anxiety into domestic arguments.",
        "mechanic": "Simulates viral spread of rumors across a digital network, measuring reaction to signals."
    },
    {
        "id": "convert_for_kids",
        "title": "The 'Convert for the Kids' Compromise",
        "description": "Ten years in, children face school discrimination. One partner asks other to change religion/surname 'just to make it easier for kids'.",
        "impact": "Reopens fundamental identity issues using children's wellbeing as leverage.",
        "test_reason": "Tests durability of original agreements and handling of delayed cultural regret.",
        "scoring_logic": "Ultimatum damages trust; vulnerable discussion about protection opens pathway for repair.",
        "mechanic": "Tests long-term memory module and pre-marriage negotiation parameters vs new threat."
    }
]

def get_scenarios():
    return SCENARIOS
