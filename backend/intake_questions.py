# backend/intake_questions.py

CORE_DIMENSIONS = [
    "family_deference", "couple_first_orientation", "boundary_strength", "egalitarianism",
    "tradition_compliance", "public_harmony_preference", "partner_advocacy", "financial_mutuality",
    "risk_tolerance", "security_need", "co_regulation_capacity", "distress_tolerance",
    "conflict_dominance", "withdrawal_tendency", "repair_skill", "shame_sensitivity",
    "guilt_susceptibility", "autonomy_need", "caregiving_flexibility", "parenting_alignment",
    "jealousy_threshold", "privacy_need", "career_priority", "resentment_accumulation_rate",
    "forgiveness_rate", "moral_reasoning_style", "burnout_vulnerability", "identity_rigidity",
    "household_order_preference", "social_image_sensitivity",
    # Phase 8 — Hygiene, Sexual Compatibility & Daily Rituals
    "hygiene_standard", "body_comfort", "sexual_openness", "libido_alignment",
    "intimacy_communication", "ritual_rigidity", "sleep_schedule_compatibility",
    "personal_space_need",
]

INTAKE_SECTIONS = [
    {
        "section": "User Identity",
        "questions": [
            {"id": "0.1", "text": "Full Name", "format": "text_input"},
            {"id": "0.2", "text": "Phone Number", "format": "text_input"},
            {"id": "0.3", "text": "Gender Identity", "format": "multiple_choice", "options": ["Male", "Female", "Other", "Prefer not to say"]},
            {"id": "0.4", "text": "Age", "format": "text_input"}
        ]
    },
    {
        "section": "Initial Match Intent Screener",
        "questions": [
            {"id": "S.1", "text": "What are you looking for right now?", "format": "multiple_choice", "options": ["Casual dating", "Short-term relationship", "Long-term committed relationship", "Marriage", "Unsure but open"]},
            {"id": "S.2", "text": "Which matters more to you right now?", "format": "forced_choice", "options": [{"id": "emotional", "text": "Emotional connection"}, {"id": "practical", "text": "Practical compatibility"}]},
            {"id": "S.3", "text": "Which description best matches the kind of person you want?", "format": "multiple_choice", "options": ["Warm and caring", "Ambitious and driven", "Calm and stable", "Fun and spontaneous", "Traditional and grounded", "Independent and modern", "Balanced mix"]},
            {"id": "S.4", "text": "Which matters more in a partner?", "format": "forced_choice", "options": [{"id": "values", "text": "Shared values"}, {"id": "chemistry", "text": "Strong chemistry"}]},
            {"id": "S.5", "text": "How important is marriage as an eventual goal for you?", "format": "importance_scale"},
            {"id": "S.6", "text": "Which matters more to you in a relationship?", "format": "forced_choice", "options": [{"id": "peace", "text": "Peace and comfort"}, {"id": "growth", "text": "Growth and challenge"}]},
            {"id": "S.7", "text": "How important is family compatibility in a serious relationship?", "format": "importance_scale"},
            {"id": "S.8", "text": "Which matters more?", "format": "forced_choice", "options": [{"id": "understands", "text": "A partner who understands me emotionally"}, {"id": "dependable", "text": "A partner who is dependable in real life"}]},
            {"id": "S.9", "text": "What kind of lifestyle are you hoping to build with someone?", "format": "multiple_choice", "options": ["Quiet and private", "Social and family-centered", "Career-focused and ambitious", "Balanced and flexible", "Adventurous and spontaneous", "Traditional and rooted"]},
            {"id": "S.10", "text": "Which is more attractive to you?", "format": "forced_choice", "options": [{"id": "maturity", "text": "Emotional maturity"}, {"id": "intensity", "text": "Excitement and intensity"}]},
            {"id": "S.11", "text": "How important is career ambition in a partner?", "format": "importance_scale"},
            {"id": "S.12", "text": "Which matters more in a serious partner?", "format": "forced_choice", "options": [{"id": "independence", "text": "Independence"}, {"id": "family", "text": "Family-mindedness"}]},
            {"id": "S.13", "text": "How important is shared religion/tradition/culture to you personally?", "format": "importance_scale"},
            {"id": "S.14", "text": "Which feels more important?", "format": "forced_choice", "options": [{"id": "chooses_me", "text": "A partner who chooses me clearly"}, {"id": "freedom", "text": "A partner who gives me freedom and space"}]},
            {"id": "S.15", "text": "What kind of conflict style can you tolerate best in a partner?", "format": "multiple_choice", "options": ["Direct but respectful", "Gentle and calm", "Emotionally expressive", "Avoids conflict unless necessary", "Playful and light", "Firm and practical"]},
            {"id": "S.16", "text": "Which matters more for long-term success?", "format": "forced_choice", "options": [{"id": "understanding", "text": "Mutual understanding"}, {"id": "commitment", "text": "Strong commitment"}]},
            {"id": "S.17", "text": "How important is physical attraction to you in the beginning?", "format": "importance_scale"},
            {"id": "S.18", "text": "Which future feels more appealing?", "format": "forced_choice", "options": [{"id": "stable", "text": "Building a stable home"}, {"id": "exciting", "text": "Building an exciting life"}]},
            {"id": "S.19", "text": "What is the biggest dealbreaker for you at first glance?", "format": "multiple_choice", "options": ["Disrespect", "Emotional immaturity", "No ambition", "Family mismatch", "Lack of attraction", "Dishonesty", "Different lifestyle", "Excessive controlling nature"]},
            {"id": "S.20", "text": "In one or two lines, what kind of person are you hoping to find, and what kind of relationship do you want with them?", "format": "short_answer"}
        ]
    },
    {
        "section": "Background and Life Context",
        "questions": [
            {"id": "1.1", "text": "What type of environment did you primarily grow up in?", "format": "multiple_choice", "options": ["Metro city", "Tier-2 city", "Small town", "Village", "Moved frequently between these"]},
            {"id": "1.2", "text": "What family structure did you grow up in?", "format": "multiple_choice", "options": ["Nuclear", "Joint", "Semi-joint", "Alternated over time"]},
            {"id": "1.3", "text": "Who typically made final decisions at home while you were growing up?", "format": "multiple_choice", "options": ["Father", "Mother", "Grandparents", "Parents jointly", "Case-by-case", "Other"]},
            {"id": "1.4", "text": "Were elders openly disagreed with in your home?", "format": "scale_7", "min_label": "Never", "max_label": "Very often"},
            {"id": "1.5", "text": "Did your family treat sons and daughters differently?", "format": "scale_7", "min_label": "No difference", "max_label": "Extreme difference"},
            {"id": "1.6", "text": "What was one unspoken rule in your house that everyone followed?", "format": "short_answer"}
        ]
    },
    {
        "section": "Core Values and Identity Priorities",
        "questions": [
            {"id": "2.1", "text": "Which matters more in a relationship?", "format": "forced_choice", "options": [{"id": "understood", "text": "Being understood"}, {"id": "respected", "text": "Being respected"}]},
            {"id": "2.2", "text": "Which matters more?", "format": "forced_choice", "options": [{"id": "peace", "text": "Peace"}, {"id": "fairness", "text": "Fairness"}]},
            {"id": "2.3", "text": "Which feels worse?", "format": "forced_choice", "options": [{"id": "controlled", "text": "Being controlled"}, {"id": "hurting", "text": "Hurting someone you love"}]},
            {"id": "2.4", "text": "Rank these from most important to least important in a life partner:", "format": "ranking", "options": ["Loyalty", "Kindness", "Ambition", "Family fit", "Emotional maturity", "Stability", "Attraction", "Shared values", "Humor", "Responsibility"]},
            {"id": "2.5", "text": "I would rather have a difficult truth than a comforting lie.", "format": "scale_7", "min_label": "Strongly disagree", "max_label": "Strongly agree"},
            {"id": "2.6", "text": "What makes you feel deeply respected in a relationship?", "format": "short_answer"}
        ]
    },
    {
        "section": "Marriage Philosophy and Couple Identity",
        "questions": [
            {"id": "3.1", "text": "Marriage is primarily:", "format": "multiple_choice", "options": ["A partnership between equals", "A union of families", "A duty and commitment", "A romantic bond", "A social institution", "A practical life arrangement"]},
            {"id": "3.2", "text": "Which statement feels more true?", "format": "forced_choice", "options": [{"id": "spouse_primary", "text": "After marriage, spouse becomes primary family"}, {"id": "parents_primary", "text": "Parents remain the primary guiding unit"}]},
            {"id": "3.3", "text": "Adjustment in marriage should happen:", "format": "multiple_choice", "options": ["Mostly by both equally", "More by the wife", "More by the husband", "Depends on practical realities", "Depends on whose family is stricter"]},
            {"id": "3.4", "text": "A successful marriage is more about compatibility than commitment.", "format": "scale_7", "min_label": "Strongly disagree", "max_label": "Strongly agree"},
            {"id": "3.5", "text": "What is one thing a spouse should never do, even under family pressure?", "format": "short_answer"}
        ]
    },
    {
        "section": "Family Boundaries and Parental Involvement",
        "questions": [
            {"id": "4.1", "text": "Parents should be consulted before major life decisions after marriage.", "format": "scale_7"},
            {"id": "4.2", "text": "It is acceptable to say no to parents if the couple agrees.", "format": "scale_7"},
            {"id": "4.3", "text": "Relatives should not stay in the couple’s home without approval from both spouses.", "format": "scale_7"},
            {"id": "4.4", "text": "Which matters more?", "format": "forced_choice", "options": [{"id": "elders", "text": "Keeping elders happy"}, {"id": "couple", "text": "Protecting couple peace"}]},
            {"id": "4.5", "text": "If parents unfairly criticize your spouse, what should happen first?", "format": "sjt", "options": [{"id": "defend", "text": "Defend immediately"}, {"id": "calm", "text": "Calm situation first"}, {"id": "silent", "text": "Stay silent"}, {"id": "private", "text": "Discuss privately"}]},
            {"id": "4.6", "text": "Parents should have a key to the couple’s home.", "format": "scale_7"},
            {"id": "4.7", "text": "What does “healthy distance from family” mean to you?", "format": "short_answer"}
        ]
    },
    {
        "section": "Gender Roles and Domestic Labor",
        "questions": [
            {"id": "5.1", "text": "If both partners work full-time, household chores should be equally shared.", "format": "scale_7"},
            {"id": "5.2", "text": "Domestic help (maid/cook) is:", "format": "multiple_choice", "options": ["Practical/Helpful", "A luxury", "A sign of laziness", "Fine when busy", "Depends on finances"]},
            {"id": "5.3", "text": "Which feels more true?", "format": "forced_choice", "options": [{"id": "adjusts", "text": "Adjust to household expectations"}, {"id": "redesign", "text": "Redesign unfair expectations"}]},
            {"id": "5.4", "text": "A daughter-in-law should naturally do more to adapt to the husband’s family.", "format": "scale_7"},
            {"id": "5.5", "text": "After a long workday, the mess at home should be handled by:", "format": "multiple_choice", "options": ["Whoever notices first", "Whoever is less tired", "Split equally", "The woman more often", "The man more often", "Outsource"]},
            {"id": "5.6", "text": "What household behavior makes you feel taken for granted?", "format": "short_answer"}
        ]
    },
    {
        "section": "Financial Philosophy and Mutuality",
        "questions": [
            {"id": "6.1", "text": "Which describes you better?", "format": "forced_choice", "options": [{"id": "saved", "text": "Calmer when money is saved"}, {"id": "enjoy", "text": "Happier when money is used to enjoy life"}]},
            {"id": "6.2", "text": "Married couples should discuss all major expenses in advance.", "format": "scale_7"},
            {"id": "6.3", "text": "Which account style feels best?", "format": "multiple_choice", "options": ["Fully joint", "Mostly joint", "Mostly separate", "Fully separate", "Depends on stage"]},
            {"id": "6.4", "text": "Supporting one’s own parents financially after marriage is:", "format": "multiple_choice", "options": ["A duty", "Optional", "Should be agreed", "Fine if both do it", "Depends on need"]},
            {"id": "6.5", "text": "If one spouse wants to support their parents, the other should:", "format": "sjt", "options": [{"id": "support", "text": "Support without question"}, {"id": "cap", "text": "Set a budget cap"}, {"id": "refuse", "text": "Refuse unless equal"}, {"id": "delay", "text": "Delay conversation"}, {"id": "evaluate", "text": "Evaluate based on need"}]},
            {"id": "6.6", "text": "What feels more threatening?", "format": "forced_choice", "options": [{"id": "spends", "text": "Partner spends too freely"}, {"id": "controls", "text": "Partner controls every rupee"}]},
            {"id": "6.7", "text": "What type of spending would you resent your partner making without discussion?", "format": "short_answer"}
        ]
    },
    {
        "section": "Conflict Style and Repair Behavior",
        "questions": [
            {"id": "7.1", "text": "When upset, my first instinct is to:", "format": "multiple_choice", "options": ["Talk immediately", "Wait/Cool down", "Withdraw", "Use humor", "Seek reassurance", "Pretend it's fine"]},
            {"id": "7.2", "text": "Which is worse in conflict?", "format": "forced_choice", "options": [{"id": "criticism", "text": "Criticism"}, {"id": "silence", "text": "Silence"}]},
            {"id": "7.3", "text": "I often agree just to end the conflict faster.", "format": "scale_7"},
            {"id": "7.4", "text": "If my partner becomes emotional, I can stay calm and helpful.", "format": "scale_7"},
            {"id": "7.5", "text": "After a bad argument, what matters most first?", "format": "forced_choice", "options": [{"id": "reassurance", "text": "Emotional reassurance"}, {"id": "solving", "text": "Solving the issue"}, {"id": "space", "text": "Space"}, {"id": "apology", "text": "An apology"}, {"id": "tone", "text": "Respectful tone"}, {"id": "alone", "text": "Time to process alone"}]},
            {"id": "7.6", "text": "I become sarcastic when I feel unheard.", "format": "scale_7"},
            {"id": "7.7", "text": "What does a genuine apology sound like to you?", "format": "short_answer"}
        ]
    },
    {
        "section": "Emotional Needs and Co-Regulation",
        "questions": [
            {"id": "8.1", "text": "When I am upset, I prefer:", "format": "multiple_choice", "options": ["Comfort first", "Solutions first", "Space first", "Loyalty first", "Silence first", "Physical presence"]},
            {"id": "8.2", "text": "I feel drained when I have to manage someone else’s emotions for too long.", "format": "scale_7"},
            {"id": "8.3", "text": "If my partner is hurt by my family, I should:", "format": "sjt", "options": [{"id": "comfort", "text": "Comfort first, defend later"}, {"id": "defend", "text": "Defend first, comfort later"}, {"id": "neutral", "text": "Stay neutral"}, {"id": "public", "text": "Ask not to react publicly"}]},
            {"id": "8.4", "text": "Reassurance in a relationship is:", "format": "multiple_choice", "options": ["Essential", "Nice but not necessary", "Needed only during stress", "Sign of insecurity", "Depends on attachment style"]},
            {"id": "8.5", "text": "When do you feel emotionally safest with someone?", "format": "short_answer"}
        ]
    },
    {
        "section": "Tradition, Religion, and Community",
        "questions": [
            {"id": "9.1", "text": "Religious compatibility in marriage is:", "format": "scale_6", "min_label": "Not important", "max_label": "Extremely important"},
            {"id": "9.2", "text": "Visible marital traditions (sindoors, mangalsutras, etc) are:", "format": "multiple_choice", "options": ["Very meaningful", "Optional", "Symbolic", "Unimportant", "Used to control"]},
            {"id": "9.3", "text": "Which matters more?", "format": "forced_choice", "options": [{"id": "tradition", "text": "Honoring tradition"}, {"id": "autonomy", "text": "Protecting autonomy"}]},
            {"id": "9.4", "text": "If a relative makes a derogatory comment, I:", "format": "sjt", "options": [{"id": "callout", "text": "Call out immediately"}, {"id": "defend", "text": "Defend and change topic"}, {"id": "private", "text": "Stay quiet, address later"}, {"id": "ignore", "text": "Ignore to avoid drama"}]},
            {"id": "9.5", "text": "Community approval matters a lot in choosing a life partner.", "format": "scale_7"},
            {"id": "9.6", "text": "Which traditions feel meaningful, and which feel performative?", "format": "short_answer"}
        ]
    },
    {
        "section": "Food, Lifestyle, and Home Culture",
        "questions": [
            {"id": "10.1", "text": "Food compatibility matters a lot in a shared home.", "format": "scale_7"},
            {"id": "10.2", "text": "If a spouse has a different diet from the family, what should happen?", "format": "multiple_choice", "options": ["Family rules dominate", "Separate arrangements", "Spouse adjust for peace", "Mutual compromise", "Depends on ownership"]},
            {"id": "10.3", "text": "Guests at home should ideally be:", "format": "multiple_choice", "options": ["Frequent/Welcome", "Occasional/Planned", "Rare", "Fine with advance notice", "Depends on role"]},
            {"id": "10.4", "text": "A home feels loving when it is:", "format": "multiple_choice", "options": ["Calm/Private", "Busy/Socially alive", "Well-organized", "Warm/Flexible", "Ritual-centered", "Open to family"]},
            {"id": "10.5", "text": "What lifestyle difference would create daily friction for you?", "format": "short_answer"}
        ]
    },
    {
        "section": "Social Image, Shame, and Public Respect",
        "questions": [
            {"id": "11.1", "text": "I care a lot about how relatives describe my relationship.", "format": "scale_7"},
            {"id": "11.2", "text": "Public disagreement between spouses is:", "format": "multiple_choice", "options": ["Healthy if respectful", "Best avoided", "Disrespectful", "Fine in private circles", "Depends on topic"]},
            {"id": "11.3", "text": "Which is worse?", "format": "forced_choice", "options": [{"id": "embarrassing_family", "text": "Embarrassing family in public"}, {"id": "not_protecting_spouse", "text": "Failing to protect spouse in public"}]},
            {"id": "11.4", "text": "A spouse should change public behavior to keep elders comfortable.", "format": "scale_7"},
            {"id": "11.5", "text": "What behavior in public feels disrespectful to you?", "format": "short_answer"}
        ]
    },
    {
        "section": "Career, Ambition, and Sacrifice",
        "questions": [
            {"id": "12.1", "text": "Career is a central part of my identity.", "format": "scale_7"},
            {"id": "12.2", "text": "If a career opportunity arises elsewhere, we should:", "format": "multiple_choice", "options": ["Move for opportunity", "Prefer husband’s", "Prefer wife’s", "Case-by-case", "Stay near family"]},
            {"id": "12.3", "text": "After childbirth, whose career slows down?", "format": "multiple_choice", "options": ["Mother’s", "Father’s", "Shared", "Flexibility-based", "Outsource support"]},
            {"id": "12.4", "text": "A demanding spouse can still be a good spouse.", "format": "scale_7"},
            {"id": "12.5", "text": "What kind of career sacrifice would feel unfair to you?", "format": "short_answer"}
        ]
    },
    {
        "section": "Children, Parenting, and Authority",
        "questions": [
            {"id": "13.1", "text": "Do you want children?", "format": "multiple_choice", "options": ["Yes", "No", "Unsure", "Open/Depends"]},
            {"id": "13.2", "text": "Grandparents should have a meaningful say in raising the child.", "format": "scale_7"},
            {"id": "13.3", "text": "Physical discipline is:", "format": "multiple_choice", "options": ["Never acceptable", "Rarely acceptable", "Sometimes necessary", "Depends on context", "Traditional discipline"]},
            {"id": "13.4", "text": "Which matters more in parenting?", "format": "forced_choice", "options": [{"id": "obedience", "text": "Obedience/Respect"}, {"id": "safety", "text": "Safety/Understanding"}]},
            {"id": "13.5", "text": "If grandparents break the parents’ rules, the couple should:", "format": "sjt", "options": [{"id": "ignore", "text": "Ignore it"}, {"id": "correct", "text": "Correct privately later"}, {"id": "firm", "text": "Set firm boundary immediately"}, {"id": "adjust", "text": "Adjust rules to avoid conflict"}]},
            {"id": "13.6", "text": "What is one parenting belief you would not compromise on?", "format": "short_answer"}
        ]
    },
    {
        "section": "Eldercare and Family Duty",
        "questions": [
            {"id": "14.1", "text": "Adult children should personally care for aging parents.", "format": "scale_7"},
            {"id": "14.2", "text": "Paid eldercare is:", "format": "multiple_choice", "options": ["Responsible", "Acceptable", "Last resort", "Wrong", "Depends"]},
            {"id": "14.3", "text": "If both parents need support, priority is:", "format": "multiple_choice", "options": ["Husband’s parents", "Wife’s parents", "Equal", "Need-based", "Sacrifice-based"]},
            {"id": "14.4", "text": "Which feels more true?", "format": "forced_choice", "options": [{"id": "sacrifice", "text": "Children sacrifice for parents"}, {"id": "protect", "text": "Protect marriage from duty"}]},
            {"id": "14.5", "text": "What eldercare expectation would feel unfair?", "format": "short_answer"}
        ]
    },
    {
        "section": "Loyalty, Public Protection, and Betrayal",
        "questions": [
            {"id": "15.1", "text": "If your spouse is being unfairly criticized in public, you should defend them even if it creates tension.", "format": "scale_7"},
            {"id": "15.2", "text": "Which feels more like betrayal?", "format": "forced_choice", "options": [{"id": "not_defending", "text": "Publicly not defending me"}, {"id": "disagreeing_privately", "text": "Privately disagreeing with me later"}]},
            {"id": "15.3", "text": "A spouse should take your side first and discuss privately later.", "format": "scale_7"},
            {"id": "15.4", "text": "If your parent and your spouse are in conflict, your first duty is to:", "format": "multiple_choice", "options": ["Protect fairness", "Protect spouse", "Protect parent", "De-escalate first", "Stay neutral"]},
            {"id": "15.5", "text": "What action from a spouse would permanently damage trust for you?", "format": "short_answer"}
        ]
    },
    {
        "section": "Intimacy, Privacy, and Reproductive Boundaries",
        "questions": [
            {"id": "16.1", "text": "Family planning is a private matter that relatives should not comment on.", "format": "scale_7"},
            {"id": "16.2", "text": "If a senior family member makes intrusive comments about intimacy, what should happen?", "format": "sjt", "options": [{"id": "stop", "text": "Firmly stop conversation"}, {"id": "laugh", "text": "Laugh it off/Move on"}, {"id": "later", "text": "Change topic/set boundary later"}, {"id": "tolerate", "text": "Tolerate for respect"}]},
            {"id": "16.3", "text": "Which matters more?", "format": "forced_choice", "options": [{"id": "respect", "text": "Maintaining respect with elders"}, {"id": "privacy", "text": "Protecting intimate privacy"}]},
            {"id": "16.4", "text": "Partners should have privacy in their messages and devices.", "format": "scale_7"},
            {"id": "16.5", "text": "What type of question from family about your relationship would cross a line for you?", "format": "short_answer"}
        ]
    },
    {
        "section": "Jealousy, Fidelity, and Third-Party Boundaries",
        "questions": [
            {"id": "17.1", "text": "Which would hurt more?", "format": "forced_choice", "options": [{"id": "emotional", "text": "Emotional closeness with someone else"}, {"id": "physical", "text": "Physical cheating"}]},
            {"id": "17.2", "text": "It is acceptable for a partner to share deep emotional problems with a close friend of the gender they are attracted to.", "format": "scale_7"},
            {"id": "17.3", "text": "If communication suddenly drops, I usually:", "format": "multiple_choice", "options": ["Get anxious", "Give space", "Assume wrong", "Distract myself", "Reach out directly", "Wait calmly"]},
            {"id": "17.4", "text": "Transparency in a relationship should be:", "format": "multiple_choice", "options": ["Very high", "Healthy but not intrusive", "Moderate", "Limited/Independence", "Depends on trust"]},
            {"id": "17.5", "text": "What kind of secrecy would bother you most in a relationship?", "format": "short_answer"}
        ]
    },
    {
        "section": "Decision-Making and Negotiation Style",
        "questions": [
            {"id": "18.1", "text": "I prefer decisions to be made after everyone has had a chance to speak.", "format": "scale_7"},
            {"id": "18.2", "text": "In a disagreement, I become uncomfortable if a decision remains unresolved for too long.", "format": "scale_7"},
            {"id": "18.3", "text": "Which feels more natural to you?", "format": "forced_choice", "options": [{"id": "quick", "text": "Decide quickly and adjust later"}, {"id": "careful", "text": "Reflect first and decide carefully"}]},
            {"id": "18.4", "text": "If two partners disagree strongly, the ideal solution is usually:", "format": "multiple_choice", "options": ["Meet halfway", "Follow the more practical option", "Follow the calmer person", "Follow the more affected person", "Delay until emotions settle", "Depends on the topic"]},
            {"id": "18.5", "text": "I usually try to understand the other person’s logic even when I disagree.", "format": "scale_7"},
            {"id": "18.6", "text": "Which matters more in a shared decision?", "format": "forced_choice", "options": [{"id": "emotional_fairness", "text": "Emotional fairness"}, {"id": "practical_efficiency", "text": "Practical efficiency"}]},
            {"id": "18.7", "text": "I prefer to consult family before making major life decisions.", "format": "scale_7"},
            {"id": "18.8", "text": "If my partner strongly disagrees with me, I tend to:", "format": "multiple_choice", "options": ["Push harder", "Pause and listen", "Withdraw", "Reframe more gently", "Give in temporarily", "Become irritated"]},
            {"id": "18.9", "text": "Rank these from most important to least important when making a joint decision.", "format": "ranking", "options": ["Fairness", "Long-term stability", "Emotional impact", "Family harmony", "Efficiency", "Personal freedom", "Reputation", "Financial safety"]},
            {"id": "18.10", "text": "If I believe I am right, I still want the other person to feel respected.", "format": "scale_7"},
            {"id": "18.11", "text": "Which is more frustrating?", "format": "forced_choice", "options": [{"id": "avoidance", "text": "Someone who avoids the issue"}, {"id": "pressure", "text": "Someone who keeps pressing the issue"}]},
            {"id": "18.12", "text": "In important conversations, I care more about:", "format": "forced_choice", "options": [{"id": "accurate", "text": "Being accurate"}, {"id": "understood", "text": "Being understood"}]},
            {"id": "18.13", "text": "SJT: Your partner wants to decide immediately, but you need time to think. What are you most likely to do?", "format": "sjt", "options": [{"id": "commitment", "text": "Ask for time and commit to a specific revisit point"}, {"id": "force", "text": "Force yourself to decide now"}, {"id": "shutdown", "text": "Shut down the conversation"}, {"id": "agree_later", "text": "Agree now and revisit later"}, {"id": "consult", "text": "Ask a third person for input"}]},
            {"id": "18.14", "text": "SJT: A family conflict needs a decision by tonight, but both spouses feel unheard. What happens next?", "format": "sjt", "options": [{"id": "practical", "text": "Prioritize the practical decision and repair later"}, {"id": "delay", "text": "Delay the decision if possible"}, {"id": "charge", "text": "One partner takes charge"}, {"id": "elders", "text": "Ask elders to decide"}, {"id": "compromise", "text": "Find the least damaging compromise"}]},
            {"id": "18.15", "text": "What makes a compromise feel genuinely fair to you?", "format": "short_answer"},
            {"id": "18.16", "text": "In what situations do you want your partner to decide for both of you?", "format": "short_answer"}
        ]
    },
    {
        "section": "Sacrifice, Resentment, and Burnout Risk",
        "questions": [
            {"id": "19.1", "text": "I can tolerate unfairness for a long time if it keeps the relationship stable.", "format": "scale_7"},
            {"id": "19.2", "text": "Which is more dangerous to a marriage?", "format": "forced_choice", "options": [{"id": "fights", "text": "Frequent fights"}, {"id": "resentment", "text": "Silent resentment"}]},
            {"id": "19.3", "text": "I usually notice early when something is building into resentment.", "format": "scale_7"},
            {"id": "19.4", "text": "When I feel unappreciated, I tend to:", "format": "multiple_choice", "options": ["Speak up directly", "Become colder", "Wait to see if they notice", "Do less", "Get sarcastic", "Feel hurt but say nothing"]},
            {"id": "19.5", "text": "Which feels more true?", "format": "forced_choice", "options": [{"id": "love_is_sacrifice", "text": "Love means sacrifice"}, {"id": "love_is_protection", "text": "Love means protecting each other from avoidable sacrifice"}]},
            {"id": "19.6", "text": "I get exhausted when I am expected to be the calmer or stronger person all the time.", "format": "scale_7"},
            {"id": "19.7", "text": "If I keep sacrificing and it is not acknowledged, my feelings change.", "format": "scale_7"},
            {"id": "19.8", "text": "Which is harder for you?", "format": "forced_choice", "options": [{"id": "asking", "text": "Asking for help"}, {"id": "had_to_ask", "text": "Feeling like you had to ask at all"}]},
            {"id": "19.9", "text": "SJT: You have been handling most chores, emotional support, and family diplomacy for weeks. Your partner seems unaware. What are you most likely to do?", "format": "sjt", "options": [{"id": "explain", "text": "Explain clearly and ask for redistribution"}, {"id": "reduce", "text": "Reduce effort and see if they notice"}, {"id": "silent", "text": "Stay silent to avoid conflict"}, {"id": "hostile", "text": "Become visibly frustrated"}, {"id": "appreciation", "text": "Ask during a calm moment for more appreciation first"}]},
            {"id": "19.10", "text": "SJT: You agree to a major family obligation to keep peace, but immediately feel it was unfair. What happens next?", "format": "sjt", "options": [{"id": "raise", "text": "Raise it soon"}, {"id": "convince", "text": "Convince yourself it was necessary"}, {"id": "distant", "text": "Grow distant"}, {"id": "blame", "text": "Blame your partner"}, {"id": "reverse", "text": "Try to reverse it later"}]},
            {"id": "19.11", "text": "A relationship becomes dangerous when one person is always expected to absorb more.", "format": "scale_7"},
            {"id": "19.12", "text": "I sometimes test whether someone cares by seeing if they notice my effort without being told.", "format": "scale_7"},
            {"id": "19.13", "text": "What repeated pattern would slowly kill your affection in a marriage?", "format": "short_answer"},
            {"id": "19.14", "text": "What kind of sacrifice would make you feel loved, and what kind would make you feel erased?", "format": "short_answer"}
        ]
    },
    {
        "section": "Moral Dilemmas and Deep Compatibility",
        "questions": [
            {"id": "20.1", "text": "Which matters more to you in a hard situation?", "format": "forced_choice", "options": [{"id": "fair", "text": "Doing what is fair"}, {"id": "preserves", "text": "Doing what preserves the relationship"}]},
            {"id": "20.2", "text": "It is acceptable to hide part of the truth if the full truth would cause unnecessary damage.", "format": "scale_7"},
            {"id": "20.3", "text": "Which feels more moral?", "format": "forced_choice", "options": [{"id": "duty", "text": "Honoring duty even at personal cost"}, {"id": "wellbeing", "text": "Protecting wellbeing even if duty is disrupted"}]},
            {"id": "20.4", "text": "If holding a firm boundary hurts family feelings, I can still do it if I believe it is right.", "format": "scale_7"},
            {"id": "20.5", "text": "Loyalty sometimes requires protecting someone even when they are imperfect.", "format": "scale_7"},
            {"id": "20.6", "text": "Which is worse?", "format": "forced_choice", "options": [{"id": "hurt_loved", "text": "Doing the right thing and hurting loved ones"}, {"id": "allow_unfair", "text": "Avoiding hurt but allowing unfairness"}]},
            {"id": "20.7", "text": "In family matters, peace should sometimes be prioritized over strict fairness.", "format": "scale_7"},
            {"id": "20.8", "text": "SJT: Your partner is technically wrong in front of family, but the family’s reaction is humiliating. What do you do first?", "format": "sjt", "options": [{"id": "protect", "text": "Protect partner first and correct privately later"}, {"id": "neutral", "text": "Stay neutral because they are wrong"}, {"id": "change", "text": "Quietly change the subject"}, {"id": "side", "text": "Side with family to preserve fairness"}, {"id": "discuss", "text": "Wait until later to discuss both sides"}]},
            {"id": "20.9", "text": "SJT: A truthful answer will create conflict with your parents, but hiding the truth protects your spouse. What are you most likely to do?", "format": "sjt", "options": [{"id": "truth", "text": "Tell full truth"}, {"id": "partial", "text": "Give partial truth"}, {"id": "deflect", "text": "Deflect"}, {"id": "protect", "text": "Protect spouse first"}, {"id": "adjust", "text": "Ask spouse to adjust instead"}]},
            {"id": "20.10", "text": "SJT: A decision is best for the couple but will disappoint both families. What is your instinct?", "format": "sjt", "options": [{"id": "fallout", "text": "Do it and handle fallout"}, {"id": "compromise", "text": "Look for a compromise"}, {"id": "delay", "text": "Delay to reduce backlash"}, {"id": "appeasement", "text": "Change course to keep families happy"}, {"id": "approval", "text": "Ask elders for approval again"}]},
            {"id": "20.11", "text": "Rank which matters most in a moral conflict.", "format": "ranking", "options": ["Truth", "Fairness", "Duty", "Love", "Stability", "Family peace", "Self-respect", "Compassion"]},
            {"id": "20.12", "text": "What kind of “right thing” is hardest for you to do in close relationships?", "format": "short_answer"},
            {"id": "20.13", "text": "When do you believe compromise becomes self-betrayal?", "format": "short_answer"}
        ]
    },
    {
        "section": "Relationship Stage Branching",
        "questions": [
            {"id": "21.1", "text": "What are you looking for right now?", "format": "multiple_choice", "options": ["Short-term dating", "Long-term committed relationship", "Marriage", "Unsure"]},
            {"id": "21.2", "text": "For you, exclusivity should ideally begin:", "format": "multiple_choice", "options": ["Immediately", "After mutual agreement", "Only in serious commitment", "Depends on chemistry", "Not essential"]},
            {"id": "21.3", "text": "In early dating, what matters most?", "format": "ranking", "options": ["Chemistry", "Emotional safety", "Fun", "Consistency", "Attraction", "Respect", "Shared values", "Independence", "Low pressure"]},
            {"id": "21.4", "text": "For long-term or marriage, alignment on family systems is:", "format": "importance_scale"},
            {"id": "21.5", "text": "I would seriously consider someone even if family integration looks difficult.", "format": "scale_7"},
            {"id": "21.6", "text": "Which matters more in a potential spouse?", "format": "forced_choice", "options": [{"id": "bond", "text": "Emotional bond"}, {"id": "compatibility", "text": "Family compatibility"}]},
            {"id": "21.7", "text": "SJT: You feel strongly connected to someone, but can already see future family conflict. What are you most likely to do?", "format": "sjt", "options": [{"id": "manage", "text": "Continue and see if it can be managed"}, {"id": "end", "text": "End it early"}, {"id": "discuss", "text": "Discuss structural concerns immediately"}, {"id": "hide", "text": "Hide the relationship for now"}, {"id": "buyin", "text": "Seek family buy-in quickly"}]},
            {"id": "21.8", "text": "What is the biggest difference between the person you want to date and the person you would actually marry?", "format": "short_answer"}
        ]
    },
    {
        "section": "Contradiction Detection and Reliability Probes",
        "questions": [
            {"id": "22.1", "text": "A married couple should be able to make most decisions independently.", "format": "scale_7"},
            {"id": "22.2", "text": "Parents deserve strong influence over their children’s married life.", "format": "scale_7"},
            {"id": "22.3", "text": "Fairness matters more than family hierarchy.", "format": "scale_7"},
            {"id": "22.4", "text": "A good spouse should adapt quietly rather than create conflict.", "format": "scale_7"},
            {"id": "22.5", "text": "I believe in equality, but some traditions are easier to maintain than challenge.", "format": "scale_7"},
            {"id": "22.6", "text": "When values conflict, I usually choose the option that causes the least immediate disruption.", "format": "scale_7"},
            {"id": "22.7", "text": "SJT: You believe spouses should be equal, but one tradition in your family clearly treats the wife unequally. What are you most likely to do?", "format": "sjt", "options": [{"id": "challenge", "text": "Challenge it"}, {"id": "accept", "text": "Accept it for that event"}, {"id": "negotiate", "text": "Negotiate partial change"}, {"id": "adjust", "text": "Ask spouse to adjust"}, {"id": "avoid", "text": "Avoid the event"}]},
            {"id": "22.8", "text": "What is one value you claim strongly but still find hard to live by?", "format": "short_answer"}
        ]
    },
    {
        "section": "Open Memory Anchors and Narrative Triggers",
        "questions": [
            {"id": "23.1", "text": "Describe a time you felt unsupported by someone important to you.", "format": "short_answer"},
            {"id": "23.2", "text": "Describe a time you were expected to sacrifice more than felt fair.", "format": "short_answer"},
            {"id": "23.3", "text": "What kind of family behavior makes you feel emotionally trapped?", "format": "short_answer"},
            {"id": "23.4", "text": "What kind of love feels strongest to you?", "format": "short_answer"},
            {"id": "23.5", "text": "Describe a moment when someone protected your dignity.", "format": "short_answer"},
            {"id": "23.6", "text": "Describe a moment when someone embarrassed or abandoned you publicly.", "format": "short_answer"},
            {"id": "23.7", "text": "What kind of apology stays with you positively?", "format": "short_answer"},
            {"id": "23.8", "text": "What kind of repeated behavior slowly makes you stop opening up?", "format": "short_answer"},
            {"id": "23.9", "text": "Describe a disagreement where you felt understood even though you did not get your way.", "format": "short_answer"},
            {"id": "23.10", "text": "What is one kind of pressure you can handle well, and one kind that gets under your skin fast?", "format": "short_answer"}
        ]
    },
    {
        "section": "Hygiene, Grooming & Domestic Standards",
        "questions": [
            {"id": "24.1", "text": "How important is daily personal grooming (shower, fresh clothes, etc.) in shared life?", "format": "scale_7", "min_label": "Not important", "max_label": "Extremely important"},
            {"id": "24.2", "text": "Which bothers you more?", "format": "forced_choice", "options": [{"id": "messy", "text": "A messy, unclean bathroom"}, {"id": "sterile", "text": "An uncomfortably sterile, clinical home"}]},
            {"id": "24.3", "text": "If your partner's hygiene standard is lower than yours, you would:", "format": "sjt", "options": [{"id": "direct", "text": "Address it directly and kindly"}, {"id": "hints", "text": "Drop hints over time"}, {"id": "adjust", "text": "Adjust your own standard downward"}, {"id": "letgo", "text": "Let it go entirely"}]},
            {"id": "24.4", "text": "Bodily functions (burping, bathroom door open, etc.) in shared space are:", "format": "multiple_choice", "options": ["Normal and comfortable", "Tolerable", "Should be private", "Deeply uncomfortable"]},
            {"id": "24.5", "text": "How often should shared spaces (kitchen, bathroom) be deep-cleaned?", "format": "multiple_choice", "options": ["Daily", "2-3 times a week", "Weekly", "When visibly dirty", "Outsource entirely"]},
            {"id": "24.6", "text": "What small hygiene or grooming habit in a partner would create daily friction for you?", "format": "short_answer"}
        ]
    },
    {
        "section": "Sexual Compatibility & Intimacy Preferences",
        "questions": [
            {"id": "25.1", "text": "How important is sexual compatibility as a foundation for a lasting relationship?", "format": "scale_7", "min_label": "Not important", "max_label": "Extremely important"},
            {"id": "25.2", "text": "In terms of intimacy style, where do you fall?", "format": "multiple_choice", "options": ["Very adventurous/experimental", "Open to trying new things", "Moderate — some variety", "Prefer familiar and comfortable", "Very traditional/vanilla"]},
            {"id": "25.3", "text": "How comfortable are you discussing sexual needs and boundaries with a partner?", "format": "scale_7", "min_label": "Very uncomfortable", "max_label": "Completely comfortable"},
            {"id": "25.4", "text": "Mismatched desire (one partner wants intimacy more frequently) should be handled by:", "format": "sjt", "options": [{"id": "higher", "text": "Prioritize higher-desire partner"}, {"id": "middle", "text": "Find a middle ground schedule"}, {"id": "lower", "text": "Lower-desire partner sets the pace"}, {"id": "causes", "text": "Address underlying causes together"}, {"id": "spontaneous", "text": "Avoid scheduling, stay spontaneous"}]},
            {"id": "25.5", "text": "Which matters more for long-term intimacy?", "format": "forced_choice", "options": [{"id": "passion", "text": "Physical passion and desire"}, {"id": "safety", "text": "Emotional safety during intimacy"}]},
            {"id": "25.6", "text": "Initiating intimacy should:", "format": "multiple_choice", "options": ["Be mutual and equal", "Usually come from one partner", "Be spontaneous and unplanned", "Depend entirely on mood", "Be discussed openly"]},
            {"id": "25.7", "text": "What would make you feel rejected or unsafe in intimate contexts?", "format": "short_answer"}
        ]
    },
    {
        "section": "Daily Rituals, Routines & Cohabitation Rhythms",
        "questions": [
            {"id": "26.1", "text": "How attached are you to a fixed daily routine (same wake time, same meals, same wind-down)?", "format": "scale_7", "min_label": "Very flexible", "max_label": "Highly structured"},
            {"id": "26.2", "text": "Which matters more in a shared home?", "format": "forced_choice", "options": [{"id": "predictable", "text": "Predictability and structure"}, {"id": "flexible", "text": "Flexibility and spontaneity"}]},
            {"id": "26.3", "text": "Morning routines should be:", "format": "multiple_choice", "options": ["Shared (breakfast together, etc.)", "Parallel (same space, own routine)", "Independent (no coordination needed)", "Family-centered (prayer/puja together)"]},
            {"id": "26.4", "text": "How important is it to eat dinner together most nights?", "format": "scale_7", "min_label": "Not important", "max_label": "Essential"},
            {"id": "26.5", "text": "My ideal sleep schedule is:", "format": "multiple_choice", "options": ["Early to bed, early to rise", "Night owl", "Flexible, no fixed pattern", "Depends on work demands"]},
            {"id": "26.6", "text": "If your partner's sleep schedule is very different from yours, you would:", "format": "sjt", "options": [{"id": "adapt", "text": "Adapt your own schedule"}, {"id": "make_them", "text": "Ask them to adapt"}, {"id": "separate", "text": "Sleep separately if needed"}, {"id": "compromise", "text": "Find a compromise in the middle"}, {"id": "accept", "text": "Accept the difference"}]},
            {"id": "26.7", "text": "How much alone time do you need in a day, even while living together?", "format": "multiple_choice", "options": ["Almost none — I want togetherness", "30 minutes to 1 hour", "1-2 hours", "2+ hours", "I recharge heavily alone"]},
            {"id": "26.8", "text": "What daily ritual or routine, if disrupted, would genuinely upset you?", "format": "short_answer"}
        ]
    }
]

def get_intake_data():
    return INTAKE_SECTIONS
