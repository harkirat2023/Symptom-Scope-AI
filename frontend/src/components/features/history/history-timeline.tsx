"use client";

import { useState, useMemo } from "react";
import { Search, Calendar, AlertTriangle } from "lucide-react";
import { motion } from "framer-motion";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { cn } from "@/lib/utils";
import { severityColorMap } from "@/components/shared/severity-badge";
import type { PredictionRecord, AnalyticsResponse } from "@/lib/api/predictions";

interface HistoryTimelineProps {
  predictions: PredictionRecord[];
  analytics: AnalyticsResponse | undefined;
  gridColor: string;
  textColor: string;
}

export function HistoryTimeline({ predictions, analytics, gridColor, textColor }: HistoryTimelineProps) {
  const [search, setSearch] = useState("");
  const [activeTab, setActiveTab] = useState("timeline");

  const filteredPredictions = predictions.filter(
    (p) =>
      !search ||
      p.prediction.toLowerCase().includes(search.toLowerCase()) ||
      p.symptoms.join(" ").toLowerCase().includes(search.toLowerCase())
  );

  const { severityCounts, conditionCounts, symptomClusters } = useMemo(() => {
    const sev: Record<string, number> = {};
    const cond: Record<string, number> = {};
    const symp: Record<string, number> = {};
    for (const p of predictions) {
      sev[p.severity] = (sev[p.severity] ?? 0) + 1;
      cond[p.prediction] = (cond[p.prediction] ?? 0) + 1;
      for (const s of p.symptoms) {
        symp[s] = (symp[s] ?? 0) + 1;
      }
    }
    return {
      severityCounts: Object.entries(sev).map(([name, value]) => ({ name, value })),
      conditionCounts: Object.entries(cond).sort(([, a], [, b]) => b - a).slice(0, 6).map(([name, value]) => ({ name, value })),
      symptomClusters: Object.entries(symp).sort(([, a], [, b]) => b - a).slice(0, 8).map(([name, value]) => ({ name, value })),
    };
  }, [predictions]);

  return (
    <>
      <div className="relative">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 size-4 text-muted-foreground" />
        <Input
          placeholder="Search by disease or symptom..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="pl-9"
        />
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-4">
        <TabsList>
          <TabsTrigger value="timeline">Timeline</TabsTrigger>
          <TabsTrigger value="conditions">By Condition</TabsTrigger>
        </TabsList>

        <TabsContent value="timeline" className="space-y-4">
          {filteredPredictions.length === 0 && (
            <Card>
              <CardContent className="py-8 text-center">
                <p className="text-muted-foreground">
                  {search ? "No matching predictions." : "No predictions yet."}
                </p>
              </CardContent>
            </Card>
          )}
          {filteredPredictions.map((p, index) => (
            <motion.div key={p.id} initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: index * 0.03 }}>
              <Card>
                <CardContent className="p-4">
                  <div className="flex items-start justify-between mb-3">
                    <div>
                      <h3 className="font-semibold text-lg">{p.prediction}</h3>
                      <div className="flex items-center gap-2 mt-1 text-sm text-muted-foreground">
                        <Calendar className="size-3" />
                        <span>{new Date(p.timestamp).toLocaleDateString("en-US", {
                          year: "numeric", month: "short", day: "numeric", hour: "2-digit", minute: "2-digit",
                        })}</span>
                      </div>
                    </div>
                    <Badge className={cn("text-sm px-3 py-1", severityColorMap[p.severity] ?? "")}>
                      {p.severity}
                    </Badge>
                  </div>
                  <div className="flex flex-wrap items-center gap-4">
                    <div>
                      <span className="text-sm text-muted-foreground">Confidence</span>
                      <p className="font-semibold text-primary">{p.confidence}%</p>
                    </div>
                    <div className="flex-1">
                      <span className="text-sm text-muted-foreground">Symptoms</span>
                      <div className="flex flex-wrap gap-1 mt-1">
                        {p.symptoms.map((s) => (
                          <Badge key={s} variant="outline" className="text-xs">{s}</Badge>
                        ))}
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </motion.div>
          ))}
        </TabsContent>

        <TabsContent value="conditions" className="space-y-4">
          {Object.entries(
            filteredPredictions.reduce((acc, p) => {
              if (!acc[p.prediction]) acc[p.prediction] = [];
              acc[p.prediction].push(p);
              return acc;
            }, {} as Record<string, PredictionRecord[]>)
          ).length === 0 && (
            <Card>
              <CardContent className="py-8 text-center">
                <p className="text-muted-foreground">No matching predictions.</p>
              </CardContent>
            </Card>
          )}
          {Object.entries(
            filteredPredictions.reduce((acc, p) => {
              if (!acc[p.prediction]) acc[p.prediction] = [];
              acc[p.prediction].push(p);
              return acc;
            }, {} as Record<string, PredictionRecord[]>)
          ).sort(([, a], [, b]) => b.length - a.length).map(([condition, records]) => (
            <motion.div key={condition} initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}>
              <Card>
                <CardContent className="p-4">
                  <div className="flex items-center justify-between mb-3">
                    <div className="flex items-center gap-2">
                      <h3 className="font-semibold">{condition}</h3>
                      <Badge variant="secondary" className="text-xs">
                        {records.length} {records.length === 1 ? "occurrence" : "occurrences"}
                      </Badge>
                    </div>
                    {records.some((r) => r.severity === "Severe") && (
                      <AlertTriangle className="size-4 text-destructive" />
                    )}
                  </div>
                  <div className="space-y-1.5">
                    {records.map((r) => (
                      <div key={r.id} className="flex items-center gap-3 text-sm">
                        <div className={cn(
                          "size-2 rounded-full shrink-0",
                          r.severity === "Mild" && "bg-success",
                          r.severity === "Moderate" && "bg-warning",
                          r.severity === "Severe" && "bg-destructive"
                        )} />
                        <span className="text-muted-foreground">
                          {new Date(r.timestamp).toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric" })}
                        </span>
                        <span className="font-medium">{r.confidence}%</span>
                        <Badge variant="outline" className="text-xs">{r.severity}</Badge>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </motion.div>
          ))}
        </TabsContent>
      </Tabs>
    </>
  );
}
