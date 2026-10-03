import { createFileRoute } from "@tanstack/react-router";

import { B2CMainLayout } from "@/components/plantatio/B2CMainLayout";

export const Route = createFileRoute("/b2c")({
  component: B2CMainLayout,
  head: () => ({
    meta: [
      { title: "Plantatio for Growers — AI plant care" },
      {
        name: "description",
        content:
          "Track your plants, scan leaves for disease, and ask an assistant grounded in agronomy research.",
      },
    ],
  }),
});
