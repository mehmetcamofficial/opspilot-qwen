"use client";

import { FormEvent, Suspense, useMemo, useState } from "react";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { OpsPilotLogo } from "@/components/OpsPilotLogo";
import { StatusBadge } from "@/components/StatusBadge";

export default function AdminLoginPage() {
  return (
    <Suspense fallback={<LoginShell />}>
      <AdminLoginForm />
    </Suspense>
  );
}

function AdminLoginForm() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const nextPath = useMemo(() => {
    const requested = searchParams.get("next");
    return requested?.startsWith("/admin") ? requested : "/admin";
  }, [searchParams]);
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  async function submitLogin(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError("");
    setIsSubmitting(true);

    try {
      const response = await fetch("/api/admin-auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ password }),
      });

      if (!response.ok) {
        const body = await response.json().catch(() => null);
        setError(body?.error || "Admin sign-in failed.");
        return;
      }

      router.replace(nextPath);
      router.refresh();
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <main className="min-h-screen bg-slate-950 text-white">
      <section className="mx-auto flex min-h-screen max-w-6xl items-center justify-center px-6 py-12">
        <div className="grid w-full gap-8 lg:grid-cols-[0.95fr_1.05fr] lg:items-center">
          <div>
            <div className="flex flex-col items-start gap-5">
              <Link
                href="/"
                className="rounded-full border border-white/10 bg-white/[0.04] px-4 py-2 text-sm font-black text-slate-200 hover:border-cyan-300/30 hover:text-cyan-100"
              >
                ← Back to Home
              </Link>
              <Link href="/" className="inline-flex">
                <OpsPilotLogo />
              </Link>
            </div>
            <div className="mt-8 flex flex-wrap gap-3">
              <StatusBadge label="Admin only" tone="amber" />
              <StatusBadge label="Governance protected" tone="violet" />
            </div>
            <h1 className="mt-6 max-w-3xl text-5xl font-black leading-none tracking-[-0.06em] md:text-6xl">
              Admin access required.
            </h1>
            <p className="mt-5 max-w-2xl text-base leading-8 text-slate-300">
              Governance controls can change model mode, policies, deployment readiness, and audit exports. Sign in with the admin password before entering this area.
            </p>
          </div>

          <form onSubmit={submitLogin} className="rounded-[2rem] border border-white/10 bg-slate-900/78 p-6 shadow-[0_0_80px_rgba(34,211,238,0.08)]">
            <div className="rounded-[1.5rem] border border-cyan-300/15 bg-cyan-300/[0.045] p-5">
              <div className="text-sm font-black uppercase tracking-[0.24em] text-cyan-200">Governance login</div>
              <h2 className="mt-4 text-3xl font-black text-white">Enter admin password</h2>
              <p className="mt-2 text-sm leading-6 text-slate-400">
                Local development password defaults to <span className="font-mono text-slate-200">opspilot-local-admin</span>. Production should set <span className="font-mono text-slate-200">OPSPILOT_ADMIN_PASSWORD</span>.
              </p>
            </div>

            <label className="mt-6 block">
              <span className="text-sm font-black text-slate-200">Password</span>
              <input
                value={password}
                onChange={(event) => setPassword(event.target.value)}
                type="password"
                autoComplete="current-password"
                className="mt-3 w-full rounded-2xl border border-white/10 bg-slate-950/70 px-4 py-4 text-sm text-white outline-none placeholder:text-slate-600 focus:border-cyan-300"
                placeholder="Enter admin password"
              />
            </label>

            {error && (
              <div className="mt-4 rounded-2xl border border-amber-400/25 bg-amber-400/10 p-4 text-sm font-bold text-amber-100">
                {error}
              </div>
            )}

            <button
              type="submit"
              disabled={isSubmitting}
              className="mt-6 w-full rounded-2xl bg-cyan-300 px-5 py-4 text-sm font-black text-slate-950 hover:bg-cyan-200 disabled:cursor-not-allowed disabled:opacity-60"
            >
              {isSubmitting ? "Checking access..." : "Enter Governance"}
            </button>
          </form>
        </div>
      </section>
    </main>
  );
}

function LoginShell() {
  return (
    <main className="min-h-screen bg-slate-950 text-white">
      <section className="mx-auto flex min-h-screen max-w-6xl items-center justify-center px-6 py-12">
        <div className="rounded-[2rem] border border-white/10 bg-slate-900/78 p-8 text-center">
          <StatusBadge label="Admin only" tone="amber" />
          <h1 className="mt-5 text-3xl font-black">Loading admin access...</h1>
        </div>
      </section>
    </main>
  );
}
