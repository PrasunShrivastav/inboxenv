#!/usr/bin/env python3
"""
InboxEnv Baseline Inference Script
Uses OpenAI client to run an LLM agent against all 3 tasks.
"""

import json
import os
import sys
from typing import Any, Dict

import requests
from openai import OpenAI

# Config from environment variables
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:7860")
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-4o-mini")
HF_TOKEN = os.getenv("HF_TOKEN")
API_KEY = os.getenv("API_KEY", HF_TOKEN or "dummy")

try:
    llm_client = OpenAI(
        api_key=API_KEY,
        base_url=os.getenv("API_BASE_URL", "https://api.openai.com/v1")
    )
except Exception:
    llm_client = None

ENV_BASE_URL = "http://localhost:7860"

TASKS = ["task_1", "task_2", "task_3"]


def run_task(task_id: str) -> dict:
    # 1. Reset environment
    try:
        reset_resp = requests.post(f"{ENV_BASE_URL}/reset", json={"task_id": task_id}, timeout=30)
        reset_resp.raise_for_status()
        obs = reset_resp.json()
    except Exception:
        print(f"[STEP] task={task_id} step=0 email_id=error reward=0.0", flush=True)
        return {"task_id": task_id, "score": 0.0, "steps": 0, "rewards": []}

    task_scores = []
    step_num = 0
    done = False

    while not done:
        email = obs["observation"]["current_email"]
        task_desc = obs["observation"]["task_description"]

        # Build prompt for LLM
        prompt = build_prompt(email, task_desc, task_id)

        response = llm_client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert email triage assistant. Always respond with valid JSON.",
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.1,
            response_format={"type": "json_object"},
        )
        raw = response.choices[0].message.content
        action_dict = json.loads(raw)

        action_dict["email_id"] = email["id"]

        # Step environment
        try:
            step_resp = requests.post(f"{ENV_BASE_URL}/step", json=action_dict, timeout=30)
            step_resp.raise_for_status()
            result = step_resp.json()
        except Exception:
            print(f"[STEP] task={task_id} step={step_num} email_id=error reward=0.0", flush=True)
            break

        print(f"[STEP] task={task_id} step={step_num} email_id={email['id']} reward={result['reward']['value']}", flush=True)

        reward = result["reward"]["value"]
        task_scores.append(reward)
        done = result["done"]

        if not done:
            obs = {"observation": result["observation"]}

        step_num += 1

    avg_score = sum(task_scores) / len(task_scores) if task_scores else 0.0
    return {"task_id": task_id, "score": avg_score, "steps": step_num, "rewards": task_scores}


def build_prompt(email: dict, task_desc: str, task_id: str) -> str:
    # Build a clear prompt, instruct JSON output with all required fields
    # For task_3, instruct to include draft_response for urgent/high emails
    response_rule = (
        "Include a concise draft_response when the email should be treated as urgent or high priority."
        if task_id == "task_3"
        else "You may set draft_response to null because it is not required for this task."
    )
    return f"""
Task: {task_id}
Task description: {task_desc}

You are triaging one inbox email. Review the email carefully and decide:
1. priority: one of urgent, high, medium, low, spam
2. category: one of customer_support, billing, technical, sales, internal, spam
3. should_escalate: true or false
4. draft_response: string or null
5. reasoning: short explanation

{response_rule}

Return valid JSON only with exactly these keys:
priority, category, should_escalate, draft_response, reasoning

Email:
Subject: {email["subject"]}
Sender: {email["sender"]}
Timestamp: {email["timestamp"]}
Has attachment: {email["has_attachment"]}
Body:
{email["body"]}
""".strip()


def main():
    all_results = []

    print(f"[START] model={MODEL_NAME} tasks={','.join(TASKS)}", flush=True)

    for task_id in TASKS:
        try:
            result = run_task(task_id)
        except Exception as e:
            result = {"task_id": task_id, "score": 0.0, "steps": 0, "rewards": [], "error": str(e)}
        all_results.append(result)

    for r in all_results:
        print(f"[END] task={r['task_id']} score={r['score']:.4f} steps={r['steps']}", flush=True)


if __name__ == "__main__":
    try:
        main()
    except Exception:
        print(f"[END] task=all score=0.0 steps=0", flush=True)
        sys.exit(0)
