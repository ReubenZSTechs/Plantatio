import { useState, useEffect, useRef } from "react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { 
  Send, Bot, User, Loader2, Database, 
  Zap, BrainCircuit, Activity, BarChart 
} from "lucide-react";

interface Message {
  role: "user" | "assistant";
  content: string;
  sources?: string[]; // Untuk menunjukkan data mana yang diakses AI
}

export function InsightEngine() {
  const [messages, setMessages] = useState<Message[]>([
    {
      role: "assistant",
      content: "Plantatio Insight Engine aktif. Saya terhubung ke Live MQTT, Carbon API, dan Model Prediksi Bioma. Apa yang ingin Anda analisis hari ini?",
    }
  ]);
  const [input, setInput] = useState("");
  const [isThinking, setIsThinking] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    scrollRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isThinking]);

  const handleSendMessage = async () => {
    if (!input.trim()) return;
    
    const userMsg = input;
    setMessages(prev => [...prev, { role: "user", content: userMsg }]);
    setInput("");
    setIsThinking(true);

    // SIMULASI KOGNISI: AI memilih data source berdasarkan keyword
    setTimeout(() => {
      let response = "";
      let sources = ["Global Knowledge Base"];

      if (userMsg.toLowerCase().includes("sensor") || userMsg.toLowerCase().includes("lembab")) {
        response = "Berdasarkan telemetry MQTT 10 menit terakhir, rata-rata kelembapan di Zona A stabil pada 68%, namun Node #04 menunjukkan deviasi -5%.";
        sources = ["Live Sensor API", "MQTT Broker"];
      } else if (userMsg.toLowerCase().includes("karbon") || userMsg.toLowerCase().includes("esg")) {
        response = "Prediksi model ML menunjukkan peningkatan serapan karbon sebesar 12% untuk kuartal depan jika pola irigasi saat ini dipertahankan.";
        sources = ["ML Carbon Model v2", "Historical ESG Data"];
      } else {
        response = "Saya telah menganalisis parameter yang Anda minta. Secara keseluruhan, performa ekosistem berada dalam batas normal sesuai standar Verra.";
        sources = ["System Logs", "Compliance Engine"];
      }

      setMessages(prev => [...prev, { role: "assistant", content: response, sources }]);
      setIsThinking(false);
    }, 2000);
  };

  return (
    <div className="flex h-[calc(100vh-140px)] flex-col gap-4">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold tracking-tight">Insight Engine</h2>
          <p className="text-sm text-muted-foreground">AI-Driven Contextual Data Analysis</p>
        </div>
        <div className="flex gap-2">
           <Badge variant="outline" className="flex gap-1.5 py-1">
             <Activity className="h-3 w-3 text-emerald-500" /> Sensor Live
           </Badge>
           <Badge variant="outline" className="flex gap-1.5 py-1">
             <BrainCircuit className="h-3 w-3 text-blue-500" /> ML Model Active
           </Badge>
        </div>
      </div>

      <Card className="flex flex-1 flex-col overflow-hidden bg-card/50 backdrop-blur">
        {/* Chat Area */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6">
          {messages.map((m, i) => (
            <div key={i} className={`flex gap-4 ${m.role === "user" ? "justify-end" : "justify-start"}`}>
              <div className={`flex max-w-[80%] gap-3 ${m.role === "user" ? "flex-row-reverse" : "flex-row"}`}>
                <div className={`mt-1 flex h-8 w-8 shrink-0 items-center justify-center rounded-full border ${m.role === "assistant" ? "bg-primary/10 text-primary" : "bg-muted"}`}>
                  {m.role === "assistant" ? <Bot className="h-4 w-4" /> : <User className="h-4 w-4" />}
                </div>
                <div className="space-y-2">
                  <div className={`rounded-2xl px-4 py-2.5 text-sm shadow-sm ${m.role === "assistant" ? "bg-background border" : "bg-primary text-primary-foreground"}`}>
                    {m.content}
                  </div>
                  {m.sources && (
                    <div className="flex flex-wrap gap-2">
                      {m.sources.map(s => (
                        <div key={s} className="flex items-center gap-1 text-[10px] text-muted-foreground font-mono bg-muted/50 px-2 py-0.5 rounded">
                          <Database className="h-2.5 w-2.5" /> {s}
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            </div>
          ))}
          {isThinking && (
            <div className="flex justify-start gap-4">
              <div className="flex h-8 w-8 items-center justify-center rounded-full border bg-primary/10 text-primary">
                <Loader2 className="h-4 w-4 animate-spin" />
              </div>
              <div className="flex items-center gap-2 text-xs text-muted-foreground italic">
                Scanning system context...
              </div>
            </div>
          )}
          <div ref={scrollRef} />
        </div>

        {/* Input Area */}
        <div className="border-t bg-background/50 p-4">
          <div className="mx-auto flex max-w-3xl gap-2">
            <Input 
              placeholder="Tanyakan analisis data, audit karbon, atau status perangkat..." 
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && handleSendMessage()}
              className="bg-background"
            />
            <Button onClick={handleSendMessage} disabled={isThinking}>
              <Send className="h-4 w-4" />
            </Button>
          </div>
          <p className="mt-2 text-center text-[10px] text-muted-foreground">
            Insight Engine dapat mengakses API Verra, Data Sensor MQTT, dan Model Prediksi Keanekaragaman Hayati.
          </p>
        </div>
      </Card>
    </div>
  );
}