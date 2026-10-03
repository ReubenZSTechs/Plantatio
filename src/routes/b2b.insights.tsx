import { createFileRoute } from "@tanstack/react-router";

import { InsightEngine } from "@/components/plantatio/InsightEngine";

export const Route = createFileRoute("/b2b/insights")({
  component: InsightEngine,
  head: () => ({ meta: [{ title: "Insight Engine — Plantatio" }] }),
});
