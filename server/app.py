"""
FastAPI server exposing the EmailTriageEnv as an OpenEnv-compatible REST API.

Endpoints:
  POST /reset        – Reset the environment (choose task)
  POST /step         – Submit an action and receive a reward
  GET  /state        – Get the current episode state
  GET  /health       – Health check
"""

import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# We need the env package on the path
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from env.environment import EmailTriageEnv
from env.models import Action, StepResult, EpisodeState, Observation


app = FastAPI(
    title="Email Triage OpenEnv",
    description="OpenEnv-compatible environment for email classification & triage.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global environment instance (single-session server)
_env: EmailTriageEnv | None = None


# ------------------------------------------------------------------
# Request / Response schemas
# ------------------------------------------------------------------

class ResetRequest(BaseModel):
    task_name: str = "easy"


class StepRequest(BaseModel):
    label: str
    optional_response: str | None = None


# ------------------------------------------------------------------
# Endpoints
# ------------------------------------------------------------------

@app.get("/health")
def health():
    return {"status": "ok", "env": "email_triage_env"}

@app.get("/")
def root():
    return {
        "name": "Email Triage OpenEnv",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "health": "/health",
            "docs": "/docs",
            "reset": "POST /reset",
            "step": "POST /step",
            "state": "GET /state"
        }
    }


from typing import Optional

@app.post("/reset", response_model=Observation)
def reset(request: Optional[ResetRequest] = None):
    global _env

    task_name = "easy"  # default

    if request and request.task_name:
        task_name = request.task_name

    valid = ["easy", "medium", "hard"]
    if task_name not in valid:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid task_name. Choose from {valid}",
        )

    _env = EmailTriageEnv(task_name=task_name)
    obs = _env.reset()
    return obs


@app.post("/step", response_model=StepResult)
def step(request: StepRequest):
    global _env
    if _env is None:
        raise HTTPException(status_code=400, detail="Environment not initialized. Call /reset first.")
    if _env.state().done:
        raise HTTPException(status_code=400, detail="Episode is done. Call /reset to start a new one.")

    valid_labels = ["spam", "important", "promotion"]
    if request.label not in valid_labels:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid label '{request.label}'. Choose from {valid_labels}",
        )

    action = Action(label=request.label, optional_response=request.optional_response)
    try:
        result = _env.step(action)
    except RuntimeError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return result


@app.get("/state", response_model=EpisodeState)
def state():
    global _env
    if _env is None:
        raise HTTPException(status_code=400, detail="Environment not initialized. Call /reset first.")
    return _env.state()


def main():
    import uvicorn
    uvicorn.run("server.app:app", host="0.0.0.0", port=7860)


if __name__ == "__main__":
    main()