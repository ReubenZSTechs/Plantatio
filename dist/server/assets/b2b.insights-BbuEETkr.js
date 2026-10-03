import { W as jsxRuntimeExports } from "./server-BG8Cz_a2.js";
import { C as ChatPanel } from "./ChatPanel-CLbb7LyA.js";
import "node:async_hooks";
import "node:stream/web";
import "node:stream";
import "./badge-Ci2zfins.js";
import "./utils-B3hKptjK.js";
import "./button-BpSWKw9G.js";
import "./index-CFniAsgI.js";
import "./input-Dc7a9lUS.js";
import "./api-BNzXBfwP.js";
import "./bot-zAHS25mR.js";
import "./loader-circle-Ba4x-1QD.js";
import "./camera-BEhya5Ry.js";
const SUGGESTIONS = [
  "Which diseases threaten tomato yield most?",
  "What conditions favour late blight?",
  "How does irrigation affect nutrient uptake?"
];
function InsightEngine() {
  return /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex h-[calc(100vh-10rem)] min-h-[480px] flex-col gap-4", children: [
    /* @__PURE__ */ jsxRuntimeExports.jsxs("header", { children: [
      /* @__PURE__ */ jsxRuntimeExports.jsx("h1", { className: "text-2xl font-semibold tracking-tight", children: "Insight Engine" }),
      /* @__PURE__ */ jsxRuntimeExports.jsx("p", { className: "text-sm text-muted-foreground", children: "Ask the knowledge graph about agronomy, disease pressure and crop conditions." })
    ] }),
    /* @__PURE__ */ jsxRuntimeExports.jsx(
      ChatPanel,
      {
        scope: "b2b",
        title: "Operations assistant",
        subtitle: "Answers cite the graph facts they came from",
        greeting: "Ask about crop conditions, disease pressure or agronomic trade-offs. Every answer links back to the facts behind it.",
        suggestions: SUGGESTIONS,
        className: "min-h-0 flex-1"
      }
    )
  ] });
}
const SplitComponent = InsightEngine;
export {
  SplitComponent as component
};
