import { r as reactExports, W as jsxRuntimeExports } from "./server-BG8Cz_a2.js";
import { C as Card, B as Badge } from "./badge-Ci2zfins.js";
import { B as Button } from "./button-BpSWKw9G.js";
import { I as Input } from "./input-Dc7a9lUS.js";
import { L as Label } from "./label-C789j1H7.js";
import { c as createLucideIcon, a as cn } from "./utils-B3hKptjK.js";
import { t as toast } from "./router-DaN2asXe.js";
import { A as API_BASE_URL } from "./api-BNzXBfwP.js";
import { P as Plus } from "./plus-I48Ihi2j.js";
import { L as LoaderCircle } from "./loader-circle-Ba4x-1QD.js";
import { C as Cpu, X } from "./x-wPsyAqoF.js";
import { C as Check } from "./check-BkbyOQtT.js";
import "node:async_hooks";
import "node:stream/web";
import "node:stream";
import "./index-CFniAsgI.js";
const __iconNode$4 = [
  ["path", { d: "M22 14v-4", key: "14q9d5" }],
  ["path", { d: "M6 14v-4", key: "14a6bd" }],
  ["rect", { x: "2", y: "6", width: "16", height: "12", rx: "2", key: "13zb55" }]
];
const BatteryLow = createLucideIcon("battery-low", __iconNode$4);
const __iconNode$3 = [
  ["path", { d: "M 22 14 L 22 10", key: "nqc4tb" }],
  ["rect", { x: "2", y: "6", width: "16", height: "12", rx: "2", key: "13zb55" }]
];
const Battery = createLucideIcon("battery", __iconNode$3);
const __iconNode$2 = [
  [
    "path",
    {
      d: "M20 10c0 4.993-5.539 10.193-7.399 11.799a1 1 0 0 1-1.202 0C9.539 20.193 4 14.993 4 10a8 8 0 0 1 16 0",
      key: "1r0f0z"
    }
  ],
  ["circle", { cx: "12", cy: "10", r: "3", key: "ilqhr7" }]
];
const MapPin = createLucideIcon("map-pin", __iconNode$2);
const __iconNode$1 = [
  ["circle", { cx: "8", cy: "21", r: "1", key: "jimo8o" }],
  ["circle", { cx: "19", cy: "21", r: "1", key: "13723u" }],
  [
    "path",
    {
      d: "M2.05 2.05h2l2.66 12.42a2 2 0 0 0 2 1.58h9.78a2 2 0 0 0 1.95-1.57l1.65-7.43H5.12",
      key: "9zh506"
    }
  ]
];
const ShoppingCart = createLucideIcon("shopping-cart", __iconNode$1);
const __iconNode = [
  [
    "path",
    {
      d: "M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.106-3.105c.32-.322.863-.22.983.218a6 6 0 0 1-8.259 7.057l-7.91 7.91a1 1 0 0 1-2.999-3l7.91-7.91a6 6 0 0 1 7.057-8.259c.438.12.54.662.219.984z",
      key: "1ngwbx"
    }
  ]
];
const Wrench = createLucideIcon("wrench", __iconNode);
const Table = reactExports.forwardRef(
  ({ className, ...props }, ref) => /* @__PURE__ */ jsxRuntimeExports.jsx("div", { className: "relative w-full overflow-auto", children: /* @__PURE__ */ jsxRuntimeExports.jsx("table", { ref, className: cn("w-full caption-bottom text-sm", className), ...props }) })
);
Table.displayName = "Table";
const TableHeader = reactExports.forwardRef(({ className, ...props }, ref) => /* @__PURE__ */ jsxRuntimeExports.jsx("thead", { ref, className: cn("[&_tr]:border-b", className), ...props }));
TableHeader.displayName = "TableHeader";
const TableBody = reactExports.forwardRef(({ className, ...props }, ref) => /* @__PURE__ */ jsxRuntimeExports.jsx("tbody", { ref, className: cn("[&_tr:last-child]:border-0", className), ...props }));
TableBody.displayName = "TableBody";
const TableFooter = reactExports.forwardRef(({ className, ...props }, ref) => /* @__PURE__ */ jsxRuntimeExports.jsx(
  "tfoot",
  {
    ref,
    className: cn("border-t bg-muted/50 font-medium [&>tr]:last:border-b-0", className),
    ...props
  }
));
TableFooter.displayName = "TableFooter";
const TableRow = reactExports.forwardRef(
  ({ className, ...props }, ref) => /* @__PURE__ */ jsxRuntimeExports.jsx(
    "tr",
    {
      ref,
      className: cn(
        "border-b transition-colors hover:bg-muted/50 data-[state=selected]:bg-muted",
        className
      ),
      ...props
    }
  )
);
TableRow.displayName = "TableRow";
const TableHead = reactExports.forwardRef(({ className, ...props }, ref) => /* @__PURE__ */ jsxRuntimeExports.jsx(
  "th",
  {
    ref,
    className: cn(
      "h-10 px-2 text-left align-middle font-medium text-muted-foreground [&:has([role=checkbox])]:pr-0 [&>[role=checkbox]]:translate-y-[2px]",
      className
    ),
    ...props
  }
));
TableHead.displayName = "TableHead";
const TableCell = reactExports.forwardRef(({ className, ...props }, ref) => /* @__PURE__ */ jsxRuntimeExports.jsx(
  "td",
  {
    ref,
    className: cn(
      "p-2 align-middle [&:has([role=checkbox])]:pr-0 [&>[role=checkbox]]:translate-y-[2px]",
      className
    ),
    ...props
  }
));
TableCell.displayName = "TableCell";
const TableCaption = reactExports.forwardRef(({ className, ...props }, ref) => /* @__PURE__ */ jsxRuntimeExports.jsx("caption", { ref, className: cn("mt-4 text-sm text-muted-foreground", className), ...props }));
TableCaption.displayName = "TableCaption";
const API_BASE = `${API_BASE_URL}/b2b`;
const statusVariant = {
  ok: "bg-emerald-500/15 text-emerald-600 border-emerald-500/30",
  warn: "bg-amber-500/15 text-amber-600 border-amber-500/30",
  critical: "bg-destructive/15 text-destructive border-destructive/30"
};
function DeviceManager() {
  const [devices, setDevices] = reactExports.useState([]);
  const [isLoading, setIsLoading] = reactExports.useState(true);
  const [showAddModal, setShowAddModal] = reactExports.useState(false);
  const [zone, setZone] = reactExports.useState("");
  const [latitude, setLatitude] = reactExports.useState("");
  const [longitude, setLongitude] = reactExports.useState("");
  const fetchDevices = () => {
    fetch(`${API_BASE}/devices`).then((res) => res.json()).then((data) => setDevices(data)).catch(() => toast.error("Could not load devices from the server.")).finally(() => setIsLoading(false));
  };
  reactExports.useEffect(() => {
    fetchDevices();
  }, []);
  const handleAddDevice = async () => {
    if (!zone || !latitude || !longitude) {
      toast.error("Zona dan titik koordinat wajib diisi");
      return;
    }
    try {
      const res = await fetch(`${API_BASE}/devices`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          zone,
          latitude: parseFloat(latitude),
          longitude: parseFloat(longitude)
        })
      });
      if (!res.ok) throw new Error();
      toast.success("Sensor registered");
      fetchDevices();
      setShowAddModal(false);
      setZone("");
      setLatitude("");
      setLongitude("");
    } catch {
      toast.error("Could not register the sensor");
    }
  };
  const handleDiagnose = async (id) => {
    await fetch(`${API_BASE}/devices/${id}/diagnose`, { method: "POST" });
    toast.info(`Ping diagnostic dikirim ke ${id}`);
  };
  const handleOrder = async () => {
    await fetch(`${API_BASE}/procurement`, { method: "POST" });
    toast.success("Cart updated · 10 probes ditambahkan");
  };
  const handleMaintenance = async () => {
    await fetch(`${API_BASE}/maintenance`, { method: "POST" });
    toast.success("Maintenance ticket #M-2419 created");
  };
  const handleGetLocation = () => {
    if ("geolocation" in navigator) {
      toast.info("Mencari sinyal GPS...");
      navigator.geolocation.getCurrentPosition(
        (position) => {
          setLatitude(position.coords.latitude.toFixed(6));
          setLongitude(position.coords.longitude.toFixed(6));
          toast.success("Koordinat didapatkan");
        },
        () => toast.error("Could not read GPS location. Check that location access is allowed.")
      );
    } else {
      toast.error("Browser Anda tidak mendukung GPS.");
    }
  };
  return /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "space-y-6 p-4 md:p-8 max-w-5xl mx-auto", children: [
    /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex flex-col sm:flex-row sm:items-end justify-between gap-4", children: [
      /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { children: [
        /* @__PURE__ */ jsxRuntimeExports.jsx("h1", { className: "text-2xl font-semibold tracking-tight", children: "Device Manager" }),
        /* @__PURE__ */ jsxRuntimeExports.jsx("p", { className: "text-sm text-muted-foreground", children: "Field sensor management, baterai, dan pengadaan barang." })
      ] }),
      /* @__PURE__ */ jsxRuntimeExports.jsxs(Button, { className: "bg-primary", onClick: () => setShowAddModal(true), children: [
        /* @__PURE__ */ jsxRuntimeExports.jsx(Plus, { className: "mr-2 h-4 w-4" }),
        " Register sensor"
      ] })
    ] }),
    /* @__PURE__ */ jsxRuntimeExports.jsx(Card, { className: "overflow-hidden", children: isLoading ? /* @__PURE__ */ jsxRuntimeExports.jsx("div", { className: "flex justify-center p-8", children: /* @__PURE__ */ jsxRuntimeExports.jsx(LoaderCircle, { className: "h-6 w-6 animate-spin text-primary" }) }) : /* @__PURE__ */ jsxRuntimeExports.jsx("div", { className: "overflow-x-auto", children: /* @__PURE__ */ jsxRuntimeExports.jsxs(Table, { children: [
      /* @__PURE__ */ jsxRuntimeExports.jsx(TableHeader, { children: /* @__PURE__ */ jsxRuntimeExports.jsxs(TableRow, { children: [
        /* @__PURE__ */ jsxRuntimeExports.jsx(TableHead, { children: "Node ID" }),
        /* @__PURE__ */ jsxRuntimeExports.jsx(TableHead, { children: "Zone & Koordinat" }),
        /* @__PURE__ */ jsxRuntimeExports.jsx(TableHead, { children: "Battery" }),
        /* @__PURE__ */ jsxRuntimeExports.jsx(TableHead, { children: "Moisture" }),
        /* @__PURE__ */ jsxRuntimeExports.jsx(TableHead, { children: "Status" }),
        /* @__PURE__ */ jsxRuntimeExports.jsx(TableHead, { className: "text-right", children: "Action" })
      ] }) }),
      /* @__PURE__ */ jsxRuntimeExports.jsx(TableBody, { children: devices.length === 0 ? /* @__PURE__ */ jsxRuntimeExports.jsx(TableRow, { children: /* @__PURE__ */ jsxRuntimeExports.jsx(TableCell, { colSpan: 6, className: "text-center py-6 text-muted-foreground", children: "Belum ada sensor terdaftar" }) }) : devices.map((n) => /* @__PURE__ */ jsxRuntimeExports.jsxs(TableRow, { children: [
        /* @__PURE__ */ jsxRuntimeExports.jsx(TableCell, { className: "font-mono text-xs font-bold text-primary/80", children: n.id }),
        /* @__PURE__ */ jsxRuntimeExports.jsxs(TableCell, { children: [
          /* @__PURE__ */ jsxRuntimeExports.jsx("p", { className: "font-medium", children: n.zone }),
          /* @__PURE__ */ jsxRuntimeExports.jsxs("p", { className: "text-[10px] text-muted-foreground flex items-center gap-1 mt-0.5", children: [
            /* @__PURE__ */ jsxRuntimeExports.jsx(MapPin, { className: "h-3 w-3" }),
            " ",
            n.latitude,
            ", ",
            n.longitude
          ] })
        ] }),
        /* @__PURE__ */ jsxRuntimeExports.jsx(TableCell, { children: /* @__PURE__ */ jsxRuntimeExports.jsxs("span", { className: "flex items-center gap-1.5 font-medium", children: [
          n.battery < 20 ? /* @__PURE__ */ jsxRuntimeExports.jsx(BatteryLow, { className: "h-4 w-4 text-destructive animate-pulse" }) : /* @__PURE__ */ jsxRuntimeExports.jsx(Battery, { className: "h-4 w-4 text-emerald-500" }),
          n.battery,
          "%"
        ] }) }),
        /* @__PURE__ */ jsxRuntimeExports.jsxs(TableCell, { children: [
          n.moisture,
          "%"
        ] }),
        /* @__PURE__ */ jsxRuntimeExports.jsx(TableCell, { children: /* @__PURE__ */ jsxRuntimeExports.jsx(Badge, { variant: "outline", className: statusVariant[n.status], children: n.status.toUpperCase() }) }),
        /* @__PURE__ */ jsxRuntimeExports.jsx(TableCell, { className: "text-right", children: /* @__PURE__ */ jsxRuntimeExports.jsx(Button, { size: "sm", variant: "ghost", onClick: () => handleDiagnose(n.id), children: "Diagnose" }) })
      ] }, n.id)) })
    ] }) }) }),
    /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { children: [
      /* @__PURE__ */ jsxRuntimeExports.jsx("h2", { className: "mb-3 text-lg font-semibold", children: "Procurement & Maintenance" }),
      /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "grid gap-4 md:grid-cols-2", children: [
        /* @__PURE__ */ jsxRuntimeExports.jsxs(Card, { className: "p-5 flex flex-col justify-between", children: [
          /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { children: [
            /* @__PURE__ */ jsxRuntimeExports.jsx(Cpu, { className: "mb-3 h-6 w-6 text-primary" }),
            /* @__PURE__ */ jsxRuntimeExports.jsx("div", { className: "font-semibold", children: "Order Smart Probes" }),
            /* @__PURE__ */ jsxRuntimeExports.jsx("p", { className: "mt-1 text-sm text-muted-foreground", children: "Plantatio Probe v3 — soil moisture, NPK, temperature, LoRa mesh." })
          ] }),
          /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "mt-4 flex items-center justify-between border-t pt-4", children: [
            /* @__PURE__ */ jsxRuntimeExports.jsx("span", { className: "text-sm font-medium", children: "€89 / unit · MOQ 10" }),
            /* @__PURE__ */ jsxRuntimeExports.jsxs(Button, { size: "sm", onClick: handleOrder, children: [
              /* @__PURE__ */ jsxRuntimeExports.jsx(ShoppingCart, { className: "mr-2 h-4 w-4" }),
              " Add to order"
            ] })
          ] })
        ] }),
        /* @__PURE__ */ jsxRuntimeExports.jsxs(Card, { className: "p-5 flex flex-col justify-between", children: [
          /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { children: [
            /* @__PURE__ */ jsxRuntimeExports.jsx(Wrench, { className: "mb-3 h-6 w-6 text-amber-500" }),
            /* @__PURE__ */ jsxRuntimeExports.jsx("div", { className: "font-semibold", children: "Request On-Site Maintenance" }),
            /* @__PURE__ */ jsxRuntimeExports.jsx("p", { className: "mt-1 text-sm text-muted-foreground", children: "Dispatch a certified field technician for failing nodes." })
          ] }),
          /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "mt-4 flex items-center justify-between border-t pt-4", children: [
            /* @__PURE__ */ jsxRuntimeExports.jsx("span", { className: "text-sm font-medium text-amber-600", children: "2 critical nodes flagged" }),
            /* @__PURE__ */ jsxRuntimeExports.jsxs(
              Button,
              {
                size: "sm",
                variant: "outline",
                className: "border-amber-200 text-amber-700 hover:bg-amber-50",
                onClick: handleMaintenance,
                children: [
                  /* @__PURE__ */ jsxRuntimeExports.jsx(Wrench, { className: "mr-2 h-4 w-4" }),
                  " Dispatch"
                ]
              }
            )
          ] })
        ] })
      ] })
    ] }),
    showAddModal && /* @__PURE__ */ jsxRuntimeExports.jsx("div", { className: "fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4", children: /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "w-full max-w-sm rounded-2xl bg-background shadow-2xl", children: [
      /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex items-center justify-between border-b px-5 py-4", children: [
        /* @__PURE__ */ jsxRuntimeExports.jsx("h2", { className: "font-semibold", children: "Register Node Sensor" }),
        /* @__PURE__ */ jsxRuntimeExports.jsx(
          Button,
          {
            size: "icon",
            variant: "ghost",
            className: "h-7 w-7",
            onClick: () => setShowAddModal(false),
            children: /* @__PURE__ */ jsxRuntimeExports.jsx(X, { className: "h-4 w-4" })
          }
        )
      ] }),
      /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "p-5 space-y-4", children: [
        /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "space-y-1.5", children: [
          /* @__PURE__ */ jsxRuntimeExports.jsx(Label, { children: "Nama Zona / Penempatan" }),
          /* @__PURE__ */ jsxRuntimeExports.jsx(
            Input,
            {
              placeholder: "e.g. West Sector C",
              value: zone,
              onChange: (e) => setZone(e.target.value)
            }
          )
        ] }),
        /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "grid grid-cols-2 gap-3", children: [
          /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "space-y-1.5", children: [
            /* @__PURE__ */ jsxRuntimeExports.jsx(Label, { children: "Latitude" }),
            /* @__PURE__ */ jsxRuntimeExports.jsx(
              Input,
              {
                type: "number",
                placeholder: "-6.200",
                value: latitude,
                onChange: (e) => setLatitude(e.target.value)
              }
            )
          ] }),
          /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "space-y-1.5", children: [
            /* @__PURE__ */ jsxRuntimeExports.jsx(Label, { children: "Longitude" }),
            /* @__PURE__ */ jsxRuntimeExports.jsx(
              Input,
              {
                type: "number",
                placeholder: "106.816",
                value: longitude,
                onChange: (e) => setLongitude(e.target.value)
              }
            )
          ] })
        ] }),
        /* @__PURE__ */ jsxRuntimeExports.jsxs(
          Button,
          {
            type: "button",
            variant: "secondary",
            className: "w-full gap-2 text-xs h-8 bg-blue-50 text-blue-600 hover:bg-blue-100 dark:bg-blue-900/30 dark:text-blue-400",
            onClick: handleGetLocation,
            children: [
              /* @__PURE__ */ jsxRuntimeExports.jsx(MapPin, { className: "h-3.5 w-3.5" }),
              " Gunakan GPS Saat Ini"
            ]
          }
        )
      ] }),
      /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex gap-2 border-t px-5 py-4", children: [
        /* @__PURE__ */ jsxRuntimeExports.jsx(Button, { variant: "outline", className: "flex-1", onClick: () => setShowAddModal(false), children: "Cancel" }),
        /* @__PURE__ */ jsxRuntimeExports.jsxs(Button, { className: "flex-1", onClick: handleAddDevice, children: [
          /* @__PURE__ */ jsxRuntimeExports.jsx(Check, { className: "mr-2 h-4 w-4" }),
          " Save Node"
        ] })
      ] })
    ] }) })
  ] });
}
const SplitComponent = DeviceManager;
export {
  SplitComponent as component
};
