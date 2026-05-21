import { createFileRoute } from "@tanstack/react-router";
// Sesuaikan bagian ujungnya menjadi "PlantDetailPage"
import { PlantDetailPage } from "@/components/plantatio/PlantDetailPage"; 

export const Route = createFileRoute("/garden/$plantId")({
  component: PlantDetailPage,
});