"""
inference.py – Runs all 3 tasks of the Email Triage environment using an
OpenAI-compatible LLM client against the live FastAPI server.

Environment variables:
  API_BASE_URL   – Base URL of the OpenAI-compatible API  (default: https://api.openai.com/v1)
  MODEL_NAME     – Model name to use                       (default: gpt-4o-mini)
  HF_TOKEN       – Hugging Face token (unused here, kept for OpenEnv compatibility)

Logging format (strict):
  [START] task=... env=... model=...
  [STEP]  step=... action=... reward=... done=... error=null
  [END]   success=... steps=... score=... rewards=...
"""
from dotenv import load_dotenv
load_dotenv()   # loads .env file automatically

import os
import json
import sys
import requests
from openai import OpenAI

# ------------------------------------------------------------------
# Configuration
# ------------------------------------------------------------------

API_BASE_URL = os.environ.get("API_BASE_URL", "https://api.openai.com/v1")
MODEL_NAME = os.environ.get("MODEL_NAME", "gpt-4o-mini")
HF_TOKEN = os.environ.get("HF_TOKEN", "")
SERVER_URL = os.environ.get("SERVER_URL", "http://localhost:7860")

client = OpenAI(base_url=API_BASE_URL, api_key=os.environ.get("OPENAI_API_KEY", HF_TOKEN or "sk-placeholder"))

TASKS = ["easy", "medium", "hard"]

ENV_NAME = "email_triage_env"


# ------------------------------------------------------------------
# Prompt template
# ------------------------------------------------------------------

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


# ------------------------------------------------------------------
# Agent call
# ------------------------------------------------------------------

def call_agent(observation: dict) -> dict:
    """Call the LLM and parse its JSON action."""
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


# ------------------------------------------------------------------
# Run one task
# ------------------------------------------------------------------

def run_task(task_name: str) -> dict:
    print(f"[START] task={task_name} env={ENV_NAME} model={MODEL_NAME}")

    # Reset the environment
    reset_resp = requests.post(f"{SERVER_URL}/reset", json={"task_name": task_name})
    reset_resp.raise_for_status()
    observation = reset_resp.json()

    step_num = 0
    all_rewards = []
    done = False
    success = True

    while not done:
        try:
            action = call_agent(observation)
        except Exception as e:
            print(f"[STEP] step={step_num} action=null reward=0 done=false error={str(e)!r}")
            # Fallback action
            action = {"label": "spam", "optional_response": None}
            success = False

        # Submit action to environment
        try:
            step_resp = requests.post(
                f"{SERVER_URL}/step",
                json=action,
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

    # Final score
    total_score = round(sum(max(0, r) for r in all_rewards) / max(len(all_rewards), 1), 4)

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


# ------------------------------------------------------------------
# Main
# ------------------------------------------------------------------

def main():
    print(f"=== Email Triage Inference ===")
    print(f"Server:  {SERVER_URL}")
    print(f"Model:   {MODEL_NAME}")
    print(f"API URL: {API_BASE_URL}")
    print()

    # Verify server is up
    try:
        h = requests.get(f"{SERVER_URL}/health", timeout=10)
        h.raise_for_status()
    except Exception as e:
        print(f"ERROR: Cannot reach server at {SERVER_URL} – {e}")
        sys.exit(1)

    results = []
    for task in TASKS:
        result = run_task(task)
        results.append(result)
        print()

    # Summary
    print("=== SUMMARY ===")
    overall = round(sum(r["score"] for r in results) / len(results), 4)
    for r in results:
        status = "✓" if r["success"] else "✗"
        print(f"  {status} {r['task']:8s}  score={r['score']}  steps={r['steps']}")
    print(f"  Overall average score: {overall}")


if __name__ == "__main__":
    main()