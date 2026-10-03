import { r as reactExports, W as jsxRuntimeExports } from "./server-BG8Cz_a2.js";
import { C as Card, B as Badge } from "./badge-Ci2zfins.js";
import { B as Button } from "./button-BpSWKw9G.js";
import { I as Input } from "./input-Dc7a9lUS.js";
import { a as api, b as ApiError } from "./api-BNzXBfwP.js";
import { c as createLucideIcon, a as cn } from "./utils-B3hKptjK.js";
import { B as Bot } from "./bot-zAHS25mR.js";
import { L as LoaderCircle } from "./loader-circle-Ba4x-1QD.js";
import { C as Camera } from "./camera-BEhya5Ry.js";
const __iconNode$2 = [
  ["ellipse", { cx: "12", cy: "5", rx: "9", ry: "3", key: "msslwz" }],
  ["path", { d: "M3 5V19A9 3 0 0 0 21 19V5", key: "1wlel7" }],
  ["path", { d: "M3 12A9 3 0 0 0 21 12", key: "mv7ke4" }]
];
const Database = createLucideIcon("database", __iconNode$2);
const __iconNode$1 = [
  [
    "path",
    {
      d: "M14.536 21.686a.5.5 0 0 0 .937-.024l6.5-19a.496.496 0 0 0-.635-.635l-19 6.5a.5.5 0 0 0-.024.937l7.93 3.18a2 2 0 0 1 1.112 1.11z",
      key: "1ffxy3"
    }
  ],
  ["path", { d: "m21.854 2.147-10.94 10.939", key: "12cjpa" }]
];
const Send = createLucideIcon("send", __iconNode$1);
const __iconNode = [
  ["path", { d: "M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2", key: "975kel" }],
  ["circle", { cx: "12", cy: "7", r: "4", key: "17ys0d" }]
];
const User = createLucideIcon("user", __iconNode);
function ChatPanel({
  scope,
  plantId,
  title,
  subtitle,
  greeting,
  suggestions = [],
  enableLeafScan = false,
  onDiagnosed,
  className
}) {
  const [messages, setMessages] = reactExports.useState([{ role: "assistant", content: greeting }]);
  const [input, setInput] = reactExports.useState("");
  const [isSending, setIsSending] = reactExports.useState(false);
  const [error, setError] = reactExports.useState(null);
  const bottomRef = reactExports.useRef(null);
  const fileInputRef = reactExports.useRef(null);
  reactExports.useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isSending]);
  const send = async (text) => {
    const trimmed = text.trim();
    if (!trimmed || isSending) return;
    const outgoing = { role: "user", content: trimmed };
    const history = [...messages, outgoing];
    setMessages(history);
    setInput("");
    setIsSending(true);
    setError(null);
    try {
      const reply = await api.chat(
        scope,
        history.map(({ role, content }) => ({ role, content })),
        plantId
      );
      setMessages((previous) => [
        ...previous,
        {
          role: "assistant",
          content: reply.text,
          tags: reply.tags,
          provenance: reply.provenance
        }
      ]);
    } catch (caught) {
      const message = caught instanceof ApiError ? caught.message : "Something went wrong reaching the assistant.";
      setError(message);
      setMessages((previous) => previous.slice(0, -1));
      setInput(trimmed);
    } finally {
      setIsSending(false);
    }
  };
  const scanLeaf = async (file) => {
    if (plantId === void 0) return;
    setMessages((previous) => [
      ...previous,
      { role: "user", content: `Uploaded a photo of ${file.name} for analysis.` }
    ]);
    setIsSending(true);
    setError(null);
    try {
      const diagnosis = await api.diagnosePlant(plantId, file);
      const ranked = diagnosis.predictions.map((p) => `${p.label} ${(p.confidence * 100).toFixed(0)}%`).join(" · ");
      setMessages((previous) => [
        ...previous,
        {
          role: "assistant",
          content: `${diagnosis.summary}

Ranked: ${ranked}`,
          tags: ["Leaf Classifier"]
        }
      ]);
      onDiagnosed?.();
    } catch (caught) {
      setError(
        caught instanceof ApiError ? caught.message : "The leaf scan could not be completed."
      );
      setMessages((previous) => previous.slice(0, -1));
    } finally {
      setIsSending(false);
    }
  };
  const handleKeyDown = (event) => {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      void send(input);
    }
  };
  return /* @__PURE__ */ jsxRuntimeExports.jsxs(Card, { className: cn("flex min-h-0 flex-col overflow-hidden", className), children: [
    /* @__PURE__ */ jsxRuntimeExports.jsxs("header", { className: "flex items-center gap-2.5 border-b bg-secondary/40 px-4 py-3", children: [
      /* @__PURE__ */ jsxRuntimeExports.jsx("span", { className: "flex h-8 w-8 items-center justify-center rounded-full bg-primary/10", children: /* @__PURE__ */ jsxRuntimeExports.jsx(Bot, { className: "h-4 w-4 text-primary", "aria-hidden": "true" }) }),
      /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "min-w-0 flex-1", children: [
        /* @__PURE__ */ jsxRuntimeExports.jsx("h2", { className: "truncate text-sm font-semibold", children: title }),
        subtitle && /* @__PURE__ */ jsxRuntimeExports.jsx("p", { className: "truncate text-xs text-muted-foreground", children: subtitle })
      ] })
    ] }),
    /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex-1 space-y-4 overflow-y-auto p-4", children: [
      messages.map((message, index) => /* @__PURE__ */ jsxRuntimeExports.jsxs(
        "article",
        {
          className: cn("flex gap-3", message.role === "user" ? "flex-row-reverse" : "flex-row"),
          children: [
            /* @__PURE__ */ jsxRuntimeExports.jsxs(
              "span",
              {
                className: cn(
                  "mt-0.5 flex h-7 w-7 shrink-0 items-center justify-center rounded-full border",
                  message.role === "assistant" ? "bg-primary/10 text-primary" : "bg-muted text-muted-foreground"
                ),
                children: [
                  message.role === "assistant" ? /* @__PURE__ */ jsxRuntimeExports.jsx(Bot, { className: "h-3.5 w-3.5", "aria-hidden": "true" }) : /* @__PURE__ */ jsxRuntimeExports.jsx(User, { className: "h-3.5 w-3.5", "aria-hidden": "true" }),
                  /* @__PURE__ */ jsxRuntimeExports.jsx("span", { className: "sr-only", children: message.role === "assistant" ? "Assistant" : "You" })
                ]
              }
            ),
            /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "min-w-0 max-w-[85%] space-y-2", children: [
              /* @__PURE__ */ jsxRuntimeExports.jsx(
                "div",
                {
                  className: cn(
                    "whitespace-pre-wrap rounded-2xl px-3.5 py-2 text-sm",
                    message.role === "assistant" ? "border bg-background" : "bg-primary text-primary-foreground"
                  ),
                  children: message.content
                }
              ),
              message.tags && message.tags.length > 0 && /* @__PURE__ */ jsxRuntimeExports.jsx("div", { className: "flex flex-wrap gap-1", children: message.tags.map((tag) => /* @__PURE__ */ jsxRuntimeExports.jsx(Badge, { variant: "outline", className: "text-[10px]", children: tag }, tag)) }),
              message.provenance && message.provenance.recordCount > 0 && /* @__PURE__ */ jsxRuntimeExports.jsxs("details", { className: "rounded-lg border bg-muted/40 px-3 py-2 text-xs", children: [
                /* @__PURE__ */ jsxRuntimeExports.jsxs("summary", { className: "cursor-pointer font-medium text-muted-foreground", children: [
                  /* @__PURE__ */ jsxRuntimeExports.jsx(Database, { className: "mr-1 inline h-3 w-3", "aria-hidden": "true" }),
                  message.provenance.recordCount,
                  " fact",
                  message.provenance.recordCount === 1 ? "" : "s",
                  " from the knowledge graph"
                ] }),
                /* @__PURE__ */ jsxRuntimeExports.jsx("ul", { className: "mt-2 space-y-1 font-mono text-[10px] text-muted-foreground", children: message.provenance.retrievedFacts.map((fact, factIndex) => /* @__PURE__ */ jsxRuntimeExports.jsx("li", { className: "whitespace-pre-wrap", children: fact }, factIndex)) })
              ] })
            ] })
          ]
        },
        index
      )),
      isSending && /* @__PURE__ */ jsxRuntimeExports.jsxs("p", { className: "flex items-center gap-2 text-xs text-muted-foreground", children: [
        /* @__PURE__ */ jsxRuntimeExports.jsx(LoaderCircle, { className: "h-3.5 w-3.5 animate-spin", "aria-hidden": "true" }),
        "Searching the knowledge graph…"
      ] }),
      /* @__PURE__ */ jsxRuntimeExports.jsx("div", { ref: bottomRef })
    ] }),
    error && /* @__PURE__ */ jsxRuntimeExports.jsx("p", { role: "alert", className: "border-t bg-destructive/10 px-4 py-2 text-xs text-destructive", children: error }),
    /* @__PURE__ */ jsxRuntimeExports.jsxs("footer", { className: "border-t p-3", children: [
      suggestions.length > 0 && messages.length <= 1 && /* @__PURE__ */ jsxRuntimeExports.jsx("div", { className: "mb-2 flex flex-wrap gap-1.5", children: suggestions.map((suggestion) => /* @__PURE__ */ jsxRuntimeExports.jsx(
        "button",
        {
          type: "button",
          onClick: () => void send(suggestion),
          className: "rounded-full border px-2.5 py-1 text-xs text-muted-foreground transition-colors hover:bg-secondary hover:text-foreground",
          children: suggestion
        },
        suggestion
      )) }),
      /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex gap-2", children: [
        enableLeafScan && plantId !== void 0 && /* @__PURE__ */ jsxRuntimeExports.jsxs(jsxRuntimeExports.Fragment, { children: [
          /* @__PURE__ */ jsxRuntimeExports.jsx(
            "input",
            {
              ref: fileInputRef,
              type: "file",
              accept: "image/*",
              capture: "environment",
              className: "hidden",
              onChange: (event) => {
                const file = event.target.files?.[0];
                if (file) void scanLeaf(file);
                event.target.value = "";
              }
            }
          ),
          /* @__PURE__ */ jsxRuntimeExports.jsx(
            Button,
            {
              variant: "outline",
              size: "icon",
              onClick: () => fileInputRef.current?.click(),
              disabled: isSending,
              "aria-label": "Scan a leaf photo",
              children: /* @__PURE__ */ jsxRuntimeExports.jsx(Camera, { className: "h-4 w-4", "aria-hidden": "true" })
            }
          )
        ] }),
        /* @__PURE__ */ jsxRuntimeExports.jsx(
          Input,
          {
            value: input,
            onChange: (event) => setInput(event.target.value),
            onKeyDown: handleKeyDown,
            disabled: isSending,
            placeholder: "Ask about your plants…",
            "aria-label": "Message the assistant"
          }
        ),
        /* @__PURE__ */ jsxRuntimeExports.jsx(
          Button,
          {
            onClick: () => void send(input),
            disabled: isSending || !input.trim(),
            size: "icon",
            "aria-label": "Send message",
            children: /* @__PURE__ */ jsxRuntimeExports.jsx(Send, { className: "h-4 w-4", "aria-hidden": "true" })
          }
        )
      ] })
    ] })
  ] });
}
export {
  ChatPanel as C
};
