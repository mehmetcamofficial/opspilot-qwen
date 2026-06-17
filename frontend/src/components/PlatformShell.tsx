"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { OpsPilotLogo } from "./OpsPilotLogo";
import { ThemeToggle } from "./ThemeToggle";
import { LanguageToggle } from "./LanguageToggle";

type PlatformShellProps = {
  children: React.ReactNode;
};

const fullNavItems = [
  ["Home", "/"],
  ["Command Center", "/dashboard"],
  ["Simulation", "/simulation"],
  ["Status", "/status"],
  ["Architecture", "/architecture"],
  ["Governance", "/admin"],
  ["Reasoning Graph", "/knowledge-graph"],
];

const pageMeta: Record<string, { title: string; subtitle: string; actions: [string, string][] }> = {
  "/dashboard": {
    title: "Command Center",
    subtitle: "Live incident lifecycle, safety gate, approval, and audit trail",
    actions: [
      ["Simulation", "/simulation"],
      ["Governance", "/admin"],
    ],
  },
  "/admin": {
    title: "Governance Console",
    subtitle: "Agent readiness, policy controls, and deployment governance",
    actions: [
      ["Command Center", "/dashboard"],
      ["Blog", "/blog"],
    ],
  },
  "/blog": {
    title: "OpsPilot Blog",
    subtitle: "AI operations and platform intelligence",
    actions: [
      ["Governance", "/admin"],
      ["Architecture", "/architecture"],
    ],
  },
  "/architecture": {
    title: "Architecture",
    subtitle: "System design and deployment model",
    actions: [
      ["Reasoning Graph", "/knowledge-graph"],
      ["Command Center", "/dashboard"],
    ],
  },
  "/simulation": {
    title: "Simulation Lab",
    subtitle: "Mission-control incident lifecycle simulation",
    actions: [
      ["Command Center", "/dashboard"],
      ["Reasoning Graph", "/knowledge-graph"],
    ],
  },
  "/status": {
    title: "Public Status",
    subtitle: "Customer-facing service health and active incident visibility",
    actions: [
      ["Command Center", "/dashboard"],
      ["Simulation", "/simulation"],
    ],
  },
  "/knowledge-graph": {
    title: "Reasoning Graph",
    subtitle: "Evidence lineage and incident explainability map",
    actions: [
      ["Simulation", "/simulation"],
      ["Architecture", "/architecture"],
    ],
  },
};

export function PlatformShell({ children }: PlatformShellProps) {
  const pathname = usePathname();
  const isHome = pathname === "/";
  const meta = pageMeta[pathname] || {
    title: "OpsPilot Platform",
    subtitle: "AI incident command system",
    actions: [["Command Center", "/dashboard"]],
  };

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
              <Link href="/" aria-label="OpsPilot home" className="shrink-0">
                <OpsPilotLogo />
              </Link>

              <nav className="hidden max-w-none flex-nowrap items-center justify-center gap-0 rounded-full border border-white/10 bg-white/[0.04] p-1 text-sm text-slate-300 shadow-[0_0_40px_rgba(15,23,42,0.35)] lg:flex">
                {fullNavItems.map(([label, href]) => (
                  <Link
                    key={href}
                    className={`rounded-full px-2.5 py-2 transition whitespace-nowrap ${
                      pathname === href
                        ? "bg-cyan-300 text-slate-950 shadow-[0_0_22px_rgba(34,211,238,0.25)]"
                        : "hover:bg-white/10 hover:text-white"
                    }`}
                    href={href}
                  >
                    {label}
                  </Link>
                ))}
              </nav>

              <div className="flex shrink-0 items-center gap-2">
                <LanguageToggle />
                <ThemeToggle />
                <Link
                  href="/dashboard"
                  className="hidden rounded-full border border-cyan-400/30 bg-cyan-400/10 px-4 py-2 text-sm font-semibold text-cyan-100 shadow-[0_0_30px_rgba(34,211,238,0.12)] hover:bg-cyan-400/20 md:inline-flex"
                >
                  Launch Console
                </Link>
              </div>
            </div>

            <div className="mx-auto block max-w-[96rem] px-6 pb-4 lg:hidden">
              <div className="flex gap-2 overflow-x-auto rounded-2xl border border-white/10 bg-white/[0.03] p-2">
                {fullNavItems.map(([label, href]) => (
                  <Link
                    key={href}
                    className="shrink-0 rounded-full px-3 py-2 text-sm text-slate-300 hover:bg-white/10 hover:text-white"
                    href={href}
                  >
                    {label}
                  </Link>
                ))}
              </div>
            </div>
          </header>
        ) : (
          <header className="sticky top-0 z-50 border-b border-white/5 bg-[#030712]/80 backdrop-blur-xl">
            <div className="mx-auto flex max-w-7xl items-center justify-between gap-4 px-6 py-4">
              <div className="flex items-center gap-4">
                <Link
                  href="/"
                  className="rounded-full border border-white/10 bg-white/[0.04] px-4 py-2 text-sm font-bold text-slate-200 hover:bg-white/[0.08] hover:text-white"
                >
                  ← Home
                </Link>
                <div className="hidden md:block">
                  <OpsPilotLogo />
                </div>
              </div>

              <div className="text-center">
                <div className="text-sm font-black uppercase tracking-[0.28em] text-cyan-300">
                  {meta.title}
                </div>
                <div className="mt-1 text-xs text-slate-500">{meta.subtitle}</div>
              </div>

              <div className="flex items-center gap-2">
                {meta.actions.map(([label, href]) => (
                  <Link
                    key={href}
                    href={href}
                    className="hidden rounded-full border border-cyan-400/20 bg-cyan-400/10 px-4 py-2 text-sm font-semibold text-cyan-100 hover:bg-cyan-400/20 md:inline-flex"
                  >
                    {label}
                  </Link>
                ))}
                <LanguageToggle />
                <ThemeToggle />
              </div>
            </div>
          </header>
        )}

        <div key={pathname} className="animate-[fadeIn_260ms_ease-out]">
          {children}
        </div>
      </div>
    </main>
  );
}
