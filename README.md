---

title: Email Triage Env
emoji: 📧
colorFrom: blue
colorTo: green
sdk: docker
pinned: false
-------------

# 📧 Email Classification & Triage — OpenEnv Environment

[![OpenEnv](https://img.shields.io/badge/OpenEnv-compatible-blue)](https://openenv.ai)
[![Python](https://img.shields.io/badge/python-3.11-green)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111-teal)](https://fastapi.tiangolo.com)

---

## 🌍 Project Overview

Every knowledge worker processes dozens or even hundreds of emails daily. These decisions seem simple — *is this spam? does this need a reply? how urgent is it?* — but they actually require contextual reasoning, pattern recognition, and the ability to detect deception (such as phishing or fake authority emails).

**Email Triage** is an OpenEnv-compatible environment that simulates this real-world problem.
An AI agent processes emails one-by-one, classifies them, and optionally generates responses — just like a real intelligent inbox assistant.

---

## 🧠 Real-World Motivation

| Problem                        | How This Environment Models It                   |
| ------------------------------ | ------------------------------------------------ |
| Spam vs legitimate emails      | Includes scams, promotions, and real work emails |
| Phishing attacks               | CEO gift card scam and fake urgent requests      |
| Promotions vs important alerts | Mixed cases like LinkedIn vs bank alerts         |
| Urgency handling               | Critical alerts vs fake urgency marketing        |
| Fraud detection                | PayPal alerts, suspicious links                  |

---

## 📥 Observation Space

Each step returns an `Observation`:

| Field             | Type        | Description             |
| ----------------- | ----------- | ----------------------- |
| `email_id`        | string      | Unique identifier       |
| `email_text`      | string      | Full email body         |
| `sender`          | string      | Sender address          |
| `subject`         | string      | Email subject           |
| `urgency`         | enum        | `low`, `medium`, `high` |
| `previous_action` | string|null | Last action taken       |
| `step_number`     | int         | Current step            |
| `total_steps`     | int         | Total emails            |

---

## 🎮 Action Space

Agent returns:

| Field               | Type        | Description                        |
| ------------------- | ----------- | ---------------------------------- |
| `label`             | enum        | `spam`, `important`, `promotion`   |
| `optional_response` | string|null | Short reply (for important emails) |

---

## 🏆 Reward Design

Reward per step ranges from **−0.2 to 1.0**:

```
reward = classification_score + urgency_score + response_score
```

* **+0.7** → correct classification
* **+0.2** → correct urgency handling
* **+0.1** → good response (important emails)

Penalties:

* **−0.1** → unnecessary response
* **−0.2** → wrong/random response

Final score = normalized average across all steps.

---

## 📋 Task Descriptions

### 🟢 Easy (5 emails)

* Obvious spam detection
* Lottery scams, pharma spam
* Simple classification

---

### 🟡 Medium (6 emails)

* Promotions vs important
* Requires understanding intent
* Mixed real-world cases

---

### 🔴 Hard (7 emails)

* Ambiguous & deceptive emails
* Includes:

  * CEO phishing attack
  * Payment alerts
  * System warnings
  * Fake urgency promotions

---

## 📈 My Model Results (Groq - Llama 3.1)

Using a free OpenAI-compatible API (Groq):

| Task        | Score    |
| ----------- | -------- |
| Easy        | 0.90     |
| Medium      | 0.95     |
| Hard        | 0.77     |
| **Average** | **0.87** |

These results show that even lightweight open-source models can perform strongly on structured reasoning tasks.

---

## 🔍 Key Insight

During evaluation, the model misclassified a **CEO gift card phishing email** as important instead of spam.

This highlights a real-world limitation:

* Phishing emails mimic authority and urgency
* Even strong models can fail under deceptive patterns

This environment effectively tests such edge cases, making it highly practical for evaluating AI robustness.

---

## 🌐 Live Demo

* 🔗 API: https://sourabh5500-email-triage-env.hf.space
* 📄 Docs: https://sourabh5500-email-triage-env.hf.space/docs

---

## 🚀 Setup Instructions

### 🔹 Local Setup

```bash
git clone https://huggingface.co/spaces/your-username/email-triage-env
cd email-triage-env

pip install -r requirements.txt
uvicorn server.app:app --host 0.0.0.0 --port 7860 --reload
```

---

### 🔹 Docker

```bash
docker build -t email-triage-env .
docker run -p 7860:7860 email-triage-env
```

---

## 🤖 Running Inference

```bash
export OPENAI_API_KEY=your_key
export API_BASE_URL=https://api.groq.com/openai/v1
export MODEL_NAME=llama-3.1-8b-instant
export SERVER_URL=http://localhost:7860

python inference.py
```

---

## 🗂️ Project Structure

```
email_triage_env/
├── env/
│   ├── models.py
│   ├── environment.py
│   └── tasks.py
├── server/
│   └── app.py
├── inference.py
├── run.py
├── Dockerfile
├── requirements.txt
├── openenv.yaml
└── README.md
```

---

## 🔌 API Reference

| Method | Endpoint  | Description    |
| ------ | --------- | -------------- |
| GET    | `/health` | Health check   |
| POST   | `/reset`  | Start new task |
| POST   | `/step`   | Submit action  |
| GET    | `/state`  | Current state  |

---

## 📝 License

MIT License — built for OpenEnv Hackathon.
