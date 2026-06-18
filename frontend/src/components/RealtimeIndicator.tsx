type RealtimeIndicatorProps = {
  active: boolean;
  label: string;
};

export function RealtimeIndicator({ active, label }: RealtimeIndicatorProps) {
  return (
    <span className="inline-flex items-center gap-2 rounded-full border border-white/10 bg-white/[0.04] px-3 py-1 text-xs font-black uppercase tracking-[0.18em] text-cyan-100">
      <span className={`relative flex h-2.5 w-2.5 ${active ? "text-emerald-300" : "text-slate-500"}`}>
        {active && <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-emerald-300 opacity-60" />}
        <span className={`relative inline-flex h-2.5 w-2.5 rounded-full ${active ? "bg-emerald-300" : "bg-slate-500"}`} />
      </span>
      {label}
    </span>
  );
}
