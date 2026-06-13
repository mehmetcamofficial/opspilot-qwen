from pathlib import Path

def write(path: str, content: str):
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content.strip() + "\n")

write("backend/app/schemas/agents.py", r'''
from typing import List, Literal
from pydantic import BaseModel, Field

AgentStatus = Literal["success", "insufficient_evidence", "failed"]


class BaseAgentOutput(BaseModel):
    agent_name: str
    status: AgentStatus
    confidence: float = Field(ge=0, le=1)
    summary: str


class InitialHypothesis(BaseModel):
    title: str
    confidence: float = Field(ge=0, le=1)
    reason: str


class TriageAgentOutput(BaseAgentOutput):
    agent_name: Literal["triage_agent"]
    incident_type: Literal["latency", "error_rate", "availability", "dependency_failure", "deployment_regression", "data_integrity", "security_signal", "unknown"]
    severity: Literal["low", "medium", "high", "critical"]
    business_impact: str
    impacted_services: List[str]
    blast_radius: Literal["single_service", "multi_service", "customer_visible", "unknown"]
    initial_hypotheses: List[InitialHypothesis]
    recommended_next_steps: List[str]
    recommended_tools: List[str]
    handoff_agents: List[str]


class MetricAnomaly(BaseModel):
    metric_name: str
    baseline: float
    current: float
    direction: Literal["up", "down"]
    severity: Literal["low", "medium", "high"]
    interpretation: str


class LogFinding(BaseModel):
    pattern: str
    count: int
    severity: Literal["info", "warn", "error"]
    interpretation: str


class DeploymentFinding(BaseModel):
    timestamp: str
    event_type: Literal["deploy", "config_change", "rollback"]
    relevance: Literal["high", "medium", "low"]
    reason: str


class SuspectedSubsystem(BaseModel):
    name: str
    confidence: float = Field(ge=0, le=1)
    reason: str


class ObservabilityAgentOutput(BaseAgentOutput):
    agent_name: Literal["observability_agent"]
    metric_anomalies: List[MetricAnomaly]
    log_findings: List[LogFinding]
    deployment_findings: List[DeploymentFinding]
    suspected_subsystems: List[SuspectedSubsystem]
    evidence_strength: Literal["weak", "moderate", "strong"]
    open_questions: List[str]


class TopMatch(BaseModel):
    doc_id: str
    doc_type: Literal["runbook", "sop", "prior_incident"]
    title: str
    relevance: Literal["high", "medium", "low"]
    reason: str


class DiagnosticStep(BaseModel):
    step: str
    source_doc_id: str
    source_type: Literal["runbook", "sop", "prior_incident"]


class RemediationStep(BaseModel):
    step: str
    source_doc_id: str
    source_type: Literal["runbook", "sop", "prior_incident"]
    risk_level: Literal["low", "medium", "high"]


class RunbookAgentOutput(BaseAgentOutput):
    agent_name: Literal["runbook_agent"]
    top_matches: List[TopMatch]
    recommended_diagnostic_steps: List[DiagnosticStep]
    recommended_remediation_steps: List[RemediationStep]
    rollback_notes: List[str]
    operational_risks: List[str]
    gaps_or_missing_guidance: List[str]


class HypothesisItem(BaseModel):
    title: str
    confidence: float = Field(ge=0, le=1)
    likelihood_rank: int = Field(ge=1)
    supporting_evidence: List[str]
    contradicting_evidence: List[str]
    blast_radius_if_true: str
    next_validation_step: str


class LeadingHypothesis(BaseModel):
    title: str
    confidence: float = Field(ge=0, le=1)
    reason: str


class HypothesisAgentOutput(BaseAgentOutput):
    agent_name: Literal["hypothesis_agent"]
    hypotheses: List[HypothesisItem]
    leading_hypothesis: LeadingHypothesis
    unknowns: List[str]


class CandidateAction(BaseModel):
    action_id: str
    title: str
    action_type: Literal["inspect", "rollback_config", "restart_service", "scale_worker", "clear_cache", "feature_flag_change", "manual_escalation", "other"]
    priority_rank: int
    targets: List[str]
    rationale: str
    expected_impact: str
    preconditions: List[str]
    rollback_plan: List[str]
    estimated_risk: Literal["low", "medium", "high"]
    automation_suitability: Literal["auto", "approval_required", "manual_only"]


class MitigationVsFix(BaseModel):
    mitigation_action_ids: List[str]
    root_cause_fix_action_ids: List[str]


class RemediationPlannerAgentOutput(BaseAgentOutput):
    agent_name: Literal["remediation_planner_agent"]
    candidate_actions: List[CandidateAction]
    recommended_primary_action_id: str
    mitigation_vs_fix: MitigationVsFix


class ActionReview(BaseModel):
    action_id: str
    risk_score: float = Field(ge=0, le=1)
    risk_level: Literal["low", "medium", "high"]
    policy_decision: Literal["allow_auto", "require_approval", "block"]
    key_risk_factors: List[str]
    recommended_guardrails: List[str]
    reason: str


class RiskSafetyAgentOutput(BaseAgentOutput):
    agent_name: Literal["risk_safety_agent"]
    action_reviews: List[ActionReview]
    recommended_action_id: str


class ApprovalAgentOutput(BaseAgentOutput):
    agent_name: Literal["approval_agent"]
    approval_required: bool
    approval_title: str
    incident_summary: str
    leading_hypothesis: str
    proposed_action: str
    expected_impact: str
    risk_statement: str
    post_action_checks: List[str]
    operator_choices: List[Literal["approve", "reject", "request_more_data"]]


class MetricChange(BaseModel):
    metric_name: str
    before: float
    after: float
    interpretation: str


class ExecutionReviewAgentOutput(BaseAgentOutput):
    agent_name: Literal["execution_review_agent"]
    outcome: Literal["resolved", "improved", "unchanged", "worsened", "inconclusive"]
    metric_changes: List[MetricChange]
    resolution_confidence: float = Field(ge=0, le=1)
    recommended_next_step: str


class FollowUpItem(BaseModel):
    title: str
    priority: Literal["low", "medium", "high"]
    owner_role: str


class PostmortemAgentOutput(BaseAgentOutput):
    agent_name: Literal["postmortem_agent"]
    incident_title: str
    impact_summary: str
    root_cause_summary: str
    timeline_summary: List[str]
    actions_taken: List[str]
    what_worked: List[str]
    what_failed_or_was_missing: List[str]
    follow_up_items: List[FollowUpItem]
''')

write("backend/app/services/mock_qwen_responses.py", r'''
from typing import Any, Dict


def get_mock_response(system_prompt: str, user_payload: Dict[str, Any]) -> Dict[str, Any]:
    prompt = system_prompt.lower()

    if "agent_id:triage_agent" in prompt:
        return {
            "agent_name": "triage_agent",
            "status": "success",
            "incident_type": "latency",
            "severity": "high",
            "business_impact": "Customer checkout requests may be slowed or abandoned.",
            "impacted_services": ["checkout-api", "cache", "orders-db"],
            "blast_radius": "customer_visible",
            "initial_hypotheses": [
                {
                    "title": "Deployment-related cache configuration regression",
                    "confidence": 0.71,
                    "reason": "Latency spike coincides with cache degradation symptoms and recent configuration change."
                }
            ],
            "recommended_next_steps": [
                "Inspect checkout latency and error metrics.",
                "Retrieve recent deployment and configuration changes.",
                "Search runbooks for checkout latency and cache regression."
            ],
            "recommended_tools": ["metrics_tool", "logs_tool", "deployment_history_tool", "runbook_search_tool"],
            "handoff_agents": ["observability_agent", "runbook_agent", "hypothesis_agent"],
            "confidence": 0.83,
            "summary": "High-severity checkout latency incident; likely customer-visible and related to cache behavior."
        }

    if "agent_id:observability_agent" in prompt:
        return {
            "agent_name": "observability_agent",
            "status": "success",
            "metric_anomalies": [
                {
                    "metric_name": "checkout_p95_latency_ms",
                    "baseline": 420,
                    "current": 1820,
                    "direction": "up",
                    "severity": "high",
                    "interpretation": "Checkout latency increased more than 4x from baseline."
                },
                {
                    "metric_name": "cache_hit_ratio",
                    "baseline": 0.91,
                    "current": 0.24,
                    "direction": "down",
                    "severity": "high",
                    "interpretation": "Cache efficiency sharply degraded and may be driving database fallback traffic."
                },
                {
                    "metric_name": "db_query_latency_ms",
                    "baseline": 38,
                    "current": 210,
                    "direction": "up",
                    "severity": "medium",
                    "interpretation": "Database latency increased, likely secondary to cache degradation."
                }
            ],
            "log_findings": [
                {
                    "pattern": "cache_miss_fallback=db",
                    "count": 1842,
                    "severity": "warn",
                    "interpretation": "The service is frequently bypassing cache and hitting the database."
                },
                {
                    "pattern": "config_version=2026.07.10-rc3",
                    "count": 1260,
                    "severity": "info",
                    "interpretation": "Requests are consistently served under a newly deployed configuration version."
                }
            ],
            "deployment_findings": [
                {
                    "timestamp": "2026-07-09T23:56:00Z",
                    "event_type": "config_change",
                    "relevance": "high",
                    "reason": "Latency spike started shortly after this cache-related config change."
                }
            ],
            "suspected_subsystems": [
                {
                    "name": "cache_layer",
                    "confidence": 0.88,
                    "reason": "Cache hit ratio dropped sharply and logs show repeated DB fallback patterns."
                }
            ],
            "evidence_strength": "strong",
            "open_questions": [
                "Was the cache configuration changed intentionally?",
                "Did cache node health remain stable?"
            ],
            "confidence": 0.87,
            "summary": "Observability evidence strongly points to cache degradation following a recent configuration change."
        }

    if "agent_id:runbook_agent" in prompt:
        return {
            "agent_name": "runbook_agent",
            "status": "success",
            "top_matches": [
                {
                    "doc_id": "rb-017",
                    "doc_type": "runbook",
                    "title": "Checkout API Latency After Cache Regression",
                    "relevance": "high",
                    "reason": "Exact service and symptom match."
                },
                {
                    "doc_id": "pi-044",
                    "doc_type": "prior_incident",
                    "title": "Cache TTL Misconfiguration Caused DB Fallback Storm",
                    "relevance": "high",
                    "reason": "Similar cache degradation pattern led to database overload."
                }
            ],
            "recommended_diagnostic_steps": [
                {
                    "step": "Compare current cache configuration with the last known good version.",
                    "source_doc_id": "rb-017",
                    "source_type": "runbook"
                }
            ],
            "recommended_remediation_steps": [
                {
                    "step": "Rollback cache-related configuration to the previous known good version.",
                    "source_doc_id": "rb-017",
                    "source_type": "runbook",
                    "risk_level": "low"
                }
            ],
            "rollback_notes": [
                "If rollback increases error rate, restore current config and switch to degraded mode."
            ],
            "operational_risks": [
                "Increasing DB pool size without fixing cache behavior may only delay saturation."
            ],
            "gaps_or_missing_guidance": [
                "No explicit runbook guidance was found for partial regional impact."
            ],
            "confidence": 0.86,
            "summary": "Runbook evidence supports rolling back recent cache-related configuration changes."
        }

    if "agent_id:hypothesis_agent" in prompt:
        return {
            "agent_name": "hypothesis_agent",
            "status": "success",
            "hypotheses": [
                {
                    "title": "Cache configuration regression introduced in the latest config change",
                    "confidence": 0.86,
                    "likelihood_rank": 1,
                    "supporting_evidence": [
                        "Cache hit ratio dropped from 0.91 to 0.24.",
                        "Logs show repeated cache miss fallback to DB.",
                        "A cache-related config change occurred shortly before the latency spike.",
                        "Runbook rb-017 recommends rollback for this symptom pattern."
                    ],
                    "contradicting_evidence": [
                        "No direct cache node health failure has been observed."
                    ],
                    "blast_radius_if_true": "Customer-visible checkout slowdown and increased DB load.",
                    "next_validation_step": "Diff current cache config against previous known good version."
                },
                {
                    "title": "Database connection pool saturation independent of cache behavior",
                    "confidence": 0.42,
                    "likelihood_rank": 2,
                    "supporting_evidence": [
                        "DB query latency increased significantly."
                    ],
                    "contradicting_evidence": [
                        "Cache degradation can explain the DB load increase."
                    ],
                    "blast_radius_if_true": "Sustained checkout latency with possible spillover to order processing.",
                    "next_validation_step": "Inspect pool utilization and connection timeout events."
                }
            ],
            "leading_hypothesis": {
                "title": "Cache configuration regression introduced in the latest config change",
                "confidence": 0.86,
                "reason": "It best explains metrics, logs, deployment timing, and runbook guidance."
            },
            "unknowns": [
                "Whether TTL, routing, or key namespace changed.",
                "Whether cache node health remained stable."
            ],
            "confidence": 0.84,
            "summary": "The most likely root cause is a recent cache configuration regression."
        }

    if "agent_id:remediation_planner_agent" in prompt:
        return {
            "agent_name": "remediation_planner_agent",
            "status": "success",
            "candidate_actions": [
                {
                    "action_id": "act-001",
                    "title": "Rollback cache-related configuration to previous known good version",
                    "action_type": "rollback_config",
                    "priority_rank": 1,
                    "targets": ["checkout-api", "cache-config"],
                    "rationale": "This directly addresses the leading hypothesis and matches runbook guidance.",
                    "expected_impact": "Should restore cache hit ratio and reduce downstream DB latency.",
                    "preconditions": [
                        "Previous known good config version is available.",
                        "Rollback target is verified."
                    ],
                    "rollback_plan": [
                        "Re-apply current config if error rate increases.",
                        "Switch to degraded mode if rollback causes unexpected failures."
                    ],
                    "estimated_risk": "low",
                    "automation_suitability": "approval_required"
                },
                {
                    "action_id": "act-002",
                    "title": "Temporarily increase DB connection pool size",
                    "action_type": "other",
                    "priority_rank": 2,
                    "targets": ["orders-db"],
                    "rationale": "May temporarily relieve pressure but does not address likely root cause.",
                    "expected_impact": "Could reduce immediate queuing pressure.",
                    "preconditions": ["DB capacity headroom is available."],
                    "rollback_plan": ["Restore previous pool size after primary issue is resolved."],
                    "estimated_risk": "medium",
                    "automation_suitability": "manual_only"
                }
            ],
            "recommended_primary_action_id": "act-001",
            "mitigation_vs_fix": {
                "mitigation_action_ids": ["act-002"],
                "root_cause_fix_action_ids": ["act-001"]
            },
            "confidence": 0.83,
            "summary": "The safest primary action is to rollback the recent cache-related configuration."
        }

    if "agent_id:risk_safety_agent" in prompt:
        return {
            "agent_name": "risk_safety_agent",
            "status": "success",
            "action_reviews": [
                {
                    "action_id": "act-001",
                    "risk_score": 0.41,
                    "risk_level": "medium",
                    "policy_decision": "require_approval",
                    "key_risk_factors": [
                        "Production configuration change",
                        "Potential short-lived service instability during rollback"
                    ],
                    "recommended_guardrails": [
                        "Require operator approval",
                        "Verify rollback target hash",
                        "Monitor latency and error rate for 5 minutes"
                    ],
                    "reason": "Reversible and runbook-aligned, but production config changes require human approval."
                },
                {
                    "action_id": "act-002",
                    "risk_score": 0.67,
                    "risk_level": "high",
                    "policy_decision": "block",
                    "key_risk_factors": [
                        "May mask the primary issue",
                        "May increase DB pressure"
                    ],
                    "recommended_guardrails": [
                        "Only reconsider after direct DB saturation evidence is confirmed."
                    ],
                    "reason": "Higher operational risk and weaker evidence basis."
                }
            ],
            "recommended_action_id": "act-001",
            "confidence": 0.88,
            "summary": "Cache config rollback is acceptable with human approval; DB pool action is blocked."
        }

    if "agent_id:approval_agent" in prompt:
        return {
            "agent_name": "approval_agent",
            "status": "success",
            "approval_required": True,
            "approval_title": "Approve rollback of cache-related production configuration",
            "incident_summary": "Checkout latency increased sharply and appears customer-visible.",
            "leading_hypothesis": "A cache configuration regression is causing cache misses and downstream database load.",
            "proposed_action": "Rollback cache-related configuration for checkout-api.",
            "expected_impact": "Cache hit ratio should recover and checkout latency should drop within minutes.",
            "risk_statement": "This is a reversible production config change and requires operator approval.",
            "post_action_checks": [
                "Monitor checkout p95 latency",
                "Monitor cache hit ratio recovery",
                "Watch for error-rate increase"
            ],
            "operator_choices": ["approve", "reject", "request_more_data"],
            "confidence": 0.9,
            "summary": "Approval brief prepared for production cache configuration rollback."
        }

    if "agent_id:execution_review_agent" in prompt:
        return {
            "agent_name": "execution_review_agent",
            "status": "success",
            "outcome": "improved",
            "metric_changes": [
                {
                    "metric_name": "checkout_p95_latency_ms",
                    "before": 1820,
                    "after": 640,
                    "interpretation": "Latency improved substantially."
                },
                {
                    "metric_name": "cache_hit_ratio",
                    "before": 0.24,
                    "after": 0.81,
                    "interpretation": "Cache performance recovered significantly."
                }
            ],
            "resolution_confidence": 0.84,
            "recommended_next_step": "Continue monitoring for 10 minutes.",
            "confidence": 0.84,
            "summary": "Rollback substantially improved the incident and supports the cache regression hypothesis."
        }

    if "agent_id:postmortem_agent" in prompt:
        return {
            "agent_name": "postmortem_agent",
            "status": "success",
            "incident_title": "Checkout latency spike after cache configuration change",
            "impact_summary": "Customers experienced elevated checkout latency and increased downstream database load.",
            "root_cause_summary": "The most likely root cause was a cache configuration regression introduced shortly before the incident.",
            "timeline_summary": [
                "Alert triggered for elevated checkout latency.",
                "Observability analysis identified cache hit ratio collapse.",
                "Matching runbook and similar prior incident were retrieved.",
                "Rollback was proposed and approved.",
                "Rollback executed and metrics improved."
            ],
            "actions_taken": [
                "Retrieved metrics, logs, deployment history, and runbooks.",
                "Generated ranked root-cause hypotheses.",
                "Rolled back cache-related configuration after approval.",
                "Reviewed post-action metric recovery."
            ],
            "what_worked": [
                "Runbook retrieval surfaced the correct remediation quickly.",
                "Approval-gated rollback enabled safe response.",
                "Post-action review confirmed improvement."
            ],
            "what_failed_or_was_missing": [
                "Cache config change was not flagged before deployment.",
                "No dedicated alert existed for sudden cache hit ratio collapse."
            ],
            "follow_up_items": [
                {
                    "title": "Add deployment guardrails for cache-related production config changes",
                    "priority": "high",
                    "owner_role": "platform_engineering"
                },
                {
                    "title": "Create targeted alert for cache hit ratio degradation",
                    "priority": "high",
                    "owner_role": "sre"
                }
            ],
            "confidence": 0.88,
            "summary": "The incident was likely caused by cache config regression and mitigated with approval-gated rollback."
        }

    return {
        "agent_name": "unknown_agent",
        "status": "failed",
        "confidence": 0.0,
        "summary": "No mock response available for this agent."
    }
''')

write("backend/app/services/qwen_client.py", r'''
import json
import logging
from typing import Any, Dict

import httpx

from app.core.config import settings
from app.services.mock_qwen_responses import get_mock_response

logger = logging.getLogger(__name__)


class QwenClient:
    def __init__(self) -> None:
        self.api_base = settings.QWEN_API_BASE
        self.api_key = settings.QWEN_API_KEY
        self.model = settings.QWEN_MODEL
        self.use_mock = settings.USE_MOCK_LLM
        self.fallback_to_mock = settings.FALLBACK_TO_MOCK_ON_ERROR

    async def generate_json(self, system_prompt: str, user_payload: Dict[str, Any]) -> Dict[str, Any]:
        if self.use_mock:
            return get_mock_response(system_prompt, user_payload)

        try:
            return await self._generate_json_from_qwen(system_prompt, user_payload)
        except Exception as exc:
            logger.exception("Qwen API call failed.")
            if self.fallback_to_mock:
                return get_mock_response(system_prompt, user_payload)
            raise exc

    async def _generate_json_from_qwen(self, system_prompt: str, user_payload: Dict[str, Any]) -> Dict[str, Any]:
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": json.dumps(user_payload)}
            ],
            "response_format": {"type": "json_object"}
        }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{self.api_base}/chat/completions",
                headers=headers,
                json=payload
            )
            response.raise_for_status()

        data = response.json()
        content = data.get("choices", [{}])[0].get("message", {}).get("content")

        if content is None:
            raise ValueError("Qwen response did not contain choices[0].message.content")

        if isinstance(content, dict):
            return content

        return json.loads(content)
''')

write("backend/app/agents/base.py", r'''
from abc import ABC, abstractmethod
from typing import Any, Dict


class BaseAgent(ABC):
    name: str = "base_agent"
    system_prompt: str = ""

    @abstractmethod
    async def run(self, payload: Dict[str, Any]) -> Any:
        raise NotImplementedError
''')

agents = {
    "triage_agent.py": ("TriageAgent", "TriageAgentOutput", "triage_agent", "Interpret an incoming alert and produce a structured triage decision."),
    "observability_agent.py": ("ObservabilityAgent", "ObservabilityAgentOutput", "observability_agent", "Analyze metrics, logs, and deployment history for incident evidence."),
    "runbook_agent.py": ("RunbookAgent", "RunbookAgentOutput", "runbook_agent", "Retrieve and summarize relevant runbooks and prior incidents."),
    "hypothesis_agent.py": ("HypothesisAgent", "HypothesisAgentOutput", "hypothesis_agent", "Generate ranked root-cause hypotheses based on evidence."),
    "remediation_planner_agent.py": ("RemediationPlannerAgent", "RemediationPlannerAgentOutput", "remediation_planner_agent", "Produce safe remediation options with rollback plans."),
    "risk_safety_agent.py": ("RiskSafetyAgent", "RiskSafetyAgentOutput", "risk_safety_agent", "Assess remediation actions for operational safety and policy compliance."),
    "approval_agent.py": ("ApprovalAgent", "ApprovalAgentOutput", "approval_agent", "Prepare a concise approval brief for a human operator."),
    "execution_review_agent.py": ("ExecutionReviewAgent", "ExecutionReviewAgentOutput", "execution_review_agent", "Evaluate observed outcome after remediation."),
    "postmortem_agent.py": ("PostmortemAgent", "PostmortemAgentOutput", "postmortem_agent", "Create a concise incident postmortem report.")
}

for filename, (class_name, model_name, agent_id, description) in agents.items():
    write(f"backend/app/agents/{filename}", f'''
from typing import Any, Dict

from app.agents.base import BaseAgent
from app.schemas.agents import {model_name}
from app.services.qwen_client import QwenClient


SYSTEM_PROMPT = """
AGENT_ID:{agent_id}

You are {class_name} in OpsPilot.

Task:
{description}

Rules:
- Use only the supplied evidence.
- Be conservative and operationally safe.
- Return strict JSON matching the required schema.
- Do not include markdown.
- Do not include extra keys.
"""


class {class_name}(BaseAgent):
    name = "{agent_id}"
    system_prompt = SYSTEM_PROMPT

    def __init__(self, qwen_client: QwenClient) -> None:
        self.qwen_client = qwen_client

    async def run(self, payload: Dict[str, Any]) -> {model_name}:
        raw = await self.qwen_client.generate_json(self.system_prompt, payload)
        return {model_name}.model_validate(raw)
''')

write("backend/app/tools/metrics_tool.py", r'''
async def get_metrics(service: str, environment: str, time_window_minutes: int = 30) -> dict:
    return {
        "series": [
            {"metric_name": "checkout_p95_latency_ms", "baseline": 420, "current": 1820, "trend": "up", "unit": "ms"},
            {"metric_name": "cache_hit_ratio", "baseline": 0.91, "current": 0.24, "trend": "down", "unit": "ratio"},
            {"metric_name": "db_query_latency_ms", "baseline": 38, "current": 210, "trend": "up", "unit": "ms"}
        ]
    }
''')

write("backend/app/tools/logs_tool.py", r'''
async def get_logs(service: str, environment: str, time_window_minutes: int = 30) -> dict:
    return {
        "top_patterns": [
            {"pattern": "cache_miss_fallback=db", "count": 1842, "severity": "warn"},
            {"pattern": "config_version=2026.07.10-rc3", "count": 1260, "severity": "info"}
        ]
    }
''')

write("backend/app/tools/deployment_history_tool.py", r'''
async def get_deployment_history(service: str, environment: str) -> dict:
    return {
        "events": [
            {
                "timestamp": "2026-07-09T23:56:00Z",
                "type": "config_change",
                "service": service,
                "description": "Updated cache TTL and namespace routing config"
            }
        ]
    }
''')

write("backend/app/tools/runbook_search_tool.py", r'''
async def search_runbooks(service: str, environment: str, symptoms: list[str]) -> dict:
    return {
        "retrieved_documents": [
            {
                "doc_id": "rb-017",
                "doc_type": "runbook",
                "title": "Checkout API Latency After Cache Regression",
                "service": service,
                "environment": environment,
                "similarity_score": 0.94,
                "content_excerpt": "Compare current cache config to last known good version and rollback if hit ratio collapses."
            },
            {
                "doc_id": "pi-044",
                "doc_type": "prior_incident",
                "title": "Cache TTL Misconfiguration Caused DB Fallback Storm",
                "service": service,
                "environment": environment,
                "similarity_score": 0.89,
                "content_excerpt": "Cache hit ratio collapse triggered DB fallback; rollback restored stability."
            }
        ]
    }
''')

write("backend/app/tools/remediation_executor.py", r'''
from datetime import datetime, UTC


async def execute_action(action_id: str, title: str) -> dict:
    return {
        "action_id": action_id,
        "title": title,
        "status": "executed",
        "executed_at": datetime.now(UTC).isoformat()
    }
''')

write("backend/app/services/orchestrator.py", r'''
import uuid
from typing import Any, Dict

from app.agents.triage_agent import TriageAgent
from app.agents.observability_agent import ObservabilityAgent
from app.agents.runbook_agent import RunbookAgent
from app.agents.hypothesis_agent import HypothesisAgent
from app.agents.remediation_planner_agent import RemediationPlannerAgent
from app.agents.risk_safety_agent import RiskSafetyAgent
from app.agents.approval_agent import ApprovalAgent
from app.agents.execution_review_agent import ExecutionReviewAgent
from app.agents.postmortem_agent import PostmortemAgent
from app.services.qwen_client import QwenClient
from app.tools.metrics_tool import get_metrics
from app.tools.logs_tool import get_logs
from app.tools.deployment_history_tool import get_deployment_history
from app.tools.runbook_search_tool import search_runbooks
from app.tools.remediation_executor import execute_action


class IncidentOrchestrator:
    def __init__(self) -> None:
        self.qwen_client = QwenClient()

        self.triage_agent = TriageAgent(self.qwen_client)
        self.observability_agent = ObservabilityAgent(self.qwen_client)
        self.runbook_agent = RunbookAgent(self.qwen_client)
        self.hypothesis_agent = HypothesisAgent(self.qwen_client)
        self.remediation_planner_agent = RemediationPlannerAgent(self.qwen_client)
        self.risk_safety_agent = RiskSafetyAgent(self.qwen_client)
        self.approval_agent = ApprovalAgent(self.qwen_client)
        self.execution_review_agent = ExecutionReviewAgent(self.qwen_client)
        self.postmortem_agent = PostmortemAgent(self.qwen_client)

        self.incident_store: dict[str, dict[str, Any]] = {}

    async def create_incident(self, alert_payload: Dict[str, Any]) -> Dict[str, Any]:
        incident_id = f"inc-{uuid.uuid4().hex[:8]}"
        state: Dict[str, Any] = {
            "incident_id": incident_id,
            "status": "triaging",
            "alert": alert_payload,
            "agent_timeline": []
        }

        triage_result = await self.triage_agent.run({
            "incident_id": incident_id,
            "alert": alert_payload
        })
        state["triage_result"] = triage_result.model_dump()
        state["agent_timeline"].append({"agent": "triage_agent", "status": "completed"})

        service = alert_payload["service"]
        environment = alert_payload["environment"]
        symptoms = alert_payload.get("observed_signals", [])

        metrics_result = await get_metrics(service, environment)
        logs_result = await get_logs(service, environment)
        deployment_result = await get_deployment_history(service, environment)
        runbook_search_result = await search_runbooks(service, environment, symptoms)

        observability_result = await self.observability_agent.run({
            "incident_id": incident_id,
            "service": service,
            "environment": environment,
            "time_window_minutes": 30,
            "metrics_tool_result": metrics_result,
            "logs_tool_result": logs_result,
            "deployment_history_result": deployment_result
        })
        state["observability_result"] = observability_result.model_dump()
        state["agent_timeline"].append({"agent": "observability_agent", "status": "completed"})

        runbook_result = await self.runbook_agent.run({
            "incident_id": incident_id,
            "query_context": {
                "service": service,
                "environment": environment,
                "incident_type": triage_result.incident_type,
                "symptoms": symptoms
            },
            "retrieved_documents": runbook_search_result["retrieved_documents"]
        })
        state["runbook_result"] = runbook_result.model_dump()
        state["agent_timeline"].append({"agent": "runbook_agent", "status": "completed"})

        hypothesis_result = await self.hypothesis_agent.run({
            "incident_id": incident_id,
            "triage_result": triage_result.model_dump(),
            "observability_result": observability_result.model_dump(),
            "runbook_result": runbook_result.model_dump()
        })
        state["hypothesis_result"] = hypothesis_result.model_dump()
        state["agent_timeline"].append({"agent": "hypothesis_agent", "status": "completed"})

        remediation_plan = await self.remediation_planner_agent.run({
            "incident_id": incident_id,
            "hypothesis_result": hypothesis_result.model_dump(),
            "runbook_result": runbook_result.model_dump(),
            "observability_result": observability_result.model_dump()
        })
        state["remediation_plan"] = remediation_plan.model_dump()
        state["agent_timeline"].append({"agent": "remediation_planner_agent", "status": "completed"})

        risk_review = await self.risk_safety_agent.run({
            "incident_id": incident_id,
            "environment": environment,
            "policy_rules": [
                {
                    "rule_id": "prod-config-change",
                    "description": "Production config changes require approval",
                    "applies_to_action_type": "rollback_config",
                    "decision": "require_approval"
                },
                {
                    "rule_id": "db-risky",
                    "description": "Risky DB changes are blocked by default",
                    "applies_to_action_type": "other",
                    "decision": "block"
                }
            ],
            "candidate_actions": [a.model_dump() for a in remediation_plan.candidate_actions]
        })
        state["risk_review"] = risk_review.model_dump()
        state["agent_timeline"].append({"agent": "risk_safety_agent", "status": "completed"})

        recommended_action = next(
            a for a in remediation_plan.candidate_actions
            if a.action_id == risk_review.recommended_action_id
        )

        selected_review = next(
            r for r in risk_review.action_reviews
            if r.action_id == risk_review.recommended_action_id
        )

        approval_brief = await self.approval_agent.run({
            "incident_id": incident_id,
            "triage_result": triage_result.model_dump(),
            "hypothesis_result": hypothesis_result.model_dump(),
            "recommended_action": recommended_action.model_dump(),
            "risk_review": selected_review.model_dump()
        })
        state["approval_brief"] = approval_brief.model_dump()
        state["agent_timeline"].append({"agent": "approval_agent", "status": "approval_required"})

        state["status"] = "awaiting_approval"
        self.incident_store[incident_id] = state
        return state

    async def approve_and_execute(self, incident_id: str) -> Dict[str, Any]:
        state = self.incident_store[incident_id]

        plan = state["remediation_plan"]
        risk = state["risk_review"]
        action_id = risk["recommended_action_id"]
        action = next(a for a in plan["candidate_actions"] if a["action_id"] == action_id)

        execution = await execute_action(action["action_id"], action["title"])
        state["executed_action"] = execution
        state["status"] = "monitoring"
        state["agent_timeline"].append({"agent": "remediation_executor", "status": "executed"})

        execution_review = await self.execution_review_agent.run({
            "incident_id": incident_id,
            "executed_action": execution,
            "before_metrics": [
                {"metric_name": "checkout_p95_latency_ms", "value": 1820},
                {"metric_name": "cache_hit_ratio", "value": 0.24}
            ],
            "after_metrics": [
                {"metric_name": "checkout_p95_latency_ms", "value": 640},
                {"metric_name": "cache_hit_ratio", "value": 0.81}
            ]
        })
        state["execution_review"] = execution_review.model_dump()
        state["agent_timeline"].append({"agent": "execution_review_agent", "status": "completed"})

        postmortem = await self.postmortem_agent.run({
            "incident_id": incident_id,
            "incident_record": {
                "title": state["alert"]["name"],
                "service": state["alert"]["service"],
                "severity": state["triage_result"]["severity"],
                "started_at": state["alert"]["triggered_at"],
                "resolved_at": execution["executed_at"],
                "hypothesis_result": state["hypothesis_result"],
                "executed_actions": [execution],
                "execution_review": state["execution_review"]
            }
        })
        state["postmortem"] = postmortem.model_dump()
        state["agent_timeline"].append({"agent": "postmortem_agent", "status": "completed"})

        state["status"] = "resolved"
        self.incident_store[incident_id] = state
        return state

    def get_incident(self, incident_id: str) -> Dict[str, Any]:
        return self.incident_store[incident_id]

    def list_incidents(self) -> list[Dict[str, Any]]:
        return list(self.incident_store.values())
''')

write("backend/app/services/incident_service.py", r'''
from app.services.orchestrator import IncidentOrchestrator

orchestrator = IncidentOrchestrator()
''')

write("backend/app/api/routes/incidents.py", r'''
from fastapi import APIRouter, HTTPException

from app.schemas.incidents import CreateIncidentRequest
from app.services.incident_service import orchestrator

router = APIRouter(prefix="/incidents", tags=["incidents"])


@router.post("")
async def create_incident(request: CreateIncidentRequest):
    state = await orchestrator.create_incident(request.alert.model_dump())
    return {
        "incident_id": state["incident_id"],
        "status": state["status"],
        "state": state
    }


@router.get("")
async def list_incidents():
    return orchestrator.list_incidents()


@router.get("/{incident_id}")
async def get_incident(incident_id: str):
    try:
        return orchestrator.get_incident(incident_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="Incident not found")


@router.post("/{incident_id}/approve")
async def approve_incident(incident_id: str):
    try:
        return await orchestrator.approve_and_execute(incident_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="Incident not found")
''')

print("OpsPilot multi-agent mock workflow added.")
