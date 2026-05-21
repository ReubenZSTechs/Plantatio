import { useState } from "react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Camera, Send, Sparkles } from "lucide-react"; 
import { chatHistory } from "@/data/mockData";

export function CognitiveAssistant() {
  const [messages, setMessages] = useState(chatHistory);
  const [input, setInput] = useState("");
  const [thinking, setThinking] = useState(false);

  // Ubah fungsi send menjadi asynchronous
  const send = async (text: string) => {
    if (!text.trim()) return;
    
    // 1. Tambahkan pesan user ke UI
    setMessages((m) => [...m, { role: "user", text }]);
    setInput("");
    setThinking(true);

    try {
      // 2. Kirim request ke FastAPI Backend
      // Pastikan URL sesuai dengan port uvicorn Anda (biasanya 8000)
      const response = await fetch("http://localhost:8000/api/b2c/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ text: text }),
      });

      if (!response.ok) {
        throw new Error("Gagal mengambil respon dari server");
      }

      // 3. Ambil hasil JSON dari backend
      const data = await response.json();

      // 4. Masukkan pesan dari backend (assistant) ke UI
      setMessages((m) => [...m, data]);
      
    } catch (error) {
      console.error("Error fetching chat:", error);
      // Tampilkan pesan error jika server mati
      setMessages((m) => [
        ...m,
        {
          role: "assistant",
          text: "Maaf, server backend tidak dapat dihubungi saat ini.",
          tags: ["Error"],
        },
      ]);
    } finally {
      // 5. Matikan status loading
      setThinking(false);
    }
  };

  return (
    <Card className="flex h-[560px] flex-col overflow-hidden">
      <div className="flex items-center gap-2 border-b bg-secondary/50 px-4 py-3">
        <Sparkles className="h-4 w-4 text-primary" />
        <div className="text-sm font-semibold">Cognitive Assistant</div>
        <Badge variant="secondary" className="ml-auto text-xs">beta</Badge>
      </div>
      <div className="flex-1 space-y-3 overflow-y-auto p-4">
        {messages.map((m, i) => (
          <div
            key={i}
            className={`max-w-[85%] rounded-2xl px-3 py-2 text-sm ${
              m.role === "assistant"
                ? "bg-secondary text-secondary-foreground"
                : "ml-auto bg-primary text-primary-foreground"
            }`}
          >
            <div>{m.text}</div>
            {m.tags && (
              <div className="mt-2 flex flex-wrap gap-1">
                {m.tags.map((t) => (
                  <Badge key={t} variant="outline" className="text-[10px]">
                    {t}
                  </Badge>
                ))}
              </div>
            )}
          </div>
        ))}
        {thinking && (
          <div className="text-xs text-muted-foreground">Diagnosing image…</div>
        )}
      </div>
      <div className="border-t p-3">
        <div className="flex gap-2">
          <Button
            variant="outline"
            size="icon"
            onClick={() => send("📷 [Photo captured] Please analyze these leaves.")}
            title="Take a photo"
          >
            <Camera className="h-4 w-4" />
          </Button>
          <Input
            placeholder="Ask about your plant…"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && send(input)}
          />
          <Button onClick={() => send(input)} size="icon">
            <Send className="h-4 w-4" />
          </Button>
        </div>
      </div>
    </Card>
  );
}