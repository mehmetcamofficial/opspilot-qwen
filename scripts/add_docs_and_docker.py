from pathlib import Path

def write(path, content):
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content.strip() + "\n")

write("backend/Dockerfile", """
FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
""")

write("infra/alibaba/docker-compose.prod.yml", """
version: "3.9"

services:
  opspilot-backend:
    build:
      context: ../../backend
      dockerfile: Dockerfile
    container_name: opspilot-backend
    ports:
      - "8000:8000"
    environment:
      APP_NAME: "OpsPilot Backend"
      APP_ENV: "prod"
      APP_HOST: "0.0.0.0"
      APP_PORT: "8000"

      USE_MOCK_LLM: "true"
      FALLBACK_TO_MOCK_ON_ERROR: "true"

      QWEN_API_BASE: "${QWEN_API_BASE:-https://dashscope-intl.aliyuncs.com/compatible-mode/v1}"
      QWEN_API_KEY: "${QWEN_API_KEY:-replace_me}"
      QWEN_MODEL: "${QWEN_MODEL:-qwen-plus}"
    restart: unless-stopped
""")

write("docs/architecture.mmd", """
flowchart TD
    SRE[Human Operator / SRE] --> FE[Next.js OpsPilot Dashboard]
    FE --> API[FastAPI Backend API]
    API --> ORCH[Incident Orchestrator]

    ORCH --> TRIAGE[Triage Agent]
    ORCH --> OBS[Observability Agent]
    ORCH --> RUNBOOK[Runbook Retrieval Agent]
    ORCH --> HYPO[Hypothesis Agent]
    ORCH --> PLAN[Remediation Planner Agent]
    ORCH --> RISK[Risk & Safety Agent]
    ORCH --> APPROVAL[Approval Agent]
    ORCH --> EXEC[Remediation Executor]
    ORCH --> REVIEW[Execution Review Agent]
    ORCH --> POST[Postmortem Agent]

    TRIAGE --> QWEN[Qwen Cloud Model API]
    OBS --> QWEN
    RUNBOOK --> QWEN
    HYPO --> QWEN
    PLAN --> QWEN
    RISK --> QWEN
    APPROVAL --> QWEN
    REVIEW --> QWEN
    POST --> QWEN

    OBS --> METRICS[Metrics Tool]
    OBS --> LOGS[Logs Tool]
    OBS --> DEPLOY[Deployment History Tool]
    RUNBOOK --> RAG[Runbook and Prior Incident Retrieval]
    EXEC --> ACTION[Controlled Remediation Simulation]

    ORCH --> STATE[Incident State Store]
    ORCH --> AUDIT[Agent Timeline and Audit Trail]

    API -. planned deployment .-> ECS[Alibaba Cloud ECS]
    FE -. deployed .-> VERCEL[Vercel Frontend]
""")

write("docs/architecture.md", """
# OpsPilot Architecture

OpsPilot is a Qwen-powered multi-agent incident response and remediation system designed for the Global AI Hackathon with Qwen Cloud.

## Layers

1. Frontend Dashboard
- Next.js
- Vercel deployment
- Incident launch, agent timeline, evidence board, approval panel, remediation result, and postmortem view

2. Backend API
- FastAPI
- Designed for Alibaba Cloud ECS deployment with Docker
- REST API for incidents and approvals

3. Agent Orchestration
- Lightweight orchestrator
- Specialist agents
- Structured JSON outputs validated with Pydantic
- Audit-friendly timeline

4. Model and Tool Layer
- Qwen-compatible client
- Mock fallback while credits are pending
- Metrics, logs, deployment history, runbook retrieval, and remediation simulation tools

## Agent Workflow

1. Triage Agent
2. Observability Agent
3. Runbook Retrieval Agent
4. Hypothesis Agent
5. Remediation Planner Agent
6. Risk & Safety Agent
7. Approval Agent
8. Remediation Executor
9. Execution Review Agent
10. Postmortem Agent

## Safety Design

OpsPilot is not a blind automation bot.

- Production config changes require human approval.
- Risky database actions can be blocked.
- Every remediation has a rollback plan.
- Every decision is recorded in the agent timeline.
- Mock fallback prevents accidental Qwen API cost before credits are activated.

## Deployment Design

Current state:

- Frontend: Vercel
- Backend: local FastAPI
- Qwen integration: implemented with mock fallback

Planned state after credits:

- Backend: Alibaba Cloud ECS
- Frontend API URL: Alibaba Cloud backend URL
- Qwen mode: real Qwen Cloud API with fallback
""")

write("docs/alibaba-cloud-deployment-proof.md", """
# Alibaba Cloud Deployment Proof Plan

## Current Billing Position

We will not use pay-as-you-go resources before Qwen Cloud hackathon credits are activated.

The coupon request has been submitted and is under registration verification.

## Planned Deployment

Backend target:

- Alibaba Cloud ECS
- Docker Compose
- FastAPI backend on port 8000

## Deployment Files

- backend/Dockerfile
- infra/alibaba/docker-compose.prod.yml
- backend/app/services/qwen_client.py

## Proof Video Checklist

The proof video should show:

1. Alibaba Cloud ECS instance running.
2. SSH connection into the instance.
3. Repository cloned.
4. Docker Compose backend startup.
5. Healthcheck:

curl http://PUBLIC_ECS_IP:8000/health

Expected result:

{
  "status": "ok",
  "service": "OpsPilot Backend",
  "mock_llm": true
}

6. Incident workflow call.
7. Vercel environment variable updated:

NEXT_PUBLIC_API_BASE_URL=http://PUBLIC_ECS_IP:8000

8. Live Vercel frontend calling Alibaba Cloud backend.

## Real Qwen Mode

After credits are activated:

USE_MOCK_LLM=false
FALLBACK_TO_MOCK_ON_ERROR=true
QWEN_API_BASE=https://dashscope-intl.aliyuncs.com/compatible-mode/v1
QWEN_API_KEY=<activated_key>
QWEN_MODEL=qwen-plus
""")

write("docs/demo-script.md", """
# OpsPilot Demo Video Script

Target duration: about 3 minutes.

## 0:00–0:20 Problem

Production incidents are noisy, expensive, and high-pressure. OpsPilot turns scattered logs, metrics, deployments, runbooks, and human decisions into a structured incident response workflow.

## 0:20–0:40 Solution

OpsPilot is a Qwen-powered multi-agent incident commander. It triages alerts, analyzes observability evidence, retrieves runbooks, generates hypotheses, proposes remediation, applies safety policy, requests approval, executes controlled remediation, and generates a postmortem.

## 0:40–1:20 Start Incident

Click Start Demo Incident.

Scenario:

Checkout API latency is triggered after a recent cache configuration change. The system detects cache hit ratio drop, DB latency increase, and cache-miss fallback logs.

## 1:20–1:55 Agent Timeline

Show:

- Triage Agent
- Observability Agent
- Runbook Agent
- Hypothesis Agent
- Remediation Planner Agent
- Risk & Safety Agent
- Approval Agent

## 1:55–2:20 Human Approval

Show the approval card.

OpsPilot does not blindly change production. The Risk & Safety Agent requires human approval.

Click Approve Remediation.

## 2:20–2:45 Remediation and Review

Show:

- remediation_executor executed
- execution_review_agent completed
- status resolved

## 2:45–3:00 Postmortem

Show root cause, actions taken, what worked, missing safeguards, and follow-up items.

Closing line:

OpsPilot is not a chatbot for DevOps. It is a safety-aware multi-agent incident operations system that investigates, plans, escalates, and documents remediation workflows end-to-end.
""")

write("docs/submission-checklist.md", """
# OpsPilot Hackathon Submission Checklist

## Required Items

- [x] Public GitHub repository
- [x] Open source license
- [x] README
- [x] Working FastAPI backend locally
- [x] Qwen-compatible client implementation
- [x] Mock fallback for demo stability
- [x] Multi-agent orchestration
- [x] Next.js frontend dashboard
- [x] Vercel frontend deployment
- [x] Architecture documentation
- [x] Architecture diagram source
- [x] Dockerfile for backend
- [x] Alibaba Cloud deployment plan
- [ ] Alibaba Cloud backend deployment proof
- [ ] Demo video
- [ ] Devpost project description
- [ ] Qwen Cloud credits activated
- [ ] Real Qwen Cloud API mode tested

## Track

Primary:

Track 4: Autopilot Agent

Secondary strength:

Track 3-style multi-agent collaboration

## Demo Scenario

Checkout API latency spike after cache configuration regression.

## Final Checks

- [ ] Replace Vercel API URL with Alibaba Cloud backend URL.
- [ ] Record Alibaba Cloud backend proof video.
- [ ] Record 3-minute demo video.
- [ ] Add architecture image or Mermaid diagram to README.
- [ ] Verify repository license is visible.
- [ ] Verify README run instructions.
""")

print("Docs and Docker files added successfully.")
