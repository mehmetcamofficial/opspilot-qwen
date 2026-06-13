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
