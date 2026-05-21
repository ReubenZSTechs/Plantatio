import { createFileRoute, Link } from "@tanstack/react-router";
import { Sprout, Flower2,Smartphone, Building2, ArrowRight } from "lucide-react";

export const Route = createFileRoute("/")({
  component: Index,
  head: () => ({
    meta: [
      { title: "PLANTATIO — Tree planting mentor & ESG orchestration" },
      {
        name: "description",
        content:
          "Deep-tech platform connecting hobby gardeners and corporate restoration through AI, IoT and audited ESG reporting.",
      },
    ],
  }),
});

function Index() {
  return (
    <div className="min-h-screen bg-background">
      <header className="border-b">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-4">
          <div className="flex items-center gap-2 font-semibold">
            <Sprout className="h-6 w-6 text-primary" />
            PLANTATIO
          </div>
          <div className="text-xs text-muted-foreground">Prototype</div>
        </div>
      </header>
      <main className="mx-auto max-w-6xl px-6 py-16">
        <section
          className="rounded-3xl p-10 text-primary-foreground md:p-16"
          style={{ background: "var(--gradient-hero)", boxShadow: "var(--shadow-elegant)" }}
        >
          <div className="max-w-2xl">
            <div className="mb-3 inline-flex rounded-full bg-white/15 px-3 py-1 text-xs backdrop-blur">
              Deep-tech · AI · IoT · ESG
            </div>
            <h1 className="text-4xl font-semibold leading-tight md:text-5xl">
              Plant smarter.<br />Restore at scale.
            </h1>
            <p className="mt-4 max-w-xl text-base opacity-90">
              Scaling from urban gardens to thousand-hectare carbon sinks. A singular cognitive engine integrating smart probes, satellite intelligence, autonomous AI, and audited ESG compliance
            </p>
          </div>
        </section>

        <section className="mt-10 grid gap-6 md:grid-cols-2">
          <Link
            to="/b2c"
            className="group rounded-2xl border bg-card p-8 transition-all hover:-translate-y-0.5 hover:shadow-lg"
          >
          <Flower2 className="h-8 w-8 text-primary" />
            <h2 className="mt-4 text-xl font-semibold">Plantatio For Hobby</h2>
            <p className="mt-2 text-sm text-muted-foreground">
              Empowering plant owners with live IoT telemetry, Omni-Scan AI context, weather-adaptive care plans, and a Vision AI assistant for instant diagnostics.
            </p>
            <div className="mt-4 inline-flex items-center gap-1 text-sm font-medium text-primary">
              Explore Plantatio For Hobby{" "}
              <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-1" />
            </div>
          </Link>
          <Link
            to="/b2b"
            className="group rounded-2xl border bg-card p-8 transition-all hover:-translate-y-0.5 hover:shadow-lg"
          >
            <Building2 className="h-8 w-8 text-primary" />
            <h2 className="mt-4 text-xl font-semibold">Plantatio For Business</h2>
            <p className="mt-2 text-sm text-muted-foreground">
              Enterprise command center for large-scale reforestation. Featuring satellite ML audits, predictive AI pipelines, IoT orchestration, and verified ESG carbon reporting.
            </p>
            <div className="mt-4 inline-flex items-center gap-1 text-sm font-medium text-primary">
              Open enterprise console{" "}
              <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-1" />
            </div>
          </Link>
        </section>
      </main>
    </div>
  );
}