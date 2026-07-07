"use client";

import { useEffect, useState } from "react";

function polarToCartesian(
  cx: number,
  cy: number,
  r: number,
  angleDeg: number
) {
  const rad = ((angleDeg - 90) * Math.PI) / 180;
  return {
    x: cx + r * Math.cos(rad),
    y: cy + r * Math.sin(rad),
  };
}

function describeArc(
  cx: number,
  cy: number,
  r: number,
  startAngle: number,
  endAngle: number
) {
  const start = polarToCartesian(cx, cy, r, endAngle);
  const end = polarToCartesian(cx, cy, r, startAngle);
  const largeArc = endAngle - startAngle > 180 ? "1" : "0";
  return [
    "M",
    start.x,
    start.y,
    "A",
    r,
    r,
    0,
    largeArc,
    0,
    end.x,
    end.y,
  ].join(" ");
}

const SCORE_R = 90;
const STROKE = 16;
const VIEWBOX = 200;

function scoreColor(score: number): string {
  if (score >= 67) return "#ef4444";
  if (score >= 34) return "#f59e0b";
  return "#22c55e";
}

function scoreLabel(score: number): string {
  if (score >= 67) return "High Risk";
  if (score >= 34) return "Medium Risk";
  return "Low Risk";
}

export default function RiskScoreGauge({
  score,
  size = 220,
}: {
  score: number;
  size?: number;
}) {
  const [animatedScore, setAnimatedScore] = useState(0);

  useEffect(() => {
    let frame = 0;
    const total = 30;
    const target = Math.round(score);
    const animate = () => {
      frame++;
      const progress = Math.min(frame / total, 1);
      setAnimatedScore(Math.round(target * easeOutCubic(progress)));
      if (progress < 1) requestAnimationFrame(animate);
    };
    animate();
  }, [score]);

  const angle = (animatedScore / 100) * 270;
  const color = scoreColor(score);

  return (
    <div
      className="relative inline-flex flex-col items-center"
      style={{ width: size, height: size + 40 }}
    >
      <svg
        width={size}
        height={size}
        viewBox={`0 0 ${VIEWBOX} ${VIEWBOX}`}
      >
        <path
          d={describeArc(VIEWBOX / 2, VIEWBOX / 2, SCORE_R, 135, 405)}
          stroke="#e5e7eb"
          strokeWidth={STROKE}
          fill="none"
          strokeLinecap="round"
        />
        <path
          d={describeArc(
            VIEWBOX / 2,
            VIEWBOX / 2,
            SCORE_R,
            135,
            135 + angle
          )}
          stroke={color}
          strokeWidth={STROKE}
          fill="none"
          strokeLinecap="round"
          className="transition-all duration-500"
        />
        <text
          x={VIEWBOX / 2}
          y={VIEWBOX / 2 - 8}
          textAnchor="middle"
          className="text-4xl font-bold"
          fill="currentColor"
          fontSize="36"
        >
          {animatedScore}
        </text>
        <text
          x={VIEWBOX / 2}
          y={VIEWBOX / 2 + 20}
          textAnchor="middle"
          className="text-sm"
          fill="#6b7280"
          fontSize="12"
        >
          out of 100
        </text>
      </svg>
      <span
        className="mt-1 text-sm font-semibold"
        style={{ color }}
      >
        {scoreLabel(score)}
      </span>
    </div>
  );
}

function easeOutCubic(t: number): number {
  return 1 - Math.pow(1 - t, 3);
}
