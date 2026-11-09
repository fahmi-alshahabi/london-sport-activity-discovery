// Types mirroring the PUBLIC ApplicationEnvelope projection (contract boundary from /api/envelope).
// The client consumes the projected envelope only; it never re-derives evidence (ADR-0001).

export type EvidenceState = "T" | "F" | "U" | "B";

export interface PublicAttribute {
  predicate_id: string;
  evidence_state: EvidenceState;
  grade?: string;
}

export interface PublicCandidate {
  candidate_id: string;
  rank: number;
  pool: "supported" | "indeterminate" | "excluded";
  provider_link?: string;
  attributes: PublicAttribute[];
}

export interface PublicDecision {
  terminal_decision: string;
  recommendation_action: string;
  scope_qualifier: string;
  coverage_qualifier?: { statement?: string };
  versions?: { vintage?: string };
  candidates: PublicCandidate[];
}

export interface PublicEnvelope {
  action_kind: string;
  payload?: { decision?: PublicDecision };
}
