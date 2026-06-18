export type Severity = "P0" | "P1" | "P2" | "P3";
export type SemanticTone = "cyan" | "green" | "amber" | "red" | "violet" | "slate";

export function toneForSeverity(severity?: string | null): SemanticTone {
  if (severity === "P0") return "red";
  if (severity === "P1") return "amber";
  if (severity === "P2") return "violet";
  return "slate";
}
