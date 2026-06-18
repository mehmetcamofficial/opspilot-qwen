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
      finalCtaTitle: "Ready to take command?",
      finalCtaBody: "Open the Command Center and walk through the controlled incident lifecycle.",
      mockupCaption: "Live incident command — see it in action →",
      mockupRows: ["Signal intake", "Evidence linked", "Human approval", "Recovery record"] as const,
    },
    socialProof: ["Built for teams running on Qwen", "Deployable on Alibaba Cloud", "Human-in-the-loop by design"] as const,
    problem: {
      title: "Incidents do not wait. Your tools should not either.",
      body:
        "Slow response turns signals into outages, chat threads into confusion, and recovery into guesswork. OpsPilot gives operators a controlled command path before pressure becomes chaos.",
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
      beforeTitle: "Before OpsPilot",
      afterTitle: "After OpsPilot",
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
        title: "Platform Engineers",
        icon: "⌘",
        body:
          "Stop triaging in scattered chat. OpsPilot gives you structured evidence, ranked hypotheses, and safe rollback in one command flow.",
      },
      {
        title: "Incident Commanders",
        icon: "◉",
        body:
          "Stay in control without slowing response. Every AI recommendation waits for your approval before touching production.",
      },
      {
        title: "Engineering Leaders",
        icon: "▥",
        body:
          "Full audit trail, MTTR trends, and post-incident reports generated automatically. Visibility without another meeting.",
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
      finalCtaTitle: "Komutayı almaya hazır mısınız?",
      finalCtaBody: "Komuta Merkezini açın ve kontrollü olay yaşam döngüsünü inceleyin.",
      mockupCaption: "Canlı olay komutunu görün — simülasyonda incele →",
      mockupRows: ["Sinyal alımı", "Kanıt bağlandı", "İnsan onayı", "Kurtarma kaydı"] as const,
    },
    socialProof: ["Qwen üzerinde çalışan ekipler için", "Alibaba Cloud'a dağıtılabilir", "Tasarım gereği insan onaylı"] as const,
    problem: {
      title: "Olaylar beklemez. Araçlarınız da beklememeli.",
      body:
        "Yavaş yanıt sinyalleri kesintiye, sohbetleri karmaşaya ve kurtarmayı tahmine dönüştürür. OpsPilot, baskı kaosa dönüşmeden operatörlere kontrollü bir komut yolu verir.",
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
      beforeTitle: "OpsPilot Öncesi",
      afterTitle: "OpsPilot Sonrası",
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
        title: "Platform Mühendisleri",
        icon: "⌘",
        body:
          "Dağınık sohbetlerde triage yapmayı bırakın. OpsPilot kanıtı, sıralı hipotezleri ve güvenli rollback'i tek komut akışında toplar.",
      },
      {
        title: "Olay Komutanları",
        icon: "◉",
        body:
          "Yanıtı yavaşlatmadan kontrolde kalın. Her AI önerisi production'a dokunmadan önce onayınızı bekler.",
      },
      {
        title: "Mühendislik Liderleri",
        icon: "▥",
        body:
          "Tam denetim izi, MTTR trendleri ve otomatik post-incident raporları. Ek toplantı olmadan görünürlük.",
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
  const [language, setLanguage] = useState<Language>("EN");
  const [mockupStep, setMockupStep] = useState(0);
  const [mockupCycle, setMockupCycle] = useState(0);

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
    const timers = [
      window.setTimeout(() => setMockupStep(1), 1500),
      window.setTimeout(() => setMockupStep(2), 3000),
      window.setTimeout(() => setMockupStep(3), 4500),
      window.setTimeout(() => setMockupStep(0), 5500),
      window.setTimeout(() => setMockupCycle((cycle) => cycle + 1), 5500),
    ];

    return () => {
      timers.forEach((timer) => window.clearTimeout(timer));
    };
  }, [mockupCycle]);

  const copy = landingContent[language];
  const overviewCards = [
    { ...copy.overview.why, dotClass: "bg-cyan-300 shadow-[0_0_18px_rgba(34,211,238,0.45)]" },
    { ...copy.overview.how, dotClass: "bg-violet-300 shadow-[0_0_18px_rgba(167,139,250,0.45)]" },
    { ...copy.overview.what, dotClass: "bg-emerald-300 shadow-[0_0_18px_rgba(52,211,153,0.42)]" },
  ] as const;
  const pillarAccentClasses = [
    "border-t-[#3B82F6]",
    "border-t-[#F59E0B]",
    "border-t-[#06B6D4]",
    "border-t-[#8B5CF6]",
  ] as const;
  const personaIconClasses = [
    "border-cyan-300/25 bg-cyan-300/10 text-cyan-100 shadow-[0_0_24px_rgba(34,211,238,0.12)]",
    "border-violet-300/25 bg-violet-300/10 text-violet-100 shadow-[0_0_24px_rgba(167,139,250,0.12)]",
    "border-emerald-300/25 bg-emerald-300/10 text-emerald-100 shadow-[0_0_24px_rgba(52,211,153,0.12)]",
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

        {/* Hero Section */}
        <div className="mb-10 grid min-h-[520px] items-center gap-10 lg:grid-cols-[1.02fr_0.98fr]">
          <div className="flex max-w-4xl flex-col justify-center">
            <div className="mb-5 flex flex-wrap gap-3">
              <StatusBadge label={copy.badges[0]} tone="cyan" />
              <StatusBadge label={copy.badges[2]} tone="green" />
            </div>

            <h1 className="max-w-4xl text-[2.5rem] font-black leading-[0.95] tracking-[-0.06em] text-white md:text-[4rem]">
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
                className="rounded-2xl border border-white/12 px-6 py-4 text-sm font-bold text-slate-300 hover:border-cyan-300/30 hover:text-white"
              >
                {copy.hero.secondaryCta}
              </Link>

              <Link
                href="/architecture"
                className="inline-flex items-center rounded-2xl px-3 py-4 text-sm font-black text-slate-300 hover:text-cyan-100"
              >
                {copy.hero.tertiaryCta} →
              </Link>
            </div>
          </div>

          <div className="relative">
            <div className="absolute inset-0 rounded-[2.5rem] bg-cyan-400/20 blur-3xl" />
            <div className="relative overflow-hidden rounded-[2rem] border border-cyan-300/18 bg-slate-950/78 p-4 shadow-[0_0_70px_rgba(34,211,238,0.16)]">
              <div className="rounded-[1.5rem] border border-white/10 bg-white/[0.04] p-4">
                <div className="flex items-center justify-between gap-3 border-b border-white/10 pb-4">
                  <div>
                    <div className="text-xs font-black uppercase tracking-[0.28em] text-cyan-300">Command Center</div>
                    <div className="mt-2 text-xl font-black text-white">Incident lifecycle console</div>
                  </div>
                  <span className="opspilot-live-pulse rounded-full border border-emerald-300/30 bg-emerald-300/10 px-3 py-1 text-xs font-black text-emerald-100">
                    live
                  </span>
                </div>

                <div className="mt-5 grid gap-3">
                  {copy.hero.mockupRows.map((row, index) => {
                    const active = index === mockupStep;
                    const completed = index < mockupStep;
                    const gated = index >= 2;
                    const status = index <= mockupStep ? (gated ? "gated" : "ready") : "standby";
                    const pulseClass = active ? (gated ? "opspilot-amber-pulse" : "opspilot-green-pulse") : "";

                    return (
                    <div
                      key={row}
                      className={`flex items-center justify-between rounded-2xl border p-4 transition-all duration-500 ${
                        active
                          ? gated
                            ? "border-amber-300/45 bg-amber-300/12"
                            : "border-emerald-300/45 bg-emerald-300/12"
                          : completed
                          ? "border-emerald-300/20 bg-emerald-300/8"
                          : "border-white/10 bg-slate-900/70"
                      } ${pulseClass}`}
                    >
                      <div className="flex items-center gap-3">
                        <div className={`flex h-8 w-8 items-center justify-center rounded-full border text-xs font-black ${
                          index <= mockupStep
                            ? gated
                              ? "border-amber-300/35 bg-amber-300/15 text-amber-100"
                              : "border-emerald-300/35 bg-emerald-300/15 text-emerald-100"
                            : "border-cyan-300/20 bg-cyan-300/8 text-cyan-100/70"
                        }`}>
                          {index + 1}
                        </div>
                        <div className="font-black text-white">{row}</div>
                      </div>
                      <StatusBadge label={status} tone={status === "ready" ? "green" : status === "gated" ? "amber" : "slate"} />
                    </div>
                    );
                  })}
                </div>

                <Link href="/simulation" className="mt-5 inline-flex text-sm font-black text-cyan-100 hover:text-cyan-50">
                  {copy.hero.mockupCaption}
                </Link>
              </div>
            </div>
          </div>
        </div>

        <style jsx>{`
          @keyframes opspilotGreenPulse {
            0%, 100% {
              box-shadow: 0 0 0 0 rgba(52, 211, 153, 0.18), 0 0 24px rgba(52, 211, 153, 0.08);
            }
            50% {
              box-shadow: 0 0 0 8px rgba(52, 211, 153, 0), 0 0 34px rgba(52, 211, 153, 0.18);
            }
          }

          @keyframes opspilotAmberPulse {
            0%, 100% {
              box-shadow: 0 0 0 0 rgba(251, 191, 36, 0.18), 0 0 24px rgba(251, 191, 36, 0.08);
            }
            50% {
              box-shadow: 0 0 0 8px rgba(251, 191, 36, 0), 0 0 34px rgba(251, 191, 36, 0.18);
            }
          }

          @keyframes opspilotLivePulse {
            0%, 100% {
              box-shadow: 0 0 0 0 rgba(52, 211, 153, 0.22);
            }
            50% {
              box-shadow: 0 0 0 7px rgba(52, 211, 153, 0);
            }
          }

          .opspilot-green-pulse {
            animation: opspilotGreenPulse 1.4s ease-in-out infinite;
          }

          .opspilot-amber-pulse {
            animation: opspilotAmberPulse 1.4s ease-in-out infinite;
          }

          .opspilot-live-pulse {
            animation: opspilotLivePulse 1.6s ease-in-out infinite;
          }

          .opspilot-reveal {
            animation: opspilotReveal 0.7s ease both;
          }

          @keyframes opspilotReveal {
            from {
              opacity: 0;
              transform: translateY(18px);
            }
            to {
              opacity: 1;
              transform: translateY(0);
            }
          }
        `}</style>

        <section className="opspilot-reveal mb-12 rounded-full border border-white/10 bg-white/[0.035] px-5 py-4">
          <div className="flex flex-wrap items-center justify-center gap-x-5 gap-y-2 text-center text-sm font-bold text-slate-400">
            {copy.socialProof.map((item, index) => (
              <div key={item} className="flex items-center gap-5">
                <span>{item}</span>
                {index < copy.socialProof.length - 1 && <span className="text-cyan-300/40">•</span>}
              </div>
            ))}
          </div>
        </section>

        <section className="opspilot-reveal mb-20 py-10 text-center">
          <h2 className="mx-auto max-w-5xl text-4xl font-black leading-tight tracking-[-0.04em] text-white md:text-6xl">
            {copy.problem.title}
          </h2>
          <p className="mx-auto mt-6 max-w-3xl text-base leading-8 text-slate-400">
            {copy.problem.body}
          </p>
        </section>
        {/* Why / How / What - Three Equal Cards */}
        <section className="opspilot-reveal mb-10 grid gap-4 lg:grid-cols-3">
          {overviewCards.map((card) => (
            <div key={card.badge} className="flex flex-col rounded-3xl border border-white/10 bg-slate-900/68 p-6">
              <div className="flex items-center gap-3">
                <span className={`h-3 w-3 rounded-full ${card.dotClass}`} />
                <span className="text-xs font-black uppercase tracking-[0.24em] text-slate-400">{card.badge}</span>
              </div>
              <h3 className="mt-5 text-2xl font-black text-white">{card.title}</h3>
              <p className="mt-3 flex-grow text-sm leading-6 text-slate-300">{card.body}</p>
            </div>
          ))}
        </section>

        {/* Before vs After - Split Layout */}
        <section className="opspilot-reveal mb-10 rounded-[2rem] border border-white/10 bg-slate-900/68 p-8">
          <div className="mb-6">
            <StatusBadge label={copy.compare.badge} tone="violet" />
            <h2 className="mt-4 text-3xl font-black text-white md:text-4xl">{copy.compare.title}</h2>
          </div>

          <div className="grid gap-5 lg:grid-cols-2">
            <CompareColumn
              title={copy.compare.beforeTitle}
              tone="before"
              items={copy.compare.pairs.map(([heading, before]) => [heading, before] as const)}
            />
            <CompareColumn
              title={copy.compare.afterTitle}
              tone="after"
              items={copy.compare.pairs.map(([heading, , after]) => [heading, after] as const)}
            />
          </div>
        </section>

        <section className="opspilot-reveal mt-8 rounded-[2rem] border border-white/10 bg-slate-900/68 p-6">
          <div className="flex flex-col gap-3 md:flex-row md:items-end md:justify-between">
            <div>
              <StatusBadge label={copy.pillars.badge} tone="cyan" />
              <h2 className="mt-4 text-3xl font-black text-white md:text-5xl">{copy.pillars.title}</h2>
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
              <div key={pillar.title} className={`rounded-3xl border border-t-[3px] border-white/10 bg-white/[0.05] p-5 ${pillarAccentClasses[index]}`}>
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

        <section className="opspilot-reveal mt-8 grid gap-5 lg:grid-cols-[1fr_1fr_1fr]">
          {copy.infoPanels.map((panel, index) => (
            <InfoPanel key={panel.title} title={panel.title} icon={panel.icon} body={panel.body} iconClass={personaIconClasses[index]} />
          ))}
        </section>

        <section className="opspilot-reveal mt-10 rounded-[2rem] border border-cyan-300/18 bg-cyan-300/[0.055] px-6 py-10 text-center shadow-[0_0_60px_rgba(34,211,238,0.08)]">
          <h2 className="text-3xl font-black tracking-[-0.04em] text-white md:text-5xl">{copy.hero.finalCtaTitle}</h2>
          <p className="mx-auto mt-4 max-w-2xl text-sm leading-7 text-slate-300">{copy.hero.finalCtaBody}</p>
          <Link
            href="/dashboard"
            className="mt-7 inline-flex rounded-2xl bg-cyan-300 px-7 py-4 text-sm font-black text-slate-950 shadow-[0_0_36px_rgba(34,211,238,0.16)] hover:bg-cyan-200"
          >
            {copy.hero.primaryCta}
          </Link>
        </section>

        <footer className="opspilot-reveal mt-10 rounded-[2rem] border border-white/10 bg-white/[0.035] px-6 py-6">
          <div className="flex flex-col gap-4 text-sm text-slate-400 md:flex-row md:items-center md:justify-between">
            <div>
              <span className="font-black text-white">OpsPilot</span>
              <span className="ml-3">AI incident command for safer recovery.</span>
            </div>
            <div className="flex flex-wrap gap-4 font-bold">
              <Link href="/dashboard" className="hover:text-cyan-100">Command Center</Link>
              <Link href="/simulation" className="hover:text-cyan-100">Simulation</Link>
              <Link href="/architecture" className="hover:text-cyan-100">Architecture</Link>
            </div>
          </div>
        </footer>
      </section>
    </PlatformShell>
  );
}

function InfoPanel({ title, icon, body, iconClass }: { title: string; icon: string; body: string; iconClass: string }) {
  return (
    <div className="rounded-3xl border border-white/10 bg-slate-900/68 p-6">
      <div className={`flex h-16 w-16 items-center justify-center rounded-3xl border text-3xl font-black ${iconClass}`}>
        {icon}
      </div>
      <h3 className="mt-5 text-2xl font-black text-white">{title}</h3>
      <p className="mt-3 text-sm leading-7 text-slate-300">{body}</p>
    </div>
  );
}

function CompareColumn({ title, tone, items }: { title: string; tone: "before" | "after"; items: readonly (readonly [string, string])[] }) {
  const toneClass =
    tone === "after"
      ? "border-emerald-300/20 bg-emerald-300/[0.06]"
      : "border-red-400/14 bg-red-500/[0.035]";
  const dotClass = tone === "after" ? "bg-[#22C55E] shadow-[0_0_14px_rgba(34,197,94,0.4)]" : "bg-[#EF4444]/70";

  return (
    <div className={`rounded-3xl border p-5 ${toneClass}`}>
      <h3 className="text-xl font-black text-white">{title}</h3>
      <div className="mt-5 space-y-3">
        {items.map(([heading, detail]) => (
          <div key={`${title}-${heading}`} className="rounded-2xl border border-white/10 bg-slate-950/42 p-4">
            <div className="flex items-center gap-3">
              <span className={`h-2.5 w-2.5 rounded-full ${dotClass}`} />
              <div className="text-sm font-black text-white">{heading}</div>
            </div>
            <p className="mt-2 text-sm leading-6 text-slate-300">{detail}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
