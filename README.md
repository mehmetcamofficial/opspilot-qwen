# OpsPilot: Qwen-Powered Multi-Agent Incident Commander

OpsPilot is a production-oriented multi-agent incident response and remediation system built with Qwen Cloud and deployed on Alibaba Cloud.

## Hackathon Track

Primary Track: Autopilot Agent  
Secondary Strength: Agent Society-style multi-agent orchestration

## What It Does

OpsPilot ingests production alerts, investigates logs and metrics, retrieves runbooks, generates root-cause hypotheses, proposes remediation plans, applies risk and safety policies, requests human approval, simulates remediation, and generates postmortem reports.

## Architecture

- FastAPI backend
- Qwen-powered agent orchestration
- Mockable LLM fallback for stable demos
- Next.js dashboard frontend
- Alibaba Cloud ECS backend deployment
- Vercel frontend deployment

## Core Demo Scenario

Checkout API latency spike caused by cache configuration regression.

## License

MIT
