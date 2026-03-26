"""
CUHK Deep Knowledge System — structured intelligence about CUHK admissions,
faculties, interview formats, values, and scoring rubrics.
"""

CUHK_VALUES = {
    "core_philosophy": "Whole Person Development — CUHK believes education goes beyond academics to develop character, social responsibility, and cultural awareness.",
    "bilingualism": "CUHK emphasizes bilingual proficiency (Chinese and English) as essential for global citizenship with Chinese roots.",
    "social_responsibility": "CUHK expects students to demonstrate awareness of and commitment to addressing social issues, both locally and globally.",
    "tradition_and_innovation": "CUHK combines respect for Chinese cultural heritage with a forward-looking embrace of innovation and global perspectives.",
    "college_system": "CUHK's unique college system (9 colleges) provides a close-knit community experience. Each college has its own culture, traditions, and pastoral care.",
    "motto": "'Through learning and temperance to virtue' (博文約禮) — intellectual excellence paired with moral character.",
}

CUHK_COLLEGES = {
    "Chung Chi": "Founded on Christian values; emphasizes service, spirituality, and community.",
    "New Asia": "Rooted in Chinese cultural heritage; values Chinese philosophy and humanistic tradition.",
    "United": "Focuses on social engagement and practical problem-solving.",
    "Shaw": "Emphasizes innovation, entrepreneurship, and modern global outlook.",
    "Morningside": "Close mentor-student relationships, interdisciplinary learning.",
    "S.H. Ho": "Community service and experiential learning.",
    "CW Chu": "Environmental consciousness and sustainability.",
    "Wu Yee Sun": "Social enterprise and creative leadership.",
    "Lee Woo Sing": "Cultural diversity and global exchange.",
}

CUHK_PROGRAMS = {
    "Medicine": {
        "faculty": "Faculty of Medicine",
        "interview_format": "Multiple Mini Interview (MMI) — 6-8 stations, 8 minutes each. Stations include ethical scenarios, role-play, group discussion, and situational judgment.",
        "key_competencies": [
            "Empathy and compassion",
            "Ethical reasoning and moral judgment",
            "Communication skills (explaining complex ideas simply)",
            "Teamwork and collaboration",
            "Self-awareness and reflective practice",
            "Resilience and stress management",
            "Commitment to lifelong learning",
        ],
        "common_question_themes": [
            "Ethical dilemmas in healthcare (e.g., resource allocation, patient autonomy)",
            "Why medicine and not another helping profession?",
            "Experience with suffering, illness, or vulnerable populations",
            "Hong Kong's healthcare challenges (aging population, mental health stigma)",
            "Work-life balance and burnout prevention",
            "A time you failed and what you learned",
        ],
        "red_flags": [
            "Memorized, rehearsed answers that lack authenticity",
            "Inability to see multiple perspectives in ethical scenarios",
            "Arrogance or lack of humility",
            "No genuine patient/healthcare exposure",
            "Choosing medicine purely for prestige or parental pressure",
        ],
        "what_they_value": "Genuine compassion demonstrated through ACTION (not just words), ability to think through ethical gray areas without defaulting to black-and-white answers, self-awareness about personal motivations, and evidence of resilience.",
        "tips": "At MMI stations, think aloud — interviewers want to see your reasoning process, not just your conclusion. Always acknowledge the complexity of ethical questions before taking a position.",
    },
    "Business Administration": {
        "faculty": "CUHK Business School",
        "interview_format": "Individual interview (15-20 minutes) and/or group discussion. Some programs include a case analysis component.",
        "key_competencies": [
            "Analytical and critical thinking",
            "Leadership potential and initiative",
            "Communication and presentation skills",
            "Global awareness and business acumen",
            "Teamwork and interpersonal skills",
            "Entrepreneurial mindset",
        ],
        "common_question_themes": [
            "Current business trends in Asia/Hong Kong",
            "A business leader you admire and why",
            "Experience leading a team or project",
            "How you handle disagreement in a group",
            "Your career vision and how CUHK fits",
            "An ethical dilemma in business",
        ],
        "red_flags": [
            "No awareness of current business events",
            "Cannot articulate why business/CUHK specifically",
            "Purely grade-focused with no extracurricular breadth",
            "Dominating group discussions without listening",
        ],
        "what_they_value": "Balanced candidates who show both analytical rigor and interpersonal warmth, awareness of Asian business context, and genuine curiosity about how business impacts society.",
        "tips": "In group discussions, demonstrate leadership by facilitating others' contributions, not by talking the most. Reference specific CUHK Business School programs or initiatives to show genuine interest.",
    },
    "Law": {
        "faculty": "Faculty of Law",
        "interview_format": "Individual interview (20-30 minutes). May include analysis of a short legal scenario or current affairs discussion.",
        "key_competencies": [
            "Logical reasoning and argumentation",
            "Articulate verbal communication",
            "Awareness of current legal and social issues",
            "Ethical sensitivity and fairness",
            "Ability to see multiple perspectives",
            "Intellectual curiosity",
        ],
        "common_question_themes": [
            "Why law and not another profession?",
            "A recent legal issue in Hong Kong that interests you",
            "Justice vs. mercy — where do you draw the line?",
            "The role of law in social change",
            "A time you had to argue for something you didn't fully believe in",
            "Hong Kong's legal system — Basic Law, common law tradition",
        ],
        "red_flags": [
            "No awareness of Hong Kong's legal landscape",
            "Inability to present balanced arguments",
            "Choosing law only for financial reasons",
            "Dogmatic thinking without nuance",
        ],
        "what_they_value": "Sharp analytical thinking, ability to construct and deconstruct arguments, genuine interest in justice and fairness, and awareness of Hong Kong's unique legal position.",
        "tips": "Always present both sides of an argument before stating your position. Reference specific aspects of CUHK Law's curriculum or clinics.",
    },
    "Engineering": {
        "faculty": "Faculty of Engineering",
        "interview_format": "Individual interview (15-20 minutes). May include a problem-solving component or discussion of a technical project.",
        "key_competencies": [
            "Problem-solving and logical thinking",
            "Technical curiosity and hands-on experience",
            "Innovation and creative thinking",
            "Teamwork in technical projects",
            "Communication of technical concepts",
        ],
        "common_question_themes": [
            "A technical project or problem you've worked on",
            "How technology can address a social challenge",
            "Why this specific engineering discipline?",
            "A time you debugged or troubleshot something",
            "Emerging technologies that excite you",
            "How you handle failure in technical work",
        ],
        "red_flags": [
            "No hands-on technical experience or projects",
            "Cannot explain technical concepts simply",
            "Pure theory without practical application interest",
        ],
        "what_they_value": "Demonstrable technical passion (projects, competitions, tinkering), ability to connect engineering to real-world impact, and collaborative mindset.",
        "tips": "Bring specific examples of things you've BUILT or FIXED. CUHK Engineering values the maker mindset.",
    },
    "Science": {
        "faculty": "Faculty of Science",
        "interview_format": "Individual interview (15-20 minutes). May include discussion of a scientific topic or research interest.",
        "key_competencies": [
            "Scientific curiosity and inquiry mindset",
            "Research interest and methodology awareness",
            "Analytical and quantitative reasoning",
            "Ability to explain scientific concepts clearly",
            "Awareness of science's role in society",
        ],
        "common_question_themes": [
            "A scientific discovery or concept that fascinates you",
            "Research experience or independent investigation",
            "How science can address global challenges",
            "Your favorite experiment and why",
            "Interdisciplinary connections in science",
        ],
        "red_flags": [
            "No genuine curiosity beyond the syllabus",
            "Cannot discuss science beyond textbook facts",
        ],
        "what_they_value": "Authentic scientific curiosity, research mindset (even informal), ability to ask good questions, and understanding of the scientific method.",
        "tips": "Discuss science you've explored BEYOND the curriculum. Show you can think like a researcher, not just a student.",
    },
    "Social Science": {
        "faculty": "Faculty of Social Science",
        "interview_format": "Individual interview (15-20 minutes). Discussion of social issues and personal perspectives.",
        "key_competencies": [
            "Critical thinking about social issues",
            "Empathy and cultural sensitivity",
            "Awareness of Hong Kong and global social dynamics",
            "Communication and articulation",
            "Community involvement",
        ],
        "common_question_themes": [
            "A social issue you care deeply about",
            "Community service or volunteer experience",
            "How social science can create change",
            "Inequality and social justice perspectives",
            "Cultural diversity and inclusion",
        ],
        "red_flags": [
            "No genuine social awareness or engagement",
            "Inability to discuss social issues with nuance",
        ],
        "what_they_value": "Demonstrated social engagement, critical awareness of inequality and social structures, and genuine desire to understand and improve society.",
        "tips": "Connect personal experiences to broader social patterns. Show you think systemically, not just individually.",
    },
    "Arts": {
        "faculty": "Faculty of Arts",
        "interview_format": "Individual interview (15-20 minutes). May include discussion of a text, cultural topic, or creative work.",
        "key_competencies": [
            "Critical and creative thinking",
            "Cultural awareness and appreciation",
            "Strong written and verbal communication",
            "Intellectual breadth and curiosity",
            "Appreciation of Chinese and Western traditions",
        ],
        "common_question_themes": [
            "A book, film, or artwork that influenced you",
            "The role of humanities in modern society",
            "Cultural identity and bilingualism",
            "A historical event that resonates with you",
            "How arts/humanities connect to other fields",
        ],
        "red_flags": [
            "No reading or cultural engagement beyond school",
            "Cannot articulate why humanities matter",
        ],
        "what_they_value": "Genuine intellectual curiosity, cultural literacy across Chinese and Western traditions (aligning with CUHK's bilingual mission), and ability to think critically about texts and ideas.",
        "tips": "Demonstrate engagement with both Chinese and Western culture — this is core to CUHK Arts' identity.",
    },
    "Education": {
        "faculty": "Faculty of Education",
        "interview_format": "Individual interview (15-20 minutes) with potential group activity or teaching demonstration.",
        "key_competencies": [
            "Passion for teaching and learning",
            "Communication and patience",
            "Empathy and understanding of diverse learners",
            "Creativity in educational approaches",
            "Awareness of Hong Kong's education system",
        ],
        "common_question_themes": [
            "Why teaching as a career?",
            "A teacher who influenced you and how",
            "How you would handle a struggling student",
            "Education reform and innovation",
            "Challenges facing Hong Kong's education system",
        ],
        "red_flags": [
            "No genuine passion for teaching (choosing it as backup)",
            "No experience working with young people",
        ],
        "what_they_value": "Authentic calling to teach, patience and empathy, creative approaches to education, and willingness to go beyond the classroom.",
        "tips": "Share specific stories of helping others learn. Show awareness of diverse learning needs.",
    },
    "General / Undecided": {
        "faculty": "General Admission",
        "interview_format": "Individual interview (15-20 minutes). Broad questions about motivations, goals, and personal development.",
        "key_competencies": [
            "Self-awareness and personal reflection",
            "Communication skills",
            "Intellectual curiosity across disciplines",
            "Community involvement",
            "Goal clarity and motivation",
        ],
        "common_question_themes": [
            "Tell me about yourself and your interests",
            "Why CUHK specifically?",
            "What do you hope to gain from university?",
            "A challenge you've overcome",
            "Your contribution to the CUHK community",
            "Where do you see yourself in 10 years?",
        ],
        "red_flags": [
            "No specific reason for choosing CUHK",
            "Cannot articulate personal goals",
            "No extracurricular engagement",
        ],
        "what_they_value": "Well-rounded individuals who demonstrate self-awareness, community spirit, and genuine enthusiasm for learning. CUHK's whole-person philosophy means they look beyond grades.",
        "tips": "Research CUHK's specific offerings — mention colleges, exchange programs, or research opportunities that interest you. Generic answers about 'good university' won't impress.",
    },
}


def get_program_context(program: str) -> str:
    """Get rich CUHK-specific context for a program to inject into prompts."""
    info = CUHK_PROGRAMS.get(program, CUHK_PROGRAMS["General / Undecided"])
    values_text = "\n".join(f"- {k}: {v}" for k, v in CUHK_VALUES.items())

    return f"""=== CUHK INTERVIEW INTELLIGENCE ===

CUHK CORE VALUES:
{values_text}

PROGRAM: {info['faculty']} — {program}
INTERVIEW FORMAT: {info['interview_format']}

KEY COMPETENCIES THEY ASSESS:
{chr(10).join(f'- {c}' for c in info['key_competencies'])}

COMMON QUESTION THEMES:
{chr(10).join(f'- {t}' for t in info['common_question_themes'])}

WHAT INTERVIEWERS ACTUALLY VALUE:
{info['what_they_value']}

RED FLAGS THAT HURT CANDIDATES:
{chr(10).join(f'- {r}' for r in info['red_flags'])}

INSIDER TIPS:
{info['tips']}
=== END CUHK INTELLIGENCE ==="""


def get_scoring_rubric(program: str) -> str:
    """Get CUHK-specific scoring criteria for response analysis."""
    info = CUHK_PROGRAMS.get(program, CUHK_PROGRAMS["General / Undecided"])

    return f"""CUHK-SPECIFIC SCORING RUBRIC for {program}:

In addition to content, relevance, and clarity, score these CUHK-specific dimensions:

- "values_alignment_score" (1-10): Does the answer reflect CUHK's core values? Look for:
  * Whole-person development (showing breadth beyond academics)
  * Social responsibility and community awareness
  * Respect for tradition combined with innovation
  * Bilingual/bicultural awareness

- "self_awareness_score" (1-10): Does the student show genuine self-reflection? Look for:
  * Honest acknowledgment of strengths AND weaknesses
  * Growth mindset (learning from failures)
  * Authentic motivation (not rehearsed or parental-pressure-driven)
  * Awareness of how their experiences shaped them

Key competencies for this program: {', '.join(info['key_competencies'][:4])}
Red flags to penalize: {', '.join(info['red_flags'][:3])}"""


def get_interview_format_info(program: str) -> dict:
    """Get interview format details for the pre-interview briefing."""
    info = CUHK_PROGRAMS.get(program, CUHK_PROGRAMS["General / Undecided"])
    return {
        "faculty": info["faculty"],
        "program": program,
        "format": info["interview_format"],
        "competencies": info["key_competencies"],
        "tips": info["tips"],
        "what_they_value": info["what_they_value"],
    }


def get_all_programs() -> list[str]:
    """Return list of all available CUHK programs."""
    return list(CUHK_PROGRAMS.keys())
