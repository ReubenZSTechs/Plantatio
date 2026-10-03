import { W as jsxRuntimeExports } from "./server-BG8Cz_a2.js";
import { C as Card, B as Badge } from "./badge-Ci2zfins.js";
import { B as Button } from "./button-BpSWKw9G.js";
import { P as Progress } from "./progress-CCR5OBxf.js";
import { B as BrainCircuit } from "./brain-circuit-6SBBv1sb.js";
import { c as createLucideIcon } from "./utils-B3hKptjK.js";
import { T as Thermometer } from "./thermometer-BSF65oTr.js";
import "node:async_hooks";
import "node:stream/web";
import "node:stream";
import "./index-CFniAsgI.js";
import "./router-DaN2asXe.js";
const __iconNode$6 = [
  ["circle", { cx: "12", cy: "12", r: "10", key: "1mglay" }],
  ["path", { d: "m9 12 2 2 4-4", key: "dzmm74" }]
];
const CircleCheck = createLucideIcon("circle-check", __iconNode$6);
const __iconNode$5 = [
  ["path", { d: "M12 2v2", key: "tus03m" }],
  ["path", { d: "m4.93 4.93 1.41 1.41", key: "149t6j" }],
  ["path", { d: "M20 12h2", key: "1q8mjw" }],
  ["path", { d: "m19.07 4.93-1.41 1.41", key: "1shlcs" }],
  ["path", { d: "M15.947 12.65a4 4 0 0 0-5.925-4.128", key: "dpwdj0" }],
  ["path", { d: "M13 22H7a5 5 0 1 1 4.9-6H13a3 3 0 0 1 0 6Z", key: "s09mg5" }]
];
const CloudSun = createLucideIcon("cloud-sun", __iconNode$5);
const __iconNode$4 = [
  [
    "path",
    {
      d: "M5 5a2 2 0 0 1 3.008-1.728l11.997 6.998a2 2 0 0 1 .003 3.458l-12 7A2 2 0 0 1 5 19z",
      key: "10ikf1"
    }
  ]
];
const Play = createLucideIcon("play", __iconNode$4);
const __iconNode$3 = [
  ["path", { d: "M16.247 7.761a6 6 0 0 1 0 8.478", key: "1fwjs5" }],
  ["path", { d: "M19.075 4.933a10 10 0 0 1 0 14.134", key: "ehdyv1" }],
  ["path", { d: "M4.925 19.067a10 10 0 0 1 0-14.134", key: "1q22gi" }],
  ["path", { d: "M7.753 16.239a6 6 0 0 1 0-8.478", key: "r2q7qm" }],
  ["circle", { cx: "12", cy: "12", r: "2", key: "1c9p78" }]
];
const Radio = createLucideIcon("radio", __iconNode$3);
const __iconNode$2 = [
  ["path", { d: "M3 12a9 9 0 0 1 9-9 9.75 9.75 0 0 1 6.74 2.74L21 8", key: "v9h5vc" }],
  ["path", { d: "M21 3v5h-5", key: "1q7to0" }],
  ["path", { d: "M21 12a9 9 0 0 1-9 9 9.75 9.75 0 0 1-6.74-2.74L3 16", key: "3uifl3" }],
  ["path", { d: "M8 16H3v5", key: "1cv678" }]
];
const RefreshCw = createLucideIcon("refresh-cw", __iconNode$2);
const __iconNode$1 = [
  ["path", { d: "M16 7h6v6", key: "box55l" }],
  ["path", { d: "m22 7-8.5 8.5-5-5L2 17", key: "1t1m79" }]
];
const TrendingUp = createLucideIcon("trending-up", __iconNode$1);
const __iconNode = [
  [
    "path",
    {
      d: "M4 14a1 1 0 0 1-.78-1.63l9.9-10.2a.5.5 0 0 1 .86.46l-1.92 6.02A1 1 0 0 0 13 10h7a1 1 0 0 1 .78 1.63l-9.9 10.2a.5.5 0 0 1-.86-.46l1.92-6.02A1 1 0 0 0 11 14z",
      key: "1xq2db"
    }
  ]
];
const Zap = createLucideIcon("zap", __iconNode);
function MLPredictionManager() {
  const models = [
    {
      id: "M-LR-01",
      name: "Water Demand Regression",
      algorithm: "Linear Regression",
      status: "Active",
      accuracy: 85.5,
      dataSource: "Moisture Sensor + Weather API",
      insight: "Memprediksi volume air (liter) yang dibutuhkan besok."
    },
    {
      id: "M-RF-02",
      name: "Pathogen Classifier",
      algorithm: "Random Forest",
      status: "Active",
      accuracy: 92.1,
      dataSource: "Humidity + Temp Sensors",
      insight: "Klasifikasi risiko penyakit: Low, Medium, High."
    },
    {
      id: "M-TS-03",
      name: "Growth Time-Series",
      algorithm: "Simple Moving Average",
      status: "Training",
      accuracy: 76.4,
      dataSource: "Camera/Image Processing API",
      insight: "Estimates plant height from weekly growth trends."
    }
  ];
  const externalData = [
    {
      label: "Weather API",
      value: "28°C",
      sub: "Cloudy / 65% Hum",
      icon: /* @__PURE__ */ jsxRuntimeExports.jsx(CloudSun, { className: "text-sky-500" })
    },
    {
      label: "MQTT Signal",
      value: "-65 dBm",
      sub: "Node A-04 (Strong)",
      icon: /* @__PURE__ */ jsxRuntimeExports.jsx(Radio, { className: "text-emerald-500" })
    },
    {
      label: "Soil Probe",
      value: "450 mV",
      sub: "Nutrient Voltage",
      icon: /* @__PURE__ */ jsxRuntimeExports.jsx(Thermometer, { className: "text-amber-500" })
    }
  ];
  return /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "space-y-6 text-left", children: [
    /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { children: [
      /* @__PURE__ */ jsxRuntimeExports.jsx("h2", { className: "text-2xl font-bold tracking-tight", children: "ML Prediction Manager" }),
      /* @__PURE__ */ jsxRuntimeExports.jsx("p", { className: "text-sm text-muted-foreground", children: "Analisis data sensor dan prediksi model secara real-time." })
    ] }),
    /* @__PURE__ */ jsxRuntimeExports.jsx("div", { className: "grid gap-4 md:grid-cols-3", children: externalData.map((data, idx) => /* @__PURE__ */ jsxRuntimeExports.jsxs(Card, { className: "p-4 flex items-center gap-4 bg-muted/30 border-none", children: [
      /* @__PURE__ */ jsxRuntimeExports.jsx("div", { className: "p-3 bg-background rounded-xl shadow-sm", children: data.icon }),
      /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { children: [
        /* @__PURE__ */ jsxRuntimeExports.jsx("p", { className: "text-[10px] uppercase font-bold text-muted-foreground tracking-wider", children: data.label }),
        /* @__PURE__ */ jsxRuntimeExports.jsx("p", { className: "text-lg font-bold", children: data.value }),
        /* @__PURE__ */ jsxRuntimeExports.jsx("p", { className: "text-[10px] opacity-70", children: data.sub })
      ] })
    ] }, idx)) }),
    /* @__PURE__ */ jsxRuntimeExports.jsx("div", { className: "grid gap-4 md:grid-cols-3", children: models.map((model) => /* @__PURE__ */ jsxRuntimeExports.jsxs(
      Card,
      {
        className: "p-5 space-y-4 shadow-sm border-primary/10 relative overflow-hidden",
        children: [
          /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex items-start justify-between", children: [
            /* @__PURE__ */ jsxRuntimeExports.jsx("div", { className: "rounded-full bg-primary/10 p-2 text-primary", children: /* @__PURE__ */ jsxRuntimeExports.jsx(BrainCircuit, { className: "h-5 w-5" }) }),
            /* @__PURE__ */ jsxRuntimeExports.jsx(Badge, { variant: model.status === "Active" ? "default" : "secondary", children: model.status })
          ] }),
          /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { children: [
            /* @__PURE__ */ jsxRuntimeExports.jsx("h3", { className: "font-bold leading-tight", children: model.name }),
            /* @__PURE__ */ jsxRuntimeExports.jsx("p", { className: "text-[10px] font-mono text-primary uppercase", children: model.algorithm })
          ] }),
          /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "space-y-2", children: [
            /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex justify-between text-xs font-medium", children: [
              /* @__PURE__ */ jsxRuntimeExports.jsx("span", { children: "Validation Accuracy" }),
              /* @__PURE__ */ jsxRuntimeExports.jsxs("span", { children: [
                model.accuracy,
                "%"
              ] })
            ] }),
            /* @__PURE__ */ jsxRuntimeExports.jsx(Progress, { value: model.accuracy, className: "h-1" })
          ] }),
          /* @__PURE__ */ jsxRuntimeExports.jsxs("p", { className: "text-xs text-muted-foreground italic leading-relaxed", children: [
            '"',
            model.insight,
            '"'
          ] }),
          /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex gap-2 pt-2", children: [
            /* @__PURE__ */ jsxRuntimeExports.jsxs(Button, { size: "sm", className: "w-full gap-1.5", variant: "outline", children: [
              /* @__PURE__ */ jsxRuntimeExports.jsx(RefreshCw, { className: "h-3.5 w-3.5" }),
              " Retrain"
            ] }),
            /* @__PURE__ */ jsxRuntimeExports.jsxs(Button, { size: "sm", className: "w-full gap-1.5 bg-primary", children: [
              /* @__PURE__ */ jsxRuntimeExports.jsx(Play, { className: "h-3.5 w-3.5" }),
              " Predict"
            ] })
          ] })
        ]
      },
      model.id
    )) }),
    /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "grid gap-4 md:grid-cols-2", children: [
      /* @__PURE__ */ jsxRuntimeExports.jsxs(Card, { className: "p-6 space-y-4 bg-card", children: [
        /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex items-center gap-2 font-bold", children: [
          /* @__PURE__ */ jsxRuntimeExports.jsx(Zap, { className: "h-5 w-5 text-amber-500" }),
          "Active Signal Processing"
        ] }),
        /* @__PURE__ */ jsxRuntimeExports.jsx("div", { className: "space-y-3", children: [1, 2, 3].map((i) => /* @__PURE__ */ jsxRuntimeExports.jsxs(
          "div",
          {
            className: "flex items-center justify-between border-b border-border/50 pb-2 last:border-0",
            children: [
              /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex items-center gap-3", children: [
                /* @__PURE__ */ jsxRuntimeExports.jsx("div", { className: "h-2 w-2 rounded-full bg-emerald-500 animate-pulse" }),
                /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { children: [
                  /* @__PURE__ */ jsxRuntimeExports.jsxs("p", { className: "text-sm font-medium", children: [
                    "Telemetry Node #",
                    i
                  ] }),
                  /* @__PURE__ */ jsxRuntimeExports.jsx("p", { className: "text-[10px] text-muted-foreground font-mono", children: "Raw: 0.42v | Map: 68%" })
                ] })
              ] }),
              /* @__PURE__ */ jsxRuntimeExports.jsx(CircleCheck, { className: "h-4 w-4 text-emerald-500" })
            ]
          },
          i
        )) })
      ] }),
      /* @__PURE__ */ jsxRuntimeExports.jsxs(Card, { className: "p-6 bg-emerald-600 text-white space-y-4", children: [
        /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex items-center gap-2 font-bold", children: [
          /* @__PURE__ */ jsxRuntimeExports.jsx(TrendingUp, { className: "h-5 w-5" }),
          "Smart Irrigation Forecast"
        ] }),
        /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "space-y-2", children: [
          /* @__PURE__ */ jsxRuntimeExports.jsx("div", { className: "text-4xl font-bold", children: "-25%" }),
          /* @__PURE__ */ jsxRuntimeExports.jsx("p", { className: "text-sm opacity-90 leading-relaxed", children: "Potensi penghematan air dalam 7 hari ke depan karena prediksi curah hujan tinggi dari Weather API." }),
          /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex gap-2 pt-2", children: [
            /* @__PURE__ */ jsxRuntimeExports.jsx(Badge, { className: "bg-white/20 text-white border-0", children: "High Precision" }),
            /* @__PURE__ */ jsxRuntimeExports.jsx(Badge, { className: "bg-white/20 text-white border-0", children: "API Synced" })
          ] })
        ] })
      ] })
    ] })
  ] });
}
const SplitComponent = MLPredictionManager;
export {
  SplitComponent as component
};
