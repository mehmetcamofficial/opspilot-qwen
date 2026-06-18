import { StatusBadge } from "@/components/StatusBadge";
import { BodyText, LabelText } from "@/components/ui/Typography";
import { toneForSeverity } from "@/lib/severity";

type IncidentCardProps = {
  incidentId?: string;
  service?: string;
  severity?: string;
  status?: string;
  assignee?: string;
  age?: string;
  copy: {
    age: string;
    assignee: string;
    incident: string;
    noActiveIncident: string;
    service: string;
    severity: string;
    status: string;
    unassigned: string;
  };
};

export function IncidentCard({ incidentId, service, severity, status, assignee, age = "now", copy }: IncidentCardProps) {
  return (
    <article className="rounded-3xl border border-white/10 bg-white/[0.04] p-5 transition hover:-translate-y-0.5 hover:border-cyan-300/25 hover:bg-white/[0.055]">
      <div className="flex items-start justify-between gap-4">
        <div className="min-w-0">
          <LabelText>{copy.incident}</LabelText>
          <div className="mt-2 truncate font-mono text-lg font-black text-cyan-100">
            {incidentId || copy.noActiveIncident}
          </div>
        </div>
        <StatusBadge label={severity || "P3"} tone={toneForSeverity(severity)} />
      </div>

      <div className="mt-4 grid gap-3 sm:grid-cols-2">
        <Meta label={copy.service} value={service || "checkout-api"} />
        <Meta label={copy.status} value={status || "standby"} />
        <Meta label={copy.assignee} value={assignee || copy.unassigned} />
        <Meta label={copy.age} value={age} />
      </div>

      <BodyText className="mt-4">
        {copy.severity}: {severity || "P3"} · {copy.status}: {status || "standby"}
      </BodyText>
    </article>
  );
}

function Meta({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <LabelText>{label}</LabelText>
      <div className="mt-1 truncate text-sm font-black text-white">{value}</div>
    </div>
  );
}
