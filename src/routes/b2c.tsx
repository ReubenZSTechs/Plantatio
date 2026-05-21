import { createFileRoute } from "@tanstack/react-router";
import { B2CMainLayout } from "@/components/plantatio/B2CMainLayout";
import { Toaster } from "@/components/ui/sonner";

export const Route = createFileRoute("/b2c")({
  component: () => (
    <>
      <B2CMainLayout />
      <Toaster />
    </>
  ),
  head: () => ({
    meta: [
      { title: "PLANTATIO B2C — Hobby & Urban Gardening" },
      { name: "description", content: "Mobile gardening companion with AI diagnostics and smart probes." },
    ],
  }),
});