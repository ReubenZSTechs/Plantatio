import { useState } from "react";
import {
  ArrowDownRight,
  ArrowUpRight,
  Camera,
  Leaf,
  Loader2,
  ScanSearch,
  ShieldCheck,
  TreePine,
  Upload,
} from "lucide-react";
import { toast } from "sonner";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Label } from "@/components/ui/label";
import { Progress } from "@/components/ui/progress";
import { api, ApiError } from "@/lib/api";
import { cn } from "@/lib/utils";
import type { SatelliteAnalysis } from "@/types/plant";

const DEMO_IMAGES = {
  baseline: { src: "/demo/restoration-1986.jpg", name: "restoration-1986.jpg" },
  current: { src: "/demo/restoration-2019.jpg", name: "restoration-2019.jpg" },
};

/** Fetch a bundled demo image as a File so it can be posted like an upload. */
async function demoFile(src: string, name: string): Promise<File> {
  const response = await fetch(src);
  const blob = await response.blob();
  return new File([blob], name, { type: blob.type || "image/jpeg" });
}

function formatRatio(value: number | null): string {
  return value === null ? "—" : `${(value * 100).toFixed(0)}%`;
}

/**
 * Satellite restoration audit: score a baseline and a current image of the
 * same site, and report the change between them.
 */
export function ESGAnalyticsDashboard() {
  const [baseline, setBaseline] = useState<File | null>(null);
  const [current, setCurrent] = useState<File | null>(null);
  const [baselinePreview, setBaselinePreview] = useState("");
  const [currentPreview, setCurrentPreview] = useState("");
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysis, setAnalysis] = useState<SatelliteAnalysis | null>(null);
  const [error, setError] = useState<string | null>(null);

  const pick = (file: File, slot: "baseline" | "current") => {
    const reader = new FileReader();
    reader.onloadend = () => {
      if (slot === "baseline") {
        setBaseline(file);
        setBaselinePreview(reader.result as string);
      } else {
        setCurrent(file);
        setCurrentPreview(reader.result as string);
      }
    };
    reader.readAsDataURL(file);
  };

  const loadDemo = async () => {
    try {
      const [before, after] = await Promise.all([
        demoFile(DEMO_IMAGES.baseline.src, DEMO_IMAGES.baseline.name),
        demoFile(DEMO_IMAGES.current.src, DEMO_IMAGES.current.name),
      ]);
      pick(before, "baseline");
      pick(after, "current");
      toast.success("Loaded the 1986 / 2019 demo pair");
    } catch {
      toast.error("Could not load the demo images");
    }
  };

  const analyze = async () => {
    if (!baseline || !current) {
      toast.error("Upload both the baseline and the current image");
      return;
    }

    setIsAnalyzing(true);
    setError(null);

    try {
      setAnalysis(await api.analyzeSatellite(baseline, current));
      toast.success("Comparison complete");
    } catch (caught) {
      const message = caught instanceof ApiError ? caught.message : "Satellite analysis failed";
      setError(message);
      toast.error(message);
    } finally {
      setIsAnalyzing(false);
    }
  };

  const labels = analysis?.labels;
  const delta = labels?.restorationDelta ?? null;

  return (
    <div className="space-y-6">
      <header>
        <h1 className="text-2xl font-semibold tracking-tight">ESG Analytics</h1>
        <p className="text-sm text-muted-foreground">
          Compare two satellite images of a site and quantify the change in vegetation, biomass and
          carbon.
        </p>
      </header>

      <Card className="space-y-4 p-5">
        <div className="grid gap-4 sm:grid-cols-2">
          <ImageSlot
            id="baseline-image"
            label="Baseline image"
            hint="Earlier state of the site"
            icon={<Camera className="h-5 w-5 opacity-60" aria-hidden="true" />}
            preview={baselinePreview}
            onPick={(file) => pick(file, "baseline")}
          />
          <ImageSlot
            id="current-image"
            label="Current image"
            hint="Most recent capture"
            icon={<Upload className="h-5 w-5 opacity-60" aria-hidden="true" />}
            preview={currentPreview}
            onPick={(file) => pick(file, "current")}
          />
        </div>

        <div className="flex flex-col gap-2 sm:flex-row">
          <Button
            onClick={() => void analyze()}
            disabled={isAnalyzing || !baseline || !current}
            className="flex-1"
          >
            {isAnalyzing ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" aria-hidden="true" />
                Analysing imagery…
              </>
            ) : (
              "Run satellite audit"
            )}
          </Button>
          <Button variant="outline" onClick={() => void loadDemo()} disabled={isAnalyzing}>
            Load demo pair
          </Button>
        </div>

        <p className="text-xs text-muted-foreground">
          The demo pair is Landsat imagery of the same terrain in 1986 and 2019, via Google Earth
          Timelapse. The frames are not co-registered, so the comparison is indicative rather than a
          pixel-level difference.
        </p>
      </Card>

      {error && (
        <Card role="alert" className="border-destructive/40 bg-destructive/5 p-4">
          <p className="text-sm text-destructive">{error}</p>
        </Card>
      )}

      {labels && (
        <Card className="overflow-hidden p-0">
          <header className="flex flex-wrap items-center justify-between gap-2 border-b bg-muted/40 px-5 py-4">
            <div className="flex min-w-0 items-center gap-3">
              <ScanSearch className="h-5 w-5 shrink-0 text-primary" aria-hidden="true" />
              <div className="min-w-0">
                <h2 className="text-sm font-semibold">Analysis result</h2>
                <p className="truncate font-mono text-[11px] text-muted-foreground">
                  {analysis.imagePath}
                </p>
              </div>
            </div>
            {labels.confidence !== null && (
              <Badge variant="secondary" className="gap-1">
                <ShieldCheck className="h-3 w-3" aria-hidden="true" />
                {formatRatio(labels.confidence)} confidence
              </Badge>
            )}
          </header>

          <div className="grid gap-4 border-b p-4 sm:grid-cols-2">
            <Fact label="Vegetation density" value={labels.vegetationDensity ?? "—"} />
            <Fact label="Restoration quality" value={labels.restorationQuality ?? "—"} />
          </div>

          <div className="grid divide-y sm:grid-cols-3 sm:divide-x sm:divide-y-0">
            <Metric
              icon={<Leaf className="h-3.5 w-3.5" aria-hidden="true" />}
              label="Canopy cover"
              value={labels.canopyCover}
              change={delta?.canopyCoverChange ?? null}
            />
            <Metric
              icon={<TreePine className="h-3.5 w-3.5" aria-hidden="true" />}
              label="Est. biomass"
              value={labels.estBiomass}
              change={delta?.biomassChange ?? null}
            />
            <Metric
              icon={<ShieldCheck className="h-3.5 w-3.5" aria-hidden="true" />}
              label="Carbon equivalent"
              value={labels.carbonEq}
              change={delta?.carbonChange ?? null}
            />
          </div>
        </Card>
      )}
    </div>
  );
}

function ImageSlot({
  id,
  label,
  hint,
  icon,
  preview,
  onPick,
}: {
  id: string;
  label: string;
  hint: string;
  icon: React.ReactNode;
  preview: string;
  onPick: (file: File) => void;
}) {
  return (
    <div className="space-y-1.5">
      <Label htmlFor={id} className="text-xs font-semibold">
        {label}
      </Label>
      <input
        id={id}
        type="file"
        accept="image/*"
        className="sr-only"
        onChange={(event) => {
          const file = event.target.files?.[0];
          if (file) onPick(file);
        }}
      />
      <Label
        htmlFor={id}
        className="relative flex aspect-video cursor-pointer flex-col items-center justify-center overflow-hidden rounded-xl border-2 border-dashed bg-muted/40 transition-colors hover:border-primary/40"
      >
        {preview ? (
          <img src={preview} alt={label} className="h-full w-full object-cover" />
        ) : (
          <span className="space-y-1 p-4 text-center text-xs text-muted-foreground">
            {icon}
            <span className="block">{hint}</span>
          </span>
        )}
      </Label>
    </div>
  );
}

function Fact({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-xl border bg-background p-3">
      <p className="text-[11px] font-semibold uppercase tracking-wide text-muted-foreground">
        {label}
      </p>
      <p className="mt-0.5 text-lg font-semibold capitalize text-primary">{value}</p>
    </div>
  );
}

/**
 * One metric with its change against the baseline.
 *
 * The change was computed server-side but dropped by the response model, so
 * the before/after comparison never reached this view.
 */
function Metric({
  icon,
  label,
  value,
  change,
}: {
  icon: React.ReactNode;
  label: string;
  value: number | null;
  change: number | null;
}) {
  const improved = change !== null && change > 0;

  return (
    <div className="space-y-1 p-4">
      <p className="flex items-center gap-1 text-[11px] font-semibold uppercase tracking-wide text-muted-foreground">
        {icon}
        {label}
      </p>
      <p className="text-xl font-semibold tabular-nums">{formatRatio(value)}</p>
      <Progress value={(value ?? 0) * 100} className="h-1" />

      {change !== null && (
        <p
          className={cn(
            "flex items-center gap-1 text-xs font-medium",
            improved ? "text-success" : "text-destructive",
          )}
        >
          {improved ? (
            <ArrowUpRight className="h-3 w-3" aria-hidden="true" />
          ) : (
            <ArrowDownRight className="h-3 w-3" aria-hidden="true" />
          )}
          {change > 0 ? "+" : ""}
          {(change * 100).toFixed(1)} pts vs baseline
        </p>
      )}
    </div>
  );
}
