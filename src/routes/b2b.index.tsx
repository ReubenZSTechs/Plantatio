import { createFileRoute, redirect } from "@tanstack/react-router";

/** The console opens on ESG analytics. */
export const Route = createFileRoute("/b2b/")({
  beforeLoad: () => {
    throw redirect({ to: "/b2b/esg" });
  },
});
