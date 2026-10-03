import { r as reactExports, W as jsxRuntimeExports } from "./server-BG8Cz_a2.js";
import { t as toast } from "./router-DaN2asXe.js";
import { C as Card, B as Badge } from "./badge-Ci2zfins.js";
import { B as Button } from "./button-BpSWKw9G.js";
import { L as Label } from "./label-C789j1H7.js";
import { P as Progress } from "./progress-CCR5OBxf.js";
import { a as api, b as ApiError } from "./api-BNzXBfwP.js";
import { c as createLucideIcon, a as cn } from "./utils-B3hKptjK.js";
import { C as Camera } from "./camera-BEhya5Ry.js";
import { L as LoaderCircle } from "./loader-circle-Ba4x-1QD.js";
import { L as Leaf } from "./leaf-Dgz3cyvi.js";
import "node:async_hooks";
import "node:stream/web";
import "node:stream";
import "./index-CFniAsgI.js";
const __iconNode$5 = [
  ["path", { d: "m7 7 10 10", key: "1fmybs" }],
  ["path", { d: "M17 7v10H7", key: "6fjiku" }]
];
const ArrowDownRight = createLucideIcon("arrow-down-right", __iconNode$5);
const __iconNode$4 = [
  ["path", { d: "M7 7h10v10", key: "1tivn9" }],
  ["path", { d: "M7 17 17 7", key: "1vkiza" }]
];
const ArrowUpRight = createLucideIcon("arrow-up-right", __iconNode$4);
const __iconNode$3 = [
  ["path", { d: "M3 7V5a2 2 0 0 1 2-2h2", key: "aa7l1z" }],
  ["path", { d: "M17 3h2a2 2 0 0 1 2 2v2", key: "4qcy5o" }],
  ["path", { d: "M21 17v2a2 2 0 0 1-2 2h-2", key: "6vwrx8" }],
  ["path", { d: "M7 21H5a2 2 0 0 1-2-2v-2", key: "ioqczr" }],
  ["circle", { cx: "12", cy: "12", r: "3", key: "1v7zrd" }],
  ["path", { d: "m16 16-1.9-1.9", key: "1dq9hf" }]
];
const ScanSearch = createLucideIcon("scan-search", __iconNode$3);
const __iconNode$2 = [
  [
    "path",
    {
      d: "M20 13c0 5-3.5 7.5-7.66 8.95a1 1 0 0 1-.67-.01C7.5 20.5 4 18 4 13V6a1 1 0 0 1 1-1c2 0 4.5-1.2 6.24-2.72a1.17 1.17 0 0 1 1.52 0C14.51 3.81 17 5 19 5a1 1 0 0 1 1 1z",
      key: "oel41y"
    }
  ],
  ["path", { d: "m9 12 2 2 4-4", key: "dzmm74" }]
];
const ShieldCheck = createLucideIcon("shield-check", __iconNode$2);
const __iconNode$1 = [
  [
    "path",
    {
      d: "m17 14 3 3.3a1 1 0 0 1-.7 1.7H4.7a1 1 0 0 1-.7-1.7L7 14h-.3a1 1 0 0 1-.7-1.7L9 9h-.2A1 1 0 0 1 8 7.3L12 3l4 4.3a1 1 0 0 1-.8 1.7H15l3 3.3a1 1 0 0 1-.7 1.7H17Z",
      key: "cpyugq"
    }
  ],
  ["path", { d: "M12 22v-3", key: "kmzjlo" }]
];
const TreePine = createLucideIcon("tree-pine", __iconNode$1);
const __iconNode = [
  ["path", { d: "M12 3v12", key: "1x0j5s" }],
  ["path", { d: "m17 8-5-5-5 5", key: "7q97r8" }],
  ["path", { d: "M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4", key: "ih7n3h" }]
];
const Upload = createLucideIcon("upload", __iconNode);
const DEMO_IMAGES = {
  baseline: { src: "/demo/restoration-1986.jpg", name: "restoration-1986.jpg" },
  current: { src: "/demo/restoration-2019.jpg", name: "restoration-2019.jpg" }
};
async function demoFile(src, name) {
  const response = await fetch(src);
  const blob = await response.blob();
  return new File([blob], name, { type: blob.type || "image/jpeg" });
}
function formatRatio(value) {
  return value === null ? "—" : `${(value * 100).toFixed(0)}%`;
}
function ESGAnalyticsDashboard() {
  const [baseline, setBaseline] = reactExports.useState(null);
  const [current, setCurrent] = reactExports.useState(null);
  const [baselinePreview, setBaselinePreview] = reactExports.useState("");
  const [currentPreview, setCurrentPreview] = reactExports.useState("");
  const [isAnalyzing, setIsAnalyzing] = reactExports.useState(false);
  const [analysis, setAnalysis] = reactExports.useState(null);
  const [error, setError] = reactExports.useState(null);
  const pick = (file, slot) => {
    const reader = new FileReader();
    reader.onloadend = () => {
      if (slot === "baseline") {
        setBaseline(file);
        setBaselinePreview(reader.result);
      } else {
        setCurrent(file);
        setCurrentPreview(reader.result);
      }
    };
    reader.readAsDataURL(file);
  };
  const loadDemo = async () => {
    try {
      const [before, after] = await Promise.all([
        demoFile(DEMO_IMAGES.baseline.src, DEMO_IMAGES.baseline.name),
        demoFile(DEMO_IMAGES.current.src, DEMO_IMAGES.current.name)
      ]);
      pick(before, "baseline");
      pick(after, "current");
      toast.success("Loaded the 1986 / 2019 demo pair");
    } catch {
      toast.error("Could not load the demo images");
    }
  };
  const analyze = async () => {
    if (!baseline || !current) {
      toast.error("Upload both the baseline and the current image");
      return;
    }
    setIsAnalyzing(true);
    setError(null);
    try {
      setAnalysis(await api.analyzeSatellite(baseline, current));
      toast.success("Comparison complete");
    } catch (caught) {
      const message = caught instanceof ApiError ? caught.message : "Satellite analysis failed";
      setError(message);
      toast.error(message);
    } finally {
      setIsAnalyzing(false);
    }
  };
  const labels = analysis?.labels;
  const delta = labels?.restorationDelta ?? null;
  return /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "space-y-6", children: [
    /* @__PURE__ */ jsxRuntimeExports.jsxs("header", { children: [
      /* @__PURE__ */ jsxRuntimeExports.jsx("h1", { className: "text-2xl font-semibold tracking-tight", children: "ESG Analytics" }),
      /* @__PURE__ */ jsxRuntimeExports.jsx("p", { className: "text-sm text-muted-foreground", children: "Compare two satellite images of a site and quantify the change in vegetation, biomass and carbon." })
    ] }),
    /* @__PURE__ */ jsxRuntimeExports.jsxs(Card, { className: "space-y-4 p-5", children: [
      /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "grid gap-4 sm:grid-cols-2", children: [
        /* @__PURE__ */ jsxRuntimeExports.jsx(
          ImageSlot,
          {
            id: "baseline-image",
            label: "Baseline image",
            hint: "Earlier state of the site",
            icon: /* @__PURE__ */ jsxRuntimeExports.jsx(Camera, { className: "h-5 w-5 opacity-60", "aria-hidden": "true" }),
            preview: baselinePreview,
            onPick: (file) => pick(file, "baseline")
          }
        ),
        /* @__PURE__ */ jsxRuntimeExports.jsx(
          ImageSlot,
          {
            id: "current-image",
            label: "Current image",
            hint: "Most recent capture",
            icon: /* @__PURE__ */ jsxRuntimeExports.jsx(Upload, { className: "h-5 w-5 opacity-60", "aria-hidden": "true" }),
            preview: currentPreview,
            onPick: (file) => pick(file, "current")
          }
        )
      ] }),
      /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex flex-col gap-2 sm:flex-row", children: [
        /* @__PURE__ */ jsxRuntimeExports.jsx(
          Button,
          {
            onClick: () => void analyze(),
            disabled: isAnalyzing || !baseline || !current,
            className: "flex-1",
            children: isAnalyzing ? /* @__PURE__ */ jsxRuntimeExports.jsxs(jsxRuntimeExports.Fragment, { children: [
              /* @__PURE__ */ jsxRuntimeExports.jsx(LoaderCircle, { className: "mr-2 h-4 w-4 animate-spin", "aria-hidden": "true" }),
              "Analysing imagery…"
            ] }) : "Run satellite audit"
          }
        ),
        /* @__PURE__ */ jsxRuntimeExports.jsx(Button, { variant: "outline", onClick: () => void loadDemo(), disabled: isAnalyzing, children: "Load demo pair" })
      ] }),
      /* @__PURE__ */ jsxRuntimeExports.jsx("p", { className: "text-xs text-muted-foreground", children: "The demo pair is Landsat imagery of the same terrain in 1986 and 2019, via Google Earth Timelapse. The frames are not co-registered, so the comparison is indicative rather than a pixel-level difference." })
    ] }),
    error && /* @__PURE__ */ jsxRuntimeExports.jsx(Card, { role: "alert", className: "border-destructive/40 bg-destructive/5 p-4", children: /* @__PURE__ */ jsxRuntimeExports.jsx("p", { className: "text-sm text-destructive", children: error }) }),
    labels && /* @__PURE__ */ jsxRuntimeExports.jsxs(Card, { className: "overflow-hidden p-0", children: [
      /* @__PURE__ */ jsxRuntimeExports.jsxs("header", { className: "flex flex-wrap items-center justify-between gap-2 border-b bg-muted/40 px-5 py-4", children: [
        /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex min-w-0 items-center gap-3", children: [
          /* @__PURE__ */ jsxRuntimeExports.jsx(ScanSearch, { className: "h-5 w-5 shrink-0 text-primary", "aria-hidden": "true" }),
          /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "min-w-0", children: [
            /* @__PURE__ */ jsxRuntimeExports.jsx("h2", { className: "text-sm font-semibold", children: "Analysis result" }),
            /* @__PURE__ */ jsxRuntimeExports.jsx("p", { className: "truncate font-mono text-[11px] text-muted-foreground", children: analysis.imagePath })
          ] })
        ] }),
        labels.confidence !== null && /* @__PURE__ */ jsxRuntimeExports.jsxs(Badge, { variant: "secondary", className: "gap-1", children: [
          /* @__PURE__ */ jsxRuntimeExports.jsx(ShieldCheck, { className: "h-3 w-3", "aria-hidden": "true" }),
          formatRatio(labels.confidence),
          " confidence"
        ] })
      ] }),
      /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "grid gap-4 border-b p-4 sm:grid-cols-2", children: [
        /* @__PURE__ */ jsxRuntimeExports.jsx(Fact, { label: "Vegetation density", value: labels.vegetationDensity ?? "—" }),
        /* @__PURE__ */ jsxRuntimeExports.jsx(Fact, { label: "Restoration quality", value: labels.restorationQuality ?? "—" })
      ] }),
      /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "grid divide-y sm:grid-cols-3 sm:divide-x sm:divide-y-0", children: [
        /* @__PURE__ */ jsxRuntimeExports.jsx(
          Metric,
          {
            icon: /* @__PURE__ */ jsxRuntimeExports.jsx(Leaf, { className: "h-3.5 w-3.5", "aria-hidden": "true" }),
            label: "Canopy cover",
            value: labels.canopyCover,
            change: delta?.canopyCoverChange ?? null
          }
        ),
        /* @__PURE__ */ jsxRuntimeExports.jsx(
          Metric,
          {
            icon: /* @__PURE__ */ jsxRuntimeExports.jsx(TreePine, { className: "h-3.5 w-3.5", "aria-hidden": "true" }),
            label: "Est. biomass",
            value: labels.estBiomass,
            change: delta?.biomassChange ?? null
          }
        ),
        /* @__PURE__ */ jsxRuntimeExports.jsx(
          Metric,
          {
            icon: /* @__PURE__ */ jsxRuntimeExports.jsx(ShieldCheck, { className: "h-3.5 w-3.5", "aria-hidden": "true" }),
            label: "Carbon equivalent",
            value: labels.carbonEq,
            change: delta?.carbonChange ?? null
          }
        )
      ] })
    ] })
  ] });
}
function ImageSlot({
  id,
  label,
  hint,
  icon,
  preview,
  onPick
}) {
  return /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "space-y-1.5", children: [
    /* @__PURE__ */ jsxRuntimeExports.jsx(Label, { htmlFor: id, className: "text-xs font-semibold", children: label }),
    /* @__PURE__ */ jsxRuntimeExports.jsx(
      "input",
      {
        id,
        type: "file",
        accept: "image/*",
        className: "sr-only",
        onChange: (event) => {
          const file = event.target.files?.[0];
          if (file) onPick(file);
        }
      }
    ),
    /* @__PURE__ */ jsxRuntimeExports.jsx(
      Label,
      {
        htmlFor: id,
        className: "relative flex aspect-video cursor-pointer flex-col items-center justify-center overflow-hidden rounded-xl border-2 border-dashed bg-muted/40 transition-colors hover:border-primary/40",
        children: preview ? /* @__PURE__ */ jsxRuntimeExports.jsx("img", { src: preview, alt: label, className: "h-full w-full object-cover" }) : /* @__PURE__ */ jsxRuntimeExports.jsxs("span", { className: "space-y-1 p-4 text-center text-xs text-muted-foreground", children: [
          icon,
          /* @__PURE__ */ jsxRuntimeExports.jsx("span", { className: "block", children: hint })
        ] })
      }
    )
  ] });
}
function Fact({ label, value }) {
  return /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "rounded-xl border bg-background p-3", children: [
    /* @__PURE__ */ jsxRuntimeExports.jsx("p", { className: "text-[11px] font-semibold uppercase tracking-wide text-muted-foreground", children: label }),
    /* @__PURE__ */ jsxRuntimeExports.jsx("p", { className: "mt-0.5 text-lg font-semibold capitalize text-primary", children: value })
  ] });
}
function Metric({
  icon,
  label,
  value,
  change
}) {
  const improved = change !== null && change > 0;
  return /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "space-y-1 p-4", children: [
    /* @__PURE__ */ jsxRuntimeExports.jsxs("p", { className: "flex items-center gap-1 text-[11px] font-semibold uppercase tracking-wide text-muted-foreground", children: [
      icon,
      label
    ] }),
    /* @__PURE__ */ jsxRuntimeExports.jsx("p", { className: "text-xl font-semibold tabular-nums", children: formatRatio(value) }),
    /* @__PURE__ */ jsxRuntimeExports.jsx(Progress, { value: (value ?? 0) * 100, className: "h-1" }),
    change !== null && /* @__PURE__ */ jsxRuntimeExports.jsxs(
      "p",
      {
        className: cn(
          "flex items-center gap-1 text-xs font-medium",
          improved ? "text-success" : "text-destructive"
        ),
        children: [
          improved ? /* @__PURE__ */ jsxRuntimeExports.jsx(ArrowUpRight, { className: "h-3 w-3", "aria-hidden": "true" }) : /* @__PURE__ */ jsxRuntimeExports.jsx(ArrowDownRight, { className: "h-3 w-3", "aria-hidden": "true" }),
          change > 0 ? "+" : "",
          (change * 100).toFixed(1),
          " pts vs baseline"
        ]
      }
    )
  ] });
}
const SplitComponent = ESGAnalyticsDashboard;
export {
  SplitComponent as component
};
