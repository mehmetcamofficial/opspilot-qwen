import { Icon } from "@/components/ui/Icon";

type InlineErrorProps = {
  title: string;
  message: string;
  actionLabel?: string;
  onAction?: () => void;
};

export function InlineError({ title, message, actionLabel, onAction }: InlineErrorProps) {
  return (
    <div className="rounded-3xl border border-amber-400/25 bg-amber-400/10 p-5 text-sm leading-6 text-amber-50">
      <div className="flex items-center gap-2 font-black text-amber-100">
        <Icon name="warning" className="h-4 w-4" />
        {title}
      </div>
      <p className="mt-2 text-amber-50/80">{message}</p>
      {actionLabel && onAction ? (
        <button
          type="button"
          onClick={onAction}
          className="mt-4 rounded-2xl border border-amber-300/25 bg-amber-300/10 px-4 py-2 text-xs font-black text-amber-50 transition hover:bg-amber-300/20 active:scale-[0.98]"
        >
          {actionLabel}
        </button>
      ) : null}
    </div>
  );
}
