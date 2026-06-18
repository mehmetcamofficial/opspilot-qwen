type PrintIncidentReportProps = {
  assignee: string;
  generatedAt: string;
  hypothesis: string;
  incidentId: string;
  postmortem: string;
  service: string;
  severity: string;
  status: string;
  title: string;
};

export function PrintIncidentReport({ assignee, generatedAt, hypothesis, incidentId, postmortem, service, severity, status, title }: PrintIncidentReportProps) {
  return (
    <section className="hidden bg-white p-10 text-slate-950 print:block">
      <div className="border-b border-slate-200 pb-6">
        <div className="text-sm font-bold uppercase tracking-[0.3em] text-slate-500">OpsPilot</div>
        <h1 className="mt-3 text-3xl font-black">{title}</h1>
        <div className="mt-2 text-sm text-slate-500">{generatedAt}</div>
      </div>

      <div className="mt-8 grid grid-cols-2 gap-4 text-sm">
        <PrintField label="Incident" value={incidentId} />
        <PrintField label="Status" value={status} />
        <PrintField label="Service" value={service} />
        <PrintField label="Severity" value={severity} />
        <PrintField label="Assignee" value={assignee} />
      </div>

      <div className="mt-8 space-y-6">
        <PrintBlock label="Leading hypothesis" value={hypothesis} />
        <PrintBlock label="Post-incident summary" value={postmortem} />
      </div>
    </section>
  );
}

function PrintField({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-xl border border-slate-200 p-4">
      <div className="text-xs font-bold uppercase tracking-wider text-slate-500">{label}</div>
      <div className="mt-2 font-black">{value}</div>
    </div>
  );
}

function PrintBlock({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <h2 className="text-lg font-black">{label}</h2>
      <p className="mt-2 leading-7 text-slate-700">{value}</p>
    </div>
  );
}
