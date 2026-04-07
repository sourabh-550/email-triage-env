from dotenv import load_dotenv
load_dotenv()

"""
inference.py – Runs all 3 tasks of the Email Triage environment.
"""

import os
import json
import sys
import requests

# --- Safe OpenAI client setup ---
from openai import OpenAI

API_BASE_URL = os.environ.get("API_BASE_URL", "https://api.openai.com/v1")
MODEL_NAME   = os.environ.get("MODEL_NAME", "gpt-4o-mini")
HF_TOKEN     = os.environ.get("HF_TOKEN", "")
SERVER_URL   = os.environ.get("SERVER_URL", "http://localhost:7860")

_api_key = os.environ.get("OPENAI_API_KEY", HF_TOKEN or "sk-placeholder")

try:
    import httpx
    client = OpenAI(
        base_url=API_BASE_URL,
        api_key=_api_key,
        http_client=httpx.Client()
    )
except TypeError:
    client = OpenAI(
        base_url=API_BASE_URL,
        api_key=_api_key,
    )

TASKS = ["easy", "medium", "hard"]
ENV_NAME = "email_triage_env"

SYSTEM_PROMPT = """You are an expert email triage assistant. Your job is to classify each email and optionally draft a brief reply.

For each email, you must respond with ONLY a valid JSON object (no markdown, no explanation) in this exact format:
{
  "label": "<spam|important|promotion>",
  "optional_response": "<short reply string or null>"
}

Classification rules:
- "spam":      Unsolicited, fraudulent, phishing, or irrelevant bulk email.
- "important": Work-related, financial, operational, security, or time-sensitive email.
- "promotion": Marketing, newsletters, deals, subscriptions, or product offers.

Response rules:
- For "important" emails: always provide a short, professional optional_response (1-2 sentences).
- For "spam" or "promotion": set optional_response to null.
- Keep responses under 200 characters.
"""

def build_user_prompt(obs: dict) -> str:
    return f"""Email to classify:

From: {obs['sender']}
Subject: {obs['subject']}
Urgency: {obs['urgency']}
Body:
{obs['email_text']}

Previous action: {obs.get('previous_action') or 'None'}
Step: {obs['step_number'] + 1} of {obs['total_steps']}

Respond with JSON only."""


def call_agent(observation: dict) -> dict:
    """Call the LLM and parse its JSON action."""
    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": build_user_prompt(observation)},
            ],
            temperature=0.0,
            max_tokens=200,
        )
        raw = response.choices[0].message.content.strip()

        # Strip markdown fences if present
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        raw = raw.strip()

        action = json.loads(raw)

        # Validate label
        valid_labels = ["spam", "important", "promotion"]
        if action.get("label") not in valid_labels:
            action["label"] = "spam"

        return action

    except Exception as e:
        # Fallback action on any error
        return {"label": "spam", "optional_response": None}


def run_task(task_name: str) -> dict:
    print(f"[START] task={task_name} env={ENV_NAME} model={MODEL_NAME}")

    try:
        reset_resp = requests.post(
            f"{SERVER_URL}/reset",
            json={"task_name": task_name},
            timeout=30
        )
        reset_resp.raise_for_status()
        observation = reset_resp.json()
    except Exception as e:
        print(f"[END] success=false steps=0 score=0.001 rewards=[] error={str(e)!r}")
        return {"task": task_name, "success": False, "steps": 0, "score": 0.001, "rewards": []}

    step_num = 0
    all_rewards = []
    done = False
    success = True

    while not done:
        action = call_agent(observation)

        try:
            step_resp = requests.post(
                f"{SERVER_URL}/step",
                json=action,
                timeout=30
            )
            step_resp.raise_for_status()
            result = step_resp.json()
        except Exception as e:
            print(f"[STEP] step={step_num} action={json.dumps(action)} reward=0 done=true error={str(e)!r}")
            success = False
            break

        reward = result["reward"]["total"]
        done = result["done"]
        all_rewards.append(reward)

        print(
            f"[STEP] step={step_num} "
            f"action={json.dumps(action)} "
            f"reward={reward} "
            f"done={str(done).lower()} "
            f"error=null"
        )

        step_num += 1

        if not done and result.get("observation"):
            observation = result["observation"]

    _raw_score = sum(max(0, r) for r in all_rewards) / max(len(all_rewards), 1)
    # Clamp strictly within (0, 1) – validator requires score != 0.0 and != 1.0
    # NOTE: 1e-9 rounds to 0.0 at 4 d.p., so use 0.001 as the safe floor.
    total_score = round(max(0.001, min(0.999, _raw_score)), 4)
    if total_score <= 0.0:
        total_score = 0.001
    elif total_score >= 1.0:
        total_score = 0.999

    print(
        f"[END] success={str(success).lower()} "
        f"steps={step_num} "
        f"score={total_score} "
        f"rewards={json.dumps(all_rewards)}"
    )

    return {
        "task": task_name,
        "success": success,
        "steps": step_num,
        "score": total_score,
        "rewards": all_rewards,
    }


def main():
    print(f"=== Email Triage Inference ===")
    print(f"Server:  {SERVER_URL}")
    print(f"Model:   {MODEL_NAME}")
    print(f"API URL: {API_BASE_URL}")
    print()

    # Verify server is up
    try:
        h = requests.get(f"{SERVER_URL}/health", timeout=30)
        h.raise_for_status()
    except Exception as e:
        print(f"ERROR: Cannot reach server at {SERVER_URL} – {e}")
        sys.exit(1)

    results = []
    for task in TASKS:
        try:
            result = run_task(task)
            results.append(result)
        except Exception as e:
            print(f"ERROR in task {task}: {e}")
            results.append({"task": task, "success": False, "steps": 0, "score": 0.001, "rewards": []})
        print()

    print("=== SUMMARY ===")
    overall = round(sum(r["score"] for r in results) / len(results), 4)
    for r in results:
        status = "✓" if r["success"] else "✗"
        print(f"  {status} {r['task']:8s}  score={r['score']}  steps={r['steps']}")
    print(f"  Overall average score: {overall}")


if __name__ == "__main__":
    main()