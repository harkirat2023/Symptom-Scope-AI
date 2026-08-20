from collections import Counter, defaultdict
from datetime import UTC, datetime, timedelta
from threading import Lock

from schemas.prediction_schema import PredictionRecord

RANGE_MAP = {
    "1m": 30,
    "3m": 90,
    "6m": 180,
    "1y": 365,
}

_ANALYTICS_CACHE: dict[str, tuple[float, dict]] = {}
_ANALYTICS_CACHE_TTL = 60
_ANALYTICS_LOCK = Lock()


def invalidate_user_cache(user_id: str) -> None:
    with _ANALYTICS_LOCK:
        for key in list(_ANALYTICS_CACHE.keys()):
            if key.startswith(f"{user_id}:"):
                del _ANALYTICS_CACHE[key]


class AnalyticsService:
    def compute(
        self,
        predictions: list[PredictionRecord],
        time_range: str = "6m",
    ) -> dict:
        if not predictions:
            return self._empty_response()

        days = RANGE_MAP.get(time_range, 180)
        cutoff = datetime.now(UTC) - timedelta(days=days)
        filtered = [p for p in predictions if self._parse_ts(p.timestamp) >= cutoff]
        if not filtered:
            filtered = predictions[-5:] if predictions else []

        if not filtered:
            return self._empty_response()

        total = len(filtered)

        collected = self._collect_prediction_data(filtered)

        disease_frequency = self._compute_disease_frequency(
            collected["disease_counts"], total
        )
        severity_breakdown = self._compute_severity_breakdown(
            collected["severity_counts"], total
        )
        disease_trends = self._compute_disease_trends(filtered)
        severity_trends = self._compute_severity_trends(filtered)
        symptom_insights = self._compute_symptom_insights(filtered)
        symptom_trends = self._compute_symptom_trends(filtered)
        confidence_trends = self._compute_confidence_trends(filtered)
        recurring_conditions = self._compute_recurring_conditions(predictions)

        disease_counts = collected["disease_counts"]
        severe_count = collected["severe_count"]
        most_common_disease = collected["most_common_disease"]
        avg_conf = collected["average_confidence"]

        health_summary = self._compute_health_summary(
            filtered, total, most_common_disease, severe_count, disease_counts, days
        )

        insights = self._generate_insights(
            filtered, total, most_common_disease, disease_counts,
            severe_count, avg_conf, recurring_conditions, symptom_trends, days,
        )

        return {
            "summary": {
                "total_predictions": total,
                "most_common_disease": most_common_disease,
                "average_confidence": avg_conf,
                "severe_count": severe_count,
                "unique_conditions": len(disease_counts),
                "time_range_days": days,
            },
            "disease_frequency": disease_frequency,
            "severity_breakdown": severity_breakdown,
            "disease_trends": disease_trends,
            "severity_trends": severity_trends,
            "symptom_insights": symptom_insights,
            "symptom_trends": symptom_trends,
            "confidence_trends": confidence_trends,
            "recurring_conditions": recurring_conditions,
            "health_summary": health_summary,
            "insights": insights,
        }

    @staticmethod
    def _collect_prediction_data(
        filtered: list[PredictionRecord],
    ) -> dict:
        disease_counts: Counter = Counter()
        severity_counts: dict[str, int] = defaultdict(int)
        total_conf = 0.0
        for p in filtered:
            disease_counts[p.prediction] += 1
            severity_counts[p.severity] += 1
            total_conf += p.confidence

        total = len(filtered)
        most_common_disease = ""
        if disease_counts:
            most_common = disease_counts.most_common(1)
            most_common_disease = most_common[0][0] if most_common else ""

        return {
            "disease_counts": disease_counts,
            "severity_counts": severity_counts,
            "severe_count": severity_counts.get("Severe", 0),
            "most_common_disease": most_common_disease,
            "average_confidence": round(total_conf / total, 1) if total > 0 else 0,
        }

    def _compute_disease_frequency(
        self, disease_counts: Counter, total: int,
    ) -> list[dict]:
        return [
            {
                "disease": disease,
                "count": count,
                "percentage": round(count / total * 100, 1) if total else 0,
            }
            for disease, count in disease_counts.most_common()
        ]

    def _compute_severity_breakdown(
        self, severity_counts: dict[str, int], total: int,
    ) -> list[dict]:
        severity_order = {"Severe": 0, "Moderate": 1, "Mild": 2}
        return [
            {
                "severity": sev,
                "count": count,
                "percentage": round(count / total * 100, 1) if total else 0,
            }
            for sev, count in sorted(
                severity_counts.items(),
                key=lambda x: severity_order.get(x[0], 3),
            )
        ]

    def _compute_disease_trends(self, filtered: list) -> list[dict]:
        monthly: dict[str, Counter] = defaultdict(Counter)
        for p in filtered:
            ts = self._parse_ts(p.timestamp)
            key = ts.strftime("%Y-%m")
            monthly[key][p.prediction] += 1

        sorted_months = sorted(monthly.keys())
        trends = []
        for i, month in enumerate(sorted_months):
            diseases = monthly[month]
            top_5 = diseases.most_common(5)

            change_from_previous = 0.0
            if i > 0:
                prev_total = sum(monthly[sorted_months[i - 1]].values())
                current_total = sum(diseases.values())
                if prev_total > 0:
                    change_from_previous = round(
                        (current_total - prev_total) / prev_total * 100, 1
                    )

            trends.append({
                "month": month,
                "total": sum(diseases.values()),
                "breakdown": [
                    {"disease": d, "count": c} for d, c in top_5
                ],
                "change_from_previous_pct": change_from_previous,
            })
        return trends

    def _compute_severity_trends(self, filtered: list) -> list[dict]:
        severity_monthly: dict[str, Counter] = defaultdict(Counter)
        for p in filtered:
            ts = self._parse_ts(p.timestamp)
            key = ts.strftime("%Y-%m")
            severity_monthly[key][p.severity] += 1

        return [
            {
                "month": month,
                "breakdown": [
                    {"severity": s, "count": c}
                    for s, c in sorted(sev.items())
                ],
            }
            for month, sev in sorted(severity_monthly.items())
        ]

    def _compute_symptom_insights(self, filtered: list) -> dict:
        all_symptoms: Counter = Counter()
        symptom_pairs: Counter = Counter()
        for p in filtered:
            for s in p.symptoms:
                all_symptoms[s] += 1
            if len(p.symptoms) >= 2:
                for i in range(len(p.symptoms)):
                    for j in range(i + 1, len(p.symptoms)):
                        pair = tuple(sorted([p.symptoms[i], p.symptoms[j]]))
                        symptom_pairs[pair] += 1

        top_symptoms = [
            {"symptom": s, "count": c}
            for s, c in all_symptoms.most_common(10)
        ]
        top_pairs = [
            {"symptoms": list(pair), "count": c}
            for pair, c in symptom_pairs.most_common(10)
        ]
        return {"top_symptoms": top_symptoms, "common_pairs": top_pairs}

    def _compute_symptom_trends(self, filtered: list) -> list[dict]:
        symptom_monthly: dict[str, Counter] = defaultdict(Counter)
        for p in filtered:
            ts = self._parse_ts(p.timestamp)
            key = ts.strftime("%Y-%m")
            for s in p.symptoms:
                symptom_monthly[s][key] += 1

        trends = []
        for symptom, month_counts in symptom_monthly.items():
            sorted_months = sorted(month_counts.items())
            data_points = [{"month": m, "count": c} for m, c in sorted_months]

            change_pct, direction = self._compute_trend_direction(sorted_months)

            trends.append({
                "symptom": symptom,
                "data": data_points,
                "direction": direction,
                "change_pct": change_pct,
            })

        return trends

    @staticmethod
    def _compute_trend_direction(
        sorted_months: list[tuple[str, int]],
    ) -> tuple[float, str]:
        if len(sorted_months) >= 3:
            n = len(sorted_months)
            mid = n // 2
            first_half = sorted_months[:mid]
            second_half = sorted_months[mid:]
            first_avg = sum(c for _, c in first_half) / len(first_half)
            second_avg = sum(c for _, c in second_half) / len(second_half)

            if first_avg > 0:
                change_pct = round(
                    ((second_avg - first_avg) / first_avg) * 100, 1
                )
                if abs(change_pct) < 10:
                    return change_pct, "stable"
                return (change_pct, "increasing") if change_pct > 0 else (change_pct, "decreasing")
            elif second_avg > 0:
                return 100.0, "increasing"

        if len(sorted_months) >= 2:
            first_count = sorted_months[0][1]
            last_count = sorted_months[-1][1]
            if first_count > 0:
                change_pct = round(
                    (last_count - first_count) / first_count * 100, 1
                )
            else:
                change_pct = 100.0 if last_count > 0 else 0.0

            if abs(change_pct) < 10:
                return change_pct, "stable"
            return (change_pct, "increasing") if change_pct > 0 else (change_pct, "decreasing")

        return 0.0, "insufficient_data"

    def _compute_confidence_trends(self, filtered: list) -> list[dict]:
        confidence_monthly: dict[str, list[float]] = defaultdict(list)
        for p in filtered:
            ts = self._parse_ts(p.timestamp)
            key = ts.strftime("%Y-%m")
            confidence_monthly[key].append(p.confidence)

        return [
            {
                "month": month,
                "average_confidence": round(sum(vals) / len(vals), 1),
                "min_confidence": round(min(vals), 1),
                "max_confidence": round(max(vals), 1),
                "count": len(vals),
            }
            for month, vals in sorted(confidence_monthly.items())
        ]

    def _compute_recurring_conditions(
        self, predictions: list[PredictionRecord],
    ) -> list[dict]:
        sorted_predictions = sorted(
            predictions, key=lambda p: self._parse_ts(p.timestamp)
        )
        condition_history: dict[str, list[str]] = defaultdict(list)
        for p in sorted_predictions:
            condition_history[p.prediction].append(p.timestamp)

        recurring = []
        for disease, timestamps in condition_history.items():
            if len(timestamps) >= 2:
                first_ts = self._parse_ts(timestamps[0])
                last_ts = self._parse_ts(timestamps[-1])
                total_days = max((last_ts - first_ts).days, 1)
                occurrences_per_month = len(timestamps) / max(total_days, 30) * 30

                if occurrences_per_month >= 1.0:
                    frequency = "frequent"
                elif occurrences_per_month >= 0.3:
                    frequency = "occasional"
                else:
                    frequency = "rare"

                recurring.append({
                    "disease": disease,
                    "occurrences": len(timestamps),
                    "first_detected": timestamps[0],
                    "last_detected": timestamps[-1],
                    "frequency": frequency,
                    "avg_days_between": round(total_days / (len(timestamps) - 1), 1),
                })

        recurring.sort(key=lambda x: x["occurrences"], reverse=True)
        return recurring

    def _compute_health_summary(
        self, filtered, total, most_common_disease, severe_count, disease_counts, days,
    ) -> dict | None:
        if total == 0:
            return None

        recurring_issues_count = sum(1 for d, c in disease_counts.items() if c >= 2)
        severe_ratio = severe_count / max(total, 1)

        if severe_ratio >= 0.2:
            risk_level = "high"
        elif severe_ratio >= 0.05:
            risk_level = "moderate"
        else:
            risk_level = "low"

        improving = severe_count <= 1 or severe_ratio < 0.1

        if days >= 180:
            period_label = "6-month"
        elif days >= 90:
            period_label = "3-month"
        elif days >= 30:
            period_label = "monthly"
        else:
            period_label = "overview"

        if total == 1:
            summary_text = (
                f"Single check-up recorded: {most_common_disease}. "
                "Continue monitoring your symptoms regularly."
            )
        else:
            parts = [f"{total} check-ups recorded"]
            if most_common_disease:
                pct = disease_counts[most_common_disease] / total * 100
                parts.append(f"most common: {most_common_disease} ({pct:.0f}%)")
            parts.append(
                f"{severe_count} severe episode{'s' if severe_count != 1 else ''}"
            )
            if recurring_issues_count > 0:
                parts.append(
                    f"{recurring_issues_count} recurring condition{'s' if recurring_issues_count != 1 else ''}"
                )
            if improving:
                parts.append("trending positive")
            summary_text = " | ".join(parts)

        return {
            "period_label": period_label,
            "total_checks": total,
            "most_common_condition": most_common_disease or "N/A",
            "risk_level": risk_level,
            "recurring_issues": recurring_issues_count,
            "improving": improving,
            "summary_text": summary_text,
        }

    def _generate_insights(
        self, filtered, total, most_common_disease, disease_counts,
        severe_count, avg_conf, recurring_conditions, symptom_trends, days,
    ) -> list[str]:
        insights: list[str] = []

        if total == 0:
            return ["No prediction data yet. Use the Symptom Checker to get started."]

        if days >= 30:
            insights.append(
                f"Analysis period: {days} days with {total} health check{'s' if total != 1 else ''} recorded."
            )

        if most_common_disease:
            pct = disease_counts[most_common_disease] / total * 100
            insights.append(
                f"Your most frequent diagnosis is {most_common_disease} "
                f"({pct:.0f}% of {total} check{'s' if total != 1 else ''})."
            )

        if severe_count > 0:
            insights.append(
                f"You have had {severe_count} severe "
                f"{'episode' if severe_count == 1 else 'episodes'} "
                f"in the analyzed period. Please discuss these with your healthcare provider."
            )

        if avg_conf < 60 and total >= 3:
            insights.append(
                "Your average confidence is below 60%, which may indicate "
                "atypical symptom patterns. Consider consulting a healthcare provider "
                "for a comprehensive evaluation."
            )
        elif avg_conf >= 85 and total >= 3:
            insights.append(
                f"Your average confidence is {avg_conf}%, indicating "
                "your symptom reports are clear and consistent."
            )

        if total >= 5 and len(disease_counts) <= 2:
            insights.append(
                "Your symptoms consistently point to the same condition. "
                "A specialist consultation is recommended for a definitive diagnosis "
                "and treatment plan."
            )

        rising_symptoms = [
            t for t in symptom_trends
            if t["direction"] == "increasing" and len(t["data"]) >= 2
        ]
        if rising_symptoms:
            names = [s["symptom"].replace("_", " ") for s in rising_symptoms[:3]]
            pcts = [s["change_pct"] for s in rising_symptoms[:3]]
            detail = ", ".join(
                f"{n} ({p:+.1f}%)" for n, p in zip(names, pcts)
            )
            insights.append(
                f"Rising symptom{'s' if len(names) != 1 else ''}: {detail}. "
                "Monitor these closely."
            )

        falling_symptoms = [
            t for t in symptom_trends
            if t["direction"] == "decreasing" and len(t["data"]) >= 2
        ]
        if falling_symptoms:
            names = [s["symptom"].replace("_", " ") for s in falling_symptoms[:2]]
            insights.append(
                f"Improving symptom{'s' if len(names) != 1 else ''}: {', '.join(names)}. "
                "Your symptom pattern is showing positive change."
            )

        if recurring_conditions:
            rc = recurring_conditions[0]
            freq_labels = {
                "frequent": "frequently recurring",
                "occasional": "occasionally recurring",
                "rare": "rarely recurring",
            }
            label = freq_labels.get(rc["frequency"], "recurring")
            insights.append(
                f"{rc['disease']} is {label} ({rc['occurrences']} "
                f"{'times' if rc['occurrences'] != 1 else 'time'}, "
                f"avg {rc['avg_days_between']} days between episodes). "
                "Consider follow-up care."
            )

        high_conf_predictions = [p for p in filtered if p.confidence >= 85]
        if len(high_conf_predictions) >= 2:
            insights.append(
                f"You had {len(high_conf_predictions)} high-confidence predictions (≥85%). "
                "Your symptom reporting is clear and consistent."
            )

        if not insights:
            insights.append(
                "Keep tracking your symptoms regularly to receive personalized health insights."
            )

        return insights[:8]

    def _empty_response(self) -> dict:
        return {
            "summary": {
                "total_predictions": 0,
                "most_common_disease": "",
                "average_confidence": 0,
                "severe_count": 0,
                "unique_conditions": 0,
                "time_range_days": 0,
            },
            "disease_frequency": [],
            "severity_breakdown": [],
            "disease_trends": [],
            "severity_trends": [],
            "symptom_insights": {"top_symptoms": [], "common_pairs": []},
            "symptom_trends": [],
            "confidence_trends": [],
            "recurring_conditions": [],
            "health_summary": None,
            "insights": ["No prediction data yet. Use the Symptom Checker to get started."],
            "risk_score": None,
        }

    def _parse_ts(self, timestamp: str) -> datetime:
        try:
            return datetime.fromisoformat(timestamp)
        except (ValueError, TypeError):
            return datetime.min.replace(tzinfo=UTC)
