import { r as reactExports, W as jsxRuntimeExports } from "./server-BG8Cz_a2.js";
import { L as Link } from "./router-DaN2asXe.js";
import { B as Button } from "./button-BpSWKw9G.js";
import { S as Sun } from "./sun-CswmqDAE.js";
import { c as createLucideIcon, a as cn } from "./utils-B3hKptjK.js";
import { S as Sprout } from "./sprout-HTLAs6KQ.js";
const __iconNode = [
  [
    "path",
    {
      d: "M20.985 12.486a9 9 0 1 1-9.473-9.472c.405-.022.617.46.402.803a6 6 0 0 0 8.268 8.268c.344-.215.825-.004.803.401",
      key: "kfwtm"
    }
  ]
];
const Moon = createLucideIcon("moon", __iconNode);
const STORAGE_KEY = "plantatio-theme";
function applyTheme(theme) {
  document.documentElement.classList.toggle("dark", theme === "dark");
}
function ThemeToggle() {
  const [theme, setTheme] = reactExports.useState("light");
  reactExports.useEffect(() => {
    let stored = null;
    try {
      stored = window.localStorage.getItem(STORAGE_KEY);
    } catch {
    }
    const initial = stored === "dark" || stored === "light" ? stored : window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
    setTheme(initial);
    applyTheme(initial);
  }, []);
  const toggle = () => {
    const next = theme === "dark" ? "light" : "dark";
    setTheme(next);
    applyTheme(next);
    try {
      window.localStorage.setItem(STORAGE_KEY, next);
    } catch {
    }
  };
  return /* @__PURE__ */ jsxRuntimeExports.jsx(
    Button,
    {
      variant: "ghost",
      size: "icon",
      onClick: toggle,
      "aria-label": `Switch to ${theme === "dark" ? "light" : "dark"} theme`,
      children: theme === "dark" ? /* @__PURE__ */ jsxRuntimeExports.jsx(Sun, { className: "h-4 w-4", "aria-hidden": "true" }) : /* @__PURE__ */ jsxRuntimeExports.jsx(Moon, { className: "h-4 w-4", "aria-hidden": "true" })
    }
  );
}
function AppHeader({ crumbs = [], actions, className }) {
  return /* @__PURE__ */ jsxRuntimeExports.jsx("header", { className: cn("sticky top-0 z-30 border-b bg-background/85 backdrop-blur", className), children: /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "mx-auto flex h-14 max-w-7xl items-center gap-3 px-4 sm:px-6", children: [
    /* @__PURE__ */ jsxRuntimeExports.jsxs(Link, { to: "/", className: "flex shrink-0 items-center gap-2 font-semibold tracking-tight", children: [
      /* @__PURE__ */ jsxRuntimeExports.jsx(Sprout, { className: "h-5 w-5 text-primary", "aria-hidden": "true" }),
      /* @__PURE__ */ jsxRuntimeExports.jsx("span", { className: "hidden sm:inline", children: "Plantatio" })
    ] }),
    crumbs.length > 0 && /* @__PURE__ */ jsxRuntimeExports.jsx("nav", { "aria-label": "Breadcrumb", className: "min-w-0 flex-1", children: /* @__PURE__ */ jsxRuntimeExports.jsx("ol", { className: "flex min-w-0 items-center gap-1.5 text-sm text-muted-foreground", children: crumbs.map((crumb, index) => /* @__PURE__ */ jsxRuntimeExports.jsxs("li", { className: "flex min-w-0 items-center gap-1.5", children: [
      index > 0 && /* @__PURE__ */ jsxRuntimeExports.jsx("span", { "aria-hidden": "true", children: "/" }),
      crumb.to ? /* @__PURE__ */ jsxRuntimeExports.jsx(
        Link,
        {
          to: crumb.to,
          className: "truncate transition-colors hover:text-foreground",
          children: crumb.label
        }
      ) : /* @__PURE__ */ jsxRuntimeExports.jsx("span", { className: "truncate text-foreground", "aria-current": "page", children: crumb.label })
    ] }, crumb.label)) }) }),
    /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "ml-auto flex items-center gap-1", children: [
      actions,
      /* @__PURE__ */ jsxRuntimeExports.jsx(ThemeToggle, {})
    ] })
  ] }) });
}
export {
  AppHeader as A
};
