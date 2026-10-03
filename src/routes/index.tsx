import { createFileRoute, Link } from "@tanstack/react-router";
import { ArrowRight, Building2, Camera, Flower2, Network, Satellite } from "lucide-react";

import { AppHeader } from "@/components/layout/AppHeader";

export const Route = createFileRoute("/")({
  component: Index,
  head: () => ({
    meta: [
      { title: "Plantatio — AI growing intelligence" },
      {
        name: "description",
        content:
          "A knowledge-graph assistant, leaf-disease classification and satellite restoration analysis, for home growers and restoration operators.",
      },
    ],
  }),
});

const CAPABILITIES = [
  {
    icon: Network,
    title: "Knowledge graph",
    body: "Answers are retrieved from a graph built from 62 tomato research papers, and every reply shows the facts behind it.",
  },
  {
    icon: Camera,
    title: "Leaf diagnosis",
    body: "A convolutional classifier reads a leaf photograph and reports the likely disease with ranked confidence.",
  },
  {
    icon: Satellite,
    title: "Restoration analysis",
    body: "Satellite imagery is scored for canopy, biomass and carbon, then compared against a baseline capture.",
  },
];

function Index() {
  return (
    <div className="min-h-screen bg-background">
      <AppHeader />

      <main className="mx-auto max-w-6xl px-4 py-10 sm:px-6 sm:py-16">
        <section
          className="rounded-3xl p-8 text-on-hero sm:p-12 md:p-16"
          style={{
            background: "var(--gradient-hero)",
            boxShadow: "var(--shadow-elegant)",
          }}
        >
          <div className="max-w-2xl">
            <p className="mb-3 inline-flex rounded-full bg-white/15 px-3 py-1 text-xs backdrop-blur">
              Knowledge graph · Computer vision · Satellite analysis
            </p>
            <h1 className="text-3xl font-semibold leading-tight sm:text-4xl md:text-5xl">
              Grow smarter.
              <br />
              Restore at scale.
            </h1>
            <p className="mt-4 max-w-xl text-base opacity-90">
              One AI system spanning a windowsill tomato and a thousand-hectare restoration site —
              grounded in published agronomy, not guesswork.
            </p>
          </div>
        </section>

        <section className="mt-10 grid gap-6 md:grid-cols-2">
          <SegmentCard
            to="/b2c"
            icon={Flower2}
            title="For growers"
            body="Track your plants, scan a leaf for disease, and ask an assistant that cites the research behind each answer."
            cta="Open the grower app"
          />
          <SegmentCard
            to="/b2b"
            icon={Building2}
            title="For enterprise"
            body="Discover restoration candidates on a live map, audit satellite imagery over time, and orchestrate the sensor fleet."
            cta="Open the console"
          />
        </section>

        <section className="mt-12">
          <h2 className="text-lg font-semibold tracking-tight">What is under the hood</h2>
          <div className="mt-4 grid gap-4 sm:grid-cols-3">
            {CAPABILITIES.map(({ icon: Icon, title, body }) => (
              <article key={title} className="rounded-2xl border bg-card p-5">
                <Icon className="h-5 w-5 text-primary" aria-hidden="true" />
                <h3 className="mt-3 text-sm font-semibold">{title}</h3>
                <p className="mt-1.5 text-sm leading-relaxed text-muted-foreground">{body}</p>
              </article>
            ))}
          </div>
        </section>
      </main>

      <footer className="border-t">
        <div className="mx-auto max-w-6xl px-4 py-6 text-xs text-muted-foreground sm:px-6">
          Plantatio — a portfolio project demonstrating GraphRAG, agentic orchestration and applied
          computer vision.
        </div>
      </footer>
    </div>
  );
}

function SegmentCard({
  to,
  icon: Icon,
  title,
  body,
  cta,
}: {
  to: string;
  icon: typeof Flower2;
  title: string;
  body: string;
  cta: string;
}) {
  return (
    <Link
      to={to}
      className="group rounded-2xl border bg-card p-7 transition-all hover:-translate-y-0.5 hover:shadow-lg"
    >
      <Icon className="h-7 w-7 text-primary" aria-hidden="true" />
      <h2 className="mt-4 text-xl font-semibold">{title}</h2>
      <p className="mt-2 text-sm leading-relaxed text-muted-foreground">{body}</p>
      <span className="mt-4 inline-flex items-center gap-1 text-sm font-medium text-primary">
        {cta}
        <ArrowRight
          className="h-4 w-4 transition-transform group-hover:translate-x-1"
          aria-hidden="true"
        />
      </span>
    </Link>
  );
}
