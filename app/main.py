from html import escape
from typing import Optional

from fastapi import FastAPI, Header, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from app.environment import ENV_STORE
from app.models import Action
from app.tasks import list_tasks


app = FastAPI(title="InboxEnv", version="1.0.0")


class ResetRequest(BaseModel):
    task_id: str = "task_1"


def _session_id(header_value: Optional[str]) -> str:
    return header_value or "default"


def _render_json_block(payload: object) -> str:
    import json

    if payload is None:
        return "<span class='muted'>None</span>"
    return f"<pre>{escape(json.dumps(payload, indent=2))}</pre>"


@app.get("/", response_class=HTMLResponse)
def index(x_session_id: Optional[str] = Header(default=None)) -> HTMLResponse:
    env = ENV_STORE.get(_session_id(x_session_id))
    state = env.state()
    current_email = None if env.done else env.records[env.current_index]["email"].model_dump()
    last_action = env.last_action.model_dump() if env.last_action else None
    last_reward = env.last_reward.model_dump() if env.last_reward else None

    html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
      <meta charset="utf-8" />
      <meta http-equiv="refresh" content="5" />
      <meta name="viewport" content="width=device-width, initial-scale=1" />
      <title>InboxEnv Monitor</title>
      <style>
        :root {{
          color-scheme: dark;
          --bg: #0b1020;
          --panel: #11192f;
          --panel-alt: #16223f;
          --text: #e8edf8;
          --muted: #93a4c3;
          --accent: #72e0c4;
          --border: #243353;
        }}
        body {{
          margin: 0;
          font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, monospace;
          background: radial-gradient(circle at top, #172341 0%, var(--bg) 55%);
          color: var(--text);
        }}
        .wrap {{
          max-width: 1180px;
          margin: 0 auto;
          padding: 32px 20px 48px;
        }}
        h1 {{
          margin: 0 0 8px;
          font-size: 28px;
        }}
        .muted {{
          color: var(--muted);
        }}
        .grid {{
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
          gap: 16px;
          margin-top: 24px;
        }}
        .panel {{
          background: linear-gradient(180deg, var(--panel) 0%, var(--panel-alt) 100%);
          border: 1px solid var(--border);
          border-radius: 14px;
          padding: 18px;
          box-shadow: 0 14px 36px rgba(0, 0, 0, 0.25);
        }}
        .stat {{
          font-size: 24px;
          color: var(--accent);
          margin-top: 6px;
        }}
        pre {{
          margin: 0;
          white-space: pre-wrap;
          word-break: break-word;
          line-height: 1.45;
          font-size: 13px;
        }}
        .footer {{
          margin-top: 20px;
          color: var(--muted);
          font-size: 12px;
        }}
      </style>
    </head>
    <body>
      <div class="wrap">
        <h1>InboxEnv</h1>
        <div class="muted">Auto-refreshing every 5 seconds for session <strong>{escape(_session_id(x_session_id))}</strong>.</div>
        <div class="grid">
          <section class="panel">
            <div class="muted">Current Task</div>
            <div class="stat">{escape(state.task_id)}</div>
            <div class="muted">Progress: {state.emails_processed} processed / {state.inbox_remaining} remaining</div>
          </section>
          <section class="panel">
            <div class="muted">Cumulative Score</div>
            <div class="stat">{state.cumulative_score:.4f}</div>
            <div class="muted">Done: {str(state.done).lower()}</div>
          </section>
          <section class="panel">
            <div class="muted">Step Number</div>
            <div class="stat">{state.step_number}</div>
            <div class="muted">Environment state is kept in memory.</div>
          </section>
        </div>
        <div class="grid">
          <section class="panel">
            <div class="muted">Last Email Received</div>
            {_render_json_block(current_email)}
          </section>
          <section class="panel">
            <div class="muted">Last Action Taken</div>
            {_render_json_block(last_action)}
          </section>
          <section class="panel">
            <div class="muted">Last Reward</div>
            {_render_json_block(last_reward)}
          </section>
        </div>
        <div class="footer">Use <code>/reset</code>, <code>/step</code>, <code>/state</code>, <code>/tasks</code>, and <code>/health</code> for API access.</div>
      </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html, status_code=200)


@app.post("/reset")
def reset(request: ResetRequest, x_session_id: Optional[str] = Header(default=None)):
    try:
        env = ENV_STORE.get(_session_id(x_session_id))
        return env.reset(request.task_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.post("/step")
def step(action: Action, x_session_id: Optional[str] = Header(default=None)):
    try:
        env = ENV_STORE.get(_session_id(x_session_id))
        return env.step(action)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.get("/state")
def state(x_session_id: Optional[str] = Header(default=None)):
    env = ENV_STORE.get(_session_id(x_session_id))
    return env.state()


@app.get("/tasks")
def tasks():
    return {"tasks": list_tasks()}


@app.get("/health")
def health():
    return {"status": "ok"}
