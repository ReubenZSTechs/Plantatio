import { O as useRouter, r as reactExports, W as jsxRuntimeExports, a1 as Outlet } from "./server-BG8Cz_a2.js";
import { L as Link } from "./router-DaN2asXe.js";
import { A as AppHeader } from "./AppHeader-B5tWhkCB.js";
import { B as Button } from "./button-BpSWKw9G.js";
import { c as createLucideIcon, a as cn } from "./utils-B3hKptjK.js";
import { S as Sprout } from "./sprout-HTLAs6KQ.js";
import { X, C as Cpu } from "./x-wPsyAqoF.js";
import { T as TreeDeciduous } from "./tree-deciduous-Bf6GH39y.js";
import { B as BrainCircuit } from "./brain-circuit-6SBBv1sb.js";
import "node:async_hooks";
import "node:stream/web";
import "node:stream";
import "./sun-CswmqDAE.js";
import "./index-CFniAsgI.js";
function useRouterState(opts) {
  const contextRouter = useRouter({ warn: opts?.router === void 0 });
  const router = opts?.router || contextRouter;
  {
    const state = router.stores.__store.get();
    return opts?.select ? opts.select(state) : state;
  }
}
const __iconNode$3 = [
  ["path", { d: "M3 3v16a2 2 0 0 0 2 2h16", key: "c24i48" }],
  ["path", { d: "M18 17V9", key: "2bz60n" }],
  ["path", { d: "M13 17V5", key: "1frdt8" }],
  ["path", { d: "M8 17v-3", key: "17ska0" }]
];
const ChartColumn = createLucideIcon("chart-column", __iconNode$3);
const __iconNode$2 = [
  [
    "path",
    {
      d: "M14.106 5.553a2 2 0 0 0 1.788 0l3.659-1.83A1 1 0 0 1 21 4.619v12.764a1 1 0 0 1-.553.894l-4.553 2.277a2 2 0 0 1-1.788 0l-4.212-2.106a2 2 0 0 0-1.788 0l-3.659 1.83A1 1 0 0 1 3 19.381V6.618a1 1 0 0 1 .553-.894l4.553-2.277a2 2 0 0 1 1.788 0z",
      key: "169xi5"
    }
  ],
  ["path", { d: "M15 5.764v15", key: "1pn4in" }],
  ["path", { d: "M9 3.236v15", key: "1uimfh" }]
];
const Map = createLucideIcon("map", __iconNode$2);
const __iconNode$1 = [
  ["path", { d: "M4 5h16", key: "1tepv9" }],
  ["path", { d: "M4 12h16", key: "1lakjw" }],
  ["path", { d: "M4 19h16", key: "1djgab" }]
];
const Menu = createLucideIcon("menu", __iconNode$1);
const __iconNode = [
  [
    "path",
    {
      d: "M22 17a2 2 0 0 1-2 2H6.828a2 2 0 0 0-1.414.586l-2.202 2.202A.71.71 0 0 1 2 21.286V5a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2z",
      key: "18887p"
    }
  ],
  ["path", { d: "m10 8-3 3 3 3", key: "fp6dz7" }],
  ["path", { d: "m14 14 3-3-3-3", key: "1yrceu" }]
];
const MessageSquareCode = createLucideIcon("message-square-code", __iconNode);
const NAV = [
  { to: "/b2b/esg", label: "ESG Analytics", icon: /* @__PURE__ */ jsxRuntimeExports.jsx(ChartColumn, { className: "h-4 w-4" }) },
  { to: "/b2b/green-lands", label: "Green Lands", icon: /* @__PURE__ */ jsxRuntimeExports.jsx(TreeDeciduous, { className: "h-4 w-4" }) },
  { to: "/b2b/map", label: "Site Map", icon: /* @__PURE__ */ jsxRuntimeExports.jsx(Map, { className: "h-4 w-4" }) },
  { to: "/b2b/devices", label: "Devices", icon: /* @__PURE__ */ jsxRuntimeExports.jsx(Cpu, { className: "h-4 w-4" }) },
  { to: "/b2b/insights", label: "Insight Engine", icon: /* @__PURE__ */ jsxRuntimeExports.jsx(MessageSquareCode, { className: "h-4 w-4" }) },
  { to: "/b2b/predictions", label: "Models", icon: /* @__PURE__ */ jsxRuntimeExports.jsx(BrainCircuit, { className: "h-4 w-4" }) }
];
function B2BMainLayout() {
  const [isNavOpen, setIsNavOpen] = reactExports.useState(false);
  const pathname = useRouterState({ select: (state) => state.location.pathname });
  const current = NAV.find((item) => pathname.startsWith(item.to));
  return /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "min-h-screen bg-background", children: [
    /* @__PURE__ */ jsxRuntimeExports.jsx(
      AppHeader,
      {
        crumbs: [
          { label: "Enterprise", to: "/b2b" },
          ...current ? [{ label: current.label }] : []
        ],
        actions: /* @__PURE__ */ jsxRuntimeExports.jsx(
          Button,
          {
            variant: "ghost",
            size: "icon",
            className: "md:hidden",
            onClick: () => setIsNavOpen(true),
            "aria-label": "Open navigation",
            children: /* @__PURE__ */ jsxRuntimeExports.jsx(Menu, { className: "h-4 w-4", "aria-hidden": "true" })
          }
        )
      }
    ),
    /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "mx-auto flex max-w-7xl", children: [
      /* @__PURE__ */ jsxRuntimeExports.jsx("aside", { className: "hidden w-60 shrink-0 border-r md:block", children: /* @__PURE__ */ jsxRuntimeExports.jsx("nav", { "aria-label": "Enterprise sections", className: "sticky top-14 space-y-1 p-3", children: NAV.map((item) => /* @__PURE__ */ jsxRuntimeExports.jsx(NavLink, { item, isActive: pathname.startsWith(item.to) }, item.to)) }) }),
      isNavOpen && /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "fixed inset-0 z-50 md:hidden", children: [
        /* @__PURE__ */ jsxRuntimeExports.jsx(
          "button",
          {
            type: "button",
            className: "absolute inset-0 bg-foreground/40",
            onClick: () => setIsNavOpen(false),
            "aria-label": "Close navigation"
          }
        ),
        /* @__PURE__ */ jsxRuntimeExports.jsxs(
          "nav",
          {
            "aria-label": "Enterprise sections",
            className: "absolute inset-y-0 left-0 w-64 space-y-1 bg-background p-3 shadow-xl",
            children: [
              /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "mb-2 flex items-center justify-between px-2 py-1", children: [
                /* @__PURE__ */ jsxRuntimeExports.jsxs("span", { className: "flex items-center gap-2 font-semibold", children: [
                  /* @__PURE__ */ jsxRuntimeExports.jsx(Sprout, { className: "h-4 w-4 text-primary", "aria-hidden": "true" }),
                  "Plantatio"
                ] }),
                /* @__PURE__ */ jsxRuntimeExports.jsx(
                  Button,
                  {
                    variant: "ghost",
                    size: "icon",
                    onClick: () => setIsNavOpen(false),
                    "aria-label": "Close navigation",
                    children: /* @__PURE__ */ jsxRuntimeExports.jsx(X, { className: "h-4 w-4", "aria-hidden": "true" })
                  }
                )
              ] }),
              NAV.map((item) => /* @__PURE__ */ jsxRuntimeExports.jsx(
                NavLink,
                {
                  item,
                  isActive: pathname.startsWith(item.to),
                  onNavigate: () => setIsNavOpen(false)
                },
                item.to
              ))
            ]
          }
        )
      ] }),
      /* @__PURE__ */ jsxRuntimeExports.jsx("main", { className: "min-w-0 flex-1 p-4 sm:p-6", children: /* @__PURE__ */ jsxRuntimeExports.jsx(Outlet, {}) })
    ] })
  ] });
}
function NavLink({
  item,
  isActive,
  onNavigate
}) {
  return /* @__PURE__ */ jsxRuntimeExports.jsxs(
    Link,
    {
      to: item.to,
      onClick: onNavigate,
      "aria-current": isActive ? "page" : void 0,
      className: cn(
        "flex items-center gap-2.5 rounded-lg px-3 py-2 text-sm transition-colors",
        isActive ? "bg-secondary font-medium text-foreground" : "text-muted-foreground hover:bg-secondary/60 hover:text-foreground"
      ),
      children: [
        item.icon,
        item.label
      ]
    }
  );
}
const SplitComponent = B2BMainLayout;
export {
  SplitComponent as component
};
