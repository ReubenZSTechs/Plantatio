import { r as reactExports, W as jsxRuntimeExports } from "./server-BG8Cz_a2.js";
import { L as Link } from "./router-DaN2asXe.js";
import { A as AppHeader } from "./AppHeader-B5tWhkCB.js";
import { C as Card } from "./badge-Ci2zfins.js";
import { C as ChatPanel } from "./ChatPanel-CLbb7LyA.js";
import { A as API_BASE_URL } from "./api-BNzXBfwP.js";
import { S as Sun } from "./sun-CswmqDAE.js";
import { T as TriangleAlert } from "./triangle-alert-jwyqnsFt.js";
import { c as createLucideIcon } from "./utils-B3hKptjK.js";
import { F as Flower2 } from "./flower-2-CY4D9gfj.js";
import "node:async_hooks";
import "node:stream/web";
import "node:stream";
import "./button-BpSWKw9G.js";
import "./index-CFniAsgI.js";
import "./sprout-HTLAs6KQ.js";
import "./input-Dc7a9lUS.js";
import "./bot-zAHS25mR.js";
import "./loader-circle-Ba4x-1QD.js";
import "./camera-BEhya5Ry.js";
const __iconNode$3 = [["path", { d: "m9 18 6-6-6-6", key: "mthhwq" }]];
const ChevronRight = createLucideIcon("chevron-right", __iconNode$3);
const __iconNode$2 = [
  ["path", { d: "M4 14.899A7 7 0 1 1 15.71 8h1.79a4.5 4.5 0 0 1 2.5 8.242", key: "1pljnt" }],
  ["path", { d: "M16 14v6", key: "1j4efv" }],
  ["path", { d: "M8 14v6", key: "17c4r9" }],
  ["path", { d: "M12 16v6", key: "c8a4gj" }]
];
const CloudRain = createLucideIcon("cloud-rain", __iconNode$2);
const __iconNode$1 = [
  ["path", { d: "M17.5 19H9a7 7 0 1 1 6.71-9h1.79a4.5 4.5 0 1 1 0 9Z", key: "p7xjir" }]
];
const Cloud = createLucideIcon("cloud", __iconNode$1);
const __iconNode = [
  [
    "path",
    {
      d: "M11.017 2.814a1 1 0 0 1 1.966 0l1.051 5.558a2 2 0 0 0 1.594 1.594l5.558 1.051a1 1 0 0 1 0 1.966l-5.558 1.051a2 2 0 0 0-1.594 1.594l-1.051 5.558a1 1 0 0 1-1.966 0l-1.051-5.558a2 2 0 0 0-1.594-1.594l-5.558-1.051a1 1 0 0 1 0-1.966l5.558-1.051a2 2 0 0 0 1.594-1.594z",
      key: "1s2grr"
    }
  ],
  ["path", { d: "M20 2v4", key: "1rf3ol" }],
  ["path", { d: "M22 4h-4", key: "gwowj6" }],
  ["circle", { cx: "4", cy: "20", r: "2", key: "6kqj1y" }]
];
const Sparkles = createLucideIcon("sparkles", __iconNode);
const iconFor = (k) => k === "rain" ? /* @__PURE__ */ jsxRuntimeExports.jsx(CloudRain, { className: "h-4 w-4" }) : k === "cloud" ? /* @__PURE__ */ jsxRuntimeExports.jsx(Cloud, { className: "h-4 w-4" }) : /* @__PURE__ */ jsxRuntimeExports.jsx(Sun, { className: "h-4 w-4" });
function WeatherSyncWidget() {
  const [weather, setWeather] = reactExports.useState(null);
  const [alert, setAlert] = reactExports.useState(null);
  const [loading, setLoading] = reactExports.useState(true);
  reactExports.useEffect(() => {
    const fetchData = async () => {
      try {
        const [weatherRes, alertRes] = await Promise.all([
          fetch(`${API_BASE_URL}/v1/weather/macro`),
          fetch(`${API_BASE_URL}/v1/weather/alert`)
        ]);
        if (!weatherRes.ok || !alertRes.ok) {
          throw new Error("Could not load conditions from the server");
        }
        const weatherData = await weatherRes.json();
        const alertData = await alertRes.json();
        setWeather(weatherData);
        setAlert(alertData);
      } catch (error) {
        console.error("Error fetching data:", error);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);
  if (loading || !weather) {
    return /* @__PURE__ */ jsxRuntimeExports.jsx(Card, { className: "flex h-[280px] items-center justify-center", children: /* @__PURE__ */ jsxRuntimeExports.jsx("div", { className: "text-sm text-muted-foreground", children: "Memuat data..." }) });
  }
  return /* @__PURE__ */ jsxRuntimeExports.jsxs(Card, { className: "overflow-hidden", children: [
    /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "p-5 text-on-hero", style: { background: "var(--gradient-hero)" }, children: [
      /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex items-center justify-between", children: [
        /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { children: [
          /* @__PURE__ */ jsxRuntimeExports.jsx("div", { className: "text-xs uppercase tracking-wide opacity-80", children: weather.city }),
          /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "text-4xl font-semibold", children: [
            weather.tempC,
            "°"
          ] }),
          /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "text-sm opacity-90", children: [
            weather.condition,
            " · ",
            weather.humidity,
            "% humidity"
          ] })
        ] }),
        /* @__PURE__ */ jsxRuntimeExports.jsx(Sun, { className: "h-12 w-12 opacity-90" })
      ] }),
      /* @__PURE__ */ jsxRuntimeExports.jsx("div", { className: "mt-4 grid grid-cols-5 gap-2", children: weather.forecast.map((d) => /* @__PURE__ */ jsxRuntimeExports.jsxs(
        "div",
        {
          className: "rounded-lg bg-white/15 p-2 text-center text-xs backdrop-blur-sm",
          children: [
            /* @__PURE__ */ jsxRuntimeExports.jsx("div", { className: "opacity-80", children: d.day }),
            /* @__PURE__ */ jsxRuntimeExports.jsx("div", { className: "my-1 flex justify-center", children: iconFor(d.icon) }),
            /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "font-medium", children: [
              d.tempC,
              "°"
            ] })
          ]
        },
        d.day
      )) })
    ] }),
    alert && /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex gap-3 border-l-4 border-warning bg-warning/10 p-4", children: [
      /* @__PURE__ */ jsxRuntimeExports.jsx(TriangleAlert, { className: "h-5 w-5 shrink-0 text-warning" }),
      /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "text-sm", children: [
        /* @__PURE__ */ jsxRuntimeExports.jsx("div", { className: "font-semibold", children: alert.title }),
        /* @__PURE__ */ jsxRuntimeExports.jsx("div", { className: "text-xs text-muted-foreground", children: alert.body })
      ] })
    ] })
  ] });
}
const SUGGESTIONS = [
  "Why are my tomato leaves yellowing?",
  "How often should I water this week?",
  "What causes brown spots on leaves?"
];
function B2CMainLayout() {
  return /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "min-h-screen bg-background", children: [
    /* @__PURE__ */ jsxRuntimeExports.jsx(AppHeader, { crumbs: [{ label: "For growers" }] }),
    /* @__PURE__ */ jsxRuntimeExports.jsx("main", { className: "mx-auto max-w-5xl px-4 py-6 sm:px-6", children: /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "grid gap-5 lg:grid-cols-[minmax(0,1fr)_minmax(0,1.1fr)]", children: [
      /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "space-y-5", children: [
        /* @__PURE__ */ jsxRuntimeExports.jsx(WeatherSyncWidget, {}),
        /* @__PURE__ */ jsxRuntimeExports.jsx(Link, { to: "/garden", className: "block transition-transform active:scale-[0.99]", children: /* @__PURE__ */ jsxRuntimeExports.jsxs(Card, { className: "flex items-center justify-between gap-4 p-4 transition-colors hover:bg-secondary/40", children: [
          /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex min-w-0 items-center gap-4", children: [
            /* @__PURE__ */ jsxRuntimeExports.jsx("span", { className: "flex h-11 w-11 shrink-0 items-center justify-center rounded-full bg-primary/10", children: /* @__PURE__ */ jsxRuntimeExports.jsx(Flower2, { className: "h-5 w-5 text-primary", "aria-hidden": "true" }) }),
            /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "min-w-0", children: [
              /* @__PURE__ */ jsxRuntimeExports.jsx("h2", { className: "text-sm font-semibold", children: "My garden" }),
              /* @__PURE__ */ jsxRuntimeExports.jsx("p", { className: "truncate text-xs text-muted-foreground", children: "Track your plants, log care, and scan leaves for disease" })
            ] })
          ] }),
          /* @__PURE__ */ jsxRuntimeExports.jsx(
            ChevronRight,
            {
              className: "h-4 w-4 shrink-0 text-muted-foreground",
              "aria-hidden": "true"
            }
          )
        ] }) }),
        /* @__PURE__ */ jsxRuntimeExports.jsxs(Card, { className: "p-4", children: [
          /* @__PURE__ */ jsxRuntimeExports.jsxs("h2", { className: "flex items-center gap-1.5 text-sm font-semibold", children: [
            /* @__PURE__ */ jsxRuntimeExports.jsx(Sparkles, { className: "h-4 w-4 text-primary", "aria-hidden": "true" }),
            "How the assistant answers"
          ] }),
          /* @__PURE__ */ jsxRuntimeExports.jsx("p", { className: "mt-2 text-xs leading-relaxed text-muted-foreground", children: "Questions are broken into parts, matched against a knowledge graph built from tomato research, and answered from what it finds. Expand the sources under any reply to see the facts behind it." })
        ] })
      ] }),
      /* @__PURE__ */ jsxRuntimeExports.jsx(
        ChatPanel,
        {
          scope: "b2c",
          title: "Growing assistant",
          subtitle: "Grounded in agronomy research",
          greeting: "Hello. Ask me anything about growing — I'll show you the evidence behind each answer.",
          suggestions: SUGGESTIONS,
          className: "h-[min(640px,calc(100vh-7rem))] lg:sticky lg:top-20"
        }
      )
    ] }) })
  ] });
}
const SplitComponent = B2CMainLayout;
export {
  SplitComponent as component
};
