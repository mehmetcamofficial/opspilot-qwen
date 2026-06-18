type TextProps = {
  children: React.ReactNode;
  className?: string;
};

export function PageTitle({ children, className = "" }: TextProps) {
  return <h1 className={`text-4xl font-black tracking-tight text-white md:text-6xl ${className}`}>{children}</h1>;
}

export function SectionTitle({ children, className = "" }: TextProps) {
  return <h2 className={`text-2xl font-black tracking-tight text-white ${className}`}>{children}</h2>;
}

export function BodyText({ children, className = "" }: TextProps) {
  return <p className={`text-sm leading-6 text-slate-400 ${className}`}>{children}</p>;
}

export function LabelText({ children, className = "" }: TextProps) {
  return <div className={`text-xs font-bold uppercase tracking-wider text-slate-500 ${className}`}>{children}</div>;
}
