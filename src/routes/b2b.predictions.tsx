import { createFileRoute } from "@tanstack/react-router";

import { MLPredictionManager } from "@/components/plantatio/MLPredictionManager";

export const Route = createFileRoute("/b2b/predictions")({
  component: MLPredictionManager,
  head: () => ({ meta: [{ title: "Models — Plantatio" }] }),
});
