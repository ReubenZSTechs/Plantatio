import { r as reactExports, W as jsxRuntimeExports } from "./server-BG8Cz_a2.js";
import { R as Route, L as Link, t as toast } from "./router-DaN2asXe.js";
import { B as Badge, C as Card } from "./badge-Ci2zfins.js";
import { B as Button } from "./button-BpSWKw9G.js";
import { P as Progress } from "./progress-CCR5OBxf.js";
import { a as api, b as ApiError, A as API_BASE_URL } from "./api-BNzXBfwP.js";
import { C as ChatPanel } from "./ChatPanel-CLbb7LyA.js";
import { L as LoaderCircle } from "./loader-circle-Ba4x-1QD.js";
import { S as Sprout } from "./sprout-HTLAs6KQ.js";
import { A as ArrowLeft, Q as QrCode, W as Wifi, S as ScanLine, M as Mountain, F as FlaskConical, P as Package } from "./wifi-B6x4EKe4.js";
import { C as Cpu, X } from "./x-wPsyAqoF.js";
import { D as Droplets } from "./droplets-wMK8aoEF.js";
import { L as Leaf } from "./leaf-Dgz3cyvi.js";
import { S as Sun } from "./sun-CswmqDAE.js";
import { T as Thermometer } from "./thermometer-BSF65oTr.js";
import { B as Bot } from "./bot-zAHS25mR.js";
import { T as TriangleAlert } from "./triangle-alert-jwyqnsFt.js";
import { C as Check } from "./check-BkbyOQtT.js";
import { F as Flower2 } from "./flower-2-CY4D9gfj.js";
import "node:async_hooks";
import "node:stream/web";
import "node:stream";
import "./utils-B3hKptjK.js";
import "./index-CFniAsgI.js";
import "./input-Dc7a9lUS.js";
import "./camera-BEhya5Ry.js";
const CATEGORY_CONFIG = {
  sensor: {
    label: "Sensor",
    icon: /* @__PURE__ */ jsxRuntimeExports.jsx(Cpu, { className: "h-4 w-4" }),
    color: "text-blue-500 bg-blue-50 border-blue-200"
  },
  seed: {
    label: "Bibit",
    icon: /* @__PURE__ */ jsxRuntimeExports.jsx(Flower2, { className: "h-4 w-4" }),
    color: "text-emerald-600 bg-emerald-50 border-emerald-200"
  },
  soil: {
    label: "Tanah",
    icon: /* @__PURE__ */ jsxRuntimeExports.jsx(Mountain, { className: "h-4 w-4" }),
    color: "text-amber-600 bg-amber-50 border-amber-200"
  },
  fertilizer: {
    label: "Pupuk",
    icon: /* @__PURE__ */ jsxRuntimeExports.jsx(FlaskConical, { className: "h-4 w-4" }),
    color: "text-purple-600 bg-purple-50 border-purple-200"
  },
  other: {
    label: "Lainnya",
    icon: /* @__PURE__ */ jsxRuntimeExports.jsx(Package, { className: "h-4 w-4" }),
    color: "text-slate-600 bg-slate-50 border-slate-200"
  }
};
const MOCK_PRODUCTS = {
  sensor: [
    { category: "sensor", id: "PRB", name: "Smart Probe Gen 2", brand: "Plantatio", scannedAt: "" }
  ],
  seed: [
    {
      category: "seed",
      id: "SEED-001",
      name: "Tomat Cherry",
      brand: "GrowKing",
      seedVariety: "Cherry Roma",
      germinationDays: 7,
      scannedAt: ""
    }
  ],
  soil: [
    {
      category: "soil",
      id: "SOIL-001",
      name: "Premium Potting Mix",
      brand: "BioBest",
      soilType: "Perlite blend",
      phLevel: 6.5,
      scannedAt: ""
    }
  ],
  fertilizer: [
    {
      category: "fertilizer",
      id: "FERT-001",
      name: "GrowMax NPK",
      brand: "NutriPlant",
      npkRatio: "20-10-10",
      applicationFrequency: "Setiap 2 minggu",
      scannedAt: ""
    }
  ],
  other: [
    {
      category: "other",
      id: "OTH-001",
      name: "Pestisida Organik",
      brand: "GreenShield",
      description: "Pengendalian hama ramah lingkungan",
      scannedAt: ""
    }
  ]
};
function Gauge({ icon, label, value, unit, max = 100, warn = false }) {
  return /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: `rounded-lg border bg-card p-3 ${warn ? "border-amber-400/60" : ""}`, children: [
    /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "mb-1 flex items-center gap-1.5 text-xs text-muted-foreground", children: [
      icon,
      label,
      warn && /* @__PURE__ */ jsxRuntimeExports.jsx(TriangleAlert, { className: "ml-auto h-3 w-3 text-amber-400" })
    ] }),
    /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "mb-1.5 text-lg font-semibold", children: [
      value,
      unit
    ] }),
    /* @__PURE__ */ jsxRuntimeExports.jsx(Progress, { value: value / max * 100, className: "h-1.5" })
  ] });
}
function OmniScannerModal({
  plantName,
  onScanComplete,
  onClose
}) {
  const [step, setStep] = reactExports.useState("select");
  const [category, setCategory] = reactExports.useState("sensor");
  const [result, setResult] = reactExports.useState(null);
  const scanCategories = [
    {
      id: "sensor",
      label: "Sensor",
      desc: "Smart probe IoT",
      icon: /* @__PURE__ */ jsxRuntimeExports.jsx(Cpu, { className: "h-5 w-5" }),
      color: "text-blue-600 bg-blue-50 border-blue-200"
    },
    {
      id: "seed",
      label: "Bibit",
      desc: "Benih & varietas",
      icon: /* @__PURE__ */ jsxRuntimeExports.jsx(Flower2, { className: "h-5 w-5" }),
      color: "text-emerald-600 bg-emerald-50 border-emerald-200"
    },
    {
      id: "soil",
      label: "Tanah",
      desc: "Media tanam",
      icon: /* @__PURE__ */ jsxRuntimeExports.jsx(Mountain, { className: "h-5 w-5" }),
      color: "text-amber-600 bg-amber-50 border-amber-200"
    },
    {
      id: "fertilizer",
      label: "Pupuk",
      desc: "Nutrisi & NPK",
      icon: /* @__PURE__ */ jsxRuntimeExports.jsx(FlaskConical, { className: "h-5 w-5" }),
      color: "text-purple-600 bg-purple-50 border-purple-200"
    },
    {
      id: "other",
      label: "Lainnya",
      desc: "Pestisida, alat...",
      icon: /* @__PURE__ */ jsxRuntimeExports.jsx(Package, { className: "h-5 w-5" }),
      color: "text-slate-600 bg-slate-50 border-slate-200"
    }
  ];
  const handleSimulateScan = () => {
    setStep("processing");
    setTimeout(() => {
      const pool = MOCK_PRODUCTS[category];
      const mock = { ...pool[0] };
      if (category === "sensor") {
        mock.id = `PRB-${Math.floor(1e3 + Math.random() * 9e3)}`;
        mock.sensorId = mock.id;
      }
      mock.scannedAt = (/* @__PURE__ */ new Date()).toISOString();
      setResult(mock);
      setStep("result");
    }, 1800);
  };
  return /* @__PURE__ */ jsxRuntimeExports.jsx("div", { className: "fixed inset-0 z-50 flex items-end justify-center bg-black/60 backdrop-blur-sm sm:items-center p-4", children: /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "w-full max-w-sm rounded-3xl bg-background shadow-2xl", children: [
    step === "select" && /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "space-y-0", children: [
      /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex items-center justify-between border-b px-5 py-4", children: [
        /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { children: [
          /* @__PURE__ */ jsxRuntimeExports.jsx("h2", { className: "font-semibold", children: "Scan to AI Context" }),
          /* @__PURE__ */ jsxRuntimeExports.jsxs("p", { className: "text-xs text-muted-foreground", children: [
            "Tambahkan data ke ",
            plantName
          ] })
        ] }),
        /* @__PURE__ */ jsxRuntimeExports.jsx(Button, { size: "icon", variant: "ghost", className: "h-7 w-7", onClick: onClose, children: /* @__PURE__ */ jsxRuntimeExports.jsx(X, { className: "h-4 w-4" }) })
      ] }),
      /* @__PURE__ */ jsxRuntimeExports.jsx("div", { className: "grid grid-cols-1 divide-y p-2", children: scanCategories.map((cat) => /* @__PURE__ */ jsxRuntimeExports.jsxs(
        "button",
        {
          onClick: () => {
            setCategory(cat.id);
            setStep("scan");
          },
          className: "flex items-center gap-3 rounded-xl px-3 py-3 text-left transition-colors hover:bg-secondary/50",
          children: [
            /* @__PURE__ */ jsxRuntimeExports.jsx(
              "div",
              {
                className: `flex h-9 w-9 shrink-0 items-center justify-center rounded-xl border ${cat.color}`,
                children: cat.icon
              }
            ),
            /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex-1", children: [
              /* @__PURE__ */ jsxRuntimeExports.jsx("p", { className: "text-sm font-medium", children: cat.label }),
              /* @__PURE__ */ jsxRuntimeExports.jsx("p", { className: "text-xs text-muted-foreground", children: cat.desc })
            ] })
          ]
        },
        cat.id
      )) }),
      /* @__PURE__ */ jsxRuntimeExports.jsx("div", { className: "border-t px-5 py-3", children: /* @__PURE__ */ jsxRuntimeExports.jsx(Button, { variant: "ghost", className: "w-full", onClick: onClose, children: "Cancel" }) })
    ] }),
    step === "scan" && /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "space-y-5 p-6 text-center", children: [
      /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex items-center gap-2", children: [
        /* @__PURE__ */ jsxRuntimeExports.jsx(
          Button,
          {
            size: "icon",
            variant: "ghost",
            className: "h-7 w-7",
            onClick: () => setStep("select"),
            children: /* @__PURE__ */ jsxRuntimeExports.jsx(ArrowLeft, { className: "h-4 w-4" })
          }
        ),
        /* @__PURE__ */ jsxRuntimeExports.jsxs("h2", { className: "font-semibold", children: [
          "Scan ",
          scanCategories.find((c) => c.id === category)?.label
        ] })
      ] }),
      /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "relative mx-auto flex h-44 w-44 items-center justify-center overflow-hidden rounded-2xl border-2 border-dashed border-primary bg-secondary/20", children: [
        /* @__PURE__ */ jsxRuntimeExports.jsx("div", { className: "absolute left-0 top-0 h-0.5 w-full bg-primary/70 animate-[scan_2s_ease-in-out_infinite]" }),
        /* @__PURE__ */ jsxRuntimeExports.jsx(ScanLine, { className: "h-12 w-12 text-primary/20" })
      ] }),
      /* @__PURE__ */ jsxRuntimeExports.jsxs(Button, { className: "w-full", onClick: handleSimulateScan, children: [
        /* @__PURE__ */ jsxRuntimeExports.jsx(QrCode, { className: "mr-2 h-4 w-4" }),
        " Simulasi Scan"
      ] }),
      /* @__PURE__ */ jsxRuntimeExports.jsx(Button, { variant: "ghost", className: "w-full", onClick: onClose, children: "Cancel" }),
      /* @__PURE__ */ jsxRuntimeExports.jsx("style", { children: `@keyframes scan { 0%, 100% { top: 5%; } 50% { top: 90%; } }` })
    ] }),
    step === "processing" && /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "py-16 text-center space-y-4 px-6", children: [
      /* @__PURE__ */ jsxRuntimeExports.jsx(LoaderCircle, { className: "mx-auto h-10 w-10 animate-spin text-primary" }),
      /* @__PURE__ */ jsxRuntimeExports.jsx("p", { className: "font-medium", children: "Memproses Context..." })
    ] }),
    step === "result" && result && /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "space-y-0", children: [
      /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex items-center gap-2 border-b px-5 py-4", children: [
        /* @__PURE__ */ jsxRuntimeExports.jsx(
          "div",
          {
            className: `flex h-9 w-9 items-center justify-center rounded-xl border ${CATEGORY_CONFIG[result.category].color}`,
            children: CATEGORY_CONFIG[result.category].icon
          }
        ),
        /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { children: [
          /* @__PURE__ */ jsxRuntimeExports.jsx("p", { className: "font-semibold", children: result.name }),
          /* @__PURE__ */ jsxRuntimeExports.jsx("p", { className: "text-xs text-muted-foreground", children: result.brand })
        ] })
      ] }),
      /* @__PURE__ */ jsxRuntimeExports.jsx("div", { className: "p-5", children: /* @__PURE__ */ jsxRuntimeExports.jsx("p", { className: "rounded-lg bg-secondary/50 px-3 py-2 text-xs text-muted-foreground border border-border", children: '✅ Info ini akan otomatis ditambahkan ke "Otak AI" untuk saran perawatan yang lebih akurat.' }) }),
      /* @__PURE__ */ jsxRuntimeExports.jsx("div", { className: "flex gap-2 border-t px-5 py-4", children: /* @__PURE__ */ jsxRuntimeExports.jsxs(
        Button,
        {
          className: "flex-1 bg-emerald-600 hover:bg-emerald-700",
          onClick: () => onScanComplete(result),
          children: [
            /* @__PURE__ */ jsxRuntimeExports.jsx(Check, { className: "mr-1.5 h-4 w-4" }),
            " Sinkronkan ke AI"
          ]
        }
      ) })
    ] })
  ] }) });
}
function PlantDetailPage() {
  const [localPlant, setLocalPlant] = reactExports.useState(null);
  const [isScanning, setIsScanning] = reactExports.useState(false);
  const [loading, setLoading] = reactExports.useState(true);
  const { plantId: plantIdParam } = Route.useParams();
  const plantId = Number(plantIdParam);
  const [loadError, setLoadError] = reactExports.useState(null);
  const reloadPlant = reactExports.useCallback(() => {
    if (!Number.isFinite(plantId)) {
      setLoadError("That plant id is not valid.");
      setLoading(false);
      return;
    }
    setLoading(true);
    api.getPlant(plantId).then((data) => {
      setLocalPlant(data);
      setLoadError(null);
    }).catch((error) => {
      setLoadError(error instanceof ApiError ? error.message : "Could not load this plant.");
    }).finally(() => setLoading(false));
  }, [plantId]);
  reactExports.useEffect(() => {
    reloadPlant();
  }, [reloadPlant]);
  const handleScanComplete = async (item) => {
    if (!localPlant) return;
    try {
      const response = await fetch(`${API_BASE_URL}/plants/${localPlant.id}/scan`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(item)
      });
      if (!response.ok) throw new Error("Could not save the scan");
      const updatedPlant = await response.json();
      setLocalPlant(updatedPlant);
      toast.success(`Context AI diperbarui dengan ${item.name}!`);
    } catch (e) {
      toast.error("Could not sync to the server.");
    } finally {
      setIsScanning(false);
    }
  };
  if (loadError) {
    return /* @__PURE__ */ jsxRuntimeExports.jsx("div", { className: "flex min-h-screen items-center justify-center px-4", children: /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "max-w-sm text-center", children: [
      /* @__PURE__ */ jsxRuntimeExports.jsx("p", { className: "text-sm font-medium", children: loadError }),
      /* @__PURE__ */ jsxRuntimeExports.jsx(
        Link,
        {
          to: "/garden",
          className: "mt-4 inline-flex items-center justify-center rounded-md border px-4 py-2 text-sm transition-colors hover:bg-accent",
          children: "Back to my garden"
        }
      )
    ] }) });
  }
  if (loading) {
    return /* @__PURE__ */ jsxRuntimeExports.jsx("div", { className: "flex min-h-screen items-center justify-center", children: /* @__PURE__ */ jsxRuntimeExports.jsx(LoaderCircle, { className: "h-8 w-8 animate-spin text-primary" }) });
  }
  if (!localPlant) {
    return /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex min-h-screen flex-col items-center justify-center gap-4 p-8 text-center", children: [
      /* @__PURE__ */ jsxRuntimeExports.jsx(Sprout, { className: "h-12 w-12 text-muted-foreground/40" }),
      /* @__PURE__ */ jsxRuntimeExports.jsx("p", { className: "text-lg font-semibold", children: "Plant not found" }),
      /* @__PURE__ */ jsxRuntimeExports.jsx(Button, { asChild: true, variant: "outline", children: /* @__PURE__ */ jsxRuntimeExports.jsxs(Link, { to: "/garden", children: [
        /* @__PURE__ */ jsxRuntimeExports.jsx(ArrowLeft, { className: "mr-1.5 h-4 w-4" }),
        " Back to garden"
      ] }) })
    ] });
  }
  const healthBadgeColor = localPlant.health >= 80 ? "bg-emerald-500" : localPlant.health >= 50 ? "bg-amber-400" : "bg-red-400";
  const activeSensor = localPlant.scannedItems?.find((item) => item.category === "sensor");
  return /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "min-h-screen bg-background", children: [
    /* @__PURE__ */ jsxRuntimeExports.jsx("header", { className: "sticky top-0 z-10 border-b bg-card/80 backdrop-blur", children: /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "mx-auto flex max-w-md items-center justify-between px-4 py-3", children: [
      /* @__PURE__ */ jsxRuntimeExports.jsxs(
        Link,
        {
          to: "/garden",
          className: "flex items-center gap-1 text-sm text-muted-foreground hover:text-foreground",
          children: [
            /* @__PURE__ */ jsxRuntimeExports.jsx(ArrowLeft, { className: "h-4 w-4" }),
            " Garden"
          ]
        }
      ),
      /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex items-center gap-1.5 font-semibold", children: [
        /* @__PURE__ */ jsxRuntimeExports.jsx(Sprout, { className: "h-5 w-5 text-primary" }),
        " ",
        localPlant.nickname
      ] }),
      /* @__PURE__ */ jsxRuntimeExports.jsxs(Badge, { className: `${healthBadgeColor} border-0 text-xs text-white`, children: [
        localPlant.health,
        "%"
      ] })
    ] }) }),
    /* @__PURE__ */ jsxRuntimeExports.jsxs("main", { className: "mx-auto max-w-md space-y-5 px-4 py-5", children: [
      /* @__PURE__ */ jsxRuntimeExports.jsxs(
        "div",
        {
          className: "relative h-52 w-full overflow-hidden rounded-2xl bg-cover bg-center",
          style: { backgroundImage: `url(${localPlant.image})` },
          children: [
            /* @__PURE__ */ jsxRuntimeExports.jsx("div", { className: "absolute inset-0 bg-gradient-to-t from-black/60 via-transparent" }),
            /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "absolute bottom-4 left-4", children: [
              /* @__PURE__ */ jsxRuntimeExports.jsx("p", { className: "text-[10px] uppercase tracking-widest text-white/60", children: localPlant.species }),
              /* @__PURE__ */ jsxRuntimeExports.jsx("h1", { className: "text-2xl font-bold text-white", children: localPlant.nickname }),
              /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "mt-1 flex items-center gap-1.5 text-xs text-white/70", children: [
                /* @__PURE__ */ jsxRuntimeExports.jsx(Sprout, { className: "h-3.5 w-3.5" }),
                " Day ",
                localPlant.daysPlanted,
                " since planted"
              ] })
            ] })
          ]
        }
      ),
      /* @__PURE__ */ jsxRuntimeExports.jsxs(
        Button,
        {
          variant: "outline",
          className: "w-full gap-2 border-primary/30 text-primary hover:bg-primary/10 transition-all shadow-sm",
          onClick: () => setIsScanning(true),
          children: [
            /* @__PURE__ */ jsxRuntimeExports.jsx(QrCode, { className: "h-4 w-4" }),
            " Scan QR to AI Context"
          ]
        }
      ),
      /* @__PURE__ */ jsxRuntimeExports.jsxs(Card, { className: "overflow-hidden", children: [
        /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex flex-col border-b px-4 py-3 bg-muted/20", children: [
          /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex items-center justify-between", children: [
            /* @__PURE__ */ jsxRuntimeExports.jsx("p", { className: "text-sm font-semibold", children: "Live Telemetry" }),
            /* @__PURE__ */ jsxRuntimeExports.jsxs(
              Badge,
              {
                variant: "outline",
                className: "text-[10px] bg-emerald-50 text-emerald-600 border-emerald-200 dark:bg-emerald-950/30",
                children: [
                  /* @__PURE__ */ jsxRuntimeExports.jsx(Wifi, { className: "mr-1 h-3 w-3 animate-pulse" }),
                  " MQTT"
                ]
              }
            )
          ] }),
          activeSensor ? /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "mt-3 flex items-center gap-3 rounded-lg border bg-background p-2 shadow-sm", children: [
            /* @__PURE__ */ jsxRuntimeExports.jsx("div", { className: "flex h-9 w-9 items-center justify-center rounded-md bg-blue-50 text-blue-600 dark:bg-blue-900/30 dark:text-blue-400", children: /* @__PURE__ */ jsxRuntimeExports.jsx(Cpu, { className: "h-5 w-5" }) }),
            /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex-1", children: [
              /* @__PURE__ */ jsxRuntimeExports.jsx("p", { className: "text-xs font-bold leading-none", children: activeSensor.name }),
              /* @__PURE__ */ jsxRuntimeExports.jsxs("p", { className: "text-[10px] text-muted-foreground mt-1 font-mono", children: [
                "ID: ",
                activeSensor.sensorId
              ] })
            ] }),
            /* @__PURE__ */ jsxRuntimeExports.jsx(
              Badge,
              {
                variant: "secondary",
                className: "text-[9px] bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-400",
                children: "Connected"
              }
            )
          ] }) : /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "mt-3 flex items-center gap-3 rounded-lg border border-dashed p-3 text-muted-foreground bg-secondary/10", children: [
            /* @__PURE__ */ jsxRuntimeExports.jsx(Cpu, { className: "h-5 w-5 opacity-50" }),
            /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { children: [
              /* @__PURE__ */ jsxRuntimeExports.jsx("p", { className: "text-xs font-medium", children: "Belum ada sensor" }),
              /* @__PURE__ */ jsxRuntimeExports.jsx("p", { className: "text-[10px] opacity-70", children: "Gunakan tombol Scan QR untuk menghubungkan perangkat." })
            ] })
          ] })
        ] }),
        /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "grid grid-cols-2 gap-3 p-4", children: [
          /* @__PURE__ */ jsxRuntimeExports.jsx(
            Gauge,
            {
              icon: /* @__PURE__ */ jsxRuntimeExports.jsx(Droplets, { className: "h-4 w-4" }),
              label: "Moisture",
              value: localPlant.probe.moisture,
              unit: "%",
              warn: localPlant.probe.moisture < 30
            }
          ),
          /* @__PURE__ */ jsxRuntimeExports.jsx(
            Gauge,
            {
              icon: /* @__PURE__ */ jsxRuntimeExports.jsx(Leaf, { className: "h-4 w-4" }),
              label: "Nutrients",
              value: localPlant.probe.nutrients,
              unit: "%",
              warn: localPlant.probe.nutrients < 30
            }
          ),
          /* @__PURE__ */ jsxRuntimeExports.jsx(
            Gauge,
            {
              icon: /* @__PURE__ */ jsxRuntimeExports.jsx(Sun, { className: "h-4 w-4" }),
              label: "Light",
              value: localPlant.probe.light,
              unit: "%",
              warn: localPlant.probe.light < 20
            }
          ),
          /* @__PURE__ */ jsxRuntimeExports.jsx(
            Gauge,
            {
              icon: /* @__PURE__ */ jsxRuntimeExports.jsx(Thermometer, { className: "h-4 w-4" }),
              label: "Temp",
              value: localPlant.probe.temperature,
              unit: "°C",
              max: 40,
              warn: localPlant.probe.temperature > 35
            }
          )
        ] })
      ] }),
      /* @__PURE__ */ jsxRuntimeExports.jsxs(Card, { children: [
        /* @__PURE__ */ jsxRuntimeExports.jsx("div", { className: "border-b px-4 py-3", children: /* @__PURE__ */ jsxRuntimeExports.jsx("p", { className: "text-sm font-semibold", children: "Care history" }) }),
        /* @__PURE__ */ jsxRuntimeExports.jsx("ol", { className: "px-4 py-3", children: localPlant.timeline.map((t, i) => /* @__PURE__ */ jsxRuntimeExports.jsxs("li", { className: "flex gap-3 py-2 text-sm", children: [
          /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex flex-col items-center gap-1", children: [
            /* @__PURE__ */ jsxRuntimeExports.jsx("div", { className: "mt-1.5 h-2 w-2 shrink-0 rounded-full bg-primary" }),
            i < localPlant.timeline.length - 1 && /* @__PURE__ */ jsxRuntimeExports.jsx("div", { className: "w-px flex-1 bg-border", style: { minHeight: 16 } })
          ] }),
          /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex-1 pb-1", children: [
            /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex justify-between", children: [
              /* @__PURE__ */ jsxRuntimeExports.jsx("span", { className: "font-medium", children: t.event }),
              /* @__PURE__ */ jsxRuntimeExports.jsx("span", { className: "text-xs text-muted-foreground", children: t.date })
            ] }),
            /* @__PURE__ */ jsxRuntimeExports.jsx("div", { className: "text-xs text-muted-foreground", children: t.note })
          ] })
        ] }, i)) })
      ] }),
      /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { children: [
        /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "mb-2 flex items-center gap-1.5 px-1", children: [
          /* @__PURE__ */ jsxRuntimeExports.jsx(Bot, { className: "h-4 w-4 text-primary" }),
          /* @__PURE__ */ jsxRuntimeExports.jsx("h2", { className: "text-sm font-semibold", children: "AI Plant Assistant" }),
          /* @__PURE__ */ jsxRuntimeExports.jsx("span", { className: "text-xs text-muted-foreground", children: "— Context Synced" })
        ] }),
        /* @__PURE__ */ jsxRuntimeExports.jsx(
          ChatPanel,
          {
            scope: "plant",
            plantId: localPlant.id,
            title: `Assistant for ${localPlant.nickname}`,
            subtitle: "Knows this plant's readings and care history",
            greeting: `Ask me about ${localPlant.nickname}. I can also classify a leaf photo for disease — tap the camera.`,
            suggestions: [
              "Does it need watering now?",
              "How are the nutrients looking?",
              "Any care tips for this week?"
            ],
            enableLeafScan: true,
            onDiagnosed: reloadPlant,
            className: "h-[560px]"
          }
        )
      ] })
    ] }),
    isScanning && /* @__PURE__ */ jsxRuntimeExports.jsx(
      OmniScannerModal,
      {
        plantName: localPlant.nickname,
        onScanComplete: handleScanComplete,
        onClose: () => setIsScanning(false)
      }
    )
  ] });
}
const SplitComponent = PlantDetailPage;
export {
  SplitComponent as component
};
