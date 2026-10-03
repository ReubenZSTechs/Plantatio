import { createFileRoute } from "@tanstack/react-router";

import { PlantGardenPage } from "@/components/plantatio/PlantGardenPage";

export const Route = createFileRoute("/garden/")({
  component: PlantGardenPage,
  head: () => ({ meta: [{ title: "My garden — Plantatio" }] }),
});
