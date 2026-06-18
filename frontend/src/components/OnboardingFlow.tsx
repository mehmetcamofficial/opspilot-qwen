import { Icon } from "@/components/ui/Icon";

type OnboardingFlowProps = {
  actionLabel: string;
  dismissLabel: string;
  onAction: () => void;
  onDismiss: () => void;
  steps: string[];
  title: string;
};

export function OnboardingFlow({ actionLabel, dismissLabel, onAction, onDismiss, steps, title }: OnboardingFlowProps) {
  return (
    <section className="mb-5 rounded-3xl border border-cyan-300/20 bg-cyan-300/10 p-5 shadow-[0_0_50px_rgba(34,211,238,0.08)]">
      <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
        <div>
          <h2 className="text-xl font-black text-white">{title}</h2>
          <div className="mt-4 grid gap-3 md:grid-cols-3">
            {steps.map((step, index) => (
              <div key={step} className="rounded-2xl border border-white/10 bg-slate-950/40 p-3">
                <div className="flex items-center gap-2 text-xs font-black uppercase tracking-wider text-cyan-200">
                  <Icon name="check" className="h-3.5 w-3.5" />
                  {index + 1}
                </div>
                <p className="mt-2 text-sm font-semibold leading-6 text-cyan-50">{step}</p>
              </div>
            ))}
          </div>
        </div>

        <div className="flex shrink-0 flex-col gap-2 sm:flex-row lg:flex-col">
          <button type="button" onClick={onAction} className="rounded-2xl bg-cyan-300 px-5 py-3 text-sm font-black text-slate-950 transition hover:bg-cyan-200 active:scale-[0.98]">
            {actionLabel}
          </button>
          <button type="button" onClick={onDismiss} className="rounded-2xl border border-white/10 bg-white/[0.04] px-5 py-3 text-sm font-black text-white transition hover:bg-white/[0.08] active:scale-[0.98]">
            {dismissLabel}
          </button>
        </div>
      </div>
    </section>
  );
}
