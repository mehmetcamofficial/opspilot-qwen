"use client";

import { useEffect, useRef, useState } from "react";
import { PlatformShell } from "@/components/PlatformShell";
import { IncidentCard } from "@/components/IncidentCard";
import { IncidentTable } from "@/components/IncidentTable";
import { OnboardingFlow } from "@/components/OnboardingFlow";
import { PrintIncidentReport } from "@/components/PrintIncidentReport";
import { RealtimeIndicator } from "@/components/RealtimeIndicator";
import { StatusBadge } from "@/components/StatusBadge";
import { TimelineRail } from "@/components/TimelineRail";
import { ConfirmDialog } from "@/components/ui/ConfirmDialog";
import { EmptyState } from "@/components/ui/EmptyState";
import { Icon } from "@/components/ui/Icon";
import { InlineError } from "@/components/ui/InlineError";
import { LoadingSkeleton } from "@/components/ui/LoadingSkeleton";
import { ToastStack, type ToastMessage, type ToastTone } from "@/components/ui/ToastStack";
import { Tooltip } from "@/components/ui/Tooltip";
import { BodyText, LabelText, PageTitle, SectionTitle } from "@/components/ui/Typography";
import { addIncidentTimelineEvent, alertStreamUrl, approveIncident, assignIncident, createIncident, createIncidentFromAlert, getIncidentAiInsights, getIncidentTimeline, healthcheck, listAlerts, listIncidents } from "@/lib/api";
import { useLanguage, type Language } from "@/lib/language";
import { toneForSeverity } from "@/lib/severity";

type TimelineItem = {
  agent: string;
  status?: string;
};

type IncidentState = {
  id?: string;
  incident_id?: string;
  status?: string;
  state?: string;
  service?: string;
  severity?: string;
  assignee?: string;
  triage_result?: {
    affected_service?: string;
    severity?: string;
  };
  hypothesis_result?: {
    confidence?: number;
    ranked_hypotheses?: Array<{ summary?: string }>;
  };
  risk_review?: {
    risk_level?: string;
  };
  remediation_plan?: {
    candidate_actions?: Array<{ title?: string }>;
  };
  postmortem?: {
    summary?: string;
  };
  agent_timeline?: TimelineItem[];
};

type EvidenceTab = "metrics" | "logs" | "deployments" | "runbooks";

type LiveAlert = {
  id: string;
  timestamp: string;
  service: string;
  severity: "P0" | "P1" | "P2" | "P3";
  message: string;
  signal: string;
  region: string;
  type: string;
  affected_users: number;
};

type IncidentTimelineEvent = {
  event: string;
  message: string;
  actor: string;
  timestamp: string;
  metadata?: Record<string, string>;
};

type AiInsight = {
  root_causes: Array<{ title: string; confidence: number; evidence: string[] }>;
  similar_incidents: Array<{ incident_id: string; service: string; severity: string; resolution: string; similarity: number }>;
  triage: { severity: string; suggested_assignee: string; reason: string };
  escalation: { should_escalate: boolean; reason: string };
  safety_check: { risk_level: string; requires_confirmation: boolean; explanation: string };
  anomaly: { detected: boolean; baseline: string; current: string; deviation: string };
  summary: string;
};

type UserRole = "viewer" | "responder" | "commander" | "admin";

const stateMachine = ["triaging", "investigating", "hypothesis", "awaiting approval", "remediating", "monitoring", "resolved"];
const responderOptions = ["alex.chen", "maria.k", "sre-primary"];

const defaultEvidence = {
  EN: {
    metrics: ["p95 latency increased from 420ms to 2.8s", "cache hit ratio dropped from 91% to 41%", "database latency increased by 63%"],
    logs: ["Repeated cache-miss fallback warnings detected", "Checkout workers report increased downstream retries", "No security-related error pattern detected"],
    deployments: ["Recent cache configuration change detected", "No application code deployment in the last 30 minutes", "Rollback candidate identified: cache-config-v18"],
    runbooks: ["Runbook match: cache configuration rollback", "Validation step: confirm cache hit ratio recovery", "Rollback plan: restore previous cache TTL and routing config"],
  },
  TR: {
    metrics: ["p95 gecikme 420ms'den 2.8s'ye yükseldi", "Önbellek isabet oranı %91'den %41'e düştü", "Veritabanı gecikmesi %63 arttı"],
    logs: ["Tekrarlanan cache-miss fallback uyarıları algılandı", "Checkout worker'ları artan downstream retry bildiriyor", "Güvenlikle ilişkili hata deseni algılanmadı"],
    deployments: ["Son önbellek yapılandırma değişikliği algılandı", "Son 30 dakikada uygulama kodu dağıtımı yok", "Geri dönüş adayı belirlendi: cache-config-v18"],
    runbooks: ["Runbook eşleşmesi: önbellek yapılandırma geri dönüşü", "Doğrulama adımı: önbellek isabet oranının toparlanmasını onayla", "Geri dönüş planı: önceki cache TTL ve routing ayarlarını geri yükle"],
  },
} satisfies Record<Language, Record<EvidenceTab, string[]>>;

const dashboardCopy = {
  EN: {
    operationalMode: "Operational Mode",
    frontendMode: "Frontend: Vercel",
    backendMode: "Backend: Local FastAPI",
    qwenReady: "Qwen-ready / mock-safe",
    bannerBody: "Live preview is deployed on Vercel. The interactive Command Center can run with a local FastAPI backend, while Qwen-compatible orchestration is shown through a safe mock fallback.",
    runSimulation: "Run safe simulation →",
    error: "Error",
    frontend: "Frontend",
    backend: "Backend",
    qwenMode: "Qwen mode",
    cloudBilling: "Cloud billing",
    localValue: "Vercel / local",
    mockFallback: "mock fallback",
    creditsPending: "credits pending",
    liveAlertStream: "Live alert stream",
    liveAlertBody: "Incoming operational alerts from the backend stream. Promote a signal when it needs incident command.",
    sseFeed: "SSE feed",
    waitingAlert: "Waiting for the first live alert...",
    waitingAlertBody: "The stream will populate automatically when the backend emits operational signals.",
    signal: "Signal",
    region: "Region",
    affectedUsers: "Affected users",
    createIncident: "Create incident",
    commandCenter: "Command Center",
    humanApproval: "human approval gated",
    title: "Incident lifecycle console",
    subtitle: "Trace evidence, review policy decisions, approve remediation, and generate an auditable postmortem.",
    checkBackend: "Check Backend",
    startIncident: "Start Incident",
    refresh: "Refresh",
    stateMachine: "Incident state machine",
    step: "Step",
    approvalGate: "approval gate",
    incidentSummary: "Incident summary",
    noActiveIncident: "No active incident yet",
    service: "Service",
    environment: "Environment",
    severity: "Severity",
    assignee: "Assignee",
    businessImpact: "Business impact",
    confidence: "Confidence",
    risk: "Risk",
    leadingHypothesis: "Leading hypothesis",
    evidenceConsole: "Evidence console",
    evidenceBody: "Evidence lineage behind the recommendation.",
    traceable: "traceable",
    source: "source",
    whyMultiAgent: "Why multi-agent?",
    whyMultiAgentBody: "Each agent owns one decision boundary: triage, evidence, hypothesis, risk, approval, execution review, and postmortem.",
    liveAgentTimeline: "Live agent timeline",
    timelineBody: "Agent progress plus recorded incident events.",
    events: "events",
    incidentEventLog: "Incident event log",
    emptyEventLog: "Create an incident from the live alert stream to populate event history.",
    emptyAlertsAction: "Check Backend",
    emptyEventAction: "Start Incident",
    executionReview: "Execution Review",
    executionReviewBody: "What happened after approval and how the platform verified recovery.",
    ownership: "Ownership",
    ownershipBody: "Assign a clear responder for the active incident.",
    safetyGate: "Safety Gate",
    safetyGateBody: "Policy-aware control before production action.",
    approvalDrawer: "Approval Drawer",
    approvalDrawerBody: "Operator decision package before remediation.",
    auditTrail: "Audit trail",
    storedIncidents: "Stored incidents",
    copySummary: "Copy incident summary",
    exportAudit: "Export audit log",
    printReport: "Print / export report",
    reportTitle: "Incident operations report",
    reportGeneratedAt: "Generated from current dashboard state",
    aiUsefulLayer: "AI useful layer",
    generateAiSummary: "Generate AI summary",
    aiSummaryReady: "AI insight summary generated.",
    aiSummaryFailed: "AI insights could not be generated.",
    rootCauseSuggestions: "Root cause suggestions",
    similarIncidents: "Similar incidents",
    automatedTriage: "Automated triage",
    escalationRecommendation: "Escalation recommendation",
    actionSafetyCheck: "Action safety check",
    anomalyDetection: "Anomaly detection",
    naturalSummary: "Natural language summary",
    noAiInsights: "Start or select an incident to generate AI insights.",
    confidenceLabel: "confidence",
    similarityLabel: "similarity",
    collaborationHub: "Collaboration hub",
    collaborationBody: "Keep the incident channel, roles, on-call routing, and stakeholder message in one place.",
    warRoomMode: "War room mode",
    warRoomBody: "Dedicated incident channel with current context and responder ownership.",
    channel: "Channel",
    participants: "Participants",
    sharedTimeline: "Shared timeline",
    sharedTimelineBody: "Add a responder note to the incident event history.",
    annotationPlaceholder: "Add timeline annotation...",
    addAnnotation: "Add annotation",
    annotationAdded: "Timeline annotation added.",
    annotationFailed: "Timeline annotation could not be added.",
    annotationRequired: "Write a short annotation first.",
    roleAccess: "Role-based access",
    roleAccessBody: "Switch role to preview permissions without changing authentication.",
    currentRole: "Current role",
    viewerRole: "viewer",
    responderRole: "responder",
    commanderRole: "commander",
    adminRole: "admin",
    readOnly: "read-only",
    canAnnotate: "can annotate",
    canAssign: "can assign",
    canApprove: "can approve",
    onCallSchedule: "On-call schedule",
    onCallBody: "Primary and secondary responders for the current operational window.",
    primary: "Primary",
    secondary: "Secondary",
    routePrimary: "Route to primary",
    stakeholderUpdate: "Stakeholder update",
    stakeholderBody: "One-click operational update for leadership and customer-facing teams.",
    copyStakeholderUpdate: "Copy stakeholder update",
    stakeholderCopied: "Stakeholder update copied.",
    postmortemTemplate: "Post-mortem template",
    postmortemTemplateBody: "Structured review fields populated from the current incident context.",
    impact: "Impact",
    rootCause: "Root cause",
    mitigation: "Mitigation",
    followUps: "Follow-ups",
    collaborationNeedsIncident: "Create or select an incident before using collaboration actions.",
    commandIntelligence: "Command intelligence",
    commandIntelligenceBody: "Operational impact, service topology, SLA risk, and guarded response actions in one compact view.",
    topologyMap: "Topology map",
    blastRadius: "Blast radius",
    rollbackTrigger: "Rollback trigger",
    runbookExecutor: "Runbook executor",
    slaTracker: "SLA tracker",
    mttrMttd: "MTTR / MTTD",
    incidentCost: "Incident cost",
    affectedServices: "Affected services",
    usersImpacted: "Users impacted",
    revenueAtRisk: "Revenue at risk",
    slaRemaining: "SLA remaining",
    breachRisk: "Breach risk",
    lastGoodDeployment: "Last known good",
    triggerRollback: "Trigger approval-gated rollback",
    executeRunbookStep: "Execute next runbook step",
    runbookComplete: "Runbook complete",
    runbookNeedsIncident: "Start or select an incident before executing a runbook.",
    runbookStepDone: "Runbook step executed.",
    mttr: "MTTR",
    mttd: "MTTD",
    affected: "affected",
    healthy: "healthy",
    advancedAi: "Advanced AI cockpit",
    advancedAiBody: "Predictive signals, learned patterns, capacity risk, safe automation, controlled failure checks, and generated runbook guidance.",
    predictiveAlerting: "Predictive alerting",
    autoRemediation: "Auto-remediation guardrail",
    patternLibrary: "Pattern library",
    capacityForecast: "Capacity forecast",
    chaosEngineering: "Chaos readiness",
    runbookGeneration: "Runbook generation",
    earlySignalDetected: "Early signal detected",
    watchMode: "watch mode",
    autonomousLowRisk: "low-risk autonomous",
    humanForHighRisk: "human approval for high-risk",
    learnedPatterns: "learned patterns",
    forecastWindow: "forecast window",
    nextLimit: "next limit",
    controlledExperiment: "controlled experiment",
    generatedRunbook: "generated runbook",
    confidenceScore: "confidence",
    onboardingTitle: "Start in three steps",
    onboardingStep1: "Check backend health and stream status.",
    onboardingStep2: "Promote an alert or start a guided incident.",
    onboardingStep3: "Review evidence, assign owner, approve only after policy check.",
    onboardingAction: "Start with backend check",
    onboardingDismiss: "Got it",
    confirmApproveTitle: "Approve production remediation?",
    confirmApproveBody: "This action simulates a production remediation approval. Review evidence and policy context before continuing.",
    confirmApproveAction: "Approve remediation",
    confirmCancel: "Cancel",
    tooltipSse: "Server-sent events stream live operational alerts from the backend.",
    tooltipEvidence: "Evidence lineage connects metrics, logs, deployments, and runbooks to the recommendation.",
    tooltipSafety: "The safety gate prevents high-risk actions from running without explicit human approval.",
    priorityMetrics: "Priority metrics",
    liveSignals: "Live signals",
    activeIncident: "Active incident",
    currentState: "Current state",
    assignedOwner: "Assigned owner",
    assignmentValidation: "Create or select an incident before assigning an owner.",
    actions: "Actions",
    age: "Age",
    all: "All",
    copyId: "Copy ID",
    filter: "Filter",
    incident: "Incident",
    next: "Next",
    open: "Open",
    page: "Page",
    previous: "Previous",
    sort: "Sort",
    production: "production",
    high: "high",
    unassigned: "unassigned",
    checkoutDegraded: "checkout degraded",
    medium: "medium",
    metrics: "metrics",
    logs: "logs",
    deployments: "deployments",
    runbooks: "runbooks",
    agentStep: "Agent step",
    verified: "verified",
    pending: "pending",
    action: "Action",
    rollbackExecuted: "Rollback executed",
    waitingApproval: "Waiting approval",
    validation: "Validation",
    latencyRecovered: "Latency recovered",
    notStarted: "Not started",
    reduced: "Reduced",
    cacheHitRatio: "Cache hit ratio",
    postmortemGenerated: "Postmortem generated",
    postmortemPreview: "Postmortem preview",
    final: "final",
    draft: "draft",
    approved: "approved",
    approvalRequired: "approval required",
    ruleMatched: "Rule matched",
    productionRollback: "production configuration rollback",
    guardrail: "Guardrail",
    humanApprovalRequired: "human approval required",
    rollbackPlan: "Rollback plan",
    restoreCacheConfig: "restore previous cache config",
    blockedAlternative: "Blocked alternative",
    databaseRestartBlocked: "database restart without evidence",
    remediationApproved: "Remediation approved",
    approveRemediation: "Approve Remediation",
    startIncidentFirst: "Start incident first",
    closed: "closed",
    review: "review",
    recommendedAction: "Recommended action",
    evidenceUsed: "Evidence used",
    evidenceUsedValue: "metrics + logs + deployment + runbook",
    policyTriggered: "Policy triggered",
    policyTriggeredValue: "production rollback requires approval",
    rollbackSafety: "Rollback safety",
    rollbackSafetyValue: "reversible config change",
    incidentCreated: "Incident created",
    recorded: "recorded",
    evidenceLinked: "Evidence linked",
    evidenceLinkedValue: "metrics/logs/runbook",
    policyEvaluated: "Policy evaluated",
    operatorApproval: "Operator approval",
    status: "Status",
    backendHealthcheckDone: "Backend healthcheck completed.",
    backendCheckFailed: "Backend check failed. Start FastAPI backend first.",
    investigationDone: "Investigation completed. Safety gate is waiting for human approval.",
    startIncidentFailed: "Failed to start incident. Check backend logs for details.",
    storedIncidentsRefreshed: "Stored incidents refreshed.",
    refreshIncidentsFailed: "Failed to refresh incidents.",
    incidentCreatedFromAlert: "Incident created from alert",
    createIncidentFromAlertFailed: "Failed to create incident from live alert.",
    assignBeforeOwner: "Create an incident from a live alert before assigning ownership.",
    incidentAssignedTo: "Incident assigned to",
    assignIncidentFailed: "Failed to assign incident owner.",
    startBeforeApproval: "Start an incident before approval.",
    remediationApprovedDone: "Remediation approved. Execution review and postmortem generated.",
    approveIncidentFailed: "Failed to approve incident remediation.",
    summaryCopied: "Incident summary copied.",
    auditExported: "Audit log exported.",
    reportPrintReady: "Print view opened. Use browser print to save as PDF.",
    fallbackHypothesis: "Cache configuration regression introduced in the latest config change",
    fallbackAction: "Rollback cache configuration safely",
    fallbackPostmortem: "The incident was likely caused by cache config regression and mitigated with approval-gated rollback.",
  },
  TR: {
    operationalMode: "Operasyon Modu",
    frontendMode: "Frontend: Vercel",
    backendMode: "Backend: Lokal FastAPI",
    qwenReady: "Qwen hazır / mock güvenli",
    bannerBody: "Canlı önizleme Vercel üzerinde çalışır. Etkileşimli Komuta Merkezi lokal FastAPI backend ile çalışabilir; Qwen uyumlu orkestrasyon güvenli mock fallback ile gösterilir.",
    runSimulation: "Güvenli simülasyonu çalıştır →",
    error: "Hata",
    frontend: "Frontend",
    backend: "Backend",
    qwenMode: "Qwen modu",
    cloudBilling: "Cloud kredileri",
    localValue: "Vercel / lokal",
    mockFallback: "mock fallback",
    creditsPending: "kredi bekliyor",
    liveAlertStream: "Canlı uyarı akışı",
    liveAlertBody: "Backend akışından gelen operasyonel uyarılar. Olay komutuna ihtiyaç olduğunda sinyali olaya dönüştür.",
    sseFeed: "SSE akışı",
    waitingAlert: "İlk canlı uyarı bekleniyor...",
    waitingAlertBody: "Backend operasyonel sinyal yayınladığında akış otomatik dolar.",
    signal: "Sinyal",
    region: "Bölge",
    affectedUsers: "Etkilenen kullanıcı",
    createIncident: "Olay oluştur",
    commandCenter: "Komuta Merkezi",
    humanApproval: "insan onayı kontrollü",
    title: "Olay yaşam döngüsü konsolu",
    subtitle: "Kanıtları izle, politika kararlarını incele, iyileştirmeyi onayla ve denetlenebilir postmortem üret.",
    checkBackend: "Backend'i Kontrol Et",
    startIncident: "Olay Başlat",
    refresh: "Yenile",
    stateMachine: "Olay state machine",
    step: "Adım",
    approvalGate: "onay kapısı",
    incidentSummary: "Olay özeti",
    noActiveIncident: "Henüz aktif olay yok",
    service: "Servis",
    environment: "Ortam",
    severity: "Önem",
    assignee: "Sorumlu",
    businessImpact: "İş etkisi",
    confidence: "Güven",
    risk: "Risk",
    leadingHypothesis: "Öne çıkan hipotez",
    evidenceConsole: "Kanıt konsolu",
    evidenceBody: "Önerinin arkasındaki kanıt zinciri.",
    traceable: "izlenebilir",
    source: "kaynak",
    whyMultiAgent: "Neden çoklu ajan?",
    whyMultiAgentBody: "Her ajan tek bir karar sınırını sahiplenir: triage, kanıt, hipotez, risk, onay, yürütme incelemesi ve postmortem.",
    liveAgentTimeline: "Canlı ajan zaman çizelgesi",
    timelineBody: "Ajan ilerleyişi ve kaydedilen olay eventleri.",
    events: "event",
    incidentEventLog: "Olay event log'u",
    emptyEventLog: "Event geçmişini doldurmak için canlı uyarı akışından bir olay oluştur.",
    emptyAlertsAction: "Backend'i Kontrol Et",
    emptyEventAction: "Olay Başlat",
    executionReview: "Yürütme İncelemesi",
    executionReviewBody: "Onaydan sonra ne olduğu ve platformun toparlanmayı nasıl doğruladığı.",
    ownership: "Sahiplik",
    ownershipBody: "Aktif olay için net bir responder ata.",
    safetyGate: "Güvenlik Kapısı",
    safetyGateBody: "Production aksiyonundan önce politika farkındalıklı kontrol.",
    approvalDrawer: "Onay Çekmecesi",
    approvalDrawerBody: "İyileştirme öncesi operatör karar paketi.",
    auditTrail: "Denetim izi",
    storedIncidents: "Kayıtlı olaylar",
    copySummary: "Olay özetini kopyala",
    exportAudit: "Denetim logunu dışa aktar",
    printReport: "Raporu yazdır / dışa aktar",
    reportTitle: "Olay operasyon raporu",
    reportGeneratedAt: "Geçerli dashboard durumundan oluşturuldu",
    aiUsefulLayer: "Faydalı AI katmanı",
    generateAiSummary: "AI özeti üret",
    aiSummaryReady: "AI içgörü özeti üretildi.",
    aiSummaryFailed: "AI içgörüleri üretilemedi.",
    rootCauseSuggestions: "Kök neden önerileri",
    similarIncidents: "Benzer olaylar",
    automatedTriage: "Otomatik triage",
    escalationRecommendation: "Eskalasyon önerisi",
    actionSafetyCheck: "Aksiyon güvenlik kontrolü",
    anomalyDetection: "Anomali tespiti",
    naturalSummary: "Doğal dil özeti",
    noAiInsights: "AI içgörüsü üretmek için bir olay başlat veya seç.",
    confidenceLabel: "güven",
    similarityLabel: "benzerlik",
    collaborationHub: "İş birliği merkezi",
    collaborationBody: "Olay kanalı, roller, nöbet yönlendirmesi ve paydaş mesajını tek yerde tut.",
    warRoomMode: "War room modu",
    warRoomBody: "Güncel bağlam ve responder sahipliğiyle ayrılmış olay kanalı.",
    channel: "Kanal",
    participants: "Katılımcılar",
    sharedTimeline: "Paylaşılan zaman çizelgesi",
    sharedTimelineBody: "Olay geçmişine responder notu ekle.",
    annotationPlaceholder: "Zaman çizelgesi notu ekle...",
    addAnnotation: "Not ekle",
    annotationAdded: "Zaman çizelgesi notu eklendi.",
    annotationFailed: "Zaman çizelgesi notu eklenemedi.",
    annotationRequired: "Önce kısa bir not yaz.",
    roleAccess: "Rol bazlı erişim",
    roleAccessBody: "Kimlik doğrulamayı değiştirmeden izinleri önizlemek için rol değiştir.",
    currentRole: "Geçerli rol",
    viewerRole: "viewer",
    responderRole: "responder",
    commanderRole: "commander",
    adminRole: "admin",
    readOnly: "sadece okuma",
    canAnnotate: "not ekleyebilir",
    canAssign: "atayabilir",
    canApprove: "onaylayabilir",
    onCallSchedule: "Nöbet çizelgesi",
    onCallBody: "Geçerli operasyon penceresi için primary ve secondary responder.",
    primary: "Primary",
    secondary: "Secondary",
    routePrimary: "Primary'ye yönlendir",
    stakeholderUpdate: "Paydaş güncellemesi",
    stakeholderBody: "Liderlik ve müşteri ekipleri için tek tık operasyon güncellemesi.",
    copyStakeholderUpdate: "Paydaş güncellemesini kopyala",
    stakeholderCopied: "Paydaş güncellemesi kopyalandı.",
    postmortemTemplate: "Post-mortem şablonu",
    postmortemTemplateBody: "Geçerli olay bağlamından doldurulmuş yapılandırılmış inceleme alanları.",
    impact: "Etki",
    rootCause: "Kök neden",
    mitigation: "Azaltma",
    followUps: "Takip aksiyonları",
    collaborationNeedsIncident: "İş birliği aksiyonları için önce bir olay oluştur veya seç.",
    commandIntelligence: "Komuta zekâsı",
    commandIntelligenceBody: "Operasyonel etki, servis topolojisi, SLA riski ve kontrollü yanıt aksiyonları tek kompakt görünümde.",
    topologyMap: "Topoloji haritası",
    blastRadius: "Etki alanı",
    rollbackTrigger: "Rollback tetikleyici",
    runbookExecutor: "Runbook çalıştırıcı",
    slaTracker: "SLA takipçisi",
    mttrMttd: "MTTR / MTTD",
    incidentCost: "Olay maliyeti",
    affectedServices: "Etkilenen servisler",
    usersImpacted: "Etkilenen kullanıcı",
    revenueAtRisk: "Risk altındaki gelir",
    slaRemaining: "Kalan SLA",
    breachRisk: "İhlal riski",
    lastGoodDeployment: "Son sağlam sürüm",
    triggerRollback: "Onay kontrollü rollback tetikle",
    executeRunbookStep: "Sonraki runbook adımını çalıştır",
    runbookComplete: "Runbook tamamlandı",
    runbookNeedsIncident: "Runbook çalıştırmadan önce bir olay başlat veya seç.",
    runbookStepDone: "Runbook adımı çalıştırıldı.",
    mttr: "MTTR",
    mttd: "MTTD",
    affected: "etkilendi",
    healthy: "sağlıklı",
    advancedAi: "Gelişmiş AI kokpiti",
    advancedAiBody: "Tahmini sinyaller, öğrenilmiş desenler, kapasite riski, güvenli otomasyon, kontrollü hata kontrolleri ve üretilmiş runbook rehberi.",
    predictiveAlerting: "Tahmini uyarı",
    autoRemediation: "Oto-iyileştirme koruması",
    patternLibrary: "Desen kütüphanesi",
    capacityForecast: "Kapasite tahmini",
    chaosEngineering: "Chaos hazırlığı",
    runbookGeneration: "Runbook üretimi",
    earlySignalDetected: "Erken sinyal algılandı",
    watchMode: "izleme modu",
    autonomousLowRisk: "düşük risk otomatik",
    humanForHighRisk: "yüksek riskte insan onayı",
    learnedPatterns: "öğrenilmiş desen",
    forecastWindow: "tahmin penceresi",
    nextLimit: "sonraki limit",
    controlledExperiment: "kontrollü deney",
    generatedRunbook: "üretilmiş runbook",
    confidenceScore: "güven",
    onboardingTitle: "Üç adımda başla",
    onboardingStep1: "Backend sağlığını ve akış durumunu kontrol et.",
    onboardingStep2: "Bir uyarıyı olaya dönüştür veya yönlendirmeli olay başlat.",
    onboardingStep3: "Kanıtı incele, sahip ata, yalnızca politika kontrolünden sonra onayla.",
    onboardingAction: "Backend kontrolüyle başla",
    onboardingDismiss: "Anladım",
    confirmApproveTitle: "Production iyileştirmesi onaylansın mı?",
    confirmApproveBody: "Bu aksiyon production iyileştirme onayını simüle eder. Devam etmeden önce kanıtı ve politika bağlamını incele.",
    confirmApproveAction: "İyileştirmeyi onayla",
    confirmCancel: "Vazgeç",
    tooltipSse: "Server-sent events backend'den canlı operasyonel uyarıları taşır.",
    tooltipEvidence: "Kanıt zinciri metrik, log, dağıtım ve runbook bilgilerini öneriye bağlar.",
    tooltipSafety: "Güvenlik kapısı yüksek riskli aksiyonların açık insan onayı olmadan çalışmasını engeller.",
    priorityMetrics: "Öncelikli metrikler",
    liveSignals: "Canlı sinyaller",
    activeIncident: "Aktif olay",
    currentState: "Geçerli durum",
    assignedOwner: "Atanan sahip",
    assignmentValidation: "Sahip atamadan önce bir olay oluştur veya seç.",
    actions: "Aksiyonlar",
    age: "Süre",
    all: "Tümü",
    copyId: "ID kopyala",
    filter: "Filtre",
    incident: "Olay",
    next: "Sonraki",
    open: "Aç",
    page: "Sayfa",
    previous: "Önceki",
    sort: "Sırala",
    production: "production",
    high: "yüksek",
    unassigned: "atanmadı",
    checkoutDegraded: "checkout yavaşladı",
    medium: "orta",
    metrics: "metrikler",
    logs: "loglar",
    deployments: "dağıtımlar",
    runbooks: "runbooklar",
    agentStep: "Ajan adımı",
    verified: "doğrulandı",
    pending: "bekliyor",
    action: "Aksiyon",
    rollbackExecuted: "Geri dönüş çalıştırıldı",
    waitingApproval: "Onay bekliyor",
    validation: "Doğrulama",
    latencyRecovered: "Gecikme toparlandı",
    notStarted: "Başlamadı",
    reduced: "Azaltıldı",
    cacheHitRatio: "Önbellek isabet oranı",
    postmortemGenerated: "Postmortem üretildi",
    postmortemPreview: "Postmortem önizlemesi",
    final: "final",
    draft: "taslak",
    approved: "onaylandı",
    approvalRequired: "onay gerekli",
    ruleMatched: "Eşleşen kural",
    productionRollback: "production yapılandırma geri dönüşü",
    guardrail: "Koruma kuralı",
    humanApprovalRequired: "insan onayı gerekli",
    rollbackPlan: "Geri dönüş planı",
    restoreCacheConfig: "önceki cache yapılandırmasını geri yükle",
    blockedAlternative: "Engellenen alternatif",
    databaseRestartBlocked: "kanıt olmadan veritabanı yeniden başlatma",
    remediationApproved: "İyileştirme onaylandı",
    approveRemediation: "İyileştirmeyi Onayla",
    startIncidentFirst: "Önce olay başlat",
    closed: "kapalı",
    review: "inceleme",
    recommendedAction: "Önerilen aksiyon",
    evidenceUsed: "Kullanılan kanıt",
    evidenceUsedValue: "metrikler + loglar + dağıtım + runbook",
    policyTriggered: "Tetiklenen politika",
    policyTriggeredValue: "production geri dönüşü onay gerektirir",
    rollbackSafety: "Geri dönüş güvenliği",
    rollbackSafetyValue: "geri alınabilir yapılandırma değişikliği",
    incidentCreated: "Olay oluşturuldu",
    recorded: "kaydedildi",
    evidenceLinked: "Kanıt bağlandı",
    evidenceLinkedValue: "metrikler/loglar/runbook",
    policyEvaluated: "Politika değerlendirildi",
    operatorApproval: "Operatör onayı",
    status: "Durum",
    backendHealthcheckDone: "Backend healthcheck tamamlandı.",
    backendCheckFailed: "Backend kontrolü başarısız. Önce FastAPI backend'i başlat.",
    investigationDone: "İnceleme tamamlandı. Güvenlik kapısı insan onayı bekliyor.",
    startIncidentFailed: "Olay başlatılamadı. Backend loglarını kontrol et.",
    storedIncidentsRefreshed: "Kayıtlı olaylar yenilendi.",
    refreshIncidentsFailed: "Kayıtlı olaylar yenilenemedi.",
    incidentCreatedFromAlert: "Uyarıdan olay oluşturuldu",
    createIncidentFromAlertFailed: "Canlı uyarıdan olay oluşturulamadı.",
    assignBeforeOwner: "Sahiplik atamadan önce canlı uyarıdan bir olay oluştur.",
    incidentAssignedTo: "Olay atandı:",
    assignIncidentFailed: "Olay sahibi atanamadı.",
    startBeforeApproval: "Onaydan önce bir olay başlat.",
    remediationApprovedDone: "İyileştirme onaylandı. Yürütme incelemesi ve postmortem üretildi.",
    approveIncidentFailed: "Olay iyileştirmesi onaylanamadı.",
    summaryCopied: "Olay özeti kopyalandı.",
    auditExported: "Denetim logu dışa aktarıldı.",
    reportPrintReady: "Yazdırma görünümü açıldı. PDF için tarayıcı yazdırmayı kullan.",
    fallbackHypothesis: "Son yapılandırma değişikliğinde gelen cache config regresyonu",
    fallbackAction: "Cache yapılandırmasını güvenli şekilde geri al",
    fallbackPostmortem: "Olay muhtemelen cache config regresyonundan kaynaklandı ve onay kontrollü geri dönüşle giderildi.",
  },
} satisfies Record<Language, Record<string, string>>;

function toneForStatus(status: string): "cyan" | "green" | "amber" | "red" | "violet" | "slate" {
  if (status === "resolved" || status === "completed") return "green";
  if (status.includes("approval") || status === "awaiting_approval") return "amber";
  if (status.includes("executed") || status.includes("remediating")) return "violet";
  if (status.includes("running") || status.includes("investigating")) return "cyan";
  return "slate";
}

function normalizeStatus(status?: string) {
  if (!status) return "standby";
  return status.replaceAll("_", " ");
}

function deriveLifecycleStep(status: string, incident: IncidentState | null) {
  if (!incident) return 0;
  if (status === "resolved") return 6;
  if (status.includes("monitoring")) return 5;
  if (status.includes("remediating") || status.includes("executed")) return 4;
  if (status.includes("approval")) return 3;
  if (status.includes("hypothesis")) return 2;
  if (status.includes("investigating")) return 1;
  return 3;
}

function agentDisplayName(agent?: string) {
  const labels: Record<string, string> = {
    triage_agent: "Triage",
    observability_agent: "Observability",
    runbook_agent: "Runbook",
    runbook_retrieval_agent: "Runbook",
    hypothesis_agent: "Hypothesis",
    remediation_planner_agent: "Planner",
    risk_safety_agent: "Safety",
    approval_agent: "Approval Gate",
    remediation_executor: "Executor",
    execution_review_agent: "Execution Review",
    postmortem_agent: "Postmortem",
  };

  if (!agent) return "Agent";
  return labels[agent] || agent.replaceAll("_agent", "").replaceAll("_", " ");
}

function displayTimelineStatus(agent: string | undefined, status: string | undefined, isResolved: boolean) {
  if (agent === "approval_agent" && isResolved) return "approved";
  if (status === "approval_required") return "awaiting approval";
  if (status === "completed") return "completed";
  if (status === "executed") return "executed";
  return status || "completed";
}

function sleep(ms: number) {
  return new Promise((resolve) => window.setTimeout(resolve, ms));
}

function leadingHypothesis(state: IncidentState | null, copy: Record<string, string>) {
  return state?.hypothesis_result?.ranked_hypotheses?.[0]?.summary || copy.fallbackHypothesis;
}

function recommendedAction(state: IncidentState | null, copy: Record<string, string>) {
  return state?.remediation_plan?.candidate_actions?.[0]?.title || copy.fallbackAction;
}

function postmortemSummary(state: IncidentState | null, copy: Record<string, string>) {
  return state?.postmortem?.summary || copy.fallbackPostmortem;
}

function roleCapabilities(role: UserRole, copy: Record<string, string>) {
  const capabilities: Record<UserRole, string[]> = {
    viewer: [copy.readOnly],
    responder: [copy.readOnly, copy.canAnnotate],
    commander: [copy.readOnly, copy.canAnnotate, copy.canAssign, copy.canApprove],
    admin: [copy.readOnly, copy.canAnnotate, copy.canAssign, copy.canApprove],
  };

  return capabilities[role];
}

function canAnnotate(role: UserRole) {
  return role !== "viewer";
}

function canAssign(role: UserRole) {
  return role === "commander" || role === "admin";
}

function canApprove(role: UserRole) {
  return role === "commander" || role === "admin";
}

function stakeholderUpdateFor(state: IncidentState | null, status: string, copy: Record<string, string>) {
  const incidentId = state?.incident_id || state?.id || copy.noActiveIncident;
  const service = state?.triage_result?.affected_service || state?.service || "checkout-api";
  const severity = state?.triage_result?.severity || state?.severity || "P3";
  const owner = state?.assignee || copy.unassigned;
  const nextStep = status === "resolved" ? copy.postmortemGenerated : recommendedAction(state, copy);

  return `${incidentId} | ${service} | ${copy.severity}: ${severity} | ${copy.status}: ${status} | ${copy.assignee}: ${owner}. ${copy.recommendedAction}: ${nextStep}.`;
}

function postmortemFieldsFor(state: IncidentState | null, aiInsight: AiInsight | null, copy: Record<string, string>) {
  return [
    { label: copy.impact, value: state ? `${state.triage_result?.affected_service || state.service || "checkout-api"} · ${state.triage_result?.severity || state.severity || "P3"}` : copy.pending },
    { label: copy.rootCause, value: aiInsight?.root_causes?.[0]?.title || leadingHypothesis(state, copy) },
    { label: copy.mitigation, value: recommendedAction(state, copy) },
    { label: copy.followUps, value: state ? copy.evidenceUsedValue : copy.pending },
  ];
}

function localAiInsightFor(state: IncidentState | null, copy: Record<string, string>): AiInsight | null {
  if (!state) return null;

  const service = state.triage_result?.affected_service || state.service || "checkout-api";
  const severity = state.triage_result?.severity || state.severity || "P3";
  const assignee = state.assignee || "sre-primary";
  const hypothesis = leadingHypothesis(state, copy);
  const action = recommendedAction(state, copy);
  const confidence = Number(state.hypothesis_result?.confidence || 0.78);

  return {
    root_causes: [
      {
        title: hypothesis,
        confidence: Math.min(0.96, confidence),
        evidence: [copy.evidenceUsedValue, action, `${copy.status}: ${normalizeStatus(state.status || state.state)}`],
      },
    ],
    similar_incidents: [],
    triage: {
      severity,
      suggested_assignee: assignee,
      reason: `${service} is currently ${normalizeStatus(state.status || state.state)} and needs clear ownership.`,
    },
    escalation: {
      should_escalate: severity.toUpperCase() === "P0",
      reason: severity.toUpperCase() === "P0" ? "P0 severity requires immediate commander escalation." : "No escalation required yet.",
    },
    safety_check: {
      risk_level: state.risk_review?.risk_level || copy.medium,
      requires_confirmation: true,
      explanation: copy.tooltipSafety,
    },
    anomaly: {
      detected: true,
      baseline: copy.evidenceUsedValue,
      current: hypothesis,
      deviation: severity.toUpperCase() === "P0" ? "critical" : "elevated",
    },
    summary: `${service} is in ${normalizeStatus(state.status || state.state)} with ${copy.severity} ${severity}. ${copy.recommendedAction}: ${action}. ${copy.assignee}: ${assignee}.`,
  };
}

function serviceForIncident(state: IncidentState | null) {
  return state?.triage_result?.affected_service || state?.service || "checkout-api";
}

function severityForIncident(state: IncidentState | null) {
  return (state?.triage_result?.severity || state?.severity || "P3").toUpperCase();
}

function affectedUsersFor(state: IncidentState | null, alerts: LiveAlert[]) {
  const service = serviceForIncident(state);
  const alertMatch = alerts.find((alert) => alert.service === service);
  const stateWithImpact = state as (IncidentState & { affected_users?: number }) | null;
  return stateWithImpact?.affected_users || alertMatch?.affected_users || (state ? 12800 : 0);
}

function slaMinutesFor(severity: string) {
  if (severity === "P0") return 15;
  if (severity === "P1") return 30;
  if (severity === "P2") return 60;
  return 120;
}

function commandMetricsFor(state: IncidentState | null, alerts: LiveAlert[], lifecycleStep: number, status: string) {
  const severity = severityForIncident(state);
  const affectedUsers = affectedUsersFor(state, alerts);
  const affectedServices = new Set([serviceForIncident(state), ...alerts.slice(0, 3).map((alert) => alert.service)]).size;
  const slaLimit = slaMinutesFor(severity);
  const elapsedEstimate = status === "resolved" ? slaLimit : Math.min(slaLimit - 1, Math.max(4, lifecycleStep * 4 + alerts.length));
  const remaining = status === "resolved" ? 0 : Math.max(0, slaLimit - elapsedEstimate);
  const revenueMultiplier = severity === "P0" ? 0.85 : severity === "P1" ? 0.45 : severity === "P2" ? 0.18 : 0.06;
  const estimatedCost = Math.max(0, Math.round(affectedUsers * revenueMultiplier));
  const resolvedIncidents = alerts.length + (state ? 1 : 0);
  const breachTone: "green" | "amber" | "red" = remaining <= 5 && status !== "resolved" ? "red" : remaining <= 15 && status !== "resolved" ? "amber" : "green";

  return {
    affectedServices,
    affectedUsers,
    estimatedCost,
    remaining,
    breachTone,
    mttr: status === "resolved" ? 18 : 24 + Math.max(0, 6 - resolvedIncidents),
    mttd: alerts.length ? 3 : 5,
  };
}

function topologyNodesFor(state: IncidentState | null, alerts: LiveAlert[]) {
  const service = serviceForIncident(state);
  const alertServices = new Set(alerts.map((alert) => alert.service));
  return ["edge-gateway", "auth-service", "checkout-api", "cache-layer", "payment-api"].map((node) => ({
    name: node,
    affected: node === service || alertServices.has(node),
  }));
}

function runbookStepsFor(copy: Record<string, string>) {
  return [
    copy.deployments,
    copy.rollbackPlan,
    copy.validation,
  ];
}

function advancedAiSignalsFor(state: IncidentState | null, alerts: LiveAlert[], metrics: ReturnType<typeof commandMetricsFor>, copy: Record<string, string>) {
  const severity = severityForIncident(state);
  const service = serviceForIncident(state);
  const alertPressure = alerts.length;
  const capacityPercent = Math.min(96, 62 + alertPressure * 7 + (severity === "P0" ? 18 : severity === "P1" ? 12 : 6));
  const confidence = severity === "P0" ? 94 : severity === "P1" ? 88 : 81;
  const lowRisk = severity === "P2" || severity === "P3";

  return [
    {
      title: copy.predictiveAlerting,
      value: alertPressure > 1 ? copy.earlySignalDetected : copy.watchMode,
      detail: `${service} · ${copy.confidenceScore} ${confidence}%`,
      tone: alertPressure > 1 ? "amber" : "green",
    },
    {
      title: copy.autoRemediation,
      value: lowRisk ? copy.autonomousLowRisk : copy.humanForHighRisk,
      detail: `${copy.risk}: ${severity}`,
      tone: lowRisk ? "green" : "amber",
    },
    {
      title: copy.patternLibrary,
      value: `${Math.max(3, metrics.affectedServices + alerts.length)} ${copy.learnedPatterns}`,
      detail: `${copy.similarityLabel}: ${Math.min(96, 72 + alerts.length * 4)}%`,
      tone: "cyan",
    },
    {
      title: copy.capacityForecast,
      value: `${capacityPercent}% ${copy.nextLimit}`,
      detail: `${copy.forecastWindow}: 45m`,
      tone: capacityPercent > 85 ? "red" : capacityPercent > 75 ? "amber" : "green",
    },
    {
      title: copy.chaosEngineering,
      value: copy.controlledExperiment,
      detail: state ? `${copy.safetyGate}: ${copy.approvalRequired}` : copy.pending,
      tone: state ? "violet" : "slate",
    },
    {
      title: copy.runbookGeneration,
      value: copy.generatedRunbook,
      detail: recommendedAction(state, copy),
      tone: "green",
    },
  ] satisfies Array<{ title: string; value: string; detail: string; tone: "cyan" | "green" | "amber" | "red" | "violet" | "slate" }>;
}

function timelineFromState(state: IncidentState | null) {
  if (state?.agent_timeline?.length) return state.agent_timeline;
  return [
    { agent: "triage_agent", status: "waiting" },
    { agent: "observability_agent", status: "waiting" },
    { agent: "runbook_agent", status: "waiting" },
    { agent: "hypothesis_agent", status: "waiting" },
    { agent: "remediation_planner_agent", status: "waiting" },
    { agent: "risk_safety_agent", status: "waiting" },
    { agent: "approval_agent", status: "waiting" },
  ];
}

function normalizeIncidentState(data: IncidentState): IncidentState {
  if (data.incident_id || data.status) return data;

  return {
    ...data,
    incident_id: data.id,
    status: data.state,
    triage_result: {
      affected_service: data.service,
      severity: data.severity?.toLowerCase(),
    },
    agent_timeline: [
      { agent: "triage_agent", status: "created from alert" },
      { agent: "observability_agent", status: "waiting" },
      { agent: "approval_agent", status: "waiting" },
    ],
  };
}

export default function DashboardPage() {
  const language = useLanguage();
  const copy = dashboardCopy[language];
  const [backendStatus, setBackendStatus] = useState<string>("not checked");
  const [incident, setIncident] = useState<IncidentState | null>(null);
  const [incidents, setIncidents] = useState<IncidentState[]>([]);
  const [alerts, setAlerts] = useState<LiveAlert[]>([]);
  const [incidentTimeline, setIncidentTimeline] = useState<IncidentTimelineEvent[]>([]);
  const [aiInsight, setAiInsight] = useState<AiInsight | null>(null);
  const [alertStreamStatus, setAlertStreamStatus] = useState<string>("connecting");
  const [loading, setLoading] = useState(false);
  const [evidenceTab, setEvidenceTab] = useState<EvidenceTab>("metrics");
  const [toasts, setToasts] = useState<ToastMessage[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [visualStep, setVisualStep] = useState<number | null>(null);
  const [assignmentValidation, setAssignmentValidation] = useState<string | null>(null);
  const [showOnboarding, setShowOnboarding] = useState(false);
  const [confirmApprovalOpen, setConfirmApprovalOpen] = useState(false);
  const [currentRole, setCurrentRole] = useState<UserRole>("commander");
  const [timelineAnnotation, setTimelineAnnotation] = useState("");
  const [runbookProgress, setRunbookProgress] = useState(0);
  const toastIdRef = useRef(0);

  const status = normalizeStatus(incident?.status);
  const timeline = timelineFromState(incident);
  const isResolved = status === "resolved";
  const isAwaitingApproval = status.includes("approval");
  const lifecycleStep = visualStep ?? deriveLifecycleStep(status, incident);
  const canAssignIncident = Boolean(incident?.incident_id || incident?.id) && canAssign(currentRole);
  const activeIncidentId = incident?.incident_id || incident?.id;
  const onCallPrimary = aiInsight?.triage.suggested_assignee || incident?.assignee || "sre-primary";
  const onCallSecondary = incident?.triage_result?.affected_service === "auth-service" || incident?.service === "auth-service" ? "identity-sre" : "platform-responder";
  const stakeholderUpdate = stakeholderUpdateFor(incident, status, copy);
  const visibleAiInsight = aiInsight ?? localAiInsightFor(incident, copy);
  const postmortemFields = postmortemFieldsFor(incident, visibleAiInsight, copy);
  const commandMetrics = commandMetricsFor(incident, alerts, lifecycleStep, status);
  const topologyNodes = topologyNodesFor(incident, alerts);
  const runbookSteps = runbookStepsFor(copy);
  const advancedAiSignals = advancedAiSignalsFor(incident, alerts, commandMetrics, copy);

  useEffect(() => {
    let mounted = true;

    listAlerts()
      .then((data) => {
        if (mounted) {
          setAlerts(data.alerts || []);
        }
      })
      .catch(() => {
        if (mounted) {
          setAlertStreamStatus("waiting for backend");
        }
      });

    const source = new EventSource(alertStreamUrl());

    source.onopen = () => {
      if (mounted) {
        setAlertStreamStatus("live");
      }
    };

    source.addEventListener("alert", (event) => {
      if (!mounted) return;
      const nextAlert = JSON.parse(event.data) as LiveAlert;
      setAlerts((current) => [nextAlert, ...current.filter((item) => item.id !== nextAlert.id)].slice(0, 6));
    });

    source.onerror = () => {
      if (mounted) {
        setAlertStreamStatus("reconnecting");
      }
    };

    return () => {
      mounted = false;
      source.close();
    };
  }, []);

  useEffect(() => {
    const timer = window.setTimeout(() => {
      const dismissed = window.localStorage.getItem("opspilot-dashboard-onboarding-dismissed");
      setShowOnboarding(dismissed !== "true");
    }, 0);

    return () => window.clearTimeout(timer);
  }, []);

  function dismissOnboarding() {
    window.localStorage.setItem("opspilot-dashboard-onboarding-dismissed", "true");
    setShowOnboarding(false);
  }

  function notify(message: string, tone: ToastTone = "success") {
    toastIdRef.current += 1;
    const id = toastIdRef.current;
    setToasts((current) => [...current, { id, message, tone }].slice(-4));
    window.setTimeout(() => {
      setToasts((current) => current.filter((item) => item.id !== id));
    }, 3000);
  }

  function showError(message: string) {
    setError(message);
    notify(message, "error");
    window.setTimeout(() => setError(null), 5000);
  }

  function extractErrorMessage(error: unknown, fallback: string) {
    if (error instanceof Error) return error.message;
    if (typeof error === "string") return error;
    return fallback;
  }

  async function loadIncidentTimeline(incidentId?: string) {
    if (!incidentId) {
      setIncidentTimeline([]);
      return;
    }

    try {
      const data = await getIncidentTimeline(incidentId);
      setIncidentTimeline(data.timeline || []);
    } catch {
      setIncidentTimeline([]);
    }
  }

  async function loadAiInsights(incidentId?: string, announce = false) {
    if (!incidentId) {
      setAiInsight(null);
      return;
    }

    try {
      const data = await getIncidentAiInsights(incidentId);
      setAiInsight(data);
      if (announce) {
        notify(copy.aiSummaryReady, "info");
      }
    } catch (error: unknown) {
      const fallbackInsight = localAiInsightFor(incident, copy);
      setAiInsight(fallbackInsight);
      if (announce && fallbackInsight) {
        notify(copy.aiSummaryReady, "info");
      } else if (announce) {
        showError(extractErrorMessage(error, copy.aiSummaryFailed));
      }
    }
  }

  async function checkBackend() {
    setLoading(true);
    setError(null);
    try {
      const data = await healthcheck();
      setBackendStatus(`${data.status} | mock_llm=${data.mock_llm}`);
      notify(copy.backendHealthcheckDone, "info");
    } catch (error: unknown) {
      const errorMsg = extractErrorMessage(error, copy.backendCheckFailed);
      setBackendStatus(`error: ${extractErrorMessage(error, "unknown")}`);
      showError(errorMsg);
      console.error("Backend check error:", error);
    } finally {
      setLoading(false);
    }
  }

  async function startIncident() {
    setLoading(true);
    setError(null);
    setVisualStep(0);
    try {
      await sleep(300);
      setVisualStep(1);

      await sleep(300);
      setVisualStep(2);

      const data = await createIncident();
      setIncident(data.state ?? data);
      await loadIncidentTimeline(data.state?.incident_id ?? data.incident_id);
      await loadAiInsights(data.state?.incident_id ?? data.incident_id);

      await sleep(300);
      setVisualStep(3);

      notify(copy.investigationDone);
    } catch (error: unknown) {
      const errorMsg = extractErrorMessage(error, copy.startIncidentFailed);
      showError(errorMsg);
      console.error("Start incident error:", error);
      setVisualStep(null);
    } finally {
      setLoading(false);
    }
  }

  async function refreshIncidents() {
    setLoading(true);
    setError(null);
    try {
      const data = await listIncidents();
      setIncidents(data.incidents || []);
      notify(copy.storedIncidentsRefreshed);
    } catch (error: unknown) {
      const errorMsg = extractErrorMessage(error, copy.refreshIncidentsFailed);
      showError(errorMsg);
      console.error("Refresh incidents error:", error);
    } finally {
      setLoading(false);
    }
  }

  async function promoteAlert(alertId: string) {
    setLoading(true);
    setError(null);
    try {
      const data = await createIncidentFromAlert(alertId);
      const normalized = normalizeIncidentState(data);
      setIncident(normalized);
      await loadIncidentTimeline(normalized.incident_id);
      await loadAiInsights(normalized.incident_id, true);
      setVisualStep(0);
      notify(`${copy.incidentCreatedFromAlert} ${alertId}.`);
    } catch (error: unknown) {
      const errorMsg = extractErrorMessage(error, copy.createIncidentFromAlertFailed);
      showError(errorMsg);
      console.error("Create incident from alert error:", error);
    } finally {
      setLoading(false);
    }
  }

  async function assignActiveIncident(assignee: string) {
    if (!incident?.incident_id || !canAssignIncident) {
      setAssignmentValidation(copy.assignmentValidation);
      notify(copy.assignBeforeOwner, "warning");
      return;
    }

    setLoading(true);
    setError(null);
    setAssignmentValidation(null);
    try {
      const data = await assignIncident(incident.incident_id, assignee);
      const normalized = normalizeIncidentState(data);
      setIncident(normalized);
      await loadIncidentTimeline(normalized.incident_id);
      await loadAiInsights(normalized.incident_id);
      notify(`${copy.incidentAssignedTo} ${assignee}.`);
    } catch (error: unknown) {
      const errorMsg = extractErrorMessage(error, copy.assignIncidentFailed);
      showError(errorMsg);
      console.error("Assign incident error:", error);
    } finally {
      setLoading(false);
    }
  }

  async function addTimelineAnnotation() {
    if (!activeIncidentId) {
      notify(copy.collaborationNeedsIncident, "warning");
      return;
    }

    if (!canAnnotate(currentRole)) {
      notify(copy.readOnly, "warning");
      return;
    }

    const message = timelineAnnotation.trim();
    if (!message) {
      notify(copy.annotationRequired, "warning");
      return;
    }

    setLoading(true);
    try {
      await addIncidentTimelineEvent(activeIncidentId, "responder_annotation", message, currentRole);
      setTimelineAnnotation("");
      await loadIncidentTimeline(activeIncidentId);
      notify(copy.annotationAdded, "info");
    } catch (error: unknown) {
      showError(extractErrorMessage(error, copy.annotationFailed));
    } finally {
      setLoading(false);
    }
  }

  async function approve() {
    if (!incident?.incident_id) {
      notify(copy.startBeforeApproval, "warning");
      return;
    }

    if (!canApprove(currentRole)) {
      notify(copy.readOnly, "warning");
      return;
    }

    setConfirmApprovalOpen(false);
    setLoading(true);
    setError(null);
    setVisualStep(4);
    try {
      await sleep(450);
      setVisualStep(5);

      const data = await approveIncident(incident.incident_id);

      await sleep(450);
      setIncident(data.state ?? data);
      await loadIncidentTimeline(data.state?.incident_id ?? data.incident_id);
      await loadAiInsights(data.state?.incident_id ?? data.incident_id);
      setVisualStep(6);
      notify(copy.remediationApprovedDone);
    } catch (error: unknown) {
      const errorMsg = extractErrorMessage(error, copy.approveIncidentFailed);
      showError(errorMsg);
      console.error("Approve error:", error);
      setVisualStep(deriveLifecycleStep(status, incident));
    } finally {
      setLoading(false);
    }
  }

  function requestApproval() {
    if (!incident?.incident_id) {
      notify(copy.startBeforeApproval, "warning");
      return;
    }

    if (!canApprove(currentRole)) {
      notify(copy.readOnly, "warning");
      return;
    }

    setConfirmApprovalOpen(true);
  }

  function printReport() {
    notify(copy.reportPrintReady, "info");
    window.setTimeout(() => window.print(), 50);
  }

  async function copyIncidentSummary() {
    const summary = {
      incident_id: incident?.incident_id || "no-active-incident",
      status,
      hypothesis: leadingHypothesis(incident, copy),
      recommended_action: recommendedAction(incident, copy),
      postmortem: postmortemSummary(incident, copy),
    };
    await navigator.clipboard?.writeText(JSON.stringify(summary, null, 2)).catch(() => undefined);
    notify(copy.summaryCopied, "info");
  }

  async function copyStakeholderUpdate() {
    await navigator.clipboard?.writeText(stakeholderUpdate).catch(() => undefined);
    notify(copy.stakeholderCopied, "info");
  }

  function executeRunbookStep() {
    if (!activeIncidentId) {
      notify(copy.runbookNeedsIncident, "warning");
      return;
    }

    setRunbookProgress((current) => Math.min(runbookSteps.length, current + 1));
    notify(copy.runbookStepDone, "info");
  }

  async function exportAuditLog() {
    const audit = timeline.map((item: TimelineItem, index: number) => ({
      step: index + 1,
      agent: item.agent,
      status: item.status || "completed",
    }));
    await navigator.clipboard?.writeText(JSON.stringify(audit, null, 2)).catch(() => undefined);
    notify(copy.auditExported, "info");
  }

  return (
    <PlatformShell>
      <PrintIncidentReport
        assignee={incident?.assignee || copy.unassigned}
        generatedAt={copy.reportGeneratedAt}
        hypothesis={leadingHypothesis(incident, copy)}
        incidentId={incident?.incident_id || copy.noActiveIncident}
        postmortem={postmortemSummary(incident, copy)}
        service={incident?.triage_result?.affected_service || "checkout-api"}
        severity={incident?.triage_result?.severity || "P3"}
        status={status}
        title={copy.reportTitle}
      />

      <section className="mx-4 mb-8 max-w-7xl rounded-[1.5rem] border border-cyan-400/15 bg-slate-950/70 p-4 shadow-[0_0_32px_rgba(34,211,238,0.06)] print:hidden sm:mx-6 xl:mx-auto">
        <div className="flex flex-col gap-4 xl:flex-row xl:items-center xl:justify-between">
          <div className="min-w-0">
            <div className="flex flex-wrap items-center gap-2">
              <span className="rounded-full border border-cyan-300/30 bg-cyan-300/10 px-3 py-1 text-[11px] font-black uppercase tracking-[0.2em] text-cyan-100">
                {copy.operationalMode}
              </span>
              <span className="rounded-full border border-white/10 bg-white/5 px-3 py-1 text-[11px] font-bold text-slate-300">
                {copy.frontendMode}
              </span>
              <span className="rounded-full border border-white/10 bg-white/5 px-3 py-1 text-[11px] font-bold text-slate-300">
                {copy.backendMode}
              </span>
              <span className="rounded-full border border-violet-300/20 bg-violet-300/10 px-3 py-1 text-[11px] font-bold text-violet-100">
                {copy.qwenReady}
              </span>
            </div>
            <p className="mt-2 max-w-5xl text-xs leading-5 text-slate-400">
              {copy.bannerBody}
            </p>
          </div>

          <a
            href="/simulation"
            className="inline-flex shrink-0 items-center justify-center rounded-xl border border-cyan-300/25 bg-cyan-300/10 px-3 py-2 text-xs font-black text-cyan-50 transition hover:bg-cyan-300/20 active:scale-[0.98]"
          >
            {copy.runSimulation}
          </a>
        </div>
      </section>

      <section className="mx-auto max-w-7xl px-4 pb-12 pt-6 print:hidden sm:px-6">
        <ToastStack items={toasts} onDismiss={(id) => setToasts((current) => current.filter((item) => item.id !== id))} />

        {showOnboarding && (
          <OnboardingFlow
            actionLabel={copy.onboardingAction}
            dismissLabel={copy.onboardingDismiss}
            onAction={checkBackend}
            onDismiss={dismissOnboarding}
            steps={[copy.onboardingStep1, copy.onboardingStep2, copy.onboardingStep3]}
            title={copy.onboardingTitle}
          />
        )}

        {error && (
          <div className="fixed right-6 top-40 z-[80] max-w-md shadow-[0_0_40px_rgba(245,158,11,0.16)]">
            <div className="flex items-start justify-between gap-3">
              <InlineError title={copy.error} message={error} />
              <button
                onClick={() => setError(null)}
                className="mt-4 shrink-0 text-amber-300 hover:text-amber-200"
                aria-label="Close error"
              >
                ✕
              </button>
            </div>
          </div>
        )}

        <div className="mb-5 rounded-3xl border border-white/10 bg-slate-950/70 p-5">
          <div className="mb-4 flex items-center justify-between gap-3">
            <SectionTitle className="text-xl">{copy.priorityMetrics}</SectionTitle>
            <StatusBadge label={copy.currentState} tone={toneForStatus(status)} />
          </div>
          <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-5">
            <SystemStripItem label={copy.liveSignals} value={String(alerts.length)} tone={alerts.length ? "green" : "slate"} />
            <SystemStripItem label={copy.activeIncident} value={incident?.incident_id || copy.noActiveIncident} tone={incident ? "cyan" : "slate"} />
            <SystemStripItem label={copy.currentState} value={status} tone={toneForStatus(status)} />
            <SystemStripItem label={copy.assignedOwner} value={incident?.assignee || copy.unassigned} tone={incident?.assignee ? "green" : "amber"} />
            <SystemStripItem label={copy.backend} value={backendStatus} tone={backendStatus.startsWith("ok") ? "green" : backendStatus.startsWith("error") ? "amber" : "slate"} />
          </div>
        </div>

        <section className="mb-5 rounded-3xl border border-cyan-400/15 bg-slate-950/70 p-5">
          <div className="flex flex-col gap-3 md:flex-row md:items-start md:justify-between">
            <div>
              <div className="flex flex-wrap items-center gap-3">
                <Tooltip label={copy.tooltipSse}>
                  <SectionTitle>{copy.liveAlertStream}</SectionTitle>
                </Tooltip>
                <StatusBadge label={alertStreamStatus} tone={alertStreamStatus === "live" ? "green" : "amber"} />
              </div>
              <BodyText className="mt-2">
                {copy.liveAlertBody}
              </BodyText>
            </div>
            <RealtimeIndicator active={alertStreamStatus === "live"} label={copy.sseFeed} />
          </div>

          <div className="mt-5 grid gap-3 lg:grid-cols-3">
            {loading && alerts.length === 0 ? (
              <div className="lg:col-span-3">
                <LoadingSkeleton rows={3} />
              </div>
            ) : alerts.length === 0 ? (
              <div className="lg:col-span-3">
                <EmptyState
                  title={copy.waitingAlert}
                  description={copy.waitingAlertBody}
                  action={{ label: copy.emptyAlertsAction, onClick: checkBackend }}
                />
              </div>
            ) : (
              alerts.slice(0, 3).map((alert) => (
                <div key={alert.id} className="rounded-2xl border border-white/10 bg-white/[0.035] p-4">
                  <div className="flex items-start justify-between gap-3">
                    <div className="min-w-0">
                      <div className="font-mono text-xs font-black text-cyan-100">{alert.id}</div>
                      <h3 className="mt-2 truncate text-lg font-black text-white">{alert.service}</h3>
                    </div>
                    <StatusBadge label={alert.severity} tone={toneForSeverity(alert.severity)} />
                  </div>
                  <p className="mt-3 text-sm leading-6 text-slate-300">{alert.message}</p>
                  <div className="mt-3 grid gap-2 text-xs text-slate-400">
                    <div>{copy.signal}: {alert.signal}</div>
                    <div>{copy.region}: {alert.region}</div>
                    <div>{copy.affectedUsers}: {alert.affected_users.toLocaleString()}</div>
                  </div>
                  <button
                    onClick={() => promoteAlert(alert.id)}
                    disabled={loading}
                    className="mt-4 w-full rounded-xl border border-cyan-300/25 bg-cyan-300/10 px-3 py-2 text-xs font-black text-cyan-50 hover:bg-cyan-300/20 disabled:opacity-50"
                  >
                    {copy.createIncident}
                  </button>
                </div>
              ))
            )}
          </div>
        </section>

        <div className="mb-6 flex flex-col gap-4 md:flex-row md:items-end md:justify-between">
          <div>
            <div className="mb-4 flex flex-wrap gap-3">
              <StatusBadge label={copy.commandCenter} tone="cyan" />
              <StatusBadge label={status} tone={toneForStatus(status)} />
              <StatusBadge label={copy.humanApproval} tone="violet" />
            </div>
            <PageTitle>{copy.title}</PageTitle>
            <BodyText className="mt-4 max-w-3xl">
              {copy.subtitle}
            </BodyText>
          </div>

          <div className="flex flex-wrap gap-3">
            <button onClick={checkBackend} disabled={loading} className="w-full rounded-2xl border border-white/10 bg-white/[0.04] px-5 py-3 text-sm font-bold text-white transition hover:bg-white/[0.08] active:scale-[0.98] disabled:opacity-50 sm:w-auto">{copy.checkBackend}</button>
            <button onClick={startIncident} disabled={loading} className="w-full rounded-2xl bg-cyan-300 px-5 py-3 text-sm font-black text-slate-950 transition hover:bg-cyan-200 active:scale-[0.98] disabled:opacity-50 sm:w-auto">{copy.startIncident}</button>
            <button onClick={refreshIncidents} disabled={loading} className="w-full rounded-2xl border border-white/10 bg-white/[0.04] px-5 py-3 text-sm font-bold text-white transition hover:bg-white/[0.08] active:scale-[0.98] disabled:opacity-50 sm:w-auto">{copy.refresh}</button>
          </div>
        </div>

        <div className="mb-5 rounded-3xl border border-white/10 bg-slate-950/70 p-5">
          <SectionTitle className="text-xl">{copy.stateMachine}</SectionTitle>
          <div className="mt-4 grid gap-3 sm:grid-cols-2 lg:grid-cols-4 xl:grid-cols-7">
            {stateMachine.map((state, index) => {
              const active = index === lifecycleStep;
              const passed = Boolean(incident) && index < lifecycleStep;
              return (
                <div
                  key={state}
                  className={`rounded-2xl border p-3 transition-all duration-300 ${
                    active
                      ? "border-cyan-300 bg-cyan-300 text-slate-950 shadow-[0_0_28px_rgba(34,211,238,0.22)]"
                      : passed
                      ? "border-emerald-400/20 bg-emerald-400/10 text-emerald-100"
                      : "border-white/10 bg-white/[0.035] text-slate-400"
                  }`}
                >
                  <div className="text-xs font-black uppercase tracking-wider">{copy.step} {index + 1}</div>
                  <div className="mt-1 text-sm font-black">
                    {state === "awaiting approval" ? copy.approvalGate : state}
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        <section className="mb-5 rounded-3xl border border-cyan-400/15 bg-slate-950/70 p-5">
          <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
            <div>
              <SectionTitle className="text-xl">{copy.commandIntelligence}</SectionTitle>
              <BodyText className="mt-1 max-w-3xl">{copy.commandIntelligenceBody}</BodyText>
            </div>
            <StatusBadge label={copy.humanApproval} tone="violet" />
          </div>

          <div className="mt-5 grid items-start gap-4 xl:grid-cols-[1.1fr_1fr_0.9fr]">
            <div className="rounded-3xl border border-cyan-400/15 bg-cyan-400/10 p-4 shadow-[0_0_28px_rgba(34,211,238,0.06)]">
              <div className="flex items-start justify-between gap-3">
                <h3 className="font-black text-white">{copy.topologyMap}</h3>
                <StatusBadge label={`${topologyNodes.filter((node) => node.affected).length} ${copy.affected}`} tone="cyan" />
              </div>
              <div className="relative mt-5 grid gap-3">
                <div className="absolute left-4 top-5 bottom-5 w-px bg-cyan-300/20" />
                {topologyNodes.map((node, index) => (
                  <div key={node.name} className="relative flex items-center gap-3">
                    <div className={`z-10 flex h-8 w-8 shrink-0 items-center justify-center rounded-full border text-xs font-black ${
                      node.affected
                        ? "border-amber-300/40 bg-amber-300/20 text-amber-100"
                        : "border-emerald-300/30 bg-emerald-300/15 text-emerald-100"
                    }`}>
                      {index + 1}
                    </div>
                    <div className={`min-w-0 flex-1 rounded-2xl border p-3 transition ${
                      node.affected
                        ? "border-amber-300/35 bg-amber-300/15 text-amber-50"
                        : "border-emerald-300/20 bg-emerald-300/10 text-emerald-50"
                    }`}>
                      <div className="flex items-center justify-between gap-3">
                        <div className="min-w-0 truncate text-sm font-black">{node.name}</div>
                        <StatusBadge label={node.affected ? copy.affected : copy.healthy} tone={node.affected ? "amber" : "green"} />
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className="grid gap-3 sm:grid-cols-2">
              <CommandMetric title={copy.blastRadius} label={copy.usersImpacted} value={commandMetrics.affectedUsers.toLocaleString()} tone="amber" />
              <CommandMetric title={copy.affectedServices} label={copy.service} value={String(commandMetrics.affectedServices)} tone="cyan" />
              <CommandMetric title={copy.slaTracker} label={copy.slaRemaining} value={`${commandMetrics.remaining}m`} tone={commandMetrics.breachTone} />
              <CommandMetric title={copy.incidentCost} label={copy.revenueAtRisk} value={`$${commandMetrics.estimatedCost.toLocaleString()}`} tone="violet" />
              <CommandMetric title={copy.mttrMttd} label={copy.mttr} value={`${commandMetrics.mttr}m`} tone="green" />
              <CommandMetric title={copy.mttrMttd} label={copy.mttd} value={`${commandMetrics.mttd}m`} tone="green" />
            </div>

            <div className="rounded-3xl border border-white/10 bg-white/[0.035] p-4">
              <div className="flex items-start justify-between gap-3">
                <h3 className="font-black text-white">{copy.rollbackTrigger}</h3>
                <StatusBadge label={copy.approvalRequired} tone={isResolved ? "green" : "amber"} />
              </div>
              <div className="mt-4 rounded-2xl border border-white/10 bg-slate-950/50 p-3">
                <div className="text-xs uppercase tracking-wider text-slate-500">{copy.lastGoodDeployment}</div>
                <div className="mt-2 font-black text-white">cache-config-v18</div>
              </div>
              <button
                onClick={requestApproval}
                disabled={loading || !activeIncidentId || isResolved}
                className="mt-3 w-full rounded-2xl border border-emerald-300/25 bg-emerald-300/15 px-4 py-3 text-sm font-black text-emerald-50 transition hover:bg-emerald-300/25 disabled:cursor-not-allowed disabled:opacity-40 active:scale-[0.98]"
              >
                {copy.triggerRollback}
              </button>

              <div className="mt-5">
                <h3 className="font-black text-white">{copy.runbookExecutor}</h3>
                <div className="mt-3 grid gap-2">
                  {runbookSteps.map((step, index) => (
                    <div key={step} className="flex items-center justify-between gap-3 rounded-2xl border border-white/10 bg-slate-950/45 p-3">
                      <span className="text-sm font-semibold text-slate-200">{step}</span>
                      <StatusBadge label={index < runbookProgress ? copy.verified : copy.pending} tone={index < runbookProgress ? "green" : "slate"} />
                    </div>
                  ))}
                </div>
                <button
                  onClick={executeRunbookStep}
                  disabled={loading || runbookProgress >= runbookSteps.length}
                  className="mt-3 w-full rounded-2xl border border-cyan-300/25 bg-cyan-300/10 px-4 py-3 text-sm font-black text-cyan-50 transition hover:bg-cyan-300/20 disabled:cursor-not-allowed disabled:opacity-40 active:scale-[0.98]"
                >
                  {runbookProgress >= runbookSteps.length ? copy.runbookComplete : copy.executeRunbookStep}
                </button>
              </div>
            </div>
          </div>

          <div className="mt-4 rounded-3xl border border-violet-400/15 bg-violet-400/10 p-4">
            <div className="flex flex-col gap-3 lg:flex-row lg:items-start lg:justify-between">
              <div>
                <h3 className="font-black text-white">{copy.advancedAi}</h3>
                <p className="mt-1 max-w-3xl text-sm leading-6 text-violet-50/75">{copy.advancedAiBody}</p>
              </div>
              <StatusBadge label={copy.confidenceScore} tone="violet" />
            </div>
            <div className="mt-4 grid gap-3 md:grid-cols-2 xl:grid-cols-3">
              {advancedAiSignals.map((signal) => (
                <div key={signal.title} className="rounded-2xl border border-white/10 bg-slate-950/45 p-4">
                  <div className="flex items-start justify-between gap-3">
                    <h4 className="text-sm font-black leading-5 text-white">{signal.title}</h4>
                    <StatusBadge label={signal.tone} tone={signal.tone} />
                  </div>
                  <div className="mt-3 text-lg font-black text-violet-50">{signal.value}</div>
                  <div className="mt-2 text-sm leading-6 text-slate-300">{signal.detail}</div>
                </div>
              ))}
            </div>
          </div>
        </section>

        <div className="grid items-start gap-5 2xl:grid-cols-[minmax(0,1fr)_360px]">
          <div className="space-y-5">
            <div className="grid items-start gap-5 2xl:grid-cols-[360px_minmax(0,1fr)]">
              <section className="rounded-3xl border border-white/10 bg-slate-950/70 p-5">
                <div className="flex items-start justify-between gap-4">
                  <div>
                    <SectionTitle>{copy.incidentSummary}</SectionTitle>
                    <p className="mt-1 font-mono text-sm text-slate-500">{incident?.incident_id || copy.noActiveIncident}</p>
                  </div>
                  <StatusBadge label={status} tone={toneForStatus(status)} />
                </div>

                <div className="mt-5 grid gap-3 md:grid-cols-2">
                  <div className="md:col-span-2">
                    <IncidentCard
                      age="live"
                      assignee={incident?.assignee}
                      copy={{
                        age: copy.age,
                        assignee: copy.assignee,
                        incident: copy.incident,
                        noActiveIncident: copy.noActiveIncident,
                        service: copy.service,
                        severity: copy.severity,
                        status: copy.status,
                        unassigned: copy.unassigned,
                      }}
                      incidentId={incident?.incident_id}
                      service={incident?.triage_result?.affected_service || "checkout-api"}
                      severity={incident?.triage_result?.severity || "P3"}
                      status={status}
                    />
                  </div>
                  <MetricCard title={copy.service} value={incident?.triage_result?.affected_service || "checkout-api"} />
                  <MetricCard title={copy.environment} value={copy.production} />
                  <MetricCard title={copy.severity} value={incident?.triage_result?.severity || copy.high} />
                  <MetricCard title={copy.assignee} value={incident?.assignee || copy.unassigned} />
                  <MetricCard title={copy.businessImpact} value={copy.checkoutDegraded} />
                  <MetricCard title={copy.confidence} value={String(incident?.hypothesis_result?.confidence || "0.86")} />
                  <MetricCard title={copy.risk} value={incident?.risk_review?.risk_level || copy.medium} />
                </div>

                <div className="mt-6 rounded-3xl border border-cyan-400/20 bg-cyan-400/10 p-5">
                  <SectionTitle className="text-xl">{copy.leadingHypothesis}</SectionTitle>
                  <p className="mt-3 leading-7 text-slate-300">{leadingHypothesis(incident, copy)}</p>
                </div>
              </section>

              <section className="rounded-3xl border border-white/10 bg-slate-950/70 p-5">
                <div className="flex flex-col gap-4 md:flex-row md:items-start md:justify-between">
                  <div>
                    <SectionTitle>{copy.collaborationHub}</SectionTitle>
                    <BodyText className="mt-1">{copy.collaborationBody}</BodyText>
                  </div>
                  <StatusBadge label={currentRole} tone="cyan" />
                </div>

                <div className="mt-5 grid gap-4 xl:grid-cols-2">
                  <div className="rounded-3xl border border-cyan-400/15 bg-cyan-400/10 p-4 shadow-[0_0_24px_rgba(34,211,238,0.05)]">
                    <div className="flex items-start justify-between gap-3">
                      <div>
                        <h3 className="font-black text-white">{copy.warRoomMode}</h3>
                        <p className="mt-2 text-sm leading-6 text-cyan-50/75">{copy.warRoomBody}</p>
                      </div>
                      <StatusBadge label={alertStreamStatus} tone={alertStreamStatus === "live" ? "green" : "amber"} />
                    </div>
                    <div className="mt-4 grid gap-2 sm:grid-cols-2">
                      <MiniReview label={copy.channel} value={`#ops-${activeIncidentId || "standby"}`} />
                      <MiniReview label={copy.participants} value={`${currentRole}, ${incident?.assignee || copy.unassigned}`} />
                    </div>
                  </div>

                  <div className="rounded-3xl border border-violet-400/15 bg-violet-400/10 p-4 shadow-[0_0_24px_rgba(139,92,246,0.05)]">
                    <h3 className="font-black text-white">{copy.roleAccess}</h3>
                    <p className="mt-2 text-sm leading-6 text-violet-50/75">{copy.roleAccessBody}</p>
                    <div className="mt-4 grid grid-cols-2 gap-2">
                      {(["viewer", "responder", "commander", "admin"] as UserRole[]).map((role) => (
                        <button
                          key={role}
                          onClick={() => setCurrentRole(role)}
                          className={`rounded-2xl border px-3 py-2 text-xs font-black transition active:scale-[0.98] ${
                            currentRole === role
                              ? "border-cyan-300 bg-cyan-300 text-slate-950"
                              : "border-white/10 bg-slate-950/40 text-slate-200 hover:bg-white/[0.08]"
                          }`}
                        >
                          {copy[`${role}Role`]}
                        </button>
                      ))}
                    </div>
                    <div className="mt-4 flex flex-wrap gap-2">
                      {roleCapabilities(currentRole, copy).map((capability) => (
                        <StatusBadge key={capability} label={capability} tone={capability === copy.readOnly ? "slate" : "green"} />
                      ))}
                    </div>
                  </div>

                  <div className="rounded-3xl border border-emerald-400/15 bg-emerald-400/10 p-4 shadow-[0_0_24px_rgba(16,185,129,0.05)]">
                    <h3 className="font-black text-white">{copy.onCallSchedule}</h3>
                    <p className="mt-2 text-sm leading-6 text-emerald-50/75">{copy.onCallBody}</p>
                    <div className="mt-4 grid gap-2 sm:grid-cols-2">
                      <MiniReview label={copy.primary} value={onCallPrimary} />
                      <MiniReview label={copy.secondary} value={onCallSecondary} />
                    </div>
                    <button
                      onClick={() => assignActiveIncident(onCallPrimary)}
                      disabled={loading || !canAssignIncident}
                      className="mt-4 w-full rounded-2xl border border-emerald-300/30 bg-emerald-300/15 px-4 py-3 text-sm font-black text-emerald-50 transition hover:bg-emerald-300/25 disabled:cursor-not-allowed disabled:opacity-40 active:scale-[0.98]"
                    >
                      {copy.routePrimary}
                    </button>
                  </div>

                  <div className="rounded-3xl border border-white/10 bg-white/[0.035] p-4">
                    <h3 className="font-black text-white">{copy.sharedTimeline}</h3>
                    <p className="mt-2 text-sm leading-6 text-slate-300">{copy.sharedTimelineBody}</p>
                    <textarea
                      value={timelineAnnotation}
                      onChange={(event) => setTimelineAnnotation(event.target.value)}
                      placeholder={copy.annotationPlaceholder}
                      className="mt-4 min-h-20 w-full resize-none rounded-2xl border border-white/10 bg-slate-950/70 p-3 text-sm text-slate-100 outline-none transition placeholder:text-slate-600 focus:border-cyan-300/50"
                    />
                    <button
                      onClick={addTimelineAnnotation}
                      disabled={loading || !canAnnotate(currentRole)}
                      className="mt-3 w-full rounded-2xl border border-cyan-300/25 bg-cyan-300/10 px-4 py-3 text-sm font-black text-cyan-50 transition hover:bg-cyan-300/20 disabled:cursor-not-allowed disabled:opacity-40 active:scale-[0.98]"
                    >
                      {copy.addAnnotation}
                    </button>
                  </div>
                </div>
              </section>

              <section className="rounded-3xl border border-white/10 bg-slate-950/70 p-5">
                <div className="flex items-start justify-between gap-4">
                  <div>
                    <Tooltip label={copy.tooltipEvidence}>
                      <SectionTitle>{copy.evidenceConsole}</SectionTitle>
                    </Tooltip>
                    <BodyText className="mt-1">{copy.evidenceBody}</BodyText>
                  </div>
                  <StatusBadge label={copy.traceable} tone="green" />
                </div>

                <div className="mt-5 flex flex-wrap gap-2">
                  {(["metrics", "logs", "deployments", "runbooks"] as EvidenceTab[]).map((tab) => (
                    <button
                      key={tab}
                      onClick={() => setEvidenceTab(tab)}
                      className={`rounded-full border px-4 py-2 text-sm font-bold ${
                        evidenceTab === tab
                          ? "border-cyan-300 bg-cyan-300 text-slate-950"
                          : "border-white/10 bg-white/[0.04] text-slate-300 hover:bg-white/[0.08]"
                      }`}
                    >
                      {copy[tab]}
                    </button>
                  ))}
                </div>

                <div className="mt-5 grid gap-3">
                  {defaultEvidence[language][evidenceTab].map((item, index) => (
                    <div key={item} className="rounded-2xl border border-white/10 bg-white/[0.035] p-4">
                      <LabelText className="text-cyan-300">{copy.source} {index + 1}</LabelText>
                      <div className="mt-2 text-sm leading-6 text-slate-300">{item}</div>
                    </div>
                  ))}
                </div>

                <div className="mt-5 rounded-3xl border border-violet-400/20 bg-violet-400/10 p-5">
                  <h3 className="font-black text-white">{copy.whyMultiAgent}</h3>
                  <p className="mt-3 text-sm leading-6 text-slate-300">
                    {copy.whyMultiAgentBody}
                  </p>
                </div>
              </section>
            </div>

            <div className="grid items-start gap-5 2xl:grid-cols-[1fr_1fr]">
              <section className="rounded-3xl border border-cyan-400/20 bg-slate-950/70 p-5 2xl:col-span-2">
                <div className="flex flex-col gap-4 md:flex-row md:items-start md:justify-between">
                  <div>
                    <SectionTitle>{copy.aiUsefulLayer}</SectionTitle>
                    <BodyText className="mt-1">{copy.naturalSummary}</BodyText>
                  </div>
                  <button
                    onClick={() => loadAiInsights(activeIncidentId, true)}
                    disabled={!activeIncidentId || loading}
                    className="rounded-2xl border border-cyan-300/20 bg-cyan-300/10 px-5 py-3 text-sm font-black text-cyan-50 transition hover:bg-cyan-300/20 active:scale-[0.98] disabled:cursor-not-allowed disabled:opacity-40"
                  >
                    {copy.generateAiSummary}
                  </button>
                </div>

                {!visibleAiInsight ? (
                  <div className="mt-5 rounded-3xl border border-white/10 bg-white/[0.035] p-5">
                    <EmptyState title={copy.aiUsefulLayer} description={copy.noAiInsights} action={{ label: copy.generateAiSummary, onClick: () => loadAiInsights(activeIncidentId, true) }} />
                  </div>
                ) : (
                  <div className="mt-5 grid gap-4 xl:grid-cols-[1.1fr_0.9fr]">
                    <div className="rounded-3xl border border-emerald-400/20 bg-emerald-400/10 p-5">
                      <div className="flex items-start justify-between gap-3">
                        <SectionTitle className="text-xl">{copy.naturalSummary}</SectionTitle>
                        <StatusBadge label={copy.verified} tone="green" />
                      </div>
                      <p className="mt-4 text-base leading-7 text-emerald-50">{visibleAiInsight.summary}</p>
                    </div>

                    <div className="rounded-3xl border border-white/10 bg-white/[0.035] p-5">
                      <div className="flex items-start justify-between gap-3">
                        <SectionTitle className="text-xl">{copy.rootCauseSuggestions}</SectionTitle>
                        <StatusBadge label={copy.confidenceLabel} tone="cyan" />
                      </div>
                      <div className="mt-4 grid gap-3">
                        {visibleAiInsight.root_causes.slice(0, 2).map((cause) => (
                          <div key={cause.title} className="rounded-2xl border border-white/10 bg-slate-950/40 p-4">
                            <div className="flex items-start justify-between gap-3">
                              <div className="font-black text-white">{cause.title}</div>
                              <StatusBadge label={`${Math.round(cause.confidence * 100)}%`} tone={cause.confidence > 0.8 ? "green" : "amber"} />
                            </div>
                            <div className="mt-3 grid gap-2">
                              {cause.evidence.map((item) => (
                                <div key={item} className="text-sm leading-6 text-slate-400">• {item}</div>
                              ))}
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>

                    <div className="grid gap-4 xl:col-span-2 md:grid-cols-2">
                      <AiInsightBlock title={copy.automatedTriage} tone="cyan" lines={[`${copy.severity}: ${visibleAiInsight.triage.severity}`, `${copy.assignee}: ${visibleAiInsight.triage.suggested_assignee}`]} />
                      <AiInsightBlock title={copy.escalationRecommendation} tone={visibleAiInsight.escalation.should_escalate ? "amber" : "green"} lines={[visibleAiInsight.escalation.reason]} />
                      <AiInsightBlock title={copy.actionSafetyCheck} tone="amber" lines={[`${copy.risk}: ${visibleAiInsight.safety_check.risk_level}`, visibleAiInsight.safety_check.explanation]} />
                      <AiInsightBlock title={copy.anomalyDetection} tone={visibleAiInsight.anomaly.detected ? "violet" : "green"} lines={[`${visibleAiInsight.anomaly.deviation}: ${visibleAiInsight.anomaly.current}`]} />
                    </div>

                    {visibleAiInsight.similar_incidents.length > 0 && (
                      <div className="rounded-3xl border border-violet-400/20 bg-violet-400/10 p-5 xl:col-span-2">
                        <SectionTitle className="text-xl">{copy.similarIncidents}</SectionTitle>
                        <div className="mt-4 grid gap-3 lg:grid-cols-3">
                          {visibleAiInsight.similar_incidents.map((item) => (
                            <div key={item.incident_id} className="rounded-2xl border border-white/10 bg-slate-950/40 p-4">
                              <div className="font-mono text-sm font-black text-cyan-100">{item.incident_id}</div>
                              <div className="mt-2 text-sm text-slate-300">{item.resolution}</div>
                              <div className="mt-3 flex items-center justify-between gap-3">
                                <StatusBadge label={item.severity} tone={toneForSeverity(item.severity)} />
                                <span className="text-xs font-black text-violet-100">{Math.round(item.similarity * 100)}% {copy.similarityLabel}</span>
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                )}
              </section>

              <section className="rounded-3xl border border-white/10 bg-slate-950/70 p-5">
                <div className="flex items-start justify-between gap-4">
                  <div>
                    <SectionTitle>{copy.liveAgentTimeline}</SectionTitle>
                    <BodyText className="mt-1">{copy.timelineBody}</BodyText>
                  </div>
                  <StatusBadge label={`${incidentTimeline.length} ${copy.events}`} tone={incidentTimeline.length ? "green" : "slate"} />
                </div>
                <div className="mt-5 grid gap-3 md:grid-cols-2">
                  {timeline.map((item: TimelineItem, index: number) => (
                    <div key={`${item.agent}-${index}`} className="rounded-2xl border border-white/10 bg-white/[0.035] p-4">
                      <div className="flex items-start justify-between gap-3">
                        <div className="min-w-0">
                          <div title={item.agent} className="text-sm font-black leading-5 text-cyan-100">
                            {agentDisplayName(item.agent)}
                          </div>
                          <div className="mt-1 text-xs text-slate-500">{copy.agentStep} {index + 1}</div>
                        </div>
                        <div className="shrink-0 rounded-full border border-white/10 bg-slate-950/50 px-2.5 py-1 text-xs font-black text-slate-400">
                          {index + 1}
                        </div>
                      </div>

                      <div className="mt-3">
                        <StatusBadge
                          label={displayTimelineStatus(item.agent, item.status, isResolved)}
                          tone={toneForStatus(displayTimelineStatus(item.agent, item.status, isResolved))}
                        />
                      </div>
                    </div>
                  ))}
                </div>

                <div className="mt-5 rounded-3xl border border-cyan-400/15 bg-cyan-400/10 p-4">
                  <h3 className="font-black text-white">{copy.incidentEventLog}</h3>
                  <div className="mt-4">
                    <TimelineRail
                      emptyActionLabel={copy.emptyEventAction}
                      emptyDescription={copy.emptyEventLog}
                      emptyTitle={copy.incidentEventLog}
                      events={incidentTimeline}
                      onEmptyAction={startIncident}
                    />
                  </div>
                </div>
              </section>

              <section className="rounded-3xl border border-white/10 bg-slate-950/70 p-5">
                <div className="flex items-start justify-between gap-4">
                  <div>
                    <SectionTitle>{copy.executionReview}</SectionTitle>
                    <BodyText className="mt-1">{copy.executionReviewBody}</BodyText>
                  </div>
                  <StatusBadge label={isResolved ? copy.verified : copy.pending} tone={isResolved ? "green" : "amber"} />
                </div>

                <div className="mt-5 grid gap-3 md:grid-cols-3">
                  <MiniReview label={copy.action} value={isResolved ? copy.rollbackExecuted : copy.waitingApproval} />
                  <MiniReview label={copy.validation} value={isResolved ? copy.latencyRecovered : copy.notStarted} />
                  <MiniReview label={copy.risk} value={isResolved ? copy.reduced : copy.medium} />
                </div>

                <div className="mt-5 grid gap-3 md:grid-cols-2">
                  <MiniReview label="p95 latency" value={isResolved ? "2.8s → 480ms" : "2.8s"} />
                  <MiniReview label={copy.cacheHitRatio} value={isResolved ? "41% → 89%" : "41%"} />
                </div>

                <div className={`mt-5 rounded-3xl border p-5 ${isResolved ? "border-emerald-400/20 bg-emerald-400/10" : "border-white/10 bg-white/[0.035]"}`}>
                  <div className="flex items-start justify-between gap-4">
                    <div>
                      <h3 className="font-black text-white">{isResolved ? copy.postmortemGenerated : copy.postmortemPreview}</h3>
                      <p className="mt-3 text-sm leading-6 text-slate-300">{postmortemSummary(incident, copy)}</p>
                    </div>
                    <StatusBadge label={isResolved ? copy.final : copy.draft} tone={isResolved ? "green" : "slate"} />
                  </div>
                </div>

                <div className="mt-5 grid gap-3 2xl:grid-cols-2">
                  <div className="rounded-3xl border border-cyan-400/15 bg-cyan-400/10 p-5">
                    <h3 className="font-black text-white">{copy.stakeholderUpdate}</h3>
                    <p className="mt-2 text-sm leading-6 text-cyan-50/75">{copy.stakeholderBody}</p>
                    <div className="mt-4 rounded-2xl border border-cyan-300/15 bg-slate-950/50 p-4 text-sm leading-6 text-cyan-50">
                      {stakeholderUpdate}
                    </div>
                    <button onClick={copyStakeholderUpdate} className="mt-4 w-full rounded-2xl border border-cyan-300/25 bg-cyan-300/10 px-4 py-3 text-sm font-black text-cyan-50 transition hover:bg-cyan-300/20 active:scale-[0.98]">
                      {copy.copyStakeholderUpdate}
                    </button>
                  </div>

                  <div className="rounded-3xl border border-white/10 bg-white/[0.035] p-5">
                    <h3 className="font-black text-white">{copy.postmortemTemplate}</h3>
                    <p className="mt-2 text-sm leading-6 text-slate-300">{copy.postmortemTemplateBody}</p>
                    <div className="mt-4 grid gap-3">
                      {postmortemFields.map((field) => (
                        <ApprovalLine key={field.label} label={field.label} value={field.value} />
                      ))}
                    </div>
                  </div>
                </div>

                <div className="mt-5 grid gap-3 md:grid-cols-2">
                  <button onClick={copyIncidentSummary} className="rounded-2xl border border-white/10 bg-white/[0.04] px-5 py-3 text-sm font-bold text-white transition hover:bg-white/[0.08] active:scale-[0.98]">
                    {copy.copySummary}
                  </button>
                  <button onClick={exportAuditLog} className="rounded-2xl border border-white/10 bg-white/[0.04] px-5 py-3 text-sm font-bold text-white transition hover:bg-white/[0.08] active:scale-[0.98]">
                    {copy.exportAudit}
                  </button>
                  <button onClick={printReport} className="rounded-2xl border border-cyan-300/20 bg-cyan-300/10 px-5 py-3 text-sm font-bold text-cyan-50 transition hover:bg-cyan-300/20 active:scale-[0.98] md:col-span-2">
                    <span className="inline-flex items-center gap-2">
                      <Icon name="print" className="h-4 w-4" />
                      {copy.printReport}
                    </span>
                  </button>
                </div>
              </section>
            </div>
          </div>

          <aside className="space-y-5 xl:sticky xl:top-24">
            <section className="rounded-3xl border border-cyan-400/20 bg-cyan-400/10 p-5">
              <div className="flex items-start justify-between gap-4">
                  <div>
                  <SectionTitle>{copy.ownership}</SectionTitle>
                  <p className="mt-1 text-sm text-cyan-100/80">{copy.ownershipBody}</p>
                </div>
                <StatusBadge label={incident?.assignee || copy.unassigned} tone={incident?.assignee && incident.assignee !== "unassigned" ? "green" : "amber"} />
              </div>

              <div className="mt-5 grid gap-2">
                {responderOptions.map((assignee) => (
                  <button
                    key={assignee}
                    onClick={() => assignActiveIncident(assignee)}
                    disabled={loading || !canAssignIncident}
                    className={`rounded-2xl border px-4 py-3 text-left text-sm font-black transition disabled:cursor-not-allowed disabled:opacity-40 ${
                      incident?.assignee === assignee
                        ? "border-emerald-300 bg-emerald-300 text-slate-950"
                        : "border-white/10 bg-slate-950/40 text-cyan-50 hover:bg-white/[0.08]"
                    }`}
                  >
                    {assignee}
                  </button>
                ))}
              </div>
              {assignmentValidation && (
                <div className="mt-4 rounded-2xl border border-amber-300/20 bg-amber-300/10 p-3 text-sm font-semibold text-amber-50">
                  {assignmentValidation}
                </div>
              )}
            </section>

            <section className="rounded-3xl border border-amber-400/20 bg-amber-400/10 p-5">
              <div className="flex items-start justify-between gap-4">
                  <div>
                  <Tooltip label={copy.tooltipSafety}>
                    <SectionTitle>{copy.safetyGate}</SectionTitle>
                  </Tooltip>
                  <p className="mt-1 text-sm text-amber-100/80">{copy.safetyGateBody}</p>
                </div>
                <StatusBadge label={isResolved ? copy.approved : copy.approvalRequired} tone={isResolved ? "green" : "amber"} />
              </div>

              <div className="mt-5 space-y-3 text-sm">
                <PolicyItem label={copy.ruleMatched} value={copy.productionRollback} />
                <PolicyItem label={copy.guardrail} value={copy.humanApprovalRequired} />
                <PolicyItem label={copy.rollbackPlan} value={copy.restoreCacheConfig} />
                <PolicyItem label={copy.blockedAlternative} value={copy.databaseRestartBlocked} />
              </div>

              <button onClick={requestApproval} disabled={loading || !incident?.incident_id || isResolved} className="mt-5 w-full rounded-2xl bg-emerald-300 px-5 py-3 text-sm font-black text-slate-950 hover:bg-emerald-200 disabled:cursor-not-allowed disabled:opacity-40">
                {isResolved ? copy.remediationApproved : isAwaitingApproval ? copy.approveRemediation : copy.startIncidentFirst}
              </button>
            </section>

            <section className="rounded-3xl border border-violet-400/20 bg-violet-400/10 p-5">
              <div className="flex items-start justify-between gap-4">
                  <div>
                  <SectionTitle>{copy.approvalDrawer}</SectionTitle>
                  <p className="mt-1 text-sm text-violet-100/80">{copy.approvalDrawerBody}</p>
                </div>
                <StatusBadge label={isResolved ? copy.closed : copy.review} tone={isResolved ? "green" : "violet"} />
              </div>

              <div className="mt-5 space-y-3">
                <ApprovalLine label={copy.recommendedAction} value={recommendedAction(incident, copy)} />
                <ApprovalLine label={copy.evidenceUsed} value={copy.evidenceUsedValue} />
                <ApprovalLine label={copy.policyTriggered} value={copy.policyTriggeredValue} />
                <ApprovalLine label={copy.rollbackSafety} value={copy.rollbackSafetyValue} />
              </div>
            </section>

            <section className="rounded-3xl border border-white/10 bg-slate-950/70 p-5">
              <SectionTitle>{copy.auditTrail}</SectionTitle>
              <div className="mt-5 space-y-3">
                <AuditItem label={copy.incidentCreated} value={incident ? copy.recorded : copy.pending} />
                <AuditItem label={copy.evidenceLinked} value={incident ? copy.evidenceLinkedValue : copy.pending} />
                <AuditItem label={copy.policyEvaluated} value={incident ? copy.approvalRequired : copy.pending} />
                <AuditItem label={copy.operatorApproval} value={isResolved ? copy.approved : copy.pending} />
              </div>
            </section>
          </aside>
        </div>

        {incidents.length > 0 && (
          <section id="incidents" className="mt-6 scroll-mt-32 rounded-3xl border border-white/10 bg-slate-950/70 p-6">
            <SectionTitle>{copy.storedIncidents}</SectionTitle>
            <div className="mt-4 grid gap-3 lg:grid-cols-3">
              {incidents.slice(0, 3).map((item) => (
                <IncidentCard
                  key={item.incident_id}
                  assignee={item.assignee}
                  copy={{
                    age: copy.age,
                    assignee: copy.assignee,
                    incident: copy.incident,
                    noActiveIncident: copy.noActiveIncident,
                    service: copy.service,
                    severity: copy.severity,
                    status: copy.status,
                    unassigned: copy.unassigned,
                  }}
                  incidentId={item.incident_id}
                  service={item.triage_result?.affected_service || item.service}
                  severity={item.triage_result?.severity || item.severity}
                  status={item.status}
                />
              ))}
            </div>
            <div className="mt-4">
              <IncidentTable
                incidents={incidents}
                copy={{
                  all: copy.all,
                  assignee: copy.assignee,
                  actions: copy.actions,
                  copyId: copy.copyId,
                  filter: copy.filter,
                  incident: copy.incident,
                  next: copy.next,
                  open: copy.open,
                  page: copy.page,
                  previous: copy.previous,
                  service: copy.service,
                  severity: copy.severity,
                  sort: copy.sort,
                  status: copy.status,
                }}
              />
            </div>
          </section>
        )}
      </section>

      <ConfirmDialog
        cancelLabel={copy.confirmCancel}
        confirmLabel={copy.confirmApproveAction}
        description={copy.confirmApproveBody}
        isOpen={confirmApprovalOpen}
        onCancel={() => setConfirmApprovalOpen(false)}
        onConfirm={approve}
        title={copy.confirmApproveTitle}
      />
    </PlatformShell>
  );
}

function SystemStripItem({ label, value, tone }: { label: string; value: string; tone: "cyan" | "green" | "amber" | "red" | "violet" | "slate" }) {
  return (
    <div className="rounded-2xl border border-white/10 bg-white/[0.035] p-4">
      <div className="text-xs uppercase tracking-wider text-slate-500">{label}</div>
      <div className="mt-2 truncate font-mono text-sm text-slate-200">{value}</div>
      <div className="mt-3"><StatusBadge label={tone} tone={tone} /></div>
    </div>
  );
}

function MetricCard({ title, value }: { title: string; value: string }) {
  return (
    <div className="rounded-3xl border border-white/10 bg-white/[0.035] p-4">
      <div className="text-xs uppercase tracking-wider text-slate-500">{title}</div>
      <div className="mt-2 truncate text-xl font-black text-white">{value}</div>
    </div>
  );
}

function PolicyItem({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-2xl border border-amber-400/20 bg-slate-950/40 p-3">
      <div className="text-xs uppercase tracking-wider text-amber-200/70">{label}</div>
      <div className="mt-1 font-semibold text-amber-50">{value}</div>
    </div>
  );
}

function AuditItem({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex items-center justify-between rounded-2xl border border-white/10 bg-white/[0.035] p-3 text-sm">
      <span className="font-semibold text-slate-200">{label}</span>
      <span className="font-mono text-cyan-200">{value}</span>
    </div>
  );
}

function ApprovalLine({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-2xl border border-violet-400/20 bg-slate-950/40 p-3">
      <div className="text-xs uppercase tracking-wider text-violet-200/70">{label}</div>
      <div className="mt-1 text-sm font-semibold leading-6 text-violet-50">{value}</div>
    </div>
  );
}

function AiInsightBlock({ title, tone, lines }: { title: string; tone: "cyan" | "green" | "amber" | "red" | "violet" | "slate"; lines: string[] }) {
  return (
    <div className="rounded-3xl border border-white/10 bg-white/[0.035] p-4">
      <div className="flex flex-col gap-2 sm:flex-row sm:items-start sm:justify-between">
        <h3 className="text-sm font-black leading-5 text-white">{title}</h3>
        <StatusBadge label={tone} tone={tone} />
      </div>
      <div className="mt-3 grid gap-2">
        {lines.map((line) => (
          <div key={line} className="text-sm leading-6 text-slate-300">{line}</div>
        ))}
      </div>
    </div>
  );
}

function CommandMetric({ title, label, value, tone }: { title: string; label: string; value: string; tone: "cyan" | "green" | "amber" | "red" | "violet" | "slate" }) {
  return (
    <div className="rounded-3xl border border-white/10 bg-white/[0.035] p-4">
      <div className="flex items-start justify-between gap-3">
        <div>
          <div className="text-xs uppercase tracking-wider text-slate-500">{title}</div>
          <div className="mt-1 text-sm font-semibold text-slate-300">{label}</div>
        </div>
        <StatusBadge label={tone} tone={tone} />
      </div>
      <div className="mt-4 text-2xl font-black text-white">{value}</div>
    </div>
  );
}

function MiniReview({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-2xl border border-white/10 bg-white/[0.035] p-4">
      <div className="text-xs uppercase tracking-wider text-slate-500">{label}</div>
      <div className="mt-2 font-black text-white">{value}</div>
    </div>
  );
}
