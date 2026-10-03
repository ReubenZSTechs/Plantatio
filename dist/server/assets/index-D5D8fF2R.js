import { W as jsxRuntimeExports } from "./server-BG8Cz_a2.js";
import { L as Link } from "./router-DaN2asXe.js";
import { A as AppHeader } from "./AppHeader-B5tWhkCB.js";
import { F as Flower2 } from "./flower-2-CY4D9gfj.js";
import { c as createLucideIcon } from "./utils-B3hKptjK.js";
import { C as Camera } from "./camera-BEhya5Ry.js";
import "node:async_hooks";
import "node:stream/web";
import "node:stream";
import "./button-BpSWKw9G.js";
import "./index-CFniAsgI.js";
import "./sun-CswmqDAE.js";
import "./sprout-HTLAs6KQ.js";
const __iconNode$3 = [
  ["path", { d: "M5 12h14", key: "1ays0h" }],
  ["path", { d: "m12 5 7 7-7 7", key: "xquz4c" }]
];
const ArrowRight = createLucideIcon("arrow-right", __iconNode$3);
const __iconNode$2 = [
  ["path", { d: "M10 12h4", key: "a56b0p" }],
  ["path", { d: "M10 8h4", key: "1sr2af" }],
  ["path", { d: "M14 21v-3a2 2 0 0 0-4 0v3", key: "1rgiei" }],
  [
    "path",
    {
      d: "M6 10H4a2 2 0 0 0-2 2v7a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2V9a2 2 0 0 0-2-2h-2",
      key: "secmi2"
    }
  ],
  ["path", { d: "M6 21V5a2 2 0 0 1 2-2h8a2 2 0 0 1 2 2v16", key: "16ra0t" }]
];
const Building2 = createLucideIcon("building-2", __iconNode$2);
const __iconNode$1 = [
  ["rect", { x: "16", y: "16", width: "6", height: "6", rx: "1", key: "4q2zg0" }],
  ["rect", { x: "2", y: "16", width: "6", height: "6", rx: "1", key: "8cvhb9" }],
  ["rect", { x: "9", y: "2", width: "6", height: "6", rx: "1", key: "1egb70" }],
  ["path", { d: "M5 16v-3a1 1 0 0 1 1-1h12a1 1 0 0 1 1 1v3", key: "1jsf9p" }],
  ["path", { d: "M12 12V8", key: "2874zd" }]
];
const Network = createLucideIcon("network", __iconNode$1);
const __iconNode = [
  [
    "path",
    {
      d: "m13.5 6.5-3.148-3.148a1.205 1.205 0 0 0-1.704 0L6.352 5.648a1.205 1.205 0 0 0 0 1.704L9.5 10.5",
      key: "dzhfyz"
    }
  ],
  ["path", { d: "M16.5 7.5 19 5", key: "1ltcjm" }],
  [
    "path",
    {
      d: "m17.5 10.5 3.148 3.148a1.205 1.205 0 0 1 0 1.704l-2.296 2.296a1.205 1.205 0 0 1-1.704 0L13.5 14.5",
      key: "nfoymv"
    }
  ],
  ["path", { d: "M9 21a6 6 0 0 0-6-6", key: "1iajcf" }],
  [
    "path",
    {
      d: "M9.352 10.648a1.205 1.205 0 0 0 0 1.704l2.296 2.296a1.205 1.205 0 0 0 1.704 0l4.296-4.296a1.205 1.205 0 0 0 0-1.704l-2.296-2.296a1.205 1.205 0 0 0-1.704 0z",
      key: "nv9zqy"
    }
  ]
];
const Satellite = createLucideIcon("satellite", __iconNode);
const CAPABILITIES = [{
  icon: Network,
  title: "Knowledge graph",
  body: "Answers are retrieved from a graph built from 62 tomato research papers, and every reply shows the facts behind it."
}, {
  icon: Camera,
  title: "Leaf diagnosis",
  body: "A convolutional classifier reads a leaf photograph and reports the likely disease with ranked confidence."
}, {
  icon: Satellite,
  title: "Restoration analysis",
  body: "Satellite imagery is scored for canopy, biomass and carbon, then compared against a baseline capture."
}];
function Index() {
  return /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "min-h-screen bg-background", children: [
    /* @__PURE__ */ jsxRuntimeExports.jsx(AppHeader, {}),
    /* @__PURE__ */ jsxRuntimeExports.jsxs("main", { className: "mx-auto max-w-6xl px-4 py-10 sm:px-6 sm:py-16", children: [
      /* @__PURE__ */ jsxRuntimeExports.jsx("section", { className: "rounded-3xl p-8 text-on-hero sm:p-12 md:p-16", style: {
        background: "var(--gradient-hero)",
        boxShadow: "var(--shadow-elegant)"
      }, children: /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "max-w-2xl", children: [
        /* @__PURE__ */ jsxRuntimeExports.jsx("p", { className: "mb-3 inline-flex rounded-full bg-white/15 px-3 py-1 text-xs backdrop-blur", children: "Knowledge graph · Computer vision · Satellite analysis" }),
        /* @__PURE__ */ jsxRuntimeExports.jsxs("h1", { className: "text-3xl font-semibold leading-tight sm:text-4xl md:text-5xl", children: [
          "Grow smarter.",
          /* @__PURE__ */ jsxRuntimeExports.jsx("br", {}),
          "Restore at scale."
        ] }),
        /* @__PURE__ */ jsxRuntimeExports.jsx("p", { className: "mt-4 max-w-xl text-base opacity-90", children: "One AI system spanning a windowsill tomato and a thousand-hectare restoration site — grounded in published agronomy, not guesswork." })
      ] }) }),
      /* @__PURE__ */ jsxRuntimeExports.jsxs("section", { className: "mt-10 grid gap-6 md:grid-cols-2", children: [
        /* @__PURE__ */ jsxRuntimeExports.jsx(SegmentCard, { to: "/b2c", icon: Flower2, title: "For growers", body: "Track your plants, scan a leaf for disease, and ask an assistant that cites the research behind each answer.", cta: "Open the grower app" }),
        /* @__PURE__ */ jsxRuntimeExports.jsx(SegmentCard, { to: "/b2b", icon: Building2, title: "For enterprise", body: "Discover restoration candidates on a live map, audit satellite imagery over time, and orchestrate the sensor fleet.", cta: "Open the console" })
      ] }),
      /* @__PURE__ */ jsxRuntimeExports.jsxs("section", { className: "mt-12", children: [
        /* @__PURE__ */ jsxRuntimeExports.jsx("h2", { className: "text-lg font-semibold tracking-tight", children: "What is under the hood" }),
        /* @__PURE__ */ jsxRuntimeExports.jsx("div", { className: "mt-4 grid gap-4 sm:grid-cols-3", children: CAPABILITIES.map(({
          icon: Icon,
          title,
          body
        }) => /* @__PURE__ */ jsxRuntimeExports.jsxs("article", { className: "rounded-2xl border bg-card p-5", children: [
          /* @__PURE__ */ jsxRuntimeExports.jsx(Icon, { className: "h-5 w-5 text-primary", "aria-hidden": "true" }),
          /* @__PURE__ */ jsxRuntimeExports.jsx("h3", { className: "mt-3 text-sm font-semibold", children: title }),
          /* @__PURE__ */ jsxRuntimeExports.jsx("p", { className: "mt-1.5 text-sm leading-relaxed text-muted-foreground", children: body })
        ] }, title)) })
      ] })
    ] }),
    /* @__PURE__ */ jsxRuntimeExports.jsx("footer", { className: "border-t", children: /* @__PURE__ */ jsxRuntimeExports.jsx("div", { className: "mx-auto max-w-6xl px-4 py-6 text-xs text-muted-foreground sm:px-6", children: "Plantatio — a portfolio project demonstrating GraphRAG, agentic orchestration and applied computer vision." }) })
  ] });
}
function SegmentCard({
  to,
  icon: Icon,
  title,
  body,
  cta
}) {
  return /* @__PURE__ */ jsxRuntimeExports.jsxs(Link, { to, className: "group rounded-2xl border bg-card p-7 transition-all hover:-translate-y-0.5 hover:shadow-lg", children: [
    /* @__PURE__ */ jsxRuntimeExports.jsx(Icon, { className: "h-7 w-7 text-primary", "aria-hidden": "true" }),
    /* @__PURE__ */ jsxRuntimeExports.jsx("h2", { className: "mt-4 text-xl font-semibold", children: title }),
    /* @__PURE__ */ jsxRuntimeExports.jsx("p", { className: "mt-2 text-sm leading-relaxed text-muted-foreground", children: body }),
    /* @__PURE__ */ jsxRuntimeExports.jsxs("span", { className: "mt-4 inline-flex items-center gap-1 text-sm font-medium text-primary", children: [
      cta,
      /* @__PURE__ */ jsxRuntimeExports.jsx(ArrowRight, { className: "h-4 w-4 transition-transform group-hover:translate-x-1", "aria-hidden": "true" })
    ] })
  ] });
}
export {
  Index as component
};
