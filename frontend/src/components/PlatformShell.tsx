"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { CommandPalette } from "./CommandPalette";
import { OpsPilotLogo } from "./OpsPilotLogo";
import { ThemeToggle } from "./ThemeToggle";
import { LanguageToggle } from "./LanguageToggle";
import { useLanguage, type Language } from "@/lib/language";

type PlatformShellProps = {
  children: React.ReactNode;
};

const navItems = [
  ["home", "/"],
  ["dashboard", "/dashboard"],
  ["simulation", "/simulation"],
  ["status", "/status"],
  ["architecture", "/architecture"],
  ["governance", "/admin"],
  ["graph", "/knowledge-graph"],
] as const;

const homeNavItems = navItems.slice(0, 5);

const shellCopy = {
  EN: {
    nav: {
      home: "Home",
      dashboard: "Command Center",
      simulation: "Simulation",
      status: "Status",
      architecture: "Architecture",
      governance: "Governance",
      graph: "Reasoning Graph",
    },
    homeAria: "OpsPilot home",
    launchConsole: "Launch Console",
    backHome: "← Home",
    commandHint: "Cmd K",
    commandTitle: "Command palette",
    commandPlaceholder: "Search pages and actions...",
    commandEmpty: "No command found.",
    shortcuts: {
      dashboard: "G D",
      incidents: "G I",
    },
    defaultTitle: "OpsPilot Platform",
    defaultSubtitle: "AI incident command system",
  },
  TR: {
    nav: {
      home: "Ana Sayfa",
      dashboard: "Komuta Merkezi",
      simulation: "Simülasyon",
      status: "Durum",
      architecture: "Mimari",
      governance: "Yönetişim",
      graph: "Akıl Yürütme Grafiği",
    },
    homeAria: "OpsPilot ana sayfa",
    launchConsole: "Konsolu Aç",
    backHome: "← Ana Sayfa",
    commandHint: "Cmd K",
    commandTitle: "Komut paleti",
    commandPlaceholder: "Sayfa ve aksiyon ara...",
    commandEmpty: "Komut bulunamadı.",
    shortcuts: {
      dashboard: "G D",
      incidents: "G I",
    },
    defaultTitle: "OpsPilot Platformu",
    defaultSubtitle: "Yapay zeka olay komuta sistemi",
  },
} satisfies Record<Language, unknown>;

const pageMeta: Record<string, Record<Language, { title: string; subtitle: string; actions: [string, string][] }>> = {
  "/dashboard": {
    EN: {
      title: "Command Center",
      subtitle: "Live incident lifecycle, safety gate, approval, and audit trail",
      actions: [["Simulation", "/simulation"], ["Governance", "/admin"]],
    },
    TR: {
      title: "Komuta Merkezi",
      subtitle: "Canlı olay yaşam döngüsü, güvenlik kapısı, onay ve denetim izi",
      actions: [["Simülasyon", "/simulation"], ["Yönetişim", "/admin"]],
    },
  },
  "/admin": {
    EN: {
      title: "Governance Console",
      subtitle: "Agent readiness, policy controls, and deployment governance",
      actions: [["Command Center", "/dashboard"], ["Blog", "/blog"]],
    },
    TR: {
      title: "Yönetişim Konsolu",
      subtitle: "Ajan hazırlığı, politika kontrolleri ve dağıtım yönetişimi",
      actions: [["Komuta Merkezi", "/dashboard"], ["Blog", "/blog"]],
    },
  },
  "/blog": {
    EN: {
      title: "OpsPilot Blog",
      subtitle: "AI operations and platform intelligence",
      actions: [["Governance", "/admin"], ["Architecture", "/architecture"]],
    },
    TR: {
      title: "OpsPilot Blog",
      subtitle: "Yapay zeka operasyonları ve platform zekası",
      actions: [["Yönetişim", "/admin"], ["Mimari", "/architecture"]],
    },
  },
  "/architecture": {
    EN: {
      title: "Architecture",
      subtitle: "System design and deployment model",
      actions: [["Reasoning Graph", "/knowledge-graph"], ["Command Center", "/dashboard"]],
    },
    TR: {
      title: "Mimari",
      subtitle: "Sistem tasarımı ve dağıtım modeli",
      actions: [["Akıl Yürütme Grafiği", "/knowledge-graph"], ["Komuta Merkezi", "/dashboard"]],
    },
  },
  "/simulation": {
    EN: {
      title: "Simulation Lab",
      subtitle: "Mission-control incident lifecycle simulation",
      actions: [["Command Center", "/dashboard"], ["Reasoning Graph", "/knowledge-graph"]],
    },
    TR: {
      title: "Simülasyon Laboratuvarı",
      subtitle: "Komuta merkezi olay yaşam döngüsü simülasyonu",
      actions: [["Komuta Merkezi", "/dashboard"], ["Akıl Yürütme Grafiği", "/knowledge-graph"]],
    },
  },
  "/status": {
    EN: {
      title: "Public Status",
      subtitle: "Customer-facing service health and active incident visibility",
      actions: [["Command Center", "/dashboard"], ["Simulation", "/simulation"]],
    },
    TR: {
      title: "Genel Durum",
      subtitle: "Müşteriye açık servis sağlığı ve aktif olay görünürlüğü",
      actions: [["Komuta Merkezi", "/dashboard"], ["Simülasyon", "/simulation"]],
    },
  },
  "/knowledge-graph": {
    EN: {
      title: "Reasoning Graph",
      subtitle: "Evidence lineage and incident explainability map",
      actions: [["Simulation", "/simulation"], ["Architecture", "/architecture"]],
    },
    TR: {
      title: "Akıl Yürütme Grafiği",
      subtitle: "Kanıt soyu ve olay açıklanabilirlik haritası",
      actions: [["Simülasyon", "/simulation"], ["Mimari", "/architecture"]],
    },
  },
};

export function PlatformShell({ children }: PlatformShellProps) {
  const pathname = usePathname();
  const router = useRouter();
  const language = useLanguage();
  const [commandOpen, setCommandOpen] = useState(false);
  const pendingGRef = useRef<number | null>(null);
  const copy = shellCopy[language];
  const isHome = pathname === "/";
  const meta = pageMeta[pathname]?.[language] || {
    title: copy.defaultTitle,
    subtitle: copy.defaultSubtitle,
    actions: [[copy.nav.dashboard, "/dashboard"]] as [string, string][],
  };
  const navLinkClass = (href: string) =>
    `shrink-0 rounded-full px-3 py-2 text-sm font-semibold transition active:scale-[0.98] ${
      pathname === href
        ? "bg-cyan-300 text-slate-950 shadow-[0_0_22px_rgba(34,211,238,0.25)]"
        : "text-slate-300 hover:bg-white/10 hover:text-white"
    }`;
  const commands = useMemo(() => {
    const navCommands = navItems.map(([key, href]) => ({
      label: copy.nav[key],
      href,
      hint: href,
    }));

    return [
      ...navCommands,
      { label: copy.launchConsole, href: "/dashboard", hint: copy.shortcuts.dashboard },
      { label: `${copy.nav.dashboard} · ${copy.nav.status}`, href: "/dashboard#incidents", hint: copy.shortcuts.incidents },
    ];
  }, [copy]);

  useEffect(() => {
    function handleKeyDown(event: KeyboardEvent) {
      const target = event.target as HTMLElement | null;
      const isTyping = target?.tagName === "INPUT" || target?.tagName === "TEXTAREA" || target?.isContentEditable;

      if ((event.metaKey || event.ctrlKey) && event.key.toLowerCase() === "k") {
        event.preventDefault();
        setCommandOpen(true);
        return;
      }

      if (event.key === "Escape") {
        setCommandOpen(false);
        return;
      }

      if (isTyping || event.metaKey || event.ctrlKey || event.altKey) return;

      const key = event.key.toLowerCase();
      if (key === "g") {
        pendingGRef.current = window.setTimeout(() => {
          pendingGRef.current = null;
        }, 900);
        return;
      }

      if (pendingGRef.current && key === "d") {
        window.clearTimeout(pendingGRef.current);
        pendingGRef.current = null;
        router.push("/dashboard");
      }

      if (pendingGRef.current && key === "i") {
        window.clearTimeout(pendingGRef.current);
        pendingGRef.current = null;
        router.push("/dashboard#incidents");
      }
    }

    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [router]);

  return (
    <main className="min-h-screen overflow-hidden bg-[#030712] text-slate-100 dark:bg-[#030712]">
      <div className="pointer-events-none fixed inset-0">
        <div className="absolute left-[-10%] top-[-20%] h-[460px] w-[460px] rounded-full bg-cyan-500/30 blur-3xl" />
        <div className="absolute right-[-10%] top-[10%] h-[460px] w-[460px] rounded-full bg-blue-500/15 blur-3xl" />
        <div className="absolute bottom-[-20%] left-[30%] h-[460px] w-[460px] rounded-full bg-blue-500/15 blur-3xl" />
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_20%_20%,rgba(34,211,238,0.10),transparent_28%),radial-gradient(circle_at_80%_0%,rgba(56,130,246,0.12),transparent_30%)]" />
        <div className="absolute inset-0 bg-[linear-gradient(rgba(148,163,184,0.045)_1px,transparent_1px),linear-gradient(90deg,rgba(148,163,184,0.045)_1px,transparent_1px)] bg-[size:42px_42px]" />
      </div>

      <div className="relative z-10">
        {isHome ? (
          <header className="sticky top-0 z-50 border-b border-white/5 bg-[#030712]/70 backdrop-blur-xl">
            <div className="mx-auto flex max-w-[96rem] items-center justify-between gap-4 px-6 py-4">
              <Link href="/" aria-label={copy.homeAria} className="shrink-0">
                <OpsPilotLogo />
              </Link>

              <nav className="hidden max-w-none flex-nowrap items-center justify-center gap-0 rounded-full border border-white/10 bg-white/[0.04] p-1 text-sm text-slate-300 shadow-[0_0_40px_rgba(15,23,42,0.35)] lg:flex">
                {homeNavItems.map(([key, href]) => (
                  <Link
                    key={href}
                    className={`${navLinkClass(href)} px-2.5 whitespace-nowrap`}
                    href={href}
                  >
                    {copy.nav[key]}
                  </Link>
                ))}
              </nav>

              <div className="flex shrink-0 items-center gap-2">
                <button
                  type="button"
                  onClick={() => setCommandOpen(true)}
                  className="hidden rounded-full border border-white/10 bg-white/[0.04] px-3 py-2 text-xs font-black text-slate-300 transition hover:bg-white/[0.08] hover:text-white active:scale-[0.98] xl:inline-flex"
                >
                  {copy.commandHint}
                </button>
                <LanguageToggle />
                <ThemeToggle />
                <Link
                  href="/dashboard"
                  className="hidden rounded-full border border-cyan-400/30 bg-cyan-400/10 px-4 py-2 text-sm font-semibold text-cyan-100 shadow-[0_0_30px_rgba(34,211,238,0.12)] transition hover:bg-cyan-400/20 active:scale-[0.98] md:inline-flex"
                >
                  {copy.launchConsole}
                </Link>
              </div>
            </div>

            <div className="mx-auto block max-w-[96rem] px-6 pb-4 lg:hidden">
              <div className="flex gap-2 overflow-x-auto rounded-2xl border border-white/10 bg-white/[0.03] p-2">
                {homeNavItems.map(([key, href]) => (
                  <Link
                    key={href}
                    className={navLinkClass(href)}
                    href={href}
                  >
                    {copy.nav[key]}
                  </Link>
                ))}
              </div>
            </div>
          </header>
        ) : (
          <header className="sticky top-0 z-50 border-b border-white/5 bg-[#030712]/80 backdrop-blur-xl">
            <div className="mx-auto flex max-w-7xl flex-col gap-4 px-6 py-4 lg:flex-row lg:items-center lg:justify-between">
              <div className="flex w-full items-center justify-between gap-4 lg:w-auto lg:justify-start">
                <Link
                  href="/"
                  className="rounded-full border border-white/10 bg-white/[0.04] px-4 py-2 text-sm font-bold text-slate-200 transition hover:bg-white/[0.08] hover:text-white active:scale-[0.98]"
                >
                  {copy.backHome}
                </Link>
                <div className="hidden sm:block lg:hidden xl:block">
                  <OpsPilotLogo />
                </div>
              </div>

              <div className="w-full text-left lg:text-center">
                <div className="mb-2 flex items-center gap-2 text-xs font-bold text-slate-500">
                  <Link href="/" className="hover:text-cyan-200">{copy.nav.home}</Link>
                  <span>/</span>
                  <span className="text-cyan-200">{meta.title}</span>
                </div>
                <div className="text-sm font-black uppercase tracking-[0.28em] text-cyan-300">
                  {meta.title}
                </div>
                <div className="mt-1 text-xs text-slate-500">{meta.subtitle}</div>
              </div>

              <div className="flex w-full items-center justify-between gap-2 lg:w-auto lg:justify-end">
                <div className="hidden gap-2 md:flex">
                  {meta.actions.map(([label, href]) => (
                    <Link
                      key={href}
                      href={href}
                      className="rounded-full border border-cyan-400/20 bg-cyan-400/10 px-4 py-2 text-sm font-semibold text-cyan-100 transition hover:bg-cyan-400/20 active:scale-[0.98]"
                    >
                      {label}
                    </Link>
                  ))}
                </div>
                <div className="flex items-center gap-2">
                  <button
                    type="button"
                    onClick={() => setCommandOpen(true)}
                    className="rounded-full border border-white/10 bg-white/[0.04] px-3 py-2 text-xs font-black text-slate-300 transition hover:bg-white/[0.08] hover:text-white active:scale-[0.98]"
                  >
                    {copy.commandHint}
                  </button>
                  <LanguageToggle />
                  <ThemeToggle />
                </div>
              </div>

              <nav className="flex w-full gap-2 overflow-x-auto rounded-2xl border border-white/10 bg-white/[0.03] p-2 lg:hidden">
                {navItems.map(([key, href]) => (
                  <Link key={href} className={navLinkClass(href)} href={href}>
                    {copy.nav[key]}
                  </Link>
                ))}
              </nav>
            </div>
          </header>
        )}

        <div key={pathname} className="animate-[fadeIn_260ms_ease-out]">
          {children}
        </div>
      </div>

      <CommandPalette
        commands={commands}
        emptyLabel={copy.commandEmpty}
        isOpen={commandOpen}
        onClose={() => setCommandOpen(false)}
        placeholder={copy.commandPlaceholder}
        title={copy.commandTitle}
      />
    </main>
  );
}
