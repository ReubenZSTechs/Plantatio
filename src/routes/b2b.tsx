import { createFileRoute } from "@tanstack/react-router";
import { B2BMainLayout } from "@/components/plantatio/B2BMainLayout";
import { Toaster } from "@/components/ui/sonner";

export const Route = createFileRoute("/b2b")({
  component: () => (
    <>
      <B2BMainLayout />
      <Toaster />
    </>
  ),
  head: () => ({
    meta: [
      { title: "PLANTATIO B2B — ESG Orchestration" },
      { name: "description", content: "Enterprise restoration dashboard, IoT orchestration, and audited ESG reporting." },
    ],
  }),
});