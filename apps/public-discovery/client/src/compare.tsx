// Optional compare view (React). Enhancement only — the SSR detail/results pages already work.
// It preserves unknown/conflict cells and never invents a "winner" (WP §7.3).

import React from "react";
import { createRoot } from "react-dom/client";
import type { PublicEnvelope, PublicCandidate, EvidenceState } from "./types";

const STATE_TEXT: Record<EvidenceState, string> = {
  T: "confirmed",
  F: "not offered (published)",
  U: "not published",
  B: "sources disagree",
};

function predicateIds(cands: PublicCandidate[]): string[] {
  const ids = new Set<string>();
  cands.forEach((c) => c.attributes.forEach((a) => ids.add(a.predicate_id)));
  return Array.from(ids);
}

function CompareTable({ env }: { env: PublicEnvelope }): React.ReactElement {
  const cands = env.payload?.decision?.candidates ?? [];
  const preds = predicateIds(cands);
  return (
    <table>
      <caption>Compare options (evidence preserved; no composite winner)</caption>
      <thead>
        <tr>
          <th scope="col">Requirement</th>
          {cands.map((c) => (
            <th scope="col" key={c.candidate_id}>{`#${c.rank} ${c.candidate_id}`}</th>
          ))}
        </tr>
      </thead>
      <tbody>
        {preds.map((pid) => (
          <tr key={pid}>
            <th scope="row">{pid}</th>
            {cands.map((c) => {
              const a = c.attributes.find((x) => x.predicate_id === pid);
              const text = a ? STATE_TEXT[a.evidence_state] : "not published";
              return <td key={c.candidate_id + pid}>{text}</td>;
            })}
          </tr>
        ))}
      </tbody>
    </table>
  );
}

export function mountCompare(el: HTMLElement, env: PublicEnvelope): void {
  createRoot(el).render(<CompareTable env={env} />);
}
