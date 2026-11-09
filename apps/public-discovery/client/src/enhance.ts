// Progressive enhancement entry. Loads ONLY after the SSR page is already usable.
// If this script never runs (JS disabled/failed), the server-rendered core is unaffected.

import type { PublicEnvelope } from "./types";

function announce(message: string): void {
  let region = document.getElementById("pe-status");
  if (!region) {
    region = document.createElement("p");
    region.id = "pe-status";
    region.setAttribute("role", "status");
    region.setAttribute("aria-live", "polite");
    region.className = "meta";
    const main = document.getElementById("main");
    main?.prepend(region);
  }
  region.textContent = message;
}

async function fetchEnvelope(scenario: string): Promise<PublicEnvelope | null> {
  try {
    const res = await fetch(`/api/envelope?scenario=${encodeURIComponent(scenario)}`, {
      headers: { Accept: "application/json" },
    });
    if (!res.ok) return null;
    return (await res.json()) as PublicEnvelope;
  } catch {
    return null; // enhancement only: never break the core
  }
}

async function init(): Promise<void> {
  const slate = document.querySelector(".slate");
  if (slate) {
    const n = slate.querySelectorAll(":scope > li").length;
    announce(`${n} option${n === 1 ? "" : "s"} shown. Order is fixed by the service and cannot be re-ranked here.`);
  }

  const compareMount = document.querySelector<HTMLElement>('[data-enhance="compare"]');
  if (compareMount) {
    const scenario = compareMount.dataset.scenario ?? "supported";
    const env = await fetchEnvelope(scenario);
    if (env) {
      const { mountCompare } = await import("./compare");
      mountCompare(compareMount, env);
    }
  }
}

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", () => void init());
} else {
  void init();
}
