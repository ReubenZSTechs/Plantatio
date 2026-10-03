import { createFileRoute } from "@tanstack/react-router";

import { PlantDetailPage } from "@/components/plantatio/PlantDetailPage";

export const Route = createFileRoute("/garden/$plantId")({
  component: PlantDetailPage,
  head: () => ({ meta: [{ title: "Plant detail — Plantatio" }] }),
});
