import { createFileRoute } from "@tanstack/react-router";
// Pastikan path import komponennya sesuai dengan struktur folder Anda
import { PlantGardenPage } from "@/components/plantatio/PlantGardenPage"; 

export const Route = createFileRoute("/garden/")({
  component: PlantGardenPage,
});