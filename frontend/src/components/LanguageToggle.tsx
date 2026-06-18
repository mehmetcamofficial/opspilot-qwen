"use client";

import { setStoredLanguage, useLanguage } from "@/lib/language";

export function LanguageToggle() {
  const language = useLanguage();

  function toggleLanguage() {
    const next = language === "EN" ? "TR" : "EN";
    setStoredLanguage(next);
  }

  return (
    <button
      onClick={toggleLanguage}
      className="rounded-full border border-cyan-400/20 bg-cyan-400/10 px-3 py-2 text-xs font-black text-cyan-100 hover:bg-cyan-400/20"
      aria-label="Toggle language"
      type="button"
    >
      {language}
    </button>
  );
}
