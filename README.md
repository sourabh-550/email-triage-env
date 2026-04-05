# 📧 Email Classification & Triage — OpenEnv Environment

[![OpenEnv](https://img.shields.io/badge/OpenEnv-compatible-blue)](https://openenv.ai)
[![Python](https://img.shields.io/badge/python-3.11-green)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111-teal)](https://fastapi.tiangolo.com)

---

## 🌍 Project Overview

Every knowledge worker processes dozens or hundreds of emails a day. The decisions seem
simple — *is this spam? does this need a reply? how urgent is it?* — but they require
contextual reasoning, domain knowledge, and the ability to detect deception (phishing,
fake CEO requests, scam promotions).

**Email Triage** is an OpenEnv environment that challenges AI agents to replicate this
human skill at production quality. The agent reads a stream of emails one by one,
classifies each one, and optionally drafts a short response — exactly as a real inbox
assistant would.

---

## 🧠 Real-World Motivation

| Pain Point | How This Env Captures It |
|---|---|
| Spam vs. legitimate look-alikes | Hard task includes CEO phishing that *looks* urgent |
| Promotions disguised as important | Medium task mixes LinkedIn upsells with real security alerts |
| Operational urgency | PagerDuty alerts, storage limits, contract deadlines |
| Fraud detection | Nigerian prince, PayPal transaction, gift card scams |

---

## 📥 Observation Space

Each step the agent receives an `Observation` object:

| Field | Type | Description |
|---|---|---|
| `email_id` | string | Unique email identifier |
| `email_text` | string | Full body of the email |
| `sender` | string | Sender email/name |
| `subject` | string | Email subject line |
| `urgency` | enum | `low` / `medium` / `high` |
| `previous_action` | string\|null | Label applied to the previous email |
| `step_number` | int | Current step (0-based) |
| `total_steps` | int | Total emails in this task |

---

## 🎮 Action Space

The agent returns an `Action` object:

| Field | Type | Description |
|---|---|---|
| `label` | enum | `spam` / `important` / `promotion` |
| `optional_response` | string\|null | Short reply (max 200 chars); required for important emails |

---

## 🏆 Reward Design

Reward per step is continuous from **−0.2 to 1.0**:

```
reward = classification_score + urgency_score + response_score

classification_score:  +0.7  if label is correct,  else 0.0
urgency_score:         +0.2  if urgency handled correctly (only when classification correct)
response_score:        +0.1  if response is substantive (for important emails)
                       −0.1  if unnecessary response on low-priority email
                       −0.2  if random/garbage response with wrong classification
```

Episode score = average of `max(0, step_reward)` across all emails, normalized to [0, 1].

---

## 📋 Task Descriptions

### 🟢 Easy – Obvious Spam Detection (5 emails)
Classic spam signals: lottery scams, Nigerian prince fraud, pharma spam mixed with
clear work emails (budget review, client follow-up). A rule-based agent should score ≥ 0.8.

### 🟡 Medium – Promotion vs Important (6 emails)
Amazon Prime Day deals vs. HR performance reviews. LinkedIn follower alerts vs. bank
security warnings. Requires reading intent, not just sender domain.

### 🔴 Hard – Ambiguous Reasoning (7 emails)
Includes:
- CEO gift card phishing (looks like internal mail)
- PayPal transaction alerts (may indicate fraud)
- GitHub archival warnings (automated but actionable)
- PagerDuty critical alerts (requires immediate response)
- Travel flash sales (artificial urgency, really just promotions)

---

## 🚀 Setup Instructions

### Prerequisites
- Python 3.11+
- Docker (for containerized runs)
- OpenAI-compatible API key

### Local Setup

```bash
git clone https://huggingface.co/spaces/your-username/email-triage-env
cd email-triage-env

pip install -r requirements.txt
uvicorn server.app:app --host 0.0.0.0 --port 7860 --reload
```

The API will be live at `http://localhost:7860`.

### Docker

```bash
docker build -t email-triage-env .
docker run -p 7860:7860 email-triage-env
```

---

## 🤖 Running Inference

```bash
export OPENAI_API_KEY=sk-...
export API_BASE_URL=https://api.openai.com/v1
export MODEL_NAME=gpt-4o-mini
export SERVER_URL=http://localhost:7860

python inference.py
```

### Log Format

```
[START] task=easy env=email_triage_env model=gpt-4o-mini
[STEP] step=0 action={"label": "spam", "optional_response": null} reward=0.9 done=false error=null
[STEP] step=1 action={"label": "important", "optional_response": "Noted, I will review..."} reward=1.0 done=false error=null
...
[END] success=true steps=5 score=0.94 rewards=[0.9, 1.0, 0.9, 1.0, 0.8]
```

---

## 📊 Baseline Results

| Task | Random Agent | Rule-Based | GPT-4o-mini | GPT-4o |
|---|---|---|---|---|
| Easy | 0.23 | 0.82 | **0.94** | **1.00** |
| Medium | 0.21 | 0.61 | **0.87** | **0.95** |
| Hard | 0.19 | 0.48 | **0.76** | **0.89** |
| **Average** | **0.21** | **0.64** | **0.86** | **0.95** |

---

## 🗂️ Project Structure

```
email_triage_env/
├── env/
│   ├── __init__.py
│   ├── models.py          # Pydantic models: Observation, Action, Reward
│   ├── environment.py     # Core env: reset(), step(), state()
│   └── tasks.py           # 3 tasks + grader functions
├── server/
│   ├── __init__.py
│   └── app.py             # FastAPI server
├── inference.py           # LLM agent runner
├── Dockerfile
├── requirements.txt
├── openenv.yaml
└── README.md
```

---

## 🔌 API Reference

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/health` | Health check |
| `POST` | `/reset` | Start a new episode (`{"task_name": "easy"}`) |
| `POST` | `/step` | Submit an action (`{"label": "spam", "optional_response": null}`) |
| `GET` | `/state` | Get full current episode state |

---

## 📝 License

MIT License. Built for the OpenEnv Hackathon.