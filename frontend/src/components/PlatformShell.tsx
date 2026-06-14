import Link from "next/link";
import { OpsPilotLogo } from "./OpsPilotLogo";

type PlatformShellProps = {
  children: React.ReactNode;
};

export function PlatformShell({ children }: PlatformShellProps) {
  return (
    <main className="min-h-screen overflow-hidden bg-[#030712] text-slate-100">
      <div className="pointer-events-none fixed inset-0">
        <div className="absolute left-[-10%] top-[-20%] h-[420px] w-[420px] rounded-full bg-cyan-500/20 blur-3xl" />
        <div className="absolute right-[-10%] top-[10%] h-[420px] w-[420px] rounded-full bg-violet-500/20 blur-3xl" />
        <div className="absolute bottom-[-20%] left-[30%] h-[420px] w-[420px] rounded-full bg-blue-500/10 blur-3xl" />
        <div className="absolute inset-0 bg-[linear-gradient(rgba(148,163,184,0.04)_1px,transparent_1px),linear-gradient(90deg,rgba(148,163,184,0.04)_1px,transparent_1px)] bg-[size:42px_42px]" />
      </div>

      <div className="relative z-10">
        <header className="mx-auto flex max-w-7xl items-center justify-between px-6 py-6">
          <Link href="/" aria-label="OpsPilot home">
            <OpsPilotLogo />
          </Link>

          <nav className="hidden items-center gap-2 rounded-full border border-white/10 bg-white/[0.03] p-1 text-sm text-slate-300 backdrop-blur md:flex">
            <Link className="rounded-full px-4 py-2 hover:bg-white/10 hover:text-white" href="/">
              Home
            </Link>
            <Link className="rounded-full px-4 py-2 hover:bg-white/10 hover:text-white" href="/dashboard">
              Dashboard
            </Link>
            <Link className="rounded-full px-4 py-2 hover:bg-white/10 hover:text-white" href="/admin">
              Admin
            </Link>
          </nav>

          <Link
            href="/dashboard"
            className="rounded-full border border-cyan-400/30 bg-cyan-400/10 px-4 py-2 text-sm font-semibold text-cyan-100 shadow-[0_0_30px_rgba(34,211,238,0.12)] hover:bg-cyan-400/20"
          >
            Launch Console
          </Link>
        </header>

        {children}
      </div>
    </main>
  );
}
