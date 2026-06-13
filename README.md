# OpsPilot: Qwen-Powered Multi-Agent Incident Commander

OpsPilot is a Qwen-powered multi-agent incident response and remediation system built for the Global AI Hackathon with Qwen Cloud.

It helps engineering and SRE teams investigate production incidents, reason over evidence, plan safe remediation, request human approval, execute controlled actions, and generate postmortems.

## Hackathon Track

Primary track: **Track 4: Autopilot Agent**

Secondary strength: **Track 3-style Agent Society**, because OpsPilot uses multiple specialized agents with separate responsibilities.

## Live Frontend

Frontend deployment:

https://opspilot-qwen.vercel.app

Note: The live Vercel frontend is deployed successfully. The backend currently runs locally until Alibaba Cloud/Qwen Cloud hackathon credits are activated. The production backend URL will later replace `NEXT_PUBLIC_API_BASE_URL`.

## Repository

https://github.com/mehmetcamofficial/opspilot-qwen

## Problem

Production incidents are noisy, high-pressure, and expensive.

During an incident, teams often need to manually inspect alerts, logs, metrics, deployment history, runbooks, prior incidents, remediation options, risk policies, and postmortem notes.

This creates delay, uncertainty, and operational risk.

## Solution

OpsPilot turns incident response into a structured multi-agent workflow.

It can:

* ingest an incident alert
* classify severity and blast radius
* analyze metrics, logs, and deployment history
* retrieve relevant runbooks and prior incidents
* generate ranked root-cause hypotheses
* propose remediation actions
* apply risk and safety policies
* request human approval for risky actions
* simulate controlled remediation
* compare before/after metrics
* generate a postmortem report

## Core Demo Scenario

The demo incident is:

**Checkout API latency spike after a cache configuration regression.**

The system detects:

* checkout latency increase
* cache hit ratio collapse
* database latency increase
* cache-miss fallback logs
* recent cache-related config change

OpsPilot concludes that the most likely root cause is a cache configuration regression and recommends a rollback with human approval.

## Agent Workflow

OpsPilot uses specialized agents:

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

Each agent returns structured JSON and contributes to an audit-friendly incident timeline.

## Qwen Cloud Usage

OpsPilot includes a Qwen-compatible client:

`backend/app/services/qwen_client.py`

The agent system is designed to call Qwen Cloud through an OpenAI-compatible chat completions interface.

Current safe demo mode:

`USE_MOCK_LLM=true`

`FALLBACK_TO_MOCK_ON_ERROR=true`

After Qwen Cloud hackathon credits are activated:

`USE_MOCK_LLM=false`

`FALLBACK_TO_MOCK_ON_ERROR=true`

`QWEN_API_BASE=https://dashscope-intl.aliyuncs.com/compatible-mode/v1`

`QWEN_API_KEY=<your_qwen_key>`

`QWEN_MODEL=qwen-plus`

Mock fallback is intentionally kept for demo stability and to avoid unintended charges before credits are available.

## Safety and Human Approval

OpsPilot is not a blind automation bot.

Safety principles:

* production configuration changes require human approval
* risky database actions can be blocked
* every remediation action includes a rollback plan
* every agent decision is recorded in the timeline
* evidence and uncertainty are separated
* low-confidence situations can be escalated

## Architecture

Architecture documentation:

* `docs/architecture.md`
* `docs/architecture.mmd`

Core components:

* Next.js dashboard frontend
* FastAPI backend
* agent orchestrator
* Qwen-compatible model client
* mock fallback layer
* metrics/logs/deployment/runbook tools
* approval and audit timeline
* planned Alibaba Cloud ECS deployment

## Local Development

### Backend

Run:

`cd backend`

`python3 -m venv .venv`

`source .venv/bin/activate`

`pip install -r requirements.txt`

`uvicorn app.main:app --reload`

Backend runs at:

`http://127.0.0.1:8000`

Swagger docs:

`http://127.0.0.1:8000/docs`

Healthcheck:

`curl http://127.0.0.1:8000/health`

### Frontend

Run:

`cd frontend`

`npm install`

`npm run dev`

Frontend runs at:

`http://localhost:3000`

Local frontend environment:

`NEXT_PUBLIC_API_BASE_URL=http://127.0.0.1:8000`

## Main API Endpoints

* `GET /health`
* `GET /`
* `POST /incidents`
* `GET /incidents`
* `GET /incidents/{incident_id}`
* `POST /incidents/{incident_id}/approve`

## Example Workflow

1. Open the dashboard.
2. Click **Start Demo Incident**.
3. Watch the agent timeline complete.
4. Review the evidence board and leading hypothesis.
5. Approve remediation.
6. See execution review and postmortem generation.

## Alibaba Cloud Deployment Plan

Deployment readiness files:

* `backend/Dockerfile`
* `infra/alibaba/docker-compose.prod.yml`
* `docs/alibaba-cloud-deployment-proof.md`

The backend will be deployed on Alibaba Cloud ECS after hackathon credits are activated.

No pay-as-you-go resources will be used before credits are available.

Planned proof:

* ECS instance running
* backend running through Docker
* public healthcheck endpoint
* public incident workflow endpoint
* Vercel frontend connected to Alibaba Cloud backend URL

## Demo Script

See:

`docs/demo-script.md`

## Submission Checklist

See:

`docs/submission-checklist.md`

## Current Status

Completed:

* public GitHub repository
* MIT license
* FastAPI backend
* Qwen-compatible client
* mock LLM fallback
* multi-agent orchestration
* incident approval workflow
* postmortem generation
* Next.js frontend
* Vercel frontend deployment
* Dockerfile
* Alibaba Cloud deployment plan
* architecture documentation

Pending:

* Qwen Cloud credits activation
* Alibaba Cloud ECS backend deployment
* deployment proof video
* final 3-minute demo video
* Devpost submission text

## License

MIT
