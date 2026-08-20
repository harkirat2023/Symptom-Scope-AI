import csv
import io
from datetime import datetime, timezone
from schemas.prediction_schema import PredictionRecord
from services.disease_registry import get_precautions, get_specialist


class ReportExportService:
    def generate_csv(self, predictions: list[PredictionRecord]) -> str:
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow([
            "Timestamp",
            "Symptoms",
            "Predicted Disease",
            "Confidence (%)",
            "Severity",
            "Recommended Specialist",
            "Precautions",
        ])

        for p in predictions:
            symptoms = "; ".join(p.symptoms) if p.symptoms else ""
            precautions_list = get_precautions(p.prediction)
            precautions_text = "; ".join(
                prec.text for prec in precautions_list[:3]
            ) if precautions_list else ""
            specialist = get_specialist(p.prediction)

            writer.writerow([
                p.timestamp,
                symptoms,
                p.prediction,
                f"{p.confidence:.2f}",
                p.severity,
                specialist,
                precautions_text,
            ])

        return output.getvalue()

    def generate_csv_summary(
        self,
        predictions: list[PredictionRecord],
        risk_score: float | None = None,
        risk_category: str | None = None,
    ) -> str:
        output = io.StringIO()
        writer = csv.writer(output)

        generated_at = datetime.now(timezone.utc).isoformat()
        total = len(predictions)

        writer.writerow(["SymptomScope AI - Health Report"])
        writer.writerow(["Generated At", generated_at])
        writer.writerow(["Total Predictions", str(total)])
        if risk_score is not None:
            writer.writerow(["Health Risk Score", f"{risk_score}/100 ({risk_category or 'N/A'})"])
        writer.writerow([])

        severe_count = sum(1 for p in predictions if p.severity == "Severe")
        moderate_count = sum(1 for p in predictions if p.severity == "Moderate")
        mild_count = sum(1 for p in predictions if p.severity == "Mild")

        writer.writerow(["Severity Distribution"])
        writer.writerow(["Severe", str(severe_count)])
        writer.writerow(["Moderate", str(moderate_count)])
        writer.writerow(["Mild", str(mild_count)])
        writer.writerow([])

        disease_counts: dict[str, int] = {}
        for p in predictions:
            disease_counts[p.prediction] = disease_counts.get(p.prediction, 0) + 1
        most_common = max(disease_counts, key=disease_counts.get) if disease_counts else "N/A"

        writer.writerow(["Most Common Condition", most_common])
        writer.writerow([])
        writer.writerow(["Full Prediction History"])
        writer.writerow([
            "Timestamp", "Symptoms", "Predicted Disease",
            "Confidence (%)", "Severity", "Specialist",
        ])

        for p in predictions:
            symptoms = "; ".join(p.symptoms) if p.symptoms else ""
            specialist = get_specialist(p.prediction)
            writer.writerow([
                p.timestamp, symptoms, p.prediction,
                f"{p.confidence:.2f}", p.severity, specialist,
            ])

        return output.getvalue()

    def generate_pdf(
        self,
        predictions: list[PredictionRecord],
        risk_score: float | None = None,
        risk_category: str | None = None,
    ) -> bytes:
        try:
            from reportlab.lib.pagesizes import A4
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import mm, cm
            from reportlab.lib.colors import HexColor
            from reportlab.platypus import (
                SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
                PageBreak,
            )
            from reportlab.lib import colors
        except ImportError:
            raise ImportError(
                "reportlab is required for PDF export. Install it with: pip install reportlab"
            )

        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer, pagesize=A4,
            topMargin=2 * cm, bottomMargin=2 * cm,
            leftMargin=2 * cm, rightMargin=2 * cm,
        )

        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            "ReportTitle", parent=styles["Title"],
            fontSize=22, textColor=HexColor("#2563eb"),
            spaceAfter=6,
        )
        subtitle_style = ParagraphStyle(
            "ReportSubtitle", parent=styles["Normal"],
            fontSize=10, textColor=HexColor("#64748b"),
            spaceAfter=20,
        )
        heading_style = ParagraphStyle(
            "ReportHeading", parent=styles["Heading2"],
            fontSize=14, textColor=HexColor("#0f172a"),
            spaceBefore=16, spaceAfter=8,
        )
        normal_style = ParagraphStyle(
            "ReportNormal", parent=styles["Normal"],
            fontSize=10, leading=14,
            spaceAfter=4,
        )
        small_style = ParagraphStyle(
            "ReportSmall", parent=styles["Normal"],
            fontSize=8, textColor=HexColor("#64748b"),
        )

        elements = []

        elements.append(Paragraph("SymptomScope AI", title_style))
        elements.append(Paragraph("Health Report", subtitle_style))

        generated_at = datetime.now(timezone.utc).isoformat()
        total = len(predictions)
        elements.append(Paragraph(
            f"Generated: {generated_at} | Total Predictions: {total}",
            small_style,
        ))
        elements.append(Spacer(1, 12 * mm))

        severe_count = sum(1 for p in predictions if p.severity == "Severe")
        moderate_count = sum(1 for p in predictions if p.severity == "Moderate")
        mild_count = sum(1 for p in predictions if p.severity == "Mild")

        disease_counts: dict[str, int] = {}
        for p in predictions:
            disease_counts[p.prediction] = disease_counts.get(p.prediction, 0) + 1
        most_common = max(disease_counts, key=disease_counts.get) if disease_counts else "N/A"
        unique_conditions = len(disease_counts)
        avg_conf = round(sum(p.confidence for p in predictions) / total, 1) if total > 0 else 0

        elements.append(Paragraph("Executive Summary", heading_style))
        summary_data = [
            ["Total Check-Ups", str(total)],
            ["Unique Conditions", str(unique_conditions)],
            ["Most Common", most_common],
            ["Average Confidence", f"{avg_conf}%"],
            ["Severe Episodes", str(severe_count)],
            ["Moderate Episodes", str(moderate_count)],
            ["Mild Episodes", str(mild_count)],
        ]
        if risk_score is not None:
            summary_data.append([
                "Health Risk Score",
                f"{risk_score}/100 ({risk_category or 'N/A'})",
            ])
        summary_table = Table(summary_data, colWidths=[140, 200])
        summary_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (0, -1), HexColor("#f8fafc")),
            ("TEXTCOLOR", (0, 0), (-1, -1), HexColor("#0f172a")),
            ("FONTSIZE", (0, 0), (-1, -1), 10),
            ("ALIGN", (1, 0), (1, -1), "RIGHT"),
            ("GRID", (0, 0), (-1, -1), 0.5, HexColor("#e2e8f0")),
            ("ROWBACKGROUNDS", (0, 0), (-1, -1), [HexColor("#ffffff"), HexColor("#f8fafc")]),
        ]))
        elements.append(summary_table)
        elements.append(Spacer(1, 8 * mm))

        elements.append(Paragraph("Prediction History", heading_style))
        header = ["Date", "Symptoms", "Prediction", "Confidence", "Severity"]
        table_cell_style = ParagraphStyle(
            "CellNormal", parent=styles["Normal"],
            fontSize=8, leading=10,
        )
        header_style = ParagraphStyle(
            "CellHeader", parent=styles["Normal"],
            fontSize=9, leading=11, textColor=HexColor("#ffffff"),
        )

        def wrap(text: str) -> Paragraph:
            return Paragraph(text, table_cell_style)

        table_data = [[Paragraph(h, header_style) for h in header]]
        for p in predictions:
            symptoms_short = "; ".join(p.symptoms[:3]) if p.symptoms else ""
            if len(p.symptoms) > 3:
                symptoms_short += "..."
            table_data.append([
                wrap(p.timestamp[:10] if p.timestamp else ""),
                wrap(symptoms_short),
                wrap(p.prediction),
                wrap(f"{p.confidence:.1f}%"),
                wrap(p.severity),
            ])

        if table_data:
            prediction_table = Table(table_data, colWidths=[65, 90, 90, 60, 55])
            prediction_table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), HexColor("#2563eb")),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("GRID", (0, 0), (-1, -1), 0.5, HexColor("#e2e8f0")),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1),
                 [HexColor("#ffffff"), HexColor("#f8fafc")]),
            ]))
            elements.append(prediction_table)

        elements.append(Spacer(1, 6 * mm))
        elements.append(Paragraph(
            "Disclaimer: This report is for informational purposes only and does not "
            "constitute a medical diagnosis. Always consult a qualified healthcare "
            "professional for medical advice.",
            ParagraphStyle(
                "Disclaimer", parent=styles["Normal"],
                fontSize=8, textColor=HexColor("#94a3b8"),
                italic=True, spaceBefore=12,
            ),
        ))

        doc.build(elements)
        return buffer.getvalue()

    def generate_pdf_detailed(
        self,
        predictions: list[PredictionRecord],
        recovery_plan: dict | None = None,
    ) -> bytes:
        try:
            from reportlab.lib.pagesizes import A4
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import mm, cm
            from reportlab.lib.colors import HexColor
            from reportlab.platypus import (
                SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
                PageBreak,
            )
            from reportlab.lib import colors
        except ImportError:
            raise ImportError(
                "reportlab is required for PDF export. Install with: pip install reportlab"
            )

        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer, pagesize=A4,
            topMargin=2 * cm, bottomMargin=2 * cm,
            leftMargin=2 * cm, rightMargin=2 * cm,
        )

        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            "ReportTitle", parent=styles["Title"],
            fontSize=22, textColor=HexColor("#2563eb"),
            spaceAfter=6,
        )
        subtitle_style = ParagraphStyle(
            "ReportSubtitle", parent=styles["Normal"],
            fontSize=10, textColor=HexColor("#64748b"),
            spaceAfter=20,
        )
        heading_style = ParagraphStyle(
            "ReportHeading", parent=styles["Heading2"],
            fontSize=14, textColor=HexColor("#0f172a"),
            spaceBefore=16, spaceAfter=8,
        )
        disease_heading = ParagraphStyle(
            "DiseaseHeading", parent=styles["Heading3"],
            fontSize=12, textColor=HexColor("#2563eb"),
            spaceBefore=10, spaceAfter=4,
        )
        normal_style = ParagraphStyle(
            "ReportNormal", parent=styles["Normal"],
            fontSize=10, leading=14,
            spaceAfter=4,
        )
        small_style = ParagraphStyle(
            "ReportSmall", parent=styles["Normal"],
            fontSize=8, textColor=HexColor("#64748b"),
        )
        bullet_style = ParagraphStyle(
            "ReportBullet", parent=styles["Normal"],
            fontSize=10, leading=14,
            leftIndent=15, spaceAfter=2,
        )

        elements = []
        elements.append(Paragraph("SymptomScope AI", title_style))
        elements.append(Paragraph("Detailed Health Report", subtitle_style))

        generated_at = datetime.now(timezone.utc).isoformat()
        total = len(predictions)
        elements.append(Paragraph(
            f"Generated: {generated_at} | Total Predictions: {total}",
            small_style,
        ))
        elements.append(Spacer(1, 12 * mm))

        if recovery_plan:
            elements.append(Paragraph("Recovery Plan Summary", heading_style))
            plan_data = recovery_plan.get("planData", {})
            elements.append(Paragraph(
                f"<b>Condition:</b> {recovery_plan.get('disease', 'N/A')} "
                f"(confidence {recovery_plan.get('confidence', 0):.1f}%, severity "
                f"{recovery_plan.get('severity', 'N/A')})",
                normal_style,
            ))
            what_it_means = plan_data.get("what_it_means")
            if what_it_means:
                elements.append(Paragraph(
                    f"<b>What it means:</b> {what_it_means}", normal_style,
                ))
            what_to_do = plan_data.get("what_to_do") or []
            if what_to_do:
                elements.append(Paragraph("<b>What to do now:</b>", normal_style))
                for item in what_to_do[:4]:
                    elements.append(Paragraph(f"• {item}", bullet_style))
            personalized = plan_data.get("personalized_recommendations") or []
            if personalized:
                elements.append(Paragraph("<b>Personalized recommendations:</b>", normal_style))
                for item in personalized[:4]:
                    elements.append(Paragraph(f"• {item}", bullet_style))

        elements.append(Paragraph("Complete Prediction Details", heading_style))

        for i, p in enumerate(predictions, 1):
            timestamp = p.timestamp[:19] if p.timestamp else "Unknown"
            elements.append(Paragraph(
                f"Check-Up #{i} — {timestamp}",
                disease_heading,
            ))

            symptoms_text = ", ".join(p.symptoms) if p.symptoms else "None reported"
            elements.append(Paragraph(
                f"<b>Symptoms:</b> {symptoms_text}", normal_style,
            ))
            elements.append(Paragraph(
                f"<b>Predicted Condition:</b> {p.prediction}", normal_style,
            ))
            elements.append(Paragraph(
                f"<b>Confidence:</b> {p.confidence:.1f}%", normal_style,
            ))
            elements.append(Paragraph(
                f"<b>Severity:</b> {p.severity}", normal_style,
            ))

            if p.age is not None or p.gender is not None:
                details = []
                if p.age is not None:
                    details.append(f"Age: {p.age}")
                if p.gender:
                    details.append(f"Gender: {p.gender}")
                elements.append(Paragraph(
                    f"<b>Demographics:</b> {' | '.join(details)}", normal_style,
                ))
            if p.existing_conditions:
                elements.append(Paragraph(
                    f"<b>Existing Conditions:</b> {', '.join(p.existing_conditions)}",
                    normal_style,
                ))
            if p.symptom_duration:
                elements.append(Paragraph(
                    f"<b>Symptom Duration:</b> {p.symptom_duration}", normal_style,
                ))
            if p.pain_level is not None:
                elements.append(Paragraph(
                    f"<b>Pain Level:</b> {p.pain_level}/10", normal_style,
                ))

            specialist = get_specialist(p.prediction)
            elements.append(Paragraph(
                f"<b>Recommended Specialist:</b> {specialist}", normal_style,
            ))

            precautions_list = get_precautions(p.prediction)
            if precautions_list:
                elements.append(Paragraph("<b>Precautions:</b>", normal_style))
                for prec in precautions_list:
                    elements.append(Paragraph(
                        f"• {prec.text}", bullet_style,
                    ))

            if i < len(predictions):
                elements.append(Spacer(1, 4 * mm))

        elements.append(Spacer(1, 10 * mm))
        elements.append(Paragraph(
            "Disclaimer: This report is for informational purposes only and does not "
            "constitute a medical diagnosis. Always consult a qualified healthcare "
            "professional for medical advice.",
            ParagraphStyle(
                "Disclaimer", parent=styles["Normal"],
                fontSize=8, textColor=HexColor("#94a3b8"),
                italic=True, spaceBefore=12,
            ),
        ))

        doc.build(elements)
        return buffer.getvalue()
