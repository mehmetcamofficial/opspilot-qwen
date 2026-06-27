import { PlatformShell } from "@/components/PlatformShell";
import { StatusBadge } from "@/components/StatusBadge";

const posts = [
  {
    title: "Why incident response needs multi-agent systems",
    category: "AI Operations",
    status: "Published",
    excerpt: "Single chatbot answers are not enough for production operations. OpsPilot separates triage, evidence, risk, approval, and postmortem work into specialized agents.",
  },
  {
    title: "Human-in-the-loop remediation for safer automation",
    category: "Safety",
    status: "Published",
    excerpt: "Production remediation should include policy checks, rollback plans, approval gates, and post-action verification.",
  },
  {
    title: "Qwen Cloud as the reasoning layer for OpsPilot",
    category: "Qwen Cloud",
    status: "Draft",
    excerpt: "OpsPilot is designed to use Qwen-compatible reasoning for hypotheses, remediation planning, risk review, and postmortem generation.",
  },
  {
    title: "Alibaba Cloud ECS rollout unlocked",
    category: "Deployment",
    status: "Published",
    excerpt: "Alibaba Cloud credits are active, so the FastAPI backend can move from rollout plan to ECS deployment execution.",
  },
];

export default function BlogPage() {
  return (
    <PlatformShell>
      <section className="mx-auto max-w-7xl px-6 pb-20 pt-10">
        <div className="mb-8">
          <div className="mb-4 flex flex-wrap gap-3">
            <StatusBadge label="Blog" tone="cyan" />
            <StatusBadge label="EN / TR ready" tone="violet" />
            <StatusBadge label="Credits active" tone="green" />
          </div>
          <h1 className="text-4xl font-black text-white md:text-6xl">OpsPilot Intelligence Blog</h1>
          <p className="mt-4 max-w-3xl text-slate-400">
            A content hub for AI operations, incident response, Qwen Cloud integration, safety policy, and the newly unlocked Alibaba Cloud rollout.
          </p>
        </div>

        <div className="grid gap-5 md:grid-cols-2">
          {posts.map((post) => (
            <article key={post.title} className="rounded-3xl border border-white/10 bg-white/[0.04] p-6 backdrop-blur">
              <div className="mb-4 flex flex-wrap items-center gap-2">
                <StatusBadge label={post.category} tone="cyan" />
                <StatusBadge
                  label={post.status}
                  tone={post.status === "Published" ? "green" : post.status === "Draft" ? "amber" : "slate"}
                />
              </div>
              <h2 className="text-2xl font-black text-white">{post.title}</h2>
              <p className="mt-4 leading-7 text-slate-400">{post.excerpt}</p>
              <div className="mt-6 rounded-2xl border border-white/10 bg-slate-950/50 p-4 text-sm text-slate-400">
                Admin actions planned: edit, publish, archive, delete, translate.
              </div>
            </article>
          ))}
        </div>
      </section>
    </PlatformShell>
  );
}
