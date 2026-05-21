import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { ScanLine, Check, Loader2 } from "lucide-react";

// TODO: replace with on-device barcode/QR scanner (e.g. zxing-js)
// + lookup against /api/b2c/seeds/{code} which returns context from GraphRAG.
export function BarcodeScannerMock() {
  const [stage, setStage] = useState<"idle" | "scanning" | "done">("idle");

  const start = () => {
    setStage("scanning");
    setTimeout(() => setStage("done"), 1600);
  };

  return (
    <Dialog onOpenChange={() => setStage("idle")}>
      <DialogTrigger asChild>
        <Button variant="outline" className="w-full">
          <ScanLine className="mr-2 h-4 w-4" />
          Scan seed packet
        </Button>
      </DialogTrigger>
      <DialogContent className="max-w-sm">
        <DialogHeader>
          <DialogTitle>Scan-to-Context</DialogTitle>
        </DialogHeader>
        <div className="relative aspect-[3/4] overflow-hidden rounded-xl bg-zinc-900">
          <div className="absolute inset-6 rounded-lg border-2 border-primary/70" />
          {stage === "scanning" && (
            <div className="absolute left-6 right-6 top-6 h-0.5 animate-[scan_1.6s_ease-in-out] bg-primary shadow-[0_0_12px_var(--primary)]"
              style={{ animation: "scan 1.6s ease-in-out infinite" }} />
          )}
          <div className="absolute inset-0 flex items-center justify-center text-primary-foreground/70">
            {stage === "idle" && <ScanLine className="h-12 w-12 opacity-50" />}
            {stage === "scanning" && <Loader2 className="h-10 w-10 animate-spin" />}
            {stage === "done" && <Check className="h-14 w-14 text-success" />}
          </div>
        </div>
        {stage === "done" ? (
          <div className="rounded-lg border bg-secondary/50 p-3 text-sm">
            <div className="font-semibold">Seed Detected: Monstera deliciosa</div>
            <div className="mt-1 text-xs text-muted-foreground">
              Soil profile loaded · pH 6.2 · indirect light · water every 9 days. Plan added to your dashboard.
            </div>
          </div>
        ) : (
          <Button onClick={start} disabled={stage === "scanning"} className="w-full">
            {stage === "scanning" ? "Scanning…" : "Simulate Scan"}
          </Button>
        )}
        <style>{`@keyframes scan { 0%{top:1.5rem} 50%{top:calc(100% - 1.75rem)} 100%{top:1.5rem} }`}</style>
      </DialogContent>
    </Dialog>
  );
}
