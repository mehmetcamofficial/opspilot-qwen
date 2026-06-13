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
