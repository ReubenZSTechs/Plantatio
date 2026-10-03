import { createFileRoute } from "@tanstack/react-router";

import { DeviceManager } from "@/components/plantatio/DeviceManager";

export const Route = createFileRoute("/b2b/devices")({
  component: DeviceManager,
  head: () => ({ meta: [{ title: "Devices — Plantatio" }] }),
});
