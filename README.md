---
title: InboxEnv
emoji: 📧
colorFrom: blue
colorTo: indigo
sdk: docker
pinned: false
tags:
  - openenv
---

# **InboxEnv**

Email triage and prioritization environment for training AI agents on realistic inbox management tasks.

## Motivation

Email triage is a strong agent benchmark because it combines classification, prioritization, escalation judgment, and concise response drafting in one workflow. Real teams do this every day across support, sales, billing, and internal operations, so a benchmark in this domain captures both decision quality and communication quality.

## Environment Description

InboxEnv simulates a stateful inbox where an agent processes one email at a time. Each episode is tied to one of three tasks with increasing difficulty. At every step the agent receives the current email plus progress metadata, then returns a structured action containing priority, category, escalation intent, and optionally a response draft.

The environment uses deterministic, hardcoded ground truth labels and per-step dense rewards. Episodes end after the task-specific inbox has been fully processed.

## Observation Space

| Field | Type | Description |
| --- | --- | --- |
| `current_email` | object | The email currently being triaged |
| `inbox_remaining` | integer | Number of emails left after the current one |
| `emails_processed` | integer | Number of emails already handled |
| `current_score` | float | Cumulative reward earned so far |
| `task_id` | string | Active task identifier |
| `task_description` | string | Human-readable task instructions |
| `step_number` | integer | Current step index, starting at 1 |

## Action Space

| Field | Type | Valid Values / Meaning |
| --- | --- | --- |
| `email_id` | string | Must match the current email ID |
| `priority` | enum | `urgent`, `high`, `medium`, `low`, `spam` |
| `category` | enum | `customer_support`, `billing`, `technical`, `sales`, `internal`, `spam` |
| `should_escalate` | boolean | Whether the email should be escalated |
| `draft_response` | string, optional | Required in Task 3 for urgent and high-priority emails |
| `reasoning` | string, optional | Gives a small explainability bonus |

## Tasks

| Task ID | Name | Difficulty | Emails | Description |
| --- | --- | --- | --- | --- |
| `task_1` | Priority Classification | easy | 10 | Classify emails by priority and category |
| `task_2` | Triage and Escalation | medium | 15 | Add escalation decisions to triage |
| `task_3` | Full Triage with Response Drafting | hard | 20 | Full triage plus response drafting for urgent/high emails |

## Reward Function

InboxEnv uses dense per-step rewards in the range `[0.0, 1.0]`.

- Task 1: `0.6 * priority + 0.4 * category`
- Task 2: `0.4 * priority + 0.3 * category + 0.3 * escalation`
- Task 3: `0.3 * priority + 0.2 * category + 0.2 * escalation + 0.3 * response_quality`
- Adjacent priority levels receive partial credit worth `0.5`
- Response quality is scored with keyword overlap against hardcoded key phrases
- A `reasoning` field adds a `+0.05` bonus
- False-positive spam labels incur a `-0.1` penalty
- Missing a required escalation in Tasks 2 and 3 incurs a `-0.1` penalty
- Missing a required draft response in Task 3 incurs a `-0.1` penalty

Rewards are clamped back into `[0.0, 1.0]` after bonuses and penalties.

## Setup

### Docker

```bash
docker build -t inboxenv .
docker run -p 7860:7860 inboxenv
```

Then open [http://localhost:7860](http://localhost:7860).

### Local Development

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 7860
```

Run tests with:

```bash
python -m pytest tests/ -v
```

Run the baseline agent with:

```bash
OPENAI_API_KEY=dummy API_BASE_URL=http://localhost:7860 python inference.py
```

## Baseline Scores

These are approximate, since the baseline can use either a real model or the built-in heuristic fallback when the OpenAI call is unavailable.

| Task | Expected Approximate Score |
| --- | --- |
| `task_1` | `0.70 - 0.90` |
| `task_2` | `0.60 - 0.80` |
| `task_3` | `0.55 - 0.75` |

## OpenEnv Compliance

The project includes `openenv.yaml` describing the environment contract, task catalog, action space, observation space, endpoints, and reward behavior. It is designed to work cleanly with a typical OpenEnv validation flow such as:

```bash
openenv validate .
```
