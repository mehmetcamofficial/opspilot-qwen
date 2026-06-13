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
