import { createFileRoute } from "@tanstack/react-router";

import { B2BMainLayout } from "@/components/plantatio/B2BMainLayout";

export const Route = createFileRoute("/b2b")({
  component: B2BMainLayout,
  head: () => ({
    meta: [
      { title: "Plantatio for Enterprise — restoration and ESG" },
      {
        name: "description",
        content:
          "Satellite restoration audits, green-land discovery, IoT orchestration and ESG reporting.",
      },
    ],
  }),
});
