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

        # Idempotency guard: if this incident is already resolved,
        # do not execute remediation or postmortem generation again.
        if state.get("status") == "resolved" and state.get("postmortem"):
            return state

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
