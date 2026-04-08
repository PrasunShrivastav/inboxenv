## Submission

- HF Space URL: https://huggingface.co/spaces/PrasunPragya/inboxenv
- GitHub repo URL: N/A
- Baseline scores:
  - `task_1`: `0.845`
  - `task_2`: `0.7800`
  - `task_3`: `0.7432`
  - `total_score`: `0.7894`
- Team name: PP Waterballs

InboxEnv is a stateful OpenEnv-compatible email triage benchmark where an agent processes realistic inbox messages one at a time and must assign priority, classify category, decide whether to escalate, and, on the hardest task, draft appropriate responses for urgent and high-priority cases. The environment uses a deterministic synthetic dataset with hardcoded ground truth, dense per-step rewards, partial credit for near-miss priority judgments, and explicit penalties for dangerous behavior such as false-positive spam classification or missed escalations.
