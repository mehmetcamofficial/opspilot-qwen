import Link from "next/link";
import { Icon } from "@/components/ui/Icon";

type EmptyStateProps = {
  title: string;
  description: string;
  action?: {
    label: string;
    href?: string;
    onClick?: () => void;
  };
};

export function EmptyState({ title, description, action }: EmptyStateProps) {
  const actionClassName =
    "mt-5 inline-flex rounded-2xl border border-cyan-300/25 bg-cyan-300/10 px-4 py-2 text-sm font-black text-cyan-50 transition hover:bg-cyan-300/20 active:scale-[0.98]";

  return (
    <div className="rounded-3xl border border-white/10 bg-white/[0.035] p-6 text-center">
      <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-2xl border border-cyan-300/25 bg-cyan-300/10 text-lg font-black text-cyan-100">
        <Icon name="spark" className="h-5 w-5" />
      </div>
      <h3 className="mt-4 text-lg font-black text-white">{title}</h3>
      <p className="mx-auto mt-2 max-w-xl text-sm leading-6 text-slate-400">{description}</p>

      {action?.href ? (
        <Link href={action.href} className={actionClassName}>
          {action.label}
        </Link>
      ) : action?.onClick ? (
        <button type="button" onClick={action.onClick} className={actionClassName}>
          {action.label}
        </button>
      ) : null}
    </div>
  );
}
