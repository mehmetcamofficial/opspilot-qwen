import { EmptyState } from "@/components/ui/EmptyState";

type TimelineEvent = {
  event: string;
  message: string;
  actor: string;
  timestamp: string;
};

type TimelineRailProps = {
  events: TimelineEvent[];
  emptyTitle: string;
  emptyDescription: string;
  emptyActionLabel: string;
  onEmptyAction: () => void;
};

export function TimelineRail({ events, emptyTitle, emptyDescription, emptyActionLabel, onEmptyAction }: TimelineRailProps) {
  if (events.length === 0) {
    return <EmptyState title={emptyTitle} description={emptyDescription} action={{ label: emptyActionLabel, onClick: onEmptyAction }} />;
  }

  return (
    <div className="space-y-0">
      {events.map((event, index) => (
        <div key={`${event.event}-${event.timestamp}-${index}`} className="relative pl-8">
          <div className="absolute left-2 top-1 h-full w-px bg-cyan-300/15" />
          <div className="absolute left-0 top-1 flex h-4 w-4 items-center justify-center rounded-full border border-cyan-300/30 bg-slate-950">
            <div className="h-1.5 w-1.5 rounded-full bg-cyan-300" />
          </div>
          <div className="mb-3 rounded-2xl border border-white/10 bg-slate-950/40 p-3">
            <div className="flex items-start justify-between gap-3">
              <div className="min-w-0">
                <div className="text-sm font-black text-cyan-100">{event.event.replaceAll("_", " ")}</div>
                <div className="mt-1 text-sm leading-6 text-slate-300">{event.message}</div>
              </div>
              <div className="shrink-0 rounded-full border border-white/10 bg-white/[0.04] px-2.5 py-1 text-[11px] font-black text-slate-400">
                {event.actor}
              </div>
            </div>
            <div className="mt-2 font-mono text-[11px] text-slate-500">{new Date(event.timestamp).toLocaleString()}</div>
          </div>
        </div>
      ))}
    </div>
  );
}
