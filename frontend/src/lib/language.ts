"use client";

import { useSyncExternalStore } from "react";

export type Language = "EN" | "TR";

export const languageStorageKey = "opspilot-language";

function getLanguageSnapshot(): Language {
  if (typeof window === "undefined") {
    return "EN";
  }

  const stored = window.localStorage.getItem(languageStorageKey);
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

export function useLanguage(): Language {
  return useSyncExternalStore(subscribe, getLanguageSnapshot, () => "EN");
}

export function setStoredLanguage(language: Language) {
  window.localStorage.setItem(languageStorageKey, language);
  window.dispatchEvent(new CustomEvent("opspilot-language-change", { detail: language }));
}
