import { Icon } from "@/components/ui/Icon";

type TooltipProps = {
  label: string;
  children: React.ReactNode;
};

export function Tooltip({ label, children }: TooltipProps) {
  return (
    <div className="group relative inline-flex items-center gap-1">
      {children}
      <Icon name="info" className="h-3.5 w-3.5 text-slate-500 transition group-hover:text-cyan-200" />
      <span className="pointer-events-none absolute left-0 top-full z-50 mt-2 w-64 translate-y-1 rounded-2xl border border-white/10 bg-slate-950/95 p-3 text-xs font-semibold leading-5 text-slate-300 opacity-0 shadow-[0_0_40px_rgba(15,23,42,0.4)] transition group-hover:translate-y-0 group-hover:opacity-100">
        {label}
      </span>
    </div>
  );
}
