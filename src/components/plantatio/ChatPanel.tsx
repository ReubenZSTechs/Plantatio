import { useEffect, useRef, useState, type KeyboardEvent } from "react";
import { Bot, Camera, Database, Loader2, Send, User } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { api, ApiError } from "@/lib/api";
import { cn } from "@/lib/utils";
import type { ChatMessage, ChatReply, GraphProvenance } from "@/types/plant";

interface ChatTurn extends ChatMessage {
  tags?: string[];
  provenance?: GraphProvenance;
}

interface ChatPanelProps {
  /** Which backend conversation this panel belongs to. */
  scope: "b2c" | "b2b" | "plant";
  /** Required when scope is "plant". */
  plantId?: number;
  title: string;
  subtitle?: string;
  greeting: string;
  suggestions?: string[];
  /** Show the leaf-scan button, which posts an image to the classifier. */
  enableLeafScan?: boolean;
  onDiagnosed?: () => void;
  className?: string;
}

/**
 * The assistant surface, shared by every part of the app.
 *
 * Replaces three divergent implementations: one that sent the wrong request
 * shape, one that worked, and one that was a setTimeout with canned replies.
 */
export function ChatPanel({
  scope,
  plantId,
  title,
  subtitle,
  greeting,
  suggestions = [],
  enableLeafScan = false,
  onDiagnosed,
  className,
}: ChatPanelProps) {
  const [messages, setMessages] = useState<ChatTurn[]>([{ role: "assistant", content: greeting }]);
  const [input, setInput] = useState("");
  const [isSending, setIsSending] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const bottomRef = useRef<HTMLDivElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isSending]);

  const send = async (text: string) => {
    const trimmed = text.trim();
    if (!trimmed || isSending) return;

    const outgoing: ChatTurn = { role: "user", content: trimmed };
    const history = [...messages, outgoing];

    setMessages(history);
    setInput("");
    setIsSending(true);
    setError(null);

    try {
      const reply: ChatReply = await api.chat(
        scope,
        history.map(({ role, content }) => ({ role, content })),
        plantId,
      );

      setMessages((previous) => [
        ...previous,
        {
          role: "assistant",
          content: reply.text,
          tags: reply.tags,
          provenance: reply.provenance,
        },
      ]);
    } catch (caught) {
      const message =
        caught instanceof ApiError
          ? caught.message
          : "Something went wrong reaching the assistant.";

      setError(message);
      // Put the question back so it is not lost.
      setMessages((previous) => previous.slice(0, -1));
      setInput(trimmed);
    } finally {
      setIsSending(false);
    }
  };

  const scanLeaf = async (file: File) => {
    if (plantId === undefined) return;

    setMessages((previous) => [
      ...previous,
      { role: "user", content: `Uploaded a photo of ${file.name} for analysis.` },
    ]);
    setIsSending(true);
    setError(null);

    try {
      const diagnosis = await api.diagnosePlant(plantId, file);
      const ranked = diagnosis.predictions
        .map((p) => `${p.label} ${(p.confidence * 100).toFixed(0)}%`)
        .join(" · ");

      setMessages((previous) => [
        ...previous,
        {
          role: "assistant",
          content: `${diagnosis.summary}\n\nRanked: ${ranked}`,
          tags: ["Leaf Classifier"],
        },
      ]);
      onDiagnosed?.();
    } catch (caught) {
      setError(
        caught instanceof ApiError ? caught.message : "The leaf scan could not be completed.",
      );
      setMessages((previous) => previous.slice(0, -1));
    } finally {
      setIsSending(false);
    }
  };

  const handleKeyDown = (event: KeyboardEvent<HTMLInputElement>) => {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      void send(input);
    }
  };

  return (
    <Card className={cn("flex min-h-0 flex-col overflow-hidden", className)}>
      <header className="flex items-center gap-2.5 border-b bg-secondary/40 px-4 py-3">
        <span className="flex h-8 w-8 items-center justify-center rounded-full bg-primary/10">
          <Bot className="h-4 w-4 text-primary" aria-hidden="true" />
        </span>
        <div className="min-w-0 flex-1">
          <h2 className="truncate text-sm font-semibold">{title}</h2>
          {subtitle && <p className="truncate text-xs text-muted-foreground">{subtitle}</p>}
        </div>
      </header>

      <div className="flex-1 space-y-4 overflow-y-auto p-4">
        {messages.map((message, index) => (
          <article
            key={index}
            className={cn("flex gap-3", message.role === "user" ? "flex-row-reverse" : "flex-row")}
          >
            <span
              className={cn(
                "mt-0.5 flex h-7 w-7 shrink-0 items-center justify-center rounded-full border",
                message.role === "assistant"
                  ? "bg-primary/10 text-primary"
                  : "bg-muted text-muted-foreground",
              )}
            >
              {message.role === "assistant" ? (
                <Bot className="h-3.5 w-3.5" aria-hidden="true" />
              ) : (
                <User className="h-3.5 w-3.5" aria-hidden="true" />
              )}
              <span className="sr-only">{message.role === "assistant" ? "Assistant" : "You"}</span>
            </span>

            <div className="min-w-0 max-w-[85%] space-y-2">
              <div
                className={cn(
                  "whitespace-pre-wrap rounded-2xl px-3.5 py-2 text-sm",
                  message.role === "assistant"
                    ? "border bg-background"
                    : "bg-primary text-primary-foreground",
                )}
              >
                {message.content}
              </div>

              {message.tags && message.tags.length > 0 && (
                <div className="flex flex-wrap gap-1">
                  {message.tags.map((tag) => (
                    <Badge key={tag} variant="outline" className="text-[10px]">
                      {tag}
                    </Badge>
                  ))}
                </div>
              )}

              {message.provenance && message.provenance.recordCount > 0 && (
                <details className="rounded-lg border bg-muted/40 px-3 py-2 text-xs">
                  <summary className="cursor-pointer font-medium text-muted-foreground">
                    <Database className="mr-1 inline h-3 w-3" aria-hidden="true" />
                    {message.provenance.recordCount} fact
                    {message.provenance.recordCount === 1 ? "" : "s"} from the knowledge graph
                  </summary>
                  <ul className="mt-2 space-y-1 font-mono text-[10px] text-muted-foreground">
                    {message.provenance.retrievedFacts.map((fact, factIndex) => (
                      <li key={factIndex} className="whitespace-pre-wrap">
                        {fact}
                      </li>
                    ))}
                  </ul>
                </details>
              )}
            </div>
          </article>
        ))}

        {isSending && (
          <p className="flex items-center gap-2 text-xs text-muted-foreground">
            <Loader2 className="h-3.5 w-3.5 animate-spin" aria-hidden="true" />
            Searching the knowledge graph…
          </p>
        )}

        <div ref={bottomRef} />
      </div>

      {error && (
        <p role="alert" className="border-t bg-destructive/10 px-4 py-2 text-xs text-destructive">
          {error}
        </p>
      )}

      <footer className="border-t p-3">
        {suggestions.length > 0 && messages.length <= 1 && (
          <div className="mb-2 flex flex-wrap gap-1.5">
            {suggestions.map((suggestion) => (
              <button
                key={suggestion}
                type="button"
                onClick={() => void send(suggestion)}
                className="rounded-full border px-2.5 py-1 text-xs text-muted-foreground transition-colors hover:bg-secondary hover:text-foreground"
              >
                {suggestion}
              </button>
            ))}
          </div>
        )}

        <div className="flex gap-2">
          {enableLeafScan && plantId !== undefined && (
            <>
              <input
                ref={fileInputRef}
                type="file"
                accept="image/*"
                capture="environment"
                className="hidden"
                onChange={(event) => {
                  const file = event.target.files?.[0];
                  if (file) void scanLeaf(file);
                  event.target.value = "";
                }}
              />
              <Button
                variant="outline"
                size="icon"
                onClick={() => fileInputRef.current?.click()}
                disabled={isSending}
                aria-label="Scan a leaf photo"
              >
                <Camera className="h-4 w-4" aria-hidden="true" />
              </Button>
            </>
          )}

          <Input
            value={input}
            onChange={(event) => setInput(event.target.value)}
            onKeyDown={handleKeyDown}
            disabled={isSending}
            placeholder="Ask about your plants…"
            aria-label="Message the assistant"
          />

          <Button
            onClick={() => void send(input)}
            disabled={isSending || !input.trim()}
            size="icon"
            aria-label="Send message"
          >
            <Send className="h-4 w-4" aria-hidden="true" />
          </Button>
        </div>
      </footer>
    </Card>
  );
}
