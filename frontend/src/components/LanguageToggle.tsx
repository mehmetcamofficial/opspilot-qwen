"use client";

import { useSyncExternalStore } from "react";

const storageKey = "opspilot-language";

function getLanguageSnapshot() {
  if (typeof window === "undefined") {
    return "EN" as const;
  }

  const stored = window.localStorage.getItem(storageKey);
  return stored === "TR" ? "TR" : "EN";
}

function subscribe(callback: () => void) {
  window.addEventListener("opspilot-language-change", callback);
  window.addEventListener("storage", callback);

  return () => {
    window.removeEventListener("opspilot-language-change", callback);
    window.removeEventListener("storage", callback);
  };
}

export function LanguageToggle() {
  const language = useSyncExternalStore(subscribe, getLanguageSnapshot, () => "EN");

  function toggleLanguage() {
    const next = language === "EN" ? "TR" : "EN";
    window.localStorage.setItem(storageKey, next);
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
