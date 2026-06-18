type LoadingSkeletonProps = {
  rows?: number;
};

export function LoadingSkeleton({ rows = 3 }: LoadingSkeletonProps) {
  return (
    <div className="grid gap-3">
      {Array.from({ length: rows }).map((_, index) => (
        <div key={index} className="overflow-hidden rounded-2xl border border-white/10 bg-white/[0.035] p-4">
          <div className="h-3 w-28 animate-pulse rounded-full bg-slate-700/80" />
          <div className="mt-4 h-4 w-2/3 animate-pulse rounded-full bg-slate-700/70" />
          <div className="mt-3 h-3 w-full animate-pulse rounded-full bg-slate-800/80" />
        </div>
      ))}
    </div>
  );
}
