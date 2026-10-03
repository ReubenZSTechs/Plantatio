import { ChatPanel } from "./ChatPanel";

const SUGGESTIONS = [
  "Which diseases threaten tomato yield most?",
  "What conditions favour late blight?",
  "How does irrigation affect nutrient uptake?",
];

/**
 * The enterprise assistant.
 *
 * This was a `setTimeout` with keyword-matched canned replies and fabricated
 * source badges claiming live MQTT and carbon-model access. It now talks to
 * the same knowledge graph as the rest of the app, and shows the facts it
 * actually retrieved.
 */
export function InsightEngine() {
  return (
    <div className="flex h-[calc(100vh-10rem)] min-h-[480px] flex-col gap-4">
      <header>
        <h1 className="text-2xl font-semibold tracking-tight">Insight Engine</h1>
        <p className="text-sm text-muted-foreground">
          Ask the knowledge graph about agronomy, disease pressure and crop conditions.
        </p>
      </header>

      <ChatPanel
        scope="b2b"
        title="Operations assistant"
        subtitle="Answers cite the graph facts they came from"
        greeting="Ask about crop conditions, disease pressure or agronomic trade-offs. Every answer links back to the facts behind it."
        suggestions={SUGGESTIONS}
        className="min-h-0 flex-1"
      />
    </div>
  );
}
