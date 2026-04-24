import json
from google.genai import types
from prompts import (
    ELIGIBILITY_ANALYZER_SYSTEM_PROMPT,
    JUDGE_EVAL_PROMPT,
    JUDGE_SYSTEM_PROMPT,
    SCHEME_GUIDE_WRITER_SYSTEM_PROMPT,
    SCHEME_RESEARCHER_SYSTEM_PROMPT,
)


class AgentExecutionError(Exception):
    def __init__(self, user_message: str, original_error: Exception | None = None):
        super().__init__(user_message)
        self.user_message = user_message
        self.original_error = original_error


tavily_decl = types.FunctionDeclaration(
    name="tavily_search_tool",
    description="Search the web for real Indian government schemes, eligibility criteria, and application procedures from official sources.",
    parameters=types.Schema(
        type="object",
        properties={
            "query": types.Schema(
                type="string",
                description="The search query string",
            )
        },
        required=["query"],
    ),
)


def _is_quota_error(error: Exception) -> bool:
    message = str(error).lower()
    return (
        "resource_exhausted" in message
        or "quota exceeded" in message
        or "429" in message
    )


def _raise_agent_error(agent_name: str, error: Exception) -> None:
    if _is_quota_error(error):
        raise AgentExecutionError(
            f"{agent_name} could not use Gemini because the API quota is exhausted.",
            original_error=error,
        ) from error

    raise AgentExecutionError(
        f"{agent_name} failed because the Gemini request returned an unexpected error.",
        original_error=error,
    ) from error


def _run_tavily_search(query: str, tavily_client) -> str:
    result = tavily_client.search(query=query, max_results=5)
    snippets = []
    for item in result.get("results", []):
        title = item.get("title", "Untitled")
        url = item.get("url", "")
        content = item.get("content", "")
        snippets.append(f"- [{title}]({url}): {content[:300]}")
    return "\n".join(snippets)


def _extract_profile_sections(user_profile: str) -> dict[str, str]:
    sections: dict[str, str] = {}
    for line in user_profile.splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        sections[key.strip().lower()] = value.strip()
    return sections


def _build_search_queries(user_profile: str) -> list[str]:
    """Build targeted search queries based on user profile."""
    sections = _extract_profile_sections(user_profile)
    queries = []

    state = sections.get("state", "")
    occupation = sections.get("occupation", "")
    income = sections.get("income range", "")
    gender = sections.get("gender", "")
    age = sections.get("age", "")
    category = sections.get("caste category", "")
    special = sections.get("special conditions", "")

    # Build targeted queries from profile
    base = "Indian government scheme eligibility"
    if occupation:
        queries.append(f"{occupation} government scheme India 2024 {state}")
    if income and ("below" in income.lower() or "bpl" in income.lower() or "low" in income.lower()):
        queries.append(f"BPL low income government scheme India {state} benefits")
    if gender.lower() == "female":
        queries.append(f"women government scheme India {state} 2024")
    if category and category.lower() not in ["general", "none", ""]:
        queries.append(f"{category} caste government scheme India reservation benefits")
    if special:
        queries.append(f"{special} government scheme India benefits 2024")
    if not queries:
        queries.append(f"government scheme India {state} citizen benefits 2024")

    return queries[:3]


# ─── FALLBACK FUNCTIONS ───────────────────────────────────────────────────────

def fallback_research_brief(tavily_client, user_profile: str) -> str:
    queries = _build_search_queries(user_profile)
    sections = [
        "## Research Brief (Fallback Mode)",
        "Gemini quota was unavailable. This brief was assembled directly from Tavily search results.",
    ]

    for query in queries:
        snippets = _run_tavily_search(query, tavily_client)
        if snippets:
            sections.append(f"### Search: {query}")
            sections.append(snippets)

    sections.append("### Key scheme categories to check")
    sections.append(
        "- PM Kisan / Agricultural support schemes (for farmers)\n"
        "- PMAY (Pradhan Mantri Awas Yojana) — housing for eligible families\n"
        "- Ayushman Bharat / PM-JAY — health insurance for low-income households\n"
        "- PM Ujjwala Yojana — LPG for BPL women\n"
        "- Scholarship schemes — for SC/ST/OBC/minority students\n"
        "- Self-employment schemes — PMEGP, Mudra Loan for entrepreneurs\n"
        "- State-specific schemes — check the respective state government portal"
    )
    return "\n\n".join(sections)


def fallback_eligibility_analysis(research_brief: str, user_profile: str) -> str:
    sections = _extract_profile_sections(user_profile)
    occupation = sections.get("occupation", "Not specified")
    income = sections.get("income range", "Not specified")
    state = sections.get("state", "Not specified")
    category = sections.get("caste category", "Not specified")
    gender = sections.get("gender", "Not specified")
    special = sections.get("special conditions", "None")

    return f"""## Eligibility Analysis (Fallback Mode)
Gemini quota was unavailable. This is a rule-based eligibility check from your profile.

### Your Profile Summary
- Occupation: {occupation}
- Income Range: {income}
- State: {state}
- Category: {category}
- Gender: {gender}
- Special Conditions: {special}

### Likely Eligible Schemes
Based on your profile, you may qualify for the following categories of schemes:

**1. Ayushman Bharat PM-JAY** *(if income is low/BPL)*
- Health insurance up to ₹5 lakh/year
- Check eligibility at: pmjay.gov.in

**2. PMAY (Housing Scheme)** *(if no pucca house)*
- Subsidy on home loans
- For EWS/LIG/MIG categories

**3. PM Kisan** *(if farmer)*
- ₹6,000/year direct to bank
- For small & marginal farmers

**4. Scholarship Schemes** *(if SC/ST/OBC/Minority)*
- Pre-matric, post-matric scholarships
- National scholarship portal: scholarships.gov.in

**5. Mudra Loan / PMEGP** *(if self-employed or business)*
- Loan up to ₹10 lakh without collateral

### Important Note
This is a preliminary match. Please verify eligibility on the official portals as criteria may vary by state.
"""


def fallback_scheme_guide(research_brief: str, eligibility_analysis: str, user_profile: str) -> str:
    return """## Scheme Application Guide (Fallback Mode)
Gemini quota was unavailable. Below is a general application guide for common schemes.

---

### How to Apply for Government Schemes in India

**Step 1: Confirm Eligibility**
- Visit myscheme.gov.in — India's official one-stop scheme portal
- Enter your profile details to get a personalized list

**Step 2: Gather Documents**
Most schemes require:
- Aadhaar Card (mandatory)
- Bank account (linked to Aadhaar)
- Income Certificate / BPL Card (if applicable)
- Caste Certificate (for SC/ST/OBC schemes)
- Ration Card
- Passport-size photo

**Step 3: Apply Online**
- Most central schemes: apply at the respective ministry portal
- State schemes: apply at your state's e-governance portal
- Common portal: services.india.gov.in

**Step 4: Apply Offline (if needed)**
- Visit your nearest Common Service Centre (CSC)
- Or your district's collectorate / block development office

**Helplines:**
- PM-JAY: 14555
- PMAY: 1800-11-3377
- PM Kisan: 155261 / 1800-115-526
- General: 1800-11-8002 (India Gov Helpline)

---
*This may vary by state. Always verify details on official gov.in portals.*
"""


def fallback_judge_result() -> dict:
    return {
        "scores": {
            "accuracy":           {"score": 3, "reasoning": "Fallback mode — accuracy based on known schemes, not live search."},
            "eligibility_match":  {"score": 3, "reasoning": "Basic profile-based matching applied."},
            "completeness":       {"score": 3, "reasoning": "Standard fields included but not fully personalized."},
            "clarity":            {"score": 4, "reasoning": "Language kept simple and citizen-friendly."},
            "relevance":          {"score": 3, "reasoning": "Schemes selected based on profile keywords."},
        },
        "overall_score": 3.2,
        "summary": "This is a fallback recommendation generated without live AI. It uses rule-based matching and may miss newer or state-specific schemes. Please verify on myscheme.gov.in for the most accurate results.",
        "top_strength": "Clear language and actionable steps provided.",
        "top_improvement": "Live AI search would improve scheme accuracy and personalization significantly.",
    }


# ─── AGENT FUNCTIONS ──────────────────────────────────────────────────────────

def scheme_researcher_agent(client, tavily_client, user_profile: str, log_step=None) -> str:
    if log_step:
        log_step("Researcher: searching for relevant government schemes")

    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(
                    text=(
                        f"Find real, currently active Indian government schemes this person is likely eligible for:\n\n"
                        f"{user_profile}\n\n"
                        "Use the search tool to find specific schemes from official sources (gov.in, nic.in, myscheme.gov.in). "
                        "Search for central and state-level schemes based on their profile. "
                        "Produce a research brief listing found schemes with their key eligibility criteria."
                    )
                )
            ],
        )
    ]

    tools = [types.Tool(function_declarations=[tavily_decl])]

    for turn in range(8):
        try:
            response = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=contents,
                config=types.GenerateContentConfig(
                    system_instruction=SCHEME_RESEARCHER_SYSTEM_PROMPT,
                    tools=tools,
                ),
            )
        except Exception as error:
            _raise_agent_error("Researcher", error)

        parts = response.candidates[0].content.parts
        function_calls = [part.function_call for part in parts if part.function_call]

        if not function_calls:
            final_text = "".join(part.text for part in parts if part.text)
            if log_step:
                log_step(f"Researcher: done in {turn + 1} turn(s)")
            return final_text

        contents.append(types.Content(role="model", parts=parts))

        tool_results = []
        for function_call in function_calls:
            query = function_call.args.get("query", "India government scheme benefits")
            if log_step:
                log_step(f"Researcher: searching → '{query}'")
            search_result = _run_tavily_search(query, tavily_client)
            tool_results.append(
                types.Part.from_function_response(
                    name=function_call.name,
                    response={"result": search_result},
                )
            )

        contents.append(types.Content(role="user", parts=tool_results))

    if log_step:
        log_step("Researcher: max turns reached")
    return "".join(part.text for part in parts if part.text)


def eligibility_analyzer_agent(client, research_brief: str, user_profile: str, log_step=None) -> str:
    if log_step:
        log_step("Eligibility Analyzer: matching schemes to your profile")

    prompt = f"""Analyze this citizen's profile and match them to the government schemes found in the research brief.

CITIZEN PROFILE:
{user_profile}

RESEARCH BRIEF (found schemes):
{research_brief}

For each scheme:
1. State clearly if this person IS or IS NOT eligible and why
2. List any conditions or caveats
3. Rank the schemes by impact (most beneficial first)
4. Flag any schemes where eligibility is uncertain and why"""

    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=[
                types.Content(
                    role="user",
                    parts=[types.Part.from_text(text=prompt)],
                )
            ],
            config=types.GenerateContentConfig(
                system_instruction=ELIGIBILITY_ANALYZER_SYSTEM_PROMPT,
            ),
        )
    except Exception as error:
        _raise_agent_error("Eligibility Analyzer", error)

    if log_step:
        log_step("Eligibility Analyzer: analysis complete")
    return response.text


def scheme_guide_writer_agent(client, research_brief: str, eligibility_analysis: str, user_profile: str, log_step=None) -> str:
    if log_step:
        log_step("Guide Writer: preparing step-by-step application guides")

    prompt = f"""Write a complete, citizen-friendly scheme application guide for this person.

CITIZEN PROFILE:
{user_profile}

RESEARCH BRIEF:
{research_brief}

ELIGIBILITY ANALYSIS:
{eligibility_analysis}

For each eligible scheme, provide:
- Scheme name + 1-line description
- Why this specific person qualifies
- Benefits (exact amounts/coverage in simple language)
- Required documents (exact list)
- Step-by-step application process (online + offline)
- Official website or helpline
- Estimated processing time

Only include schemes this person is eligible for. Write for a first-time applicant."""

    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=[
                types.Content(
                    role="user",
                    parts=[types.Part.from_text(text=prompt)],
                )
            ],
            config=types.GenerateContentConfig(
                system_instruction=SCHEME_GUIDE_WRITER_SYSTEM_PROMPT,
            ),
        )
    except Exception as error:
        _raise_agent_error("Guide Writer", error)

    if log_step:
        log_step("Guide Writer: application guides ready")
    return response.text


def judge_agent(client, user_profile: str, research_brief: str, scheme_guide: str, log_step=None) -> dict:
    if log_step:
        log_step("Judge: evaluating recommendation quality")

    eval_prompt = JUDGE_EVAL_PROMPT.format(
        user_profile=user_profile,
        research_brief=research_brief,
        scheme_guide=scheme_guide,
    )

    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=[
                types.Content(
                    role="user",
                    parts=[types.Part.from_text(text=eval_prompt)],
                )
            ],
            config=types.GenerateContentConfig(
                system_instruction=JUDGE_SYSTEM_PROMPT,
            ),
        )
    except Exception as error:
        _raise_agent_error("Judge", error)

    raw = response.text.strip()
    raw = raw.replace("```json", "").replace("```", "").strip()

    try:
        result = json.loads(raw)
    except json.JSONDecodeError:
        result = {
            "scores": {
                "accuracy":          {"score": 0, "reasoning": "Could not parse"},
                "eligibility_match": {"score": 0, "reasoning": "Could not parse"},
                "completeness":      {"score": 0, "reasoning": "Could not parse"},
                "clarity":           {"score": 0, "reasoning": "Could not parse"},
                "relevance":         {"score": 0, "reasoning": "Could not parse"},
            },
            "overall_score": 0,
            "summary": "Judge response could not be parsed.",
            "top_strength": "N/A",
            "top_improvement": "N/A",
        }

    if log_step:
        log_step(f"Judge: overall score = {result.get('overall_score', '?')}/5")
    return result
