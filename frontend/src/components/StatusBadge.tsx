type StatusBadgeProps = {
  label: string;
  tone?: "cyan" | "green" | "amber" | "red" | "violet" | "slate";
};

const styles: Record<NonNullable<StatusBadgeProps["tone"]>, string> = {
  cyan: "border-cyan-400/30 bg-cyan-400/10 text-cyan-200",
  green: "border-emerald-400/30 bg-emerald-400/10 text-emerald-200",
  amber: "border-amber-400/30 bg-amber-400/10 text-amber-200",
  red: "border-red-400/30 bg-red-400/10 text-red-200",
  violet: "border-violet-400/30 bg-violet-400/10 text-violet-200",
  slate: "border-slate-500/40 bg-slate-800/70 text-slate-200",
};

export function StatusBadge({ label, tone = "slate" }: StatusBadgeProps) {
  return (
    <span className={`inline-flex items-center rounded-full border px-3 py-1 text-xs font-semibold ${styles[tone]}`}>
      {label}
    </span>
  );
}
