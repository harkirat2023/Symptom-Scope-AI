"use client";

import { useEffect } from "react";
import { useAuth } from "@clerk/nextjs";
import { useRiskScoreStore } from "@/lib/stores/risk-score-store";
import RiskScoreGauge from "./risk-score-gauge";
import RiskFactorBreakdown from "./risk-factor-breakdown";
import RiskTrendChart from "./risk-trend-chart";
import RiskTips from "./risk-tips";
import { Loader2 } from "lucide-react";

export default function RiskScoreDashboardCard() {
  const { getToken } = useAuth();
  const {
    score,
    history,
    tips,
    loading,
    fetchScore,
    fetchHistory,
    fetchTips,
    setGetToken,
  } = useRiskScoreStore();

  useEffect(() => {
    setGetToken(getToken);
  }, [setGetToken, getToken]);

  useEffect(() => {
    fetchScore();
    fetchHistory();
    fetchTips();
  }, [fetchScore, fetchHistory, fetchTips]);

  if (loading && !score) {
    return (
      <div className="flex items-center justify-center rounded-lg border p-8">
        <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
      </div>
    );
  }

  if (!score) {
    return null;
  }

  return (
    <div className="space-y-4">
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        <div className="flex flex-col items-center rounded-lg border p-4">
          <RiskScoreGauge score={score.current_score} />
        </div>
        <RiskFactorBreakdown breakdown={score.breakdown} />
        <RiskTips tips={tips} />
      </div>
      {history.length > 0 && (
        <RiskTrendChart data={history} />
      )}
    </div>
  );
}
