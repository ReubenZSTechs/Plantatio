import { r as reactExports, W as jsxRuntimeExports } from "./server-BG8Cz_a2.js";
import { u as useQuery, S as SiteMap, p as potentialColor } from "./SiteMap-ToYsFHEg.js";
import { C as Card, B as Badge } from "./badge-Ci2zfins.js";
import { P as Progress } from "./progress-CCR5OBxf.js";
import { a as api } from "./api-BNzXBfwP.js";
import { c as createLucideIcon, a as cn } from "./utils-B3hKptjK.js";
import { L as LoaderCircle } from "./loader-circle-Ba4x-1QD.js";
import { T as TreeDeciduous } from "./tree-deciduous-Bf6GH39y.js";
import "node:async_hooks";
import "node:stream/web";
import "node:stream";
import "./router-DaN2asXe.js";
import "./index-CFniAsgI.js";
const __iconNode = [
  ["circle", { cx: "12", cy: "12", r: "10", key: "1mglay" }],
  ["path", { d: "M12 16v-4", key: "1dtifu" }],
  ["path", { d: "M12 8h.01", key: "e9boi3" }]
];
const Info = createLucideIcon("info", __iconNode);
const POTENTIAL_FILTERS = [
  { label: "All sites", value: 0 },
  { label: "Promising", value: 0.35 },
  { label: "High potential", value: 0.6 }
];
function GreenLandsView() {
  const [minPotential, setMinPotential] = reactExports.useState(0);
  const [selected, setSelected] = reactExports.useState(null);
  const parcels = useQuery({
    queryKey: ["land-parcels", minPotential],
    queryFn: () => api.listLandParcels({ minPotential: minPotential || void 0 })
  });
  const nodes = useQuery({ queryKey: ["devices"], queryFn: api.listDevices });
  const legend = useQuery({
    queryKey: ["land-cover-classes"],
    queryFn: api.getLandCoverClasses
  });
  const totals = reactExports.useMemo(() => {
    const rows = parcels.data ?? [];
    return {
      count: rows.length,
      hectares: rows.reduce((sum, p) => sum + (p.areaHectares ?? 0), 0),
      best: rows[0] ?? null
    };
  }, [parcels.data]);
  const active = selected ?? totals.best;
  return /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "space-y-6", children: [
    /* @__PURE__ */ jsxRuntimeExports.jsxs("header", { className: "flex flex-wrap items-end justify-between gap-3", children: [
      /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { children: [
        /* @__PURE__ */ jsxRuntimeExports.jsx("h1", { className: "text-2xl font-semibold tracking-tight", children: "Green Lands" }),
        /* @__PURE__ */ jsxRuntimeExports.jsx("p", { className: "text-sm text-muted-foreground", children: "Candidate parcels ranked by how much restoration they could support." })
      ] }),
      /* @__PURE__ */ jsxRuntimeExports.jsx("div", { className: "flex gap-1.5", role: "group", "aria-label": "Filter by potential", children: POTENTIAL_FILTERS.map((filter) => /* @__PURE__ */ jsxRuntimeExports.jsx(
        "button",
        {
          type: "button",
          onClick: () => setMinPotential(filter.value),
          "aria-pressed": minPotential === filter.value,
          className: cn(
            "rounded-full border px-3 py-1 text-xs transition-colors",
            minPotential === filter.value ? "border-primary bg-primary text-primary-foreground" : "text-muted-foreground hover:bg-secondary"
          ),
          children: filter.label
        },
        filter.label
      )) })
    ] }),
    /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "grid gap-3 sm:grid-cols-3", children: [
      /* @__PURE__ */ jsxRuntimeExports.jsx(SummaryTile, { label: "Candidate parcels", value: String(totals.count) }),
      /* @__PURE__ */ jsxRuntimeExports.jsx(SummaryTile, { label: "Total area", value: `${totals.hectares.toFixed(1)} ha` }),
      /* @__PURE__ */ jsxRuntimeExports.jsx(
        SummaryTile,
        {
          label: "Best opportunity",
          value: totals.best?.name ?? "—",
          hint: totals.best ? `${((totals.best.restorationPotential ?? 0) * 100).toFixed(0)}% potential` : void 0
        }
      )
    ] }),
    /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "grid gap-4 lg:grid-cols-[minmax(0,1.5fr)_minmax(0,1fr)]", children: [
      /* @__PURE__ */ jsxRuntimeExports.jsx(Card, { className: "overflow-hidden p-0", children: parcels.isLoading ? /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex h-[420px] items-center justify-center text-sm text-muted-foreground", children: [
        /* @__PURE__ */ jsxRuntimeExports.jsx(LoaderCircle, { className: "mr-2 h-4 w-4 animate-spin", "aria-hidden": "true" }),
        "Loading site map…"
      ] }) : parcels.isError ? /* @__PURE__ */ jsxRuntimeExports.jsx("div", { className: "flex h-[420px] items-center justify-center px-6 text-center text-sm text-muted-foreground", children: "Could not load parcels. Check that the API is running." }) : /* @__PURE__ */ jsxRuntimeExports.jsx(
        SiteMap,
        {
          className: "h-[420px]",
          parcels: parcels.data ?? [],
          nodes: nodes.data ?? [],
          selectedParcelId: active?.id ?? null,
          onSelectParcel: setSelected
        }
      ) }),
      /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "space-y-4", children: [
        /* @__PURE__ */ jsxRuntimeExports.jsxs(Card, { className: "divide-y p-0", children: [
          /* @__PURE__ */ jsxRuntimeExports.jsx("h2", { className: "px-4 py-3 text-sm font-semibold", children: "Ranked candidates" }),
          (parcels.data ?? []).length === 0 && !parcels.isLoading && /* @__PURE__ */ jsxRuntimeExports.jsx("p", { className: "px-4 py-6 text-center text-sm text-muted-foreground", children: "No parcels match this filter." }),
          /* @__PURE__ */ jsxRuntimeExports.jsx("ul", { children: (parcels.data ?? []).map((parcel) => /* @__PURE__ */ jsxRuntimeExports.jsx("li", { children: /* @__PURE__ */ jsxRuntimeExports.jsxs(
            "button",
            {
              type: "button",
              onClick: () => setSelected(parcel),
              "aria-current": active?.id === parcel.id,
              className: cn(
                "flex w-full items-center gap-3 px-4 py-3 text-left transition-colors hover:bg-secondary/50",
                active?.id === parcel.id && "bg-secondary/60"
              ),
              children: [
                /* @__PURE__ */ jsxRuntimeExports.jsx(
                  "span",
                  {
                    className: "h-8 w-1.5 shrink-0 rounded-full",
                    style: { background: potentialColor(parcel.restorationPotential) },
                    "aria-hidden": "true"
                  }
                ),
                /* @__PURE__ */ jsxRuntimeExports.jsxs("span", { className: "min-w-0 flex-1", children: [
                  /* @__PURE__ */ jsxRuntimeExports.jsx("span", { className: "block truncate text-sm font-medium", children: parcel.name }),
                  /* @__PURE__ */ jsxRuntimeExports.jsxs("span", { className: "block truncate text-xs text-muted-foreground", children: [
                    parcel.landCoverClass,
                    " · ",
                    parcel.areaHectares,
                    " ha"
                  ] })
                ] }),
                /* @__PURE__ */ jsxRuntimeExports.jsxs("span", { className: "text-sm font-semibold tabular-nums", children: [
                  ((parcel.restorationPotential ?? 0) * 100).toFixed(0),
                  "%"
                ] })
              ]
            }
          ) }, parcel.id)) })
        ] }),
        active && /* @__PURE__ */ jsxRuntimeExports.jsx(ParcelDetail, { parcel: active })
      ] })
    ] }),
    legend.data && legend.data.length > 0 && /* @__PURE__ */ jsxRuntimeExports.jsxs(Card, { className: "p-4", children: [
      /* @__PURE__ */ jsxRuntimeExports.jsxs("h2", { className: "flex items-center gap-1.5 text-sm font-semibold", children: [
        "Land-cover reference",
        /* @__PURE__ */ jsxRuntimeExports.jsx(Info, { className: "h-3.5 w-3.5 text-muted-foreground", "aria-hidden": "true" })
      ] }),
      /* @__PURE__ */ jsxRuntimeExports.jsx("p", { className: "mt-1 text-xs text-muted-foreground", children: "Headroom is how much restoration each cover type can absorb. Reference tile counts come from a labelled EuroSAT sample used to illustrate the classes — they are synthetic examples, not measurements of this site." }),
      /* @__PURE__ */ jsxRuntimeExports.jsx("ul", { className: "mt-3 grid gap-2 sm:grid-cols-2 lg:grid-cols-3", children: legend.data.map((entry) => /* @__PURE__ */ jsxRuntimeExports.jsxs("li", { className: "rounded-lg border p-2.5", children: [
        /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex items-center justify-between gap-2", children: [
          /* @__PURE__ */ jsxRuntimeExports.jsx("span", { className: "text-xs font-medium", children: entry.name }),
          /* @__PURE__ */ jsxRuntimeExports.jsxs(Badge, { variant: "secondary", className: "text-[10px]", children: [
            (entry.headroom * 100).toFixed(0),
            "%"
          ] })
        ] }),
        /* @__PURE__ */ jsxRuntimeExports.jsx("p", { className: "mt-1 text-[11px] leading-snug text-muted-foreground", children: entry.description })
      ] }, entry.name)) })
    ] })
  ] });
}
function SummaryTile({ label, value, hint }) {
  return /* @__PURE__ */ jsxRuntimeExports.jsxs(Card, { className: "p-4", children: [
    /* @__PURE__ */ jsxRuntimeExports.jsx("p", { className: "text-[11px] font-semibold uppercase tracking-wide text-muted-foreground", children: label }),
    /* @__PURE__ */ jsxRuntimeExports.jsx("p", { className: "mt-1 truncate text-xl font-semibold", children: value }),
    hint && /* @__PURE__ */ jsxRuntimeExports.jsx("p", { className: "text-xs text-muted-foreground", children: hint })
  ] });
}
function ParcelDetail({ parcel }) {
  const metrics = [
    { label: "Canopy cover", value: parcel.canopyCover },
    { label: "Est. biomass", value: parcel.estBiomass },
    { label: "Carbon equivalent", value: parcel.carbonEq }
  ];
  return /* @__PURE__ */ jsxRuntimeExports.jsxs(Card, { className: "space-y-3 p-4", children: [
    /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex items-start gap-2", children: [
      /* @__PURE__ */ jsxRuntimeExports.jsx(TreeDeciduous, { className: "mt-0.5 h-4 w-4 shrink-0 text-primary", "aria-hidden": "true" }),
      /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "min-w-0", children: [
        /* @__PURE__ */ jsxRuntimeExports.jsx("h2", { className: "truncate text-sm font-semibold", children: parcel.name }),
        /* @__PURE__ */ jsxRuntimeExports.jsxs("p", { className: "text-xs text-muted-foreground", children: [
          parcel.zone,
          " · ",
          parcel.areaHectares,
          " ha"
        ] })
      ] })
    ] }),
    parcel.rationale && /* @__PURE__ */ jsxRuntimeExports.jsx("p", { className: "rounded-lg bg-secondary/50 p-2.5 text-xs text-muted-foreground", children: parcel.rationale }),
    /* @__PURE__ */ jsxRuntimeExports.jsx("dl", { className: "space-y-2.5", children: metrics.map((metric) => /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { children: [
      /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex items-center justify-between text-xs", children: [
        /* @__PURE__ */ jsxRuntimeExports.jsx("dt", { className: "text-muted-foreground", children: metric.label }),
        /* @__PURE__ */ jsxRuntimeExports.jsx("dd", { className: "font-medium tabular-nums", children: metric.value === null ? "—" : `${(metric.value * 100).toFixed(0)}%` })
      ] }),
      /* @__PURE__ */ jsxRuntimeExports.jsx(Progress, { value: (metric.value ?? 0) * 100, className: "mt-1 h-1" })
    ] }, metric.label)) }),
    parcel.analyzedAt ? /* @__PURE__ */ jsxRuntimeExports.jsxs("p", { className: "text-[11px] text-muted-foreground", children: [
      "Last analysed ",
      new Date(parcel.analyzedAt).toLocaleDateString()
    ] }) : /* @__PURE__ */ jsxRuntimeExports.jsx("p", { className: "text-[11px] text-muted-foreground", children: "Not yet analysed from imagery; values are the seeded baseline." })
  ] });
}
const SplitComponent = GreenLandsView;
export {
  SplitComponent as component
};
