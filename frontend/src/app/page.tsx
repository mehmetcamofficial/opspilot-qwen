"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { PlatformShell } from "@/components/PlatformShell";
import { StatusBadge } from "@/components/StatusBadge";

type Language = "EN" | "TR";

const storageKey = "opspilot-language";

const landingContent = {
  EN: {
    badges: ["Qwen-powered", "Autopilot Agent Track", "Human-in-the-loop"],
    hero: {
      titleLine1: "AI incident operations,",
      titleLine2: "controlled by agents.",
      description:
        "OpsPilot investigates incidents, proposes safe remediation, keeps operators in control, and documents everything.",
      primaryCta: "Open Command Center",
      secondaryCta: "Run Simulation",
      tertiaryCta: "View Architecture",
      proofItems: [
        ["Track fit", "Autopilot Agent"],
        ["Core loop", "Investigate -> approve -> recover"],
        ["Model layer", "Qwen-ready / mock-safe"],
        ["Deployment", "Vercel + FastAPI + Alibaba plan"],
      ] as const,
    },
    live: {
      title: "Live command flow",
      subtitle: "Checkout API latency incident",
      autoplay: "autoplay",
      stepLabel: "Step",
      steps: [
        {
          title: "Alert intake",
          detail: "Checkout API latency anomaly enters the incident command flow.",
          metric: "p95 latency",
          value: "2.8s",
        },
        {
          title: "Evidence correlation",
          detail: "Metrics, logs, deployment context, and runbooks are linked.",
          metric: "cache hit ratio",
          value: "41%",
        },
        {
          title: "Safety gate",
          detail: "Production rollback is paused until human approval.",
          metric: "policy",
          value: "approval",
        },
        {
          title: "Recovery verified",
          detail: "Rollback completes and telemetry confirms recovery.",
          metric: "p95 latency",
          value: "480ms",
        },
      ] as const,
      metrics: {
        latency: {
          title: "p95 latency",
          criticalValue: "2.8s",
          criticalDetail: "critical",
          healthyValue: "480ms",
          healthyDetail: "recovered",
        },
        cache: {
          title: "cache hit ratio",
          criticalValue: "41%",
          criticalDetail: "degraded",
          healthyValue: "89%",
          healthyDetail: "healthy",
        },
        risk: {
          title: "risk gate",
          criticalValue: "watching",
          criticalDetail: "standby",
          healthyValue: "approval",
          healthyDetail: "active",
        },
        postmortem: {
          title: "postmortem",
          criticalValue: "draft",
          criticalDetail: "pending",
          healthyValue: "ready",
          healthyDetail: "generated",
        },
      },
    },
    overview: {
      why: {
        badge: "Why",
        title: "Reduce incident noise.",
        body:
          "Turn scattered alerts into a prioritized, evidence-backed command path. Operators focus on decisions, not data gathering.",
      },
      how: {
        badge: "How",
        title: "AI agents gather and score context.",
        body:
          "Qwen-powered agents correlate metrics, logs, deployment data, and runbooks automatically in seconds.",
      },
      what: {
        badge: "What",
        title: "A trusted recovery workflow.",
        body:
          "Human approval stays central. Every step is documented for audit, learning, and compliance.",
      },
    },
    compare: {
      badge: "Before vs After OpsPilot",
      title: "From chaotic remediation to structured incident command.",
      pairs: [
        ["Manual triage", "Slow, inconsistent decisions", "Fast, evidence-backed actions"],
        ["Slack chaos", "Scattered chat threads", "Clear command flow"],
        ["Missing audit trail", "Unclear postmortem", "Full reasoning log"],
        ["Risky fixes", "Unsafe manual rollback", "Human-approved remediation"],
      ] as const,
    },
    pillars: {
      badge: "Core platform pillars",
      title: "One lifecycle. Four controlled stages.",
      description:
        "The landing page now focuses on the product's core path instead of scattering attention across secondary modules.",
      cta: "Inspect Command Center",
      items: [
        {
          title: "Investigation",
          subtitle: "Agents reduce alert noise into evidence-backed incident context.",
          bullets: ["Triage", "Observability signals", "Runbook retrieval"],
        },
        {
          title: "Safety",
          subtitle: "Risk policy blocks unsafe automation before production impact grows.",
          bullets: ["Policy evaluation", "Risk separation", "Rollback guardrails"],
        },
        {
          title: "Approval",
          subtitle: "Operators stay in control with a clear decision package.",
          bullets: ["Approval drawer", "Evidence lineage", "Human-in-the-loop"],
        },
        {
          title: "Postmortem",
          subtitle: "Every action becomes an auditable learning record.",
          bullets: ["Execution review", "Recovery proof", "Incident summary"],
        },
      ] as const,
    },
    infoPanels: [
      {
        title: "For judges",
        label: "proof path",
        body:
          "Start at the landing page, open the Command Center, run an incident, approve remediation, then show the generated postmortem.",
      },
      {
        title: "For operators",
        label: "control",
        body:
          "OpsPilot does not blindly execute production actions. It separates confidence, risk, policy, and human approval.",
      },
      {
        title: "For cloud proof",
        label: "architecture",
        body:
          "The backend is Qwen-ready and can move from local mock mode to Alibaba Cloud deployment once credits are active.",
      },
    ] as const,
  },
  TR: {
    badges: ["Qwen destekli", "Autopilot ajan akışı", "İnsan onaylı"],
    hero: {
      titleLine1: "Yapay zeka olay operasyonları,",
      titleLine2: "ajanlar tarafından kontrol edilir.",
      description:
        "OpsPilot olayları inceler, güvenli iyileştirme önerir, operatörleri kontrolde tutar ve her şeyi belgelendirir.",
      primaryCta: "Komuta Merkezini Aç",
      secondaryCta: "Simülasyonu Çalıştır",
      tertiaryCta: "Mimariyi Gör",
      proofItems: [
        ["Eşleşme", "Autopilot Agent"],
        ["Ana döngü", "İncele -> onayla -> kurtar"],
        ["Model katmanı", "Qwen uyumlu / mock-safe"],
        ["Dağıtım", "Vercel + FastAPI + Alibaba planı"],
      ] as const,
    },
    live: {
      title: "Canlı komut akışı",
      subtitle: "Checkout API gecikme olayı",
      autoplay: "otomatik",
      stepLabel: "Adım",
      steps: [
        {
          title: "Uyarı alımı",
          detail: "Checkout API gecikme anomalisi olay komut akışına girer.",
          metric: "p95 gecikme",
          value: "2.8s",
        },
        {
          title: "Kanıt eşleme",
          detail: "Metrikler, loglar, dağıtım bağlamı ve runbook'lar bağlanır.",
          metric: "önbellek isabet oranı",
          value: "41%",
        },
        {
          title: "Güvenlik kapısı",
          detail: "Üretim geri dönüşü insan onayı gelene kadar bekletilir.",
          metric: "politika",
          value: "onay",
        },
        {
          title: "Kurtarma doğrulandı",
          detail: "Geri dönüş tamamlanır ve telemetri kurtarmayı doğrular.",
          metric: "p95 gecikme",
          value: "480ms",
        },
      ] as const,
      metrics: {
        latency: {
          title: "p95 gecikme",
          criticalValue: "2.8s",
          criticalDetail: "kritik",
          healthyValue: "480ms",
          healthyDetail: "iyileşti",
        },
        cache: {
          title: "önbellek isabet oranı",
          criticalValue: "41%",
          criticalDetail: "zayıf",
          healthyValue: "89%",
          healthyDetail: "sağlıklı",
        },
        risk: {
          title: "risk kapısı",
          criticalValue: "izleniyor",
          criticalDetail: "beklemede",
          healthyValue: "onay",
          healthyDetail: "aktif",
        },
        postmortem: {
          title: "postmortem",
          criticalValue: "taslak",
          criticalDetail: "bekliyor",
          healthyValue: "hazır",
          healthyDetail: "oluşturuldu",
        },
      },
    },
    overview: {
      why: {
        badge: "Neden",
        title: "Olay gürültüsünü azaltın.",
        body:
          "Dağınık alarmları öncelikli, kanıta dayalı bir komut akışına dönüştürün. Operatörler veri toplamak yerine kararlara odaklanır.",
      },
      how: {
        badge: "Nasıl",
        title: "Yapay zeka ajanları bağlamı toplar ve puanlar.",
        body:
          "Qwen destekli ajanlar metrikleri, logları, dağıtım verisini ve runbook'ları saniyeler içinde otomatik olarak ilişkilendirir.",
      },
      what: {
        badge: "Ne",
        title: "Güvenilir bir kurtarma akışı.",
        body:
          "İnsan onayı merkezde kalır. Her adım denetim, öğrenme ve uyumluluk için belgelenir.",
      },
    },
    compare: {
      badge: "OpsPilot Önce / Sonra",
      title: "Kaotik müdahaleden yapılandırılmış olay komutasına.",
      pairs: [
        ["Manuel triage", "Yavaş, tutarsız kararlar", "Hızlı, kanıta dayalı eylemler"],
        ["Slack karmaşası", "Dağınık sohbet başlıkları", "Net komut akışı"],
        ["Eksik denetim izi", "Belirsiz postmortem", "Tam akıl yürütme kaydı"],
        ["Riskli düzeltmeler", "Güvensiz manuel geri dönüş", "İnsan onaylı iyileştirme"],
      ] as const,
    },
    pillars: {
      badge: "Temel platform sütunları",
      title: "Tek yaşam döngüsü. Dört kontrollü aşama.",
      description:
        "Açılış sayfası artık dikkatleri ikincil modüllere dağıtmak yerine ürünün ana akışına odaklanıyor.",
      cta: "Komuta Merkezini İncele",
      items: [
        {
          title: "İnceleme",
          subtitle: "Ajanlar alarm gürültüsünü kanıta dayalı olay bağlamına indirir.",
          bullets: ["Triage", "Gözlemlenebilirlik sinyalleri", "Runbook erişimi"],
        },
        {
          title: "Güvenlik",
          subtitle: "Risk politikası, üretim etkisi büyümeden güvensiz otomasyonu engeller.",
          bullets: ["Politika değerlendirmesi", "Risk ayrımı", "Geri dönüş korkulukları"],
        },
        {
          title: "Onay",
          subtitle: "Operatörler net bir karar paketiyle kontrolde kalır.",
          bullets: ["Onay paneli", "Kanıt zinciri", "İnsan onayı"],
        },
        {
          title: "Postmortem",
          subtitle: "Her eylem denetlenebilir bir öğrenme kaydına dönüşür.",
          bullets: ["Yürütme incelemesi", "Kurtarma kanıtı", "Olay özeti"],
        },
      ] as const,
    },
    infoPanels: [
      {
        title: "Jüri için",
        label: "kanıt yolu",
        body:
          "Açılış sayfasından başlayın, Komuta Merkezini açın, bir olayı çalıştırın, iyileştirmeyi onaylayın, sonra oluşturulan postmortem'i gösterin.",
      },
      {
        title: "Operatörler için",
        label: "kontrol",
        body:
          "OpsPilot üretim eylemlerini körü körüne yürütmez. Güven, risk, politika ve insan onayını ayırır.",
      },
      {
        title: "Bulut kanıtı için",
        label: "mimari",
        body:
          "Arka uç Qwen uyumludur ve krediler aktif olduğunda yerel mock modundan Alibaba Cloud dağıtımına geçebilir.",
      },
    ] as const,
  },
} satisfies Record<Language, unknown>;

function getStoredLanguage(): Language {
  if (typeof window === "undefined") {
    return "EN";
  }

  const stored = window.localStorage.getItem(storageKey);
  return stored === "TR" ? "TR" : "EN";
}

export default function Home() {
  const [activeStep, setActiveStep] = useState(0);
  const [language, setLanguage] = useState<Language>("EN");

  useEffect(() => {
    const syncLanguage = () => {
      setLanguage(getStoredLanguage());
    };

    const handleStorage = () => {
      syncLanguage();
    };

    syncLanguage();
    window.addEventListener("opspilot-language-change", syncLanguage as EventListener);
    window.addEventListener("storage", handleStorage);

    return () => {
      window.removeEventListener("opspilot-language-change", syncLanguage as EventListener);
      window.removeEventListener("storage", handleStorage);
    };
  }, []);

  useEffect(() => {
    const timer = window.setTimeout(() => {
      setActiveStep((current) => (current + 1) % landingContent[language].live.steps.length);
    }, 1700);

    return () => window.clearTimeout(timer);
  }, [language, activeStep]);

  const copy = landingContent[language];
  const current = copy.live.steps[activeStep];
  const selectedMetrics = copy.live.metrics;
  const activeMetrics = [
    [selectedMetrics.latency.title, activeStep >= 3 ? selectedMetrics.latency.healthyValue : selectedMetrics.latency.criticalValue, activeStep >= 3 ? selectedMetrics.latency.healthyDetail : selectedMetrics.latency.criticalDetail],
    [selectedMetrics.cache.title, activeStep >= 3 ? selectedMetrics.cache.healthyValue : selectedMetrics.cache.criticalValue, activeStep >= 3 ? selectedMetrics.cache.healthyDetail : selectedMetrics.cache.criticalDetail],
    [selectedMetrics.risk.title, activeStep >= 2 ? selectedMetrics.risk.healthyValue : selectedMetrics.risk.criticalValue, activeStep >= 2 ? selectedMetrics.risk.healthyDetail : selectedMetrics.risk.criticalDetail],
    [selectedMetrics.postmortem.title, activeStep >= 3 ? selectedMetrics.postmortem.healthyValue : selectedMetrics.postmortem.criticalValue, activeStep >= 3 ? selectedMetrics.postmortem.healthyDetail : selectedMetrics.postmortem.criticalDetail],
  ] as const;

  return (
    <PlatformShell>
      <section className="mx-auto max-w-7xl px-6 pb-12 pt-10 relative overflow-hidden">
        {/* landing-video-background-layer */}
        <div className="pointer-events-none absolute inset-0 -z-10 overflow-hidden">
          <video
            className="absolute inset-0 h-full w-full object-cover opacity-[0.28]"
            src="/opspilot-ambient-bg.webm"
            autoPlay
            muted
            loop
            playsInline
            preload="metadata"
            aria-hidden="true"
          />
          <div className="absolute inset-0 bg-[radial-gradient(circle_at_18%_28%,rgba(56,189,248,0.16),transparent_34%),radial-gradient(circle_at_86%_18%,rgba(167,139,250,0.14),transparent_36%),radial-gradient(circle_at_50%_100%,rgba(34,211,238,0.08),transparent_28%)]" />
          <div className="absolute inset-0 bg-[linear-gradient(to_right,rgba(2,6,23,0.18),rgba(15,23,42,0.42)_48%,rgba(15,23,42,0.56))]" />
          <div className="absolute inset-0 bg-[linear-gradient(to_bottom,rgba(2,6,23,0.02),rgba(15,23,42,0.48)_72%,rgba(15,23,42,0.76))]" />
        </div>

        {/* Hero Section with Live Command Flow on Right */}
        <div className="grid min-h-[550px] items-center gap-8 lg:grid-cols-2 mb-6">
          {/* Left: Hero Content */}
          <div className="flex flex-col justify-center">
            <div className="mb-5 flex flex-wrap gap-3">
              <StatusBadge label={copy.badges[0]} tone="cyan" />
              <StatusBadge label={copy.badges[1]} tone="violet" />
              <StatusBadge label={copy.badges[2]} tone="green" />
            </div>

            <h1 className="max-w-4xl text-5xl font-black leading-[0.95] tracking-[-0.06em] text-white md:text-6xl">
              {copy.hero.titleLine1}
              <span className="block bg-gradient-to-r from-cyan-300 via-sky-300 to-violet-300 bg-clip-text text-transparent">
                {copy.hero.titleLine2}
              </span>
            </h1>

            <p className="mt-6 max-w-2xl text-base leading-7 text-slate-200">
              {copy.hero.description}
            </p>

            <div className="mt-8 flex flex-wrap gap-3">
              <Link
                href="/dashboard"
                className="rounded-2xl bg-cyan-300 px-6 py-4 text-sm font-black text-slate-950 shadow-[0_0_36px_rgba(34,211,238,0.14)] hover:bg-cyan-200"
              >
                {copy.hero.primaryCta}
              </Link>

              <Link
                href="/simulation"
                className="rounded-2xl border border-white/10 bg-white/[0.05] px-6 py-4 text-sm font-black text-white hover:bg-white/[0.09]"
              >
                {copy.hero.secondaryCta}
              </Link>

              <Link
                href="/architecture"
                className="rounded-2xl border border-violet-400/20 bg-violet-400/12 px-6 py-4 text-sm font-black text-violet-100 hover:bg-violet-400/22"
              >
                {copy.hero.tertiaryCta}
              </Link>
            </div>

            <div className="mt-6 grid gap-3 sm:grid-cols-2 max-w-2xl">
              {copy.hero.proofItems.map(([label, value]) => (
                <div key={label} className="rounded-2xl border border-white/10 bg-white/[0.05] p-4">
                  <div className="text-xs uppercase tracking-wider text-slate-400">{label}</div>
                  <div className="mt-2 font-black text-white">{value}</div>
                </div>
              ))}
            </div>
          </div>

          {/* Right: Live Command Flow (Compact) */}
          <div className="rounded-[2rem] border border-cyan-400/18 bg-slate-900/72 p-6 shadow-[0_0_50px_rgba(34,211,238,0.1)] h-full flex flex-col">
            <div className="flex items-start justify-between gap-3 mb-4">
              <div>
                <h2 className="text-xl font-black text-white">{copy.live.title}</h2>
              <p className="mt-1 text-xs text-slate-300">{copy.live.subtitle}</p>
            </div>
            <StatusBadge label={copy.live.autoplay} tone="green" />
          </div>

            <div className="grid gap-2 grid-cols-2 mb-4 flex-grow">
              <MetricCard title={activeMetrics[0][0]} value={activeMetrics[0][1]} detail={activeMetrics[0][2]} />
              <MetricCard title={activeMetrics[1][0]} value={activeMetrics[1][1]} detail={activeMetrics[1][2]} />
              <MetricCard title={activeMetrics[2][0]} value={activeMetrics[2][1]} detail={activeMetrics[2][2]} />
              <MetricCard title={activeMetrics[3][0]} value={activeMetrics[3][1]} detail={activeMetrics[3][2]} />
            </div>

            <div className="rounded-2xl border border-white/10 bg-white/[0.05] p-4 mb-4 flex-grow flex flex-col justify-center">
              <div className="text-xs font-black uppercase tracking-[0.24em] text-cyan-300">
                {copy.live.stepLabel} {activeStep + 1}
              </div>
              <h3 className="mt-2 text-lg font-black text-white">{current.title}</h3>
              <p className="mt-2 text-xs leading-5 text-slate-200">{current.detail}</p>

              <div className="mt-3 rounded-xl border border-white/10 bg-slate-900/65 p-3">
                <div className="text-xs uppercase tracking-wider text-slate-400">{current.metric}</div>
                <div className="mt-1 text-2xl font-black text-white">{current.value}</div>
              </div>
            </div>

            <div className="space-y-2 max-h-[160px] overflow-y-auto">
              {copy.live.steps.map((step, index) => (
                <button
                  key={step.title}
                  onClick={() => setActiveStep(index)}
                  className={`flex w-full items-center justify-between rounded-xl border p-2 text-left transition text-xs ${
                    index === activeStep
                      ? "border-cyan-300 bg-cyan-300 text-slate-950"
                      : index < activeStep
                      ? "border-emerald-400/20 bg-emerald-400/10 text-emerald-100"
                      : "border-white/10 bg-white/[0.05] text-slate-200 hover:bg-white/[0.09]"
                  }`}
                >
                  <span className="font-black">{step.title}</span>
                  <span className="rounded-full border border-current/20 px-2 py-0.5 text-xs font-black">
                    {index + 1}
                  </span>
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Why / How / What - Three Equal Cards */}
        <section className="mb-6 grid gap-4 lg:grid-cols-3">
          <div className="rounded-3xl border border-white/10 bg-slate-900/68 p-6 flex flex-col">
            <StatusBadge label={copy.overview.why.badge} tone="cyan" />
            <h3 className="mt-4 text-2xl font-black text-white">{copy.overview.why.title}</h3>
            <p className="mt-3 text-sm leading-6 text-slate-300 flex-grow">{copy.overview.why.body}</p>
          </div>

          <div className="rounded-3xl border border-white/10 bg-slate-900/68 p-6 flex flex-col">
            <StatusBadge label={copy.overview.how.badge} tone="violet" />
            <h3 className="mt-4 text-2xl font-black text-white">{copy.overview.how.title}</h3>
            <p className="mt-3 text-sm leading-6 text-slate-300 flex-grow">{copy.overview.how.body}</p>
          </div>

          <div className="rounded-3xl border border-white/10 bg-slate-900/68 p-6 flex flex-col">
            <StatusBadge label={copy.overview.what.badge} tone="green" />
            <h3 className="mt-4 text-2xl font-black text-white">{copy.overview.what.title}</h3>
            <p className="mt-3 text-sm leading-6 text-slate-300 flex-grow">{copy.overview.what.body}</p>
          </div>
        </section>

        {/* Before vs After - Full Width 2x2 Grid */}
        <section className="mb-6 rounded-[2rem] border border-white/10 bg-slate-900/68 p-8">
          <div className="mb-6">
            <StatusBadge label={copy.compare.badge} tone="violet" />
            <h2 className="mt-4 text-3xl font-black text-white md:text-4xl">{copy.compare.title}</h2>
          </div>

          <div className="grid gap-6 md:grid-cols-2">
            {copy.compare.pairs.map(([heading, before, after]) => (
              <ValuePair key={heading} heading={heading} before={before} after={after} />
            ))}
          </div>
        </section>

        <section className="mt-8 rounded-[2rem] border border-white/10 bg-slate-900/68 p-6">
          <div className="flex flex-col gap-3 md:flex-row md:items-end md:justify-between">
            <div>
              <StatusBadge label={copy.pillars.badge} tone="cyan" />
              <h2 className="mt-4 text-3xl font-black text-white md:text-5xl">{copy.pillars.title}</h2>
              <p className="mt-4 max-w-3xl text-slate-300">{copy.pillars.description}</p>
            </div>

            <Link
              href="/dashboard"
              className="rounded-2xl border border-cyan-400/20 bg-cyan-400/10 px-5 py-3 text-sm font-black text-cyan-100 hover:bg-cyan-400/20"
            >
              {copy.pillars.cta}
            </Link>
          </div>

          <div className="mt-6 grid gap-4 md:grid-cols-2 xl:grid-cols-4">
            {copy.pillars.items.map((pillar, index) => (
              <div key={pillar.title} className="rounded-3xl border border-white/10 bg-white/[0.05] p-5">
                <div className="flex items-center justify-between gap-3">
                  <div className="rounded-2xl border border-cyan-400/20 bg-cyan-400/10 px-3 py-2 text-xs font-black text-cyan-100">
                    0{index + 1}
                  </div>
                  <StatusBadge
                    label={pillar.title.toLowerCase()}
                    tone={index === 0 ? "cyan" : index === 1 ? "amber" : index === 2 ? "violet" : "green"}
                  />
                </div>

                <h3 className="mt-5 text-2xl font-black text-white">{pillar.title}</h3>
                <p className="mt-3 min-h-[72px] text-sm leading-6 text-slate-300">{pillar.subtitle}</p>

                <div className="mt-5 space-y-2">
                  {pillar.bullets.map((bullet) => (
                    <div key={bullet} className="rounded-2xl border border-white/10 bg-slate-900/60 px-4 py-3 text-sm font-bold text-slate-100">
                      {bullet}
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </section>

        <section className="mt-8 grid gap-5 lg:grid-cols-[1fr_1fr_1fr]">
          {copy.infoPanels.map((panel) => (
            <InfoPanel key={panel.title} title={panel.title} label={panel.label} body={panel.body} />
          ))}
        </section>
      </section>
    </PlatformShell>
  );
}

function MetricCard({ title, value, detail }: { title: string; value: string; detail: string }) {
  return (
    <div className="rounded-2xl border border-white/10 bg-white/[0.035] p-4">
      <div className="text-xs uppercase tracking-wider text-slate-500">{title}</div>
      <div className="mt-2 text-2xl font-black text-white">{value}</div>
      <div className="mt-2 text-xs font-bold text-cyan-200">{detail}</div>
    </div>
  );
}

function InfoPanel({ title, label, body }: { title: string; label: string; body: string }) {
  return (
    <div className="rounded-3xl border border-white/10 bg-slate-900/68 p-6">
      <StatusBadge label={label} tone="violet" />
      <h3 className="mt-4 text-2xl font-black text-white">{title}</h3>
      <p className="mt-3 text-sm leading-7 text-slate-300">{body}</p>
    </div>
  );
}

function ValuePair({ heading, before, after }: { heading: string; before: string; after: string }) {
  return (
    <div className="rounded-3xl border border-white/10 bg-white/[0.035] p-5">
      <div className="text-xs uppercase tracking-wider text-slate-500">{heading}</div>
      <div className="mt-4 flex items-start gap-3 text-sm text-slate-300">
        <div className="min-w-[8rem] font-black text-white">Before</div>
        <div>{before}</div>
      </div>
      <div className="mt-3 flex items-start gap-3 text-sm text-slate-300">
        <div className="min-w-[8rem] font-black text-white">After</div>
        <div>{after}</div>
      </div>
    </div>
  );
}
