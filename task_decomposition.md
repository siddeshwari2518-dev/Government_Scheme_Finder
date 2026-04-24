# 📄 Task Decomposition & Specifications

## Project: Smart Government Scheme Advisor (India)

---

## 🔹 1. Overview

This project builds an **AI-powered agent** that helps citizens discover government schemes they are eligible for.
The agent dynamically interacts with users, gathers relevant information, fetches real-time data, and provides structured recommendations.

---

## 🎯 2. Agent Objective

**Input → Reason → Fetch → Match → Evaluate → Output**

The agent performs the following end-to-end workflow:

1. Collect user details through conversation
2. Generate intelligent search queries
3. Retrieve latest schemes using external tools
4. Match eligibility criteria
5. Generate structured recommendations
6. Evaluate response quality
7. Display results via UI

---

## 🧩 3. Task Breakdown

---

### 🔹 Task 1 — Collect User Profile (Dynamic Interaction)

**Description:**
The agent collects user data through a conversational interface instead of a static form.

**Inputs:**

* Age
* Gender
* State / District
* Income range
* Occupation
* Category (if applicable)
* Special conditions (e.g., disability, student, farmer)

**Output:**

```json
{
  "age": 21,
  "state": "Maharashtra",
  "income": "low",
  "occupation": "student",
  "category": "OBC"
}
```

**Decision Logic:**

* Ask questions step-by-step (not all at once)
* If data missing → continue asking
* Stop when sufficient information is collected

---

### 🔹 Task 2 — Query Generation

**Description:**
Convert the user profile into optimized search queries.

**Input:**

* Structured user profile

**Output Examples:**

```
government schemes for students Maharashtra low income 2025
scholarship schemes India OBC eligibility
```

**Decision Logic:**

* Generate multiple queries if needed
* If profile incomplete → return to Task 1

---

### 🔹 Task 3 — Scheme Retrieval (Tavily Tool)

**Description:**
Fetch real-time scheme data using Tavily Search.

**Input:**

* Queries from Task 2

**Output:**

* List of schemes with:

  * Name
  * Description
  * Source link

**Decision Logic:**

* Prefer trusted domains (gov.in, nic.in)
* If no results → retry with broader query

---

### 🔹 Task 4 — Eligibility Matching

**Description:**
Filter schemes based on user eligibility.

**Input:**

* User profile
* Retrieved scheme data

**Output:**

```
Eligible:
- PM Scholarship Scheme
- State Education Grant

Not Eligible:
- Farmer Subsidy Scheme (Reason: Not a farmer)
```

**Decision Logic:**

* Remove irrelevant schemes
* If uncertain → mark as "May vary by state"
* If no schemes → suggest alternatives

---

### 🔹 Task 5 — Structured Response Generation

**Description:**
Generate clean, structured outputs for each scheme.

**Output Format:**

```
Scheme Name: XYZ Scheme

Why Eligible:
Matches student + income criteria

Benefits:
₹25,000/year

Documents Required:
Income certificate, ID proof

How to Apply:
1. Visit official website  
2. Fill application form  
3. Upload documents  

Official Link:
https://...
```

**Decision Logic:**

* Avoid vague explanations
* Do not hallucinate schemes
* Keep language simple

---

### 🔹 Task 6 — Output Evaluation (LLM-as-Judge)

**Description:**
Evaluate the generated response using a secondary LLM.

**Input:**

* Generated output
* User profile

**Evaluation Criteria:**

| Criteria             | Max Score |
| -------------------- | --------- |
| Eligibility accuracy | 3         |
| Relevance            | 3         |
| Clarity              | 2         |
| Completeness         | 2         |
| **Total**            | **10**    |

**Output:**

* Score (0–10)
* Feedback (2–3 lines)

**Decision Logic:**

* If score < 6 → regenerate once

---

### 🔹 Task 7 — Output Display (UI Layer)

**Description:**
Display results in a chat-based interface (Streamlit).

**Output:**

* Chat messages
* Structured scheme cards
* Evaluation score

**Score Indicators:**

* 🟢 8–10 → Good
* 🟡 5–7 → Average
* 🔴 <5 → Needs improvement

---

## 🔄 4. System Flow

```
User Input (Chat)
        ↓
Dynamic Questioning
        ↓
User Profile Creation
        ↓
Query Generation
        ↓
Tavily Search (Tool)
        ↓
Eligibility Matching
        ↓
Structured Output Generation
        ↓
LLM-as-Judge Evaluation
        ↓
Final Output Display (UI)
```

---

## ⚠️ 5. Key Design Principles

* Dynamic interaction (not static forms)
* Real-time data fetching
* Strict eligibility filtering
* Structured outputs (not raw text)
* Evaluation-driven improvement

---

## 🚀 6. Outcome

The final system delivers:

* Personalized scheme recommendations
* Clear eligibility explanations
* Step-by-step application guidance
* Reliable and updated information

---
