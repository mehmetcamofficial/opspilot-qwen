export function OpsPilotLogo() {
  return (
    <div className="flex items-center gap-3">
      <div className="relative flex h-10 w-10 items-center justify-center rounded-2xl border border-cyan-400/40 bg-cyan-400/10 shadow-[0_0_35px_rgba(34,211,238,0.22)]">
        <div className="h-3 w-3 rounded-full bg-cyan-300 shadow-[0_0_20px_rgba(34,211,238,0.95)]" />
        <div className="absolute h-7 w-7 rounded-full border border-violet-400/50" />
      </div>
      <div>
        <div className="text-xl font-black tracking-tight text-white">
          Ops<span className="text-cyan-300">Pilot</span>
        </div>
        <div className="text-[10px] font-semibold uppercase tracking-[0.28em] text-slate-400">
          AI Incident Command
        </div>
      </div>
    </div>
  );
}
