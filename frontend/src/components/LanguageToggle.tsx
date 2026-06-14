"use client";

import { useEffect, useState } from "react";

export function LanguageToggle() {
  const [language, setLanguage] = useState<"EN" | "TR">("EN");

  useEffect(() => {
    const stored = window.localStorage.getItem("opspilot-language");
    if (stored === "TR" || stored === "EN") {
      setLanguage(stored);
    }
  }, []);

  function toggleLanguage() {
    const next = language === "EN" ? "TR" : "EN";
    setLanguage(next);
    window.localStorage.setItem("opspilot-language", next);
    window.dispatchEvent(new CustomEvent("opspilot-language-change", { detail: next }));
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
