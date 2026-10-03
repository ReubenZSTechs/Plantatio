import { createFileRoute } from "@tanstack/react-router";

import { MacroDataMap } from "@/components/plantatio/MacroDataMap";

export const Route = createFileRoute("/b2b/map")({
  component: MacroDataMap,
  head: () => ({ meta: [{ title: "Site Map — Plantatio" }] }),
});
