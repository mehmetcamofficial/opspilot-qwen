"use client";

import Link from "next/link";
import { useMemo, useState } from "react";
import { Icon } from "@/components/ui/Icon";

type Command = {
  label: string;
  href: string;
  hint: string;
};

type CommandPaletteProps = {
  commands: Command[];
  emptyLabel: string;
  isOpen: boolean;
  onClose: () => void;
  placeholder: string;
  title: string;
};

export function CommandPalette({ commands, emptyLabel, isOpen, onClose, placeholder, title }: CommandPaletteProps) {
  const [query, setQuery] = useState("");
  const filteredCommands = useMemo(() => {
    const normalizedQuery = query.trim().toLowerCase();
    if (!normalizedQuery) return commands;
    return commands.filter((command) => `${command.label} ${command.hint}`.toLowerCase().includes(normalizedQuery));
  }, [commands, query]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-[100] bg-slate-950/70 p-4 backdrop-blur-xl" role="dialog" aria-modal="true">
      <button type="button" aria-label="Close command palette" className="absolute inset-0 cursor-default" onClick={onClose} />
      <div className="relative mx-auto mt-20 max-w-2xl overflow-hidden rounded-[2rem] border border-white/10 bg-slate-950/95 shadow-[0_0_80px_rgba(34,211,238,0.16)]">
        <div className="border-b border-white/10 p-4">
          <div className="mb-3 flex items-center justify-between gap-4">
            <div className="flex items-center gap-2 text-sm font-black text-white">
              <Icon name="spark" className="h-4 w-4 text-cyan-200" />
              {title}
            </div>
            <kbd className="rounded-lg border border-white/10 bg-white/[0.04] px-2 py-1 text-[11px] font-black text-slate-400">Esc</kbd>
          </div>
          <input
            autoFocus
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            placeholder={placeholder}
            className="w-full rounded-2xl border border-white/10 bg-white/[0.04] px-4 py-3 text-sm font-bold text-white outline-none placeholder:text-slate-600 focus:border-cyan-300/40"
          />
        </div>

        <div className="max-h-[420px] overflow-y-auto p-2">
          {filteredCommands.length === 0 ? (
            <div className="p-4 text-sm text-slate-500">{emptyLabel}</div>
          ) : (
            filteredCommands.map((command) => (
              <Link
                key={`${command.href}-${command.label}`}
                href={command.href}
                onClick={onClose}
                className="flex items-center justify-between gap-4 rounded-2xl px-4 py-3 text-sm transition hover:bg-cyan-300/10 active:scale-[0.99]"
              >
                <span className="font-black text-slate-100">{command.label}</span>
                <span className="text-xs font-bold text-slate-500">{command.hint}</span>
              </Link>
            ))
          )}
        </div>
      </div>
    </div>
  );
}
