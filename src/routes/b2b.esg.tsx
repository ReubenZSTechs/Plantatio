import { createFileRoute } from "@tanstack/react-router";

import { ESGAnalyticsDashboard } from "@/components/plantatio/ESGAnalyticsDashboard";

export const Route = createFileRoute("/b2b/esg")({
  component: ESGAnalyticsDashboard,
  head: () => ({ meta: [{ title: "ESG Analytics — Plantatio" }] }),
});
