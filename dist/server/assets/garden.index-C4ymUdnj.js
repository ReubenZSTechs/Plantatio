import { r as reactExports, W as jsxRuntimeExports } from "./server-BG8Cz_a2.js";
import { L as Link, t as toast } from "./router-DaN2asXe.js";
import { B as Badge, C as Card } from "./badge-Ci2zfins.js";
import { B as Button } from "./button-BpSWKw9G.js";
import { P as Progress } from "./progress-CCR5OBxf.js";
import { I as Input } from "./input-Dc7a9lUS.js";
import { L as Label } from "./label-C789j1H7.js";
import { A as ArrowLeft, W as Wifi, Q as QrCode, S as ScanLine, P as Package, F as FlaskConical, M as Mountain } from "./wifi-B6x4EKe4.js";
import { S as Sprout } from "./sprout-HTLAs6KQ.js";
import { P as Plus } from "./plus-I48Ihi2j.js";
import { c as createLucideIcon } from "./utils-B3hKptjK.js";
import { D as Droplets } from "./droplets-wMK8aoEF.js";
import { L as Leaf } from "./leaf-Dgz3cyvi.js";
import { B as Bot } from "./bot-zAHS25mR.js";
import { X, C as Cpu } from "./x-wPsyAqoF.js";
import { C as Camera } from "./camera-BEhya5Ry.js";
import { C as Check } from "./check-BkbyOQtT.js";
import { L as LoaderCircle } from "./loader-circle-Ba4x-1QD.js";
import { F as Flower2 } from "./flower-2-CY4D9gfj.js";
import "node:async_hooks";
import "node:stream/web";
import "node:stream";
import "./index-CFniAsgI.js";
const __iconNode$1 = [
  [
    "path",
    {
      d: "M21.174 6.812a1 1 0 0 0-3.986-3.987L3.842 16.174a2 2 0 0 0-.5.83l-1.321 4.352a.5.5 0 0 0 .623.622l4.353-1.32a2 2 0 0 0 .83-.497z",
      key: "1a8usu"
    }
  ],
  ["path", { d: "m15 5 4 4", key: "1mk7zo" }]
];
const Pencil = createLucideIcon("pencil", __iconNode$1);
const __iconNode = [
  ["path", { d: "M10 11v6", key: "nco0om" }],
  ["path", { d: "M14 11v6", key: "outv1u" }],
  ["path", { d: "M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6", key: "miytrc" }],
  ["path", { d: "M3 6h18", key: "d0wm0j" }],
  ["path", { d: "M8 6V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2", key: "e791ji" }]
];
const Trash2 = createLucideIcon("trash-2", __iconNode);
const SEED_PLANTS = [
  {
    id: 1,
    nickname: "Tomato",
    species: "Solanum lycopersicum",
    image: "https://images.unsplash.com/photo-1416879595882-3373a0480b5b?w=600&q=80",
    health: 85,
    daysPlanted: 14,
    probe: { moisture: 45, nutrients: 60, light: 80, temperature: 26 },
    scannedItems: [],
    timeline: [
      { date: "10 Oct", event: "Ditanam", note: "Bibit dipindahkan ke pot" },
      { date: "12 Oct", event: "Disiram", note: "Penyiraman pertama" }
    ]
  }
];
function healthColor(v) {
  if (v >= 80) return "bg-emerald-500";
  if (v >= 50) return "bg-amber-400";
  return "bg-red-400";
}
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
function Gauge({
  icon,
  label,
  value,
  unit,
  max = 100
}) {
  return /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "rounded-lg border bg-card p-3 text-left", children: [
    /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "mb-1 flex items-center gap-1.5 text-xs text-muted-foreground", children: [
      icon,
      " ",
      label
    ] }),
    /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "mb-1.5 text-lg font-semibold", children: [
      value,
      unit
    ] }),
    /* @__PURE__ */ jsxRuntimeExports.jsx(Progress, { value: value / max * 100, className: "h-1.5" })
  ] });
}
function ScannedItemsSection({ items }) {
  if (items.length === 0) return null;
  const sensor = items.find((i) => i.category === "sensor");
  const seed = items.find((i) => i.category === "seed");
  const soil = items.find((i) => i.category === "soil");
  const fertilizer = items.find((i) => i.category === "fertilizer");
  return /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "space-y-1.5 rounded-xl border bg-secondary/30 p-3", children: [
    /* @__PURE__ */ jsxRuntimeExports.jsx("p", { className: "mb-2 text-[10px] font-semibold uppercase tracking-widest text-muted-foreground", children: "Scanned items" }),
    sensor && /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex items-center justify-between text-xs", children: [
      /* @__PURE__ */ jsxRuntimeExports.jsxs("span", { className: "flex items-center gap-1.5 text-muted-foreground", children: [
        /* @__PURE__ */ jsxRuntimeExports.jsx(Wifi, { className: "h-3 w-3 text-blue-500 animate-pulse" }),
        " Sensor"
      ] }),
      /* @__PURE__ */ jsxRuntimeExports.jsxs("span", { className: "font-medium", children: [
        sensor.sensorId,
        " · ",
        sensor.name
      ] })
    ] }),
    seed && /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex items-center justify-between text-xs", children: [
      /* @__PURE__ */ jsxRuntimeExports.jsxs("span", { className: "flex items-center gap-1.5 text-muted-foreground", children: [
        /* @__PURE__ */ jsxRuntimeExports.jsx(Flower2, { className: "h-3 w-3 text-emerald-500" }),
        " Bibit"
      ] }),
      /* @__PURE__ */ jsxRuntimeExports.jsxs("span", { className: "font-medium", children: [
        seed.name,
        seed.seedVariety ? ` · ${seed.seedVariety}` : ""
      ] })
    ] }),
    soil && /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex items-center justify-between text-xs", children: [
      /* @__PURE__ */ jsxRuntimeExports.jsxs("span", { className: "flex items-center gap-1.5 text-muted-foreground", children: [
        /* @__PURE__ */ jsxRuntimeExports.jsx(Mountain, { className: "h-3 w-3 text-amber-500" }),
        " Tanah"
      ] }),
      /* @__PURE__ */ jsxRuntimeExports.jsxs("span", { className: "font-medium", children: [
        soil.name,
        soil.phLevel ? ` · pH ${soil.phLevel}` : ""
      ] })
    ] }),
    fertilizer && /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex items-center justify-between text-xs", children: [
      /* @__PURE__ */ jsxRuntimeExports.jsxs("span", { className: "flex items-center gap-1.5 text-muted-foreground", children: [
        /* @__PURE__ */ jsxRuntimeExports.jsx(FlaskConical, { className: "h-3 w-3 text-purple-500" }),
        " Pupuk"
      ] }),
      /* @__PURE__ */ jsxRuntimeExports.jsxs("span", { className: "font-medium", children: [
        fertilizer.name,
        fertilizer.npkRatio ? ` · NPK ${fertilizer.npkRatio}` : ""
      ] })
    ] })
  ] });
}
function PlantCard({
  plant,
  onEdit,
  onDelete,
  onScan
}) {
  const activeSensor = plant.scannedItems.find((i) => i.category === "sensor");
  return /* @__PURE__ */ jsxRuntimeExports.jsxs(Card, { className: "overflow-hidden transition-shadow hover:shadow-md", children: [
    /* @__PURE__ */ jsxRuntimeExports.jsx(Link, { to: "/garden/$plantId", params: { plantId: String(plant.id) }, className: "block w-full", children: /* @__PURE__ */ jsxRuntimeExports.jsxs(
      "div",
      {
        className: "relative h-40 w-full bg-cover bg-center",
        style: { backgroundImage: `url(${plant.image})` },
        children: [
          /* @__PURE__ */ jsxRuntimeExports.jsx("div", { className: "absolute inset-0 bg-gradient-to-t from-black/60 to-transparent" }),
          /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "absolute bottom-3 left-4 right-4 flex items-end justify-between text-white", children: [
            /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { children: [
              /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "mb-0.5 flex items-center gap-1", children: [
                /* @__PURE__ */ jsxRuntimeExports.jsx(
                  Wifi,
                  {
                    className: `h-2.5 w-2.5 ${activeSensor ? "text-emerald-400 animate-pulse" : "text-slate-400"}`
                  }
                ),
                /* @__PURE__ */ jsxRuntimeExports.jsx("p", { className: "text-[9px] uppercase tracking-widest", children: activeSensor ? `Sensor ${activeSensor.sensorId}` : "No Sensor" })
              ] }),
              /* @__PURE__ */ jsxRuntimeExports.jsx("h3", { className: "text-base font-semibold", children: plant.nickname })
            ] }),
            /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex flex-col items-end gap-1", children: [
              /* @__PURE__ */ jsxRuntimeExports.jsxs(Badge, { className: `${healthColor(plant.health)} border-0 text-white`, children: [
                plant.health,
                "%"
              ] }),
              plant.scannedItems.length > 0 && /* @__PURE__ */ jsxRuntimeExports.jsx("div", { className: "flex gap-0.5", children: plant.scannedItems.slice(0, 4).map((item, i) => /* @__PURE__ */ jsxRuntimeExports.jsx(
                "span",
                {
                  className: "flex h-4 w-4 items-center justify-center rounded-full bg-white/20 text-[8px] text-white",
                  title: CATEGORY_CONFIG[item.category].label,
                  children: item.category === "sensor" ? "📡" : item.category === "seed" ? "🌱" : item.category === "soil" ? "🪨" : item.category === "fertilizer" ? "🧪" : "📦"
                },
                i
              )) })
            ] })
          ] })
        ]
      }
    ) }),
    /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "space-y-3 p-4", children: [
      /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex items-center justify-between", children: [
        /* @__PURE__ */ jsxRuntimeExports.jsxs("span", { className: "text-xs text-muted-foreground", children: [
          "Day ",
          plant.daysPlanted
        ] }),
        /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex gap-1", children: [
          /* @__PURE__ */ jsxRuntimeExports.jsx(
            Button,
            {
              size: "icon",
              variant: "outline",
              className: "h-7 w-7 border-emerald-500 text-emerald-600",
              onClick: () => onScan(plant),
              title: "Scan Item",
              children: /* @__PURE__ */ jsxRuntimeExports.jsx(QrCode, { className: "h-3.5 w-3.5" })
            }
          ),
          /* @__PURE__ */ jsxRuntimeExports.jsx(Button, { size: "icon", variant: "ghost", className: "h-7 w-7", onClick: () => onEdit(plant), children: /* @__PURE__ */ jsxRuntimeExports.jsx(Pencil, { className: "h-3.5 w-3.5" }) }),
          /* @__PURE__ */ jsxRuntimeExports.jsx(
            Button,
            {
              size: "icon",
              variant: "ghost",
              className: "h-7 w-7 text-destructive",
              onClick: () => onDelete(plant.id),
              children: /* @__PURE__ */ jsxRuntimeExports.jsx(Trash2, { className: "h-3.5 w-3.5" })
            }
          )
        ] })
      ] }),
      /* @__PURE__ */ jsxRuntimeExports.jsx(ScannedItemsSection, { items: plant.scannedItems }),
      /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: `grid grid-cols-2 gap-2 ${!activeSensor && "opacity-50 grayscale"}`, children: [
        /* @__PURE__ */ jsxRuntimeExports.jsx(
          Gauge,
          {
            icon: /* @__PURE__ */ jsxRuntimeExports.jsx(Droplets, { className: "h-3 w-3" }),
            label: "Moisture",
            value: plant.probe.moisture,
            unit: "%"
          }
        ),
        /* @__PURE__ */ jsxRuntimeExports.jsx(
          Gauge,
          {
            icon: /* @__PURE__ */ jsxRuntimeExports.jsx(Leaf, { className: "h-3 w-3" }),
            label: "Nutrients",
            value: plant.probe.nutrients,
            unit: "%"
          }
        )
      ] }),
      /* @__PURE__ */ jsxRuntimeExports.jsx(
        Button,
        {
          asChild: true,
          className: "w-full gap-2 bg-primary/10 text-primary hover:bg-primary/20",
          variant: "secondary",
          children: /* @__PURE__ */ jsxRuntimeExports.jsxs(Link, { to: "/garden/$plantId", params: { plantId: String(plant.id) }, children: [
            /* @__PURE__ */ jsxRuntimeExports.jsx(Bot, { className: "h-4 w-4" }),
            " Chat with AI"
          ] })
        }
      )
    ] })
  ] });
}
function AddPlantModal({
  onSave,
  onClose
}) {
  const [form, setForm] = reactExports.useState({ nickname: "", species: "", image: "" });
  const set = (key, val) => setForm((f) => ({ ...f, [key]: val }));
  const handleImageUpload = (e) => {
    const file = e.target.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onloadend = () => {
        set("image", reader.result);
      };
      reader.readAsDataURL(file);
    }
  };
  const handleSubmit = () => {
    if (!form.nickname.trim()) {
      toast.error("Give the plant a name");
      return;
    }
    onSave(form);
  };
  return /* @__PURE__ */ jsxRuntimeExports.jsx(
    "div",
    {
      className: "fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4",
      onClick: (e) => e.target === e.currentTarget && onClose(),
      children: /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "relative w-full max-w-sm rounded-3xl bg-background shadow-2xl", children: [
        /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex items-center justify-between border-b px-5 py-4", children: [
          /* @__PURE__ */ jsxRuntimeExports.jsx("h2", { className: "font-semibold", children: "Add plant" }),
          /* @__PURE__ */ jsxRuntimeExports.jsx(Button, { size: "icon", variant: "ghost", className: "h-7 w-7", onClick: onClose, children: /* @__PURE__ */ jsxRuntimeExports.jsx(X, { className: "h-4 w-4" }) })
        ] }),
        /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "space-y-4 px-5 py-4", children: [
          /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "space-y-2", children: [
            /* @__PURE__ */ jsxRuntimeExports.jsx(Label, { children: "Foto Tanaman" }),
            /* @__PURE__ */ jsxRuntimeExports.jsx(
              "input",
              {
                type: "file",
                accept: "image/*",
                capture: "environment",
                id: "upload-add",
                className: "hidden",
                onChange: handleImageUpload
              }
            ),
            /* @__PURE__ */ jsxRuntimeExports.jsx(
              Label,
              {
                htmlFor: "upload-add",
                className: "cursor-pointer flex h-36 w-full flex-col items-center justify-center overflow-hidden rounded-2xl border-2 border-dashed border-primary/30 bg-secondary/30 transition-colors hover:bg-secondary/50",
                children: form.image ? /* @__PURE__ */ jsxRuntimeExports.jsx(
                  "div",
                  {
                    className: "h-full w-full bg-cover bg-center",
                    style: { backgroundImage: `url(${form.image})` }
                  }
                ) : /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex flex-col items-center gap-2 text-muted-foreground/60", children: [
                  /* @__PURE__ */ jsxRuntimeExports.jsx(Camera, { className: "h-8 w-8 text-primary/40" }),
                  /* @__PURE__ */ jsxRuntimeExports.jsx("span", { className: "text-xs font-medium text-primary/60", children: "Kamera / Unggah Foto" })
                ] })
              }
            )
          ] }),
          /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "space-y-1", children: [
            /* @__PURE__ */ jsxRuntimeExports.jsx(Label, { htmlFor: "nickname", children: "Nama tanaman *" }),
            /* @__PURE__ */ jsxRuntimeExports.jsx(
              Input,
              {
                id: "nickname",
                value: form.nickname,
                onChange: (e) => set("nickname", e.target.value),
                placeholder: "e.g. Tomato Cherry"
              }
            )
          ] }),
          /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "space-y-1", children: [
            /* @__PURE__ */ jsxRuntimeExports.jsx(Label, { htmlFor: "species", children: "Jenis / spesies" }),
            /* @__PURE__ */ jsxRuntimeExports.jsx(
              Input,
              {
                id: "species",
                value: form.species,
                onChange: (e) => set("species", e.target.value),
                placeholder: "e.g. Solanum lycopersicum"
              }
            )
          ] }),
          /* @__PURE__ */ jsxRuntimeExports.jsx("p", { className: "rounded-lg bg-emerald-50 px-3 py-2 text-[10px] text-emerald-700 dark:bg-emerald-950/30 dark:text-emerald-400 leading-relaxed", children: "💡 Scan sensor, pupuk, tanah, atau bibit nanti menggunakan tombol QR pada kartu tanaman." })
        ] }),
        /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex gap-2 border-t px-5 py-4", children: [
          /* @__PURE__ */ jsxRuntimeExports.jsx(Button, { variant: "outline", className: "flex-1", onClick: onClose, children: "Cancel" }),
          /* @__PURE__ */ jsxRuntimeExports.jsxs(Button, { className: "flex-1", onClick: handleSubmit, children: [
            /* @__PURE__ */ jsxRuntimeExports.jsx(Check, { className: "mr-1.5 h-4 w-4" }),
            " Tambah"
          ] })
        ] })
      ] })
    }
  );
}
function EditPlantModal({
  plant,
  onSave,
  onClose
}) {
  const [form, setForm] = reactExports.useState({
    id: plant.id,
    nickname: plant.nickname,
    species: plant.species,
    image: plant.image
  });
  const set = (key, val) => setForm((f) => ({ ...f, [key]: val }));
  const handleImageUpload = (e) => {
    const file = e.target.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onloadend = () => set("image", reader.result);
      reader.readAsDataURL(file);
    }
  };
  const handleSubmit = () => {
    if (!form.nickname.trim()) {
      toast.error("Give the plant a name");
      return;
    }
    onSave(form);
  };
  return /* @__PURE__ */ jsxRuntimeExports.jsx(
    "div",
    {
      className: "fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4",
      onClick: (e) => e.target === e.currentTarget && onClose(),
      children: /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "relative w-full max-w-sm rounded-3xl bg-background shadow-2xl", children: [
        /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex items-center justify-between border-b px-5 py-4", children: [
          /* @__PURE__ */ jsxRuntimeExports.jsx("h2", { className: "font-semibold", children: "Edit tanaman" }),
          /* @__PURE__ */ jsxRuntimeExports.jsx(Button, { size: "icon", variant: "ghost", className: "h-7 w-7", onClick: onClose, children: /* @__PURE__ */ jsxRuntimeExports.jsx(X, { className: "h-4 w-4" }) })
        ] }),
        /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "space-y-4 px-5 py-4", children: [
          /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "space-y-2", children: [
            /* @__PURE__ */ jsxRuntimeExports.jsx(Label, { children: "Foto Tanaman" }),
            /* @__PURE__ */ jsxRuntimeExports.jsx(
              "input",
              {
                type: "file",
                accept: "image/*",
                capture: "environment",
                id: "upload-edit",
                className: "hidden",
                onChange: handleImageUpload
              }
            ),
            /* @__PURE__ */ jsxRuntimeExports.jsx(
              Label,
              {
                htmlFor: "upload-edit",
                className: "cursor-pointer flex h-36 w-full flex-col items-center justify-center overflow-hidden rounded-2xl border-2 border-dashed border-primary/30 bg-secondary/30 transition-colors hover:bg-secondary/50",
                children: form.image ? /* @__PURE__ */ jsxRuntimeExports.jsx(
                  "div",
                  {
                    className: "relative h-full w-full bg-cover bg-center group",
                    style: { backgroundImage: `url(${form.image})` },
                    children: /* @__PURE__ */ jsxRuntimeExports.jsx("div", { className: "absolute inset-0 bg-black/40 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity", children: /* @__PURE__ */ jsxRuntimeExports.jsx(Camera, { className: "h-8 w-8 text-white" }) })
                  }
                ) : /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex flex-col items-center gap-2 text-muted-foreground/60", children: [
                  /* @__PURE__ */ jsxRuntimeExports.jsx(Camera, { className: "h-8 w-8 text-primary/40" }),
                  /* @__PURE__ */ jsxRuntimeExports.jsx("span", { className: "text-xs font-medium text-primary/60", children: "Kamera / Unggah Foto" })
                ] })
              }
            )
          ] }),
          /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "space-y-1", children: [
            /* @__PURE__ */ jsxRuntimeExports.jsx(Label, { children: "Nama tanaman *" }),
            /* @__PURE__ */ jsxRuntimeExports.jsx(Input, { value: form.nickname, onChange: (e) => set("nickname", e.target.value) })
          ] }),
          /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "space-y-1", children: [
            /* @__PURE__ */ jsxRuntimeExports.jsx(Label, { children: "Jenis / spesies" }),
            /* @__PURE__ */ jsxRuntimeExports.jsx(Input, { value: form.species, onChange: (e) => set("species", e.target.value) })
          ] })
        ] }),
        /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex gap-2 border-t px-5 py-4", children: [
          /* @__PURE__ */ jsxRuntimeExports.jsx(Button, { variant: "outline", className: "flex-1", onClick: onClose, children: "Cancel" }),
          /* @__PURE__ */ jsxRuntimeExports.jsxs(Button, { className: "flex-1", onClick: handleSubmit, children: [
            /* @__PURE__ */ jsxRuntimeExports.jsx(Check, { className: "mr-1.5 h-4 w-4" }),
            " Save"
          ] })
        ] })
      ] })
    }
  );
}
const MOCK_PRODUCTS = {
  sensor: [
    {
      category: "sensor",
      id: `PRB-${Math.floor(1e3 + Math.random() * 9e3)}`,
      name: "Smart Probe Gen 2",
      brand: "Plantatio",
      sensorId: `PRB-${Math.floor(1e3 + Math.random() * 9e3)}`,
      scannedAt: ""
    }
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
    },
    {
      category: "seed",
      id: "SEED-002",
      name: "Basil Genovese",
      brand: "HerbLab",
      seedVariety: "Genovese",
      germinationDays: 5,
      scannedAt: ""
    },
    {
      category: "seed",
      id: "SEED-003",
      name: "Cabe Rawit",
      brand: "Nusantara Seeds",
      seedVariety: "Rawit Hijau",
      germinationDays: 10,
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
    },
    {
      category: "soil",
      id: "SOIL-002",
      name: "Cocopeat Pro",
      brand: "TropicGrow",
      soilType: "Cocopeat",
      phLevel: 5.8,
      scannedAt: ""
    },
    {
      category: "soil",
      id: "SOIL-003",
      name: "Vermicompost Blend",
      brand: "EarthWorm Co.",
      soilType: "Organic compost",
      phLevel: 7,
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
    },
    {
      category: "fertilizer",
      id: "FERT-002",
      name: "BloomBooster",
      brand: "FloraFeed",
      npkRatio: "10-30-20",
      applicationFrequency: "Sekali seminggu",
      scannedAt: ""
    },
    {
      category: "fertilizer",
      id: "FERT-003",
      name: "Organic Liquid",
      brand: "BioNatur",
      npkRatio: "5-3-4",
      applicationFrequency: "3x seminggu",
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
    },
    {
      category: "other",
      id: "OTH-002",
      name: "Pot Hidroponik 5L",
      brand: "HydroKit",
      description: "Pot dengan sistem drainase aktif",
      scannedAt: ""
    }
  ]
};
function OmniScannerModal({
  plant,
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
      color: "text-blue-600 bg-blue-50 border-blue-200 dark:bg-blue-950/30"
    },
    {
      id: "seed",
      label: "Bibit",
      desc: "Benih & varietas",
      icon: /* @__PURE__ */ jsxRuntimeExports.jsx(Flower2, { className: "h-5 w-5" }),
      color: "text-emerald-600 bg-emerald-50 border-emerald-200 dark:bg-emerald-950/30"
    },
    {
      id: "soil",
      label: "Tanah",
      desc: "Media tanam",
      icon: /* @__PURE__ */ jsxRuntimeExports.jsx(Mountain, { className: "h-5 w-5" }),
      color: "text-amber-600 bg-amber-50 border-amber-200 dark:bg-amber-950/30"
    },
    {
      id: "fertilizer",
      label: "Pupuk",
      desc: "Nutrisi & NPK",
      icon: /* @__PURE__ */ jsxRuntimeExports.jsx(FlaskConical, { className: "h-5 w-5" }),
      color: "text-purple-600 bg-purple-50 border-purple-200 dark:bg-purple-950/30"
    },
    {
      id: "other",
      label: "Lainnya",
      desc: "Pestisida, alat...",
      icon: /* @__PURE__ */ jsxRuntimeExports.jsx(Package, { className: "h-5 w-5" }),
      color: "text-slate-600 bg-slate-50 border-slate-200 dark:bg-slate-800/50"
    }
  ];
  const handleSimulateScan = () => {
    setStep("processing");
    setTimeout(() => {
      const pool = MOCK_PRODUCTS[category];
      const mock = { ...pool[Math.floor(Math.random() * pool.length)] };
      if (category === "sensor") {
        const id = `PRB-${Math.floor(1e3 + Math.random() * 9e3)}`;
        mock.id = id;
        mock.sensorId = id;
      }
      mock.scannedAt = (/* @__PURE__ */ new Date()).toLocaleDateString("id-ID", { day: "numeric", month: "short" });
      setResult(mock);
      setStep("result");
    }, 1800);
  };
  const handleConfirm = () => {
    if (result) onScanComplete(result);
  };
  return /* @__PURE__ */ jsxRuntimeExports.jsx("div", { className: "fixed inset-0 z-50 flex items-end justify-center bg-black/60 backdrop-blur-sm sm:items-center p-4", children: /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "w-full max-w-sm rounded-3xl bg-background shadow-2xl", children: [
    step === "select" && /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "space-y-0", children: [
      /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex items-center justify-between border-b px-5 py-4", children: [
        /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { children: [
          /* @__PURE__ */ jsxRuntimeExports.jsxs("h2", { className: "font-semibold", children: [
            "Scan ke ",
            plant.nickname
          ] }),
          /* @__PURE__ */ jsxRuntimeExports.jsx("p", { className: "text-xs text-muted-foreground", children: "Pilih jenis item yang akan discan" })
        ] }),
        /* @__PURE__ */ jsxRuntimeExports.jsx(Button, { size: "icon", variant: "ghost", className: "h-7 w-7", onClick: onClose, children: /* @__PURE__ */ jsxRuntimeExports.jsx(X, { className: "h-4 w-4" }) })
      ] }),
      /* @__PURE__ */ jsxRuntimeExports.jsx("div", { className: "grid grid-cols-1 divide-y p-2", children: scanCategories.map((cat) => {
        const alreadyScanned = plant.scannedItems.some((i) => i.category === cat.id);
        return /* @__PURE__ */ jsxRuntimeExports.jsxs(
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
              ] }),
              alreadyScanned && /* @__PURE__ */ jsxRuntimeExports.jsxs(
                Badge,
                {
                  variant: "outline",
                  className: "text-[9px] text-emerald-600 border-emerald-300",
                  children: [
                    /* @__PURE__ */ jsxRuntimeExports.jsx(Check, { className: "mr-0.5 h-2.5 w-2.5" }),
                    " Sudah"
                  ]
                }
              )
            ]
          },
          cat.id
        );
      }) }),
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
      /* @__PURE__ */ jsxRuntimeExports.jsxs("p", { className: "text-sm text-muted-foreground", children: [
        "Arahkan kamera ke barcode / QR pada kemasan",
        " ",
        scanCategories.find((c) => c.id === category)?.label.toLowerCase()
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
      /* @__PURE__ */ jsxRuntimeExports.jsx("p", { className: "font-medium", children: "Memproses data produk..." }),
      /* @__PURE__ */ jsxRuntimeExports.jsx("p", { className: "text-xs text-muted-foreground", children: "Mengambil info dari database" })
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
          /* @__PURE__ */ jsxRuntimeExports.jsxs("p", { className: "text-xs text-muted-foreground", children: [
            result.brand,
            " · ",
            CATEGORY_CONFIG[result.category].label
          ] })
        ] })
      ] }),
      /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "space-y-2 px-5 py-4", children: [
        result.category === "sensor" && /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "rounded-xl bg-blue-50 dark:bg-blue-950/30 p-3 space-y-1", children: [
          /* @__PURE__ */ jsxRuntimeExports.jsx("p", { className: "text-xs font-medium text-blue-700 dark:text-blue-300", children: "ID Sensor" }),
          /* @__PURE__ */ jsxRuntimeExports.jsx("p", { className: "font-mono text-sm font-bold text-blue-800 dark:text-blue-200", children: result.sensorId }),
          /* @__PURE__ */ jsxRuntimeExports.jsx("p", { className: "text-xs text-blue-600 dark:text-blue-400", children: "Akan dihubungkan via MQTT broker" })
        ] }),
        result.category === "seed" && /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "rounded-xl bg-emerald-50 dark:bg-emerald-950/30 p-3 space-y-1.5", children: [
          /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex justify-between text-xs", children: [
            /* @__PURE__ */ jsxRuntimeExports.jsx("span", { className: "text-emerald-600", children: "Varietas" }),
            /* @__PURE__ */ jsxRuntimeExports.jsx("span", { className: "font-medium text-emerald-800 dark:text-emerald-200", children: result.seedVariety })
          ] }),
          /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex justify-between text-xs", children: [
            /* @__PURE__ */ jsxRuntimeExports.jsx("span", { className: "text-emerald-600", children: "Estimasi tumbuh" }),
            /* @__PURE__ */ jsxRuntimeExports.jsxs("span", { className: "font-medium text-emerald-800 dark:text-emerald-200", children: [
              result.germinationDays,
              " hari"
            ] })
          ] })
        ] }),
        result.category === "soil" && /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "rounded-xl bg-amber-50 dark:bg-amber-950/30 p-3 space-y-1.5", children: [
          /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex justify-between text-xs", children: [
            /* @__PURE__ */ jsxRuntimeExports.jsx("span", { className: "text-amber-600", children: "Tipe media" }),
            /* @__PURE__ */ jsxRuntimeExports.jsx("span", { className: "font-medium text-amber-800 dark:text-amber-200", children: result.soilType })
          ] }),
          /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex justify-between text-xs", children: [
            /* @__PURE__ */ jsxRuntimeExports.jsx("span", { className: "text-amber-600", children: "Tingkat pH" }),
            /* @__PURE__ */ jsxRuntimeExports.jsx("span", { className: "font-medium text-amber-800 dark:text-amber-200", children: result.phLevel })
          ] })
        ] }),
        result.category === "fertilizer" && /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "rounded-xl bg-purple-50 dark:bg-purple-950/30 p-3 space-y-1.5", children: [
          /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex justify-between text-xs", children: [
            /* @__PURE__ */ jsxRuntimeExports.jsx("span", { className: "text-purple-600", children: "Rasio NPK" }),
            /* @__PURE__ */ jsxRuntimeExports.jsx("span", { className: "font-mono font-bold text-purple-800 dark:text-purple-200", children: result.npkRatio })
          ] }),
          /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex justify-between text-xs", children: [
            /* @__PURE__ */ jsxRuntimeExports.jsx("span", { className: "text-purple-600", children: "Frekuensi" }),
            /* @__PURE__ */ jsxRuntimeExports.jsx("span", { className: "font-medium text-purple-800 dark:text-purple-200", children: result.applicationFrequency })
          ] })
        ] }),
        result.category === "other" && /* @__PURE__ */ jsxRuntimeExports.jsx("div", { className: "rounded-xl bg-slate-50 dark:bg-slate-800/50 p-3", children: /* @__PURE__ */ jsxRuntimeExports.jsx("p", { className: "text-xs text-slate-600 dark:text-slate-400", children: result.description }) }),
        /* @__PURE__ */ jsxRuntimeExports.jsx("p", { className: "rounded-lg bg-secondary/50 px-3 py-2 text-xs text-muted-foreground", children: "✅ Info ini akan ditambahkan ke konteks AI chatbot untuk saran perawatan yang lebih akurat." })
      ] }),
      /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex gap-2 border-t px-5 py-4", children: [
        /* @__PURE__ */ jsxRuntimeExports.jsx(Button, { variant: "outline", className: "flex-1", onClick: () => setStep("select"), children: "Scan Lagi" }),
        /* @__PURE__ */ jsxRuntimeExports.jsxs(
          Button,
          {
            className: "flex-1 bg-emerald-600 hover:bg-emerald-700",
            onClick: handleConfirm,
            children: [
              /* @__PURE__ */ jsxRuntimeExports.jsx(Check, { className: "mr-1.5 h-4 w-4" }),
              " Tambahkan"
            ]
          }
        )
      ] })
    ] })
  ] }) });
}
function PlantGardenPage() {
  const [plants, setPlants] = reactExports.useState(SEED_PLANTS);
  const [showAddForm, setShowAddForm] = reactExports.useState(false);
  const [editingPlant, setEditingPlant] = reactExports.useState(null);
  const [scanningPlant, setScanningPlant] = reactExports.useState(null);
  const handleAddPlant = (form) => {
    const today = (/* @__PURE__ */ new Date()).toLocaleDateString("id-ID", { day: "numeric", month: "short" });
    const newPlant = {
      id: Date.now(),
      nickname: form.nickname,
      species: form.species,
      image: form.image,
      health: 100,
      daysPlanted: 0,
      probe: { moisture: 50, nutrients: 50, light: 60, temperature: 24 },
      scannedItems: [],
      timeline: [
        {
          date: today,
          event: "Terdaftar",
          note: "Plant added"
        }
      ]
    };
    setPlants((prev) => [newPlant, ...prev]);
    toast.success(`${form.nickname} ditambahkan ke kebun 🌿`);
    setShowAddForm(false);
  };
  const handleEditPlant = (form) => {
    setPlants(
      (prev) => prev.map(
        (p) => p.id === form.id ? { ...p, nickname: form.nickname, species: form.species, image: form.image } : p
      )
    );
    toast.success("Plant updated");
    setEditingPlant(null);
  };
  const handleScanComplete = (item) => {
    if (!scanningPlant) return;
    setPlants(
      (prev) => prev.map((p) => {
        if (p.id !== scanningPlant.id) return p;
        const filteredItems = p.scannedItems.filter((i) => i.category !== item.category);
        const newItems = [...filteredItems, item];
        const updatedProbe = item.category === "sensor" ? {
          moisture: 65 + Math.floor(Math.random() * 20),
          nutrients: 60 + Math.floor(Math.random() * 25),
          light: 55 + Math.floor(Math.random() * 30),
          temperature: 22 + Math.floor(Math.random() * 6)
        } : p.probe;
        const today = (/* @__PURE__ */ new Date()).toLocaleDateString("id-ID", { day: "numeric", month: "short" });
        const eventLabel = {
          sensor: "Sensor dipasang",
          seed: "Bibit didaftarkan",
          soil: "Media tanam dicatat",
          fertilizer: "Pupuk diterapkan",
          other: "Item ditambahkan"
        }[item.category];
        const noteText = item.category === "sensor" ? `${item.sensorId} via MQTT` : item.category === "soil" ? `${item.name} pH ${item.phLevel}` : item.category === "fertilizer" ? `${item.name} NPK ${item.npkRatio}` : item.name;
        return {
          ...p,
          probe: updatedProbe,
          scannedItems: newItems,
          timeline: [
            { date: today, event: eventLabel, note: noteText, scanCategory: item.category },
            ...p.timeline
          ]
        };
      })
    );
    const label = CATEGORY_CONFIG[item.category].label;
    toast.success(`${label} "${item.name}" ditambahkan ke ${scanningPlant.nickname}`);
    setScanningPlant(null);
  };
  return /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "min-h-screen bg-background", children: [
    /* @__PURE__ */ jsxRuntimeExports.jsx("header", { className: "sticky top-0 z-10 border-b bg-card/80 backdrop-blur px-4 py-3", children: /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "mx-auto flex max-w-2xl items-center justify-between", children: [
      /* @__PURE__ */ jsxRuntimeExports.jsxs(Link, { to: "/", className: "flex items-center gap-1 text-sm text-muted-foreground", children: [
        /* @__PURE__ */ jsxRuntimeExports.jsx(ArrowLeft, { className: "h-4 w-4" }),
        " Back"
      ] }),
      /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex items-center gap-2 font-bold", children: [
        /* @__PURE__ */ jsxRuntimeExports.jsx(Sprout, { className: "h-5 w-5 text-primary" }),
        " My Garden"
      ] }),
      /* @__PURE__ */ jsxRuntimeExports.jsxs(Badge, { variant: "outline", children: [
        plants.length,
        " Units"
      ] })
    ] }) }),
    /* @__PURE__ */ jsxRuntimeExports.jsxs("main", { className: "mx-auto max-w-2xl space-y-6 p-4", children: [
      /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex items-end justify-between", children: [
        /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { children: [
          /* @__PURE__ */ jsxRuntimeExports.jsx("h1", { className: "text-2xl font-bold", children: "Plant Collection" }),
          /* @__PURE__ */ jsxRuntimeExports.jsx("p", { className: "text-sm text-muted-foreground", children: "Live Telemetry" })
        ] }),
        /* @__PURE__ */ jsxRuntimeExports.jsxs(
          Button,
          {
            onClick: () => setShowAddForm(true),
            size: "sm",
            className: "bg-emerald-600 hover:bg-emerald-700",
            children: [
              /* @__PURE__ */ jsxRuntimeExports.jsx(Plus, { className: "mr-2 h-4 w-4" }),
              " Add Plant"
            ]
          }
        )
      ] }),
      plants.length === 0 && /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex flex-col items-center justify-center space-y-3 rounded-2xl border border-dashed py-16 text-center", children: [
        /* @__PURE__ */ jsxRuntimeExports.jsx(Sprout, { className: "h-10 w-10 text-muted-foreground/40" }),
        /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { children: [
          /* @__PURE__ */ jsxRuntimeExports.jsx("p", { className: "font-medium text-muted-foreground", children: "Belum ada tanaman" }),
          /* @__PURE__ */ jsxRuntimeExports.jsx("p", { className: "text-sm text-muted-foreground/60", children: "Add plant pertama kamu" })
        ] }),
        /* @__PURE__ */ jsxRuntimeExports.jsxs(Button, { variant: "outline", onClick: () => setShowAddForm(true), children: [
          /* @__PURE__ */ jsxRuntimeExports.jsx(Plus, { className: "mr-1.5 h-4 w-4" }),
          " Add plant"
        ] })
      ] }),
      /* @__PURE__ */ jsxRuntimeExports.jsx("div", { className: "grid grid-cols-1 gap-4 sm:grid-cols-2", children: plants.map((p) => /* @__PURE__ */ jsxRuntimeExports.jsx(
        PlantCard,
        {
          plant: p,
          onEdit: (plant) => setEditingPlant(plant),
          onDelete: (id) => {
            setPlants((prev) => prev.filter((x) => x.id !== id));
            toast.success("Plant removed");
          },
          onScan: (plant) => setScanningPlant(plant)
        },
        p.id
      )) })
    ] }),
    showAddForm && /* @__PURE__ */ jsxRuntimeExports.jsx(AddPlantModal, { onSave: handleAddPlant, onClose: () => setShowAddForm(false) }),
    editingPlant && /* @__PURE__ */ jsxRuntimeExports.jsx(
      EditPlantModal,
      {
        plant: editingPlant,
        onSave: handleEditPlant,
        onClose: () => setEditingPlant(null)
      }
    ),
    scanningPlant && /* @__PURE__ */ jsxRuntimeExports.jsx(
      OmniScannerModal,
      {
        plant: scanningPlant,
        onScanComplete: handleScanComplete,
        onClose: () => setScanningPlant(null)
      }
    )
  ] });
}
const SplitComponent = PlantGardenPage;
export {
  SplitComponent as component
};
