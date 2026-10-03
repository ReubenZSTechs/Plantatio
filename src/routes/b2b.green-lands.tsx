import { createFileRoute } from "@tanstack/react-router";

import { GreenLandsView } from "@/components/plantatio/GreenLandsView";

export const Route = createFileRoute("/b2b/green-lands")({
  component: GreenLandsView,
  head: () => ({ meta: [{ title: "Green Lands — Plantatio" }] }),
});
