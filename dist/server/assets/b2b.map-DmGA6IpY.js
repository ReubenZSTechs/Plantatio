import { W as jsxRuntimeExports } from "./server-BG8Cz_a2.js";
import { u as useQuery, S as SiteMap } from "./SiteMap-ToYsFHEg.js";
import { C as Card, B as Badge } from "./badge-Ci2zfins.js";
import { a as api } from "./api-BNzXBfwP.js";
import { L as LoaderCircle } from "./loader-circle-Ba4x-1QD.js";
import { T as Thermometer } from "./thermometer-BSF65oTr.js";
import { D as Droplets } from "./droplets-wMK8aoEF.js";
import { c as createLucideIcon } from "./utils-B3hKptjK.js";
import "node:async_hooks";
import "node:stream/web";
import "node:stream";
import "./router-DaN2asXe.js";
const __iconNode$1 = [
  [
    "path",
    {
      d: "M22 12h-2.48a2 2 0 0 0-1.93 1.46l-2.35 8.36a.25.25 0 0 1-.48 0L9.24 2.18a.25.25 0 0 0-.48 0l-2.35 8.36A2 2 0 0 1 4.49 12H2",
      key: "169zse"
    }
  ]
];
const Activity = createLucideIcon("activity", __iconNode$1);
const __iconNode = [
  ["path", { d: "M12.8 19.6A2 2 0 1 0 14 16H2", key: "148xed" }],
  ["path", { d: "M17.5 8a2.5 2.5 0 1 1 2 4H2", key: "1u4tom" }],
  ["path", { d: "M9.8 4.4A2 2 0 1 1 11 8H2", key: "75valh" }]
];
const Wind = createLucideIcon("wind", __iconNode);
const SEVERITY_STYLES = {
  critical: "bg-destructive/15 text-destructive",
  warn: "bg-warning/15 text-warning-foreground",
  info: "bg-secondary text-secondary-foreground"
};
function MacroDataMap() {
  const nodes = useQuery({ queryKey: ["devices"], queryFn: api.listDevices });
  const parcels = useQuery({
    queryKey: ["land-parcels", 0],
    queryFn: () => api.listLandParcels()
  });
  const weather = useQuery({ queryKey: ["weather-macro"], queryFn: api.getWeatherMacro });
  const logs = useQuery({ queryKey: ["tactical-logs"], queryFn: api.getTacticalLogs });
  const online = (nodes.data ?? []).filter((node) => node.status === "ok").length;
  return /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "space-y-6", children: [
    /* @__PURE__ */ jsxRuntimeExports.jsxs("header", { children: [
      /* @__PURE__ */ jsxRuntimeExports.jsx("h1", { className: "text-2xl font-semibold tracking-tight", children: "Site Map" }),
      /* @__PURE__ */ jsxRuntimeExports.jsx("p", { className: "text-sm text-muted-foreground", children: "Sensor fleet and restoration parcels across the monitored area." })
    ] }),
    /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "grid gap-4 lg:grid-cols-[minmax(0,2fr)_minmax(0,1fr)]", children: [
      /* @__PURE__ */ jsxRuntimeExports.jsx(Card, { className: "overflow-hidden p-0", children: nodes.isLoading ? /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex h-[420px] items-center justify-center text-sm text-muted-foreground", children: [
        /* @__PURE__ */ jsxRuntimeExports.jsx(LoaderCircle, { className: "mr-2 h-4 w-4 animate-spin", "aria-hidden": "true" }),
        "Loading map…"
      ] }) : nodes.isError ? /* @__PURE__ */ jsxRuntimeExports.jsx("div", { className: "flex h-[420px] items-center justify-center px-6 text-center text-sm text-muted-foreground", children: "Could not load the sensor fleet. Check that the API is running." }) : /* @__PURE__ */ jsxRuntimeExports.jsx(SiteMap, { className: "h-[420px]", nodes: nodes.data ?? [], parcels: parcels.data ?? [] }) }),
      /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "space-y-4", children: [
        /* @__PURE__ */ jsxRuntimeExports.jsxs(Card, { className: "p-4", children: [
          /* @__PURE__ */ jsxRuntimeExports.jsx("h2", { className: "text-sm font-semibold", children: "Conditions" }),
          weather.isLoading ? /* @__PURE__ */ jsxRuntimeExports.jsx("p", { className: "mt-3 text-xs text-muted-foreground", children: "Loading…" }) : weather.isError ? /* @__PURE__ */ jsxRuntimeExports.jsx("p", { className: "mt-3 text-xs text-muted-foreground", children: "Unavailable." }) : /* @__PURE__ */ jsxRuntimeExports.jsxs("dl", { className: "mt-3 space-y-2.5 text-sm", children: [
            /* @__PURE__ */ jsxRuntimeExports.jsx(
              Reading,
              {
                icon: /* @__PURE__ */ jsxRuntimeExports.jsx(Thermometer, { className: "h-3.5 w-3.5" }),
                label: weather.data.city,
                value: `${weather.data.tempC}°C`
              }
            ),
            /* @__PURE__ */ jsxRuntimeExports.jsx(
              Reading,
              {
                icon: /* @__PURE__ */ jsxRuntimeExports.jsx(Droplets, { className: "h-3.5 w-3.5" }),
                label: "Humidity",
                value: `${weather.data.humidity}%`
              }
            ),
            /* @__PURE__ */ jsxRuntimeExports.jsx(
              Reading,
              {
                icon: /* @__PURE__ */ jsxRuntimeExports.jsx(Wind, { className: "h-3.5 w-3.5" }),
                label: "Condition",
                value: weather.data.condition
              }
            ),
            /* @__PURE__ */ jsxRuntimeExports.jsx(
              Reading,
              {
                icon: /* @__PURE__ */ jsxRuntimeExports.jsx(Activity, { className: "h-3.5 w-3.5" }),
                label: "Nodes online",
                value: `${online} / ${nodes.data?.length ?? 0}`
              }
            )
          ] })
        ] }),
        /* @__PURE__ */ jsxRuntimeExports.jsxs(Card, { className: "p-4", children: [
          /* @__PURE__ */ jsxRuntimeExports.jsx("h2", { className: "text-sm font-semibold", children: "Recent activity" }),
          (logs.data ?? []).length === 0 ? /* @__PURE__ */ jsxRuntimeExports.jsx("p", { className: "mt-3 text-xs text-muted-foreground", children: "No activity recorded yet." }) : /* @__PURE__ */ jsxRuntimeExports.jsx("ul", { className: "mt-3 space-y-2", children: (logs.data ?? []).map((log) => /* @__PURE__ */ jsxRuntimeExports.jsxs("li", { className: "flex items-start gap-2 text-xs", children: [
            /* @__PURE__ */ jsxRuntimeExports.jsx(
              Badge,
              {
                variant: "secondary",
                className: SEVERITY_STYLES[log.severity] ?? SEVERITY_STYLES.info,
                children: log.time
              }
            ),
            /* @__PURE__ */ jsxRuntimeExports.jsx("span", { className: "min-w-0 flex-1 text-muted-foreground", children: log.action })
          ] }, log.id)) })
        ] })
      ] })
    ] })
  ] });
}
function Reading({ icon, label, value }) {
  return /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex items-center justify-between gap-3", children: [
    /* @__PURE__ */ jsxRuntimeExports.jsxs("dt", { className: "flex min-w-0 items-center gap-1.5 text-muted-foreground", children: [
      /* @__PURE__ */ jsxRuntimeExports.jsx("span", { "aria-hidden": "true", children: icon }),
      /* @__PURE__ */ jsxRuntimeExports.jsx("span", { className: "truncate text-xs", children: label })
    ] }),
    /* @__PURE__ */ jsxRuntimeExports.jsx("dd", { className: "shrink-0 text-sm font-medium", children: value })
  ] });
}
const SplitComponent = MacroDataMap;
export {
  SplitComponent as component
};
