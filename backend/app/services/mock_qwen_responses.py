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
