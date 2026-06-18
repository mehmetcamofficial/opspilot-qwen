import { Icon } from "@/components/ui/Icon";

export type ToastTone = "success" | "error" | "warning" | "info";

export type ToastMessage = {
  id: number;
  message: string;
  tone: ToastTone;
};

type ToastStackProps = {
  items: ToastMessage[];
  onDismiss: (id: number) => void;
};

const styles: Record<ToastTone, string> = {
  success: "border-emerald-400/25 bg-emerald-400/10 text-emerald-50",
  error: "border-red-400/25 bg-red-400/10 text-red-50",
  warning: "border-amber-400/25 bg-amber-400/10 text-amber-50",
  info: "border-cyan-400/25 bg-cyan-400/10 text-cyan-50",
};

const icons: Record<ToastTone, "alert" | "check" | "info" | "warning"> = {
  success: "check",
  error: "alert",
  warning: "warning",
  info: "info",
};

export function ToastStack({ items, onDismiss }: ToastStackProps) {
  return (
    <div className="fixed bottom-6 right-6 z-[90] grid w-[min(360px,calc(100vw-2rem))] gap-3">
      {items.map((item) => (
        <div key={item.id} className={`rounded-2xl border p-4 shadow-[0_0_40px_rgba(15,23,42,0.35)] backdrop-blur-xl ${styles[item.tone]}`}>
          <div className="flex items-start gap-3">
            <Icon name={icons[item.tone]} className="mt-0.5 h-4 w-4 shrink-0" />
            <div className="min-w-0 flex-1 text-sm font-bold leading-5">{item.message}</div>
            <button type="button" onClick={() => onDismiss(item.id)} className="shrink-0 opacity-70 hover:opacity-100" aria-label="Dismiss notification">
              <Icon name="x" className="h-4 w-4" />
            </button>
          </div>
        </div>
      ))}
    </div>
  );
}
