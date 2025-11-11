from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.graphics.shapes import Drawing, Rect, String
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from datetime import datetime

class ReportGenerator:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._create_custom_styles()

        # Level colors
        self.level_colors = {
            'Awareness': colors.HexColor('#90CAF9'),
            'Application': colors.HexColor('#66BB6A'),
            'Mastery': colors.HexColor('#FFA726'),
            'Influence': colors.HexColor('#5C6BC0')
        }

    def _create_custom_styles(self):
        """Create custom styles for the reports"""
        self.styles.add(ParagraphStyle(
            name='CertificateTitle',
            parent=self.styles['Heading1'],
            fontSize=32,
            textColor=colors.HexColor('#1a237e'),
            spaceAfter=20,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))

        self.styles.add(ParagraphStyle(
            name='CertificateSubtitle',
            parent=self.styles['Normal'],
            fontSize=16,
            textColor=colors.HexColor('#283593'),
            spaceAfter=15,
            alignment=TA_CENTER,
            fontName='Helvetica-Oblique'
        ))

        self.styles.add(ParagraphStyle(
            name='SectionTitle',
            parent=self.styles['Heading1'],
            fontSize=16,
            textColor=colors.HexColor('#1a237e'),
            spaceAfter=12,
            spaceBefore=6,
            fontName='Helvetica-Bold',
            alignment=TA_LEFT
        ))

    def _get_level_icon(self, level: str) -> str:
        """Get unicode icon for competency level"""
        icons = {
            'Awareness': '[A]',
            'Application': '[Ap]',
            'Mastery': '[M]',
            'Influence': '[I]'
        }
        return icons.get(level, '[?]')

    def generate_certificate(self, candidate_name: str, job_role: str,
                           evaluation: dict, cv_evaluation: dict,
                           output_path: str = "certificate.pdf"):
        """Generate professional certificate - 1 page"""
        doc = SimpleDocTemplate(output_path, pagesize=A4,
                              rightMargin=1*inch, leftMargin=1*inch,
                              topMargin=1*inch, bottomMargin=1*inch)

        story = []

        # Border
        border_drawing = Drawing(6.3*inch, 0.1*inch)
        border_rect = Rect(0, 0, 6.3*inch, 0.1*inch, fillColor=colors.HexColor('#1a237e'))
        border_drawing.add(border_rect)
        story.append(border_drawing)
        story.append(Spacer(1, 0.3*inch))

        # Title
        title = Paragraph("CERTIFICATE OF COMPETENCY ACHIEVEMENT", self.styles['CertificateTitle'])
        story.append(title)
        story.append(Spacer(1, 0.4*inch))

        subtitle = Paragraph("AI-Powered Competency Assessment System", self.styles['CertificateSubtitle'])
        story.append(subtitle)
        story.append(Spacer(1, 0.4*inch))

        # Candidate Info
        cert_text = f"""<para align=center>
This certifies that<br/><br/>
<b><font size=24 color="#1a237e">{candidate_name}</font></b><br/><br/>
has successfully completed the competency-based assessment<br/>
for the position of<br/><br/>
<b><font size=18 color="#283593">{job_role}</font></b><br/><br/>
on <b>{datetime.now().strftime('%B %d, %Y')}</b>
</para>"""
        story.append(Paragraph(cert_text, self.styles['Normal']))
        story.append(Spacer(1, 0.4*inch))

        # Score
        exam_score = evaluation.get('overall_score', 0)
        cv_score = cv_evaluation.get('cv_match_score', 0)
        total_score = exam_score + cv_score

        score_box = f"""<para align=center>
<font size=20 color="#1a237e"><b>OVERALL SCORE: {total_score}/100</b></font><br/>
<font size=11 color="#424242">(Exam: {exam_score}/85 + CV: {cv_score}/15)</font>
</para>"""
        story.append(Paragraph(score_box, self.styles['Normal']))
        story.append(Spacer(1, 0.3*inch))

        # Competency Table
        competency_scores = evaluation.get('competency_scores', {})
        comp_data = [['Competency', 'Level Achieved', 'Score']]

        for comp_name, details in competency_scores.items():
            level = details.get('achieved_level', 'N/A')
            icon = self._get_level_icon(level)
            comp_data.append([
                comp_name,
                f"{icon} {level}",
                f"{details.get('total_score', 0)}/{details.get('max_score', 30)}"
            ])

        comp_table = Table(comp_data, colWidths=[4.0*inch, 2.0*inch, 1.5*inch])
        comp_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a237e')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('FONTSIZE', (0, 1), (-1, -1), 11),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#E8EAF6')),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#1a237e')),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')
        ]))
        story.append(comp_table)
        story.append(Spacer(1, 0.3*inch))

        # Strengths
        all_strengths = []
        for details in competency_scores.values():
            if details.get('strengths'):
                all_strengths.extend(details['strengths'][:2])

        if all_strengths:
            story.append(Paragraph("<b><font size=12 color='#1a237e'>Key Strengths:</font></b>", self.styles['Normal']))
            story.append(Spacer(1, 0.08*inch))
            for strength in all_strengths[:3]:
                story.append(Paragraph(f"<font size=10>• {strength}</font>", self.styles['Normal']))
            story.append(Spacer(1, 0.25*inch))

        # Recommendation
        cv_recommendation = cv_evaluation.get('recommendation', 'N/A')
        rec_text = f"<para align=center><b><font size=12 color='#1a237e'>Overall Recommendation:</font></b> <font size=11>{cv_recommendation}</font></para>"
        story.append(Paragraph(rec_text, self.styles['Normal']))

        # Footer
        story.append(Spacer(1, 0.3*inch))
        story.append(border_drawing)
        story.append(Spacer(1, 0.1*inch))

        footer_text = f"""<para align=center>
<font size=9 color="#616161"><i>Certificate ID: CERT-{datetime.now().strftime('%Y%m%d%H%M%S')}<br/>
Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</i></font>
</para>"""
        story.append(Paragraph(footer_text, self.styles['Normal']))

        doc.build(story)
        print(f"\n Candidate certificate generated: {output_path}")

    def generate_admin_report(self, candidate_name: str, job_role: str,
                            questions: dict, answers: dict, evaluation: dict,
                            cv_evaluation: dict, cv_text: str,
                            output_path: str = "admin_report.pdf"):
        """Generate professional 2-page admin report"""
        doc = SimpleDocTemplate(output_path, pagesize=A4,
                              rightMargin=1*inch, leftMargin=1*inch,
                              topMargin=1*inch, bottomMargin=1*inch)

        story = []

        # PAGE 1: Summary
        header = Paragraph("<b><font size=24 color='#1a237e'>ADMIN EVALUATION REPORT</font></b>",
                          self.styles['Title'])
        story.append(header)
        story.append(Spacer(1, 0.15*inch))

        # Candidate Info
        exam_score = evaluation.get('overall_score', 0)
        cv_score = cv_evaluation.get('cv_match_score', 0)
        total_score = exam_score + cv_score

        info_data = [
            ['Candidate Name', candidate_name, 'Overall Score', f'{total_score}/100'],
            ['Position Applied', job_role, 'Exam Date', datetime.now().strftime('%B %d, %Y')]
        ]

        info_table = Table(info_data, colWidths=[1.6*inch, 2.2*inch, 1.5*inch, 1.2*inch])
        info_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#E3F2FD')),
            ('BACKGROUND', (2, 0), (2, -1), colors.HexColor('#E3F2FD')),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey)
        ]))
        story.append(info_table)
        story.append(Spacer(1, 0.25*inch))

        # Competency Scores
        story.append(Paragraph("<b><font size=16 color='#1a237e'>Competency Score & Levels</font></b>",
                              self.styles['SectionTitle']))
        story.append(Spacer(1, 0.1*inch))

        competency_scores = evaluation.get('competency_scores', {})
        score_data = [['Competency', 'Marks', 'Level', 'Rubric-Based Feedback', 'Improvement']]

        for comp_name, details in competency_scores.items():
            level = details.get('achieved_level', 'N/A')
            icon = self._get_level_icon(level)
            strengths = details.get('strengths', [])
            improvements = details.get('areas_for_improvement', [])

            feedback_text = strengths[0] if strengths else 'N/A'
            improvement_text = improvements[0] if improvements else 'N/A'

            score_data.append([
                comp_name,
                f"{details.get('total_score', 0)}/{details.get('max_score', 30)}",
                f"{icon} {level}",
                feedback_text,
                improvement_text
            ])

        score_data.append(['CV Analysis', f'{cv_score}/15', '-',
                          cv_evaluation.get('recommendation', 'N/A'), '-'])
        score_data.append(['TOTAL', f'{total_score}/100', '-', '-', '-'])

        score_table = Table(score_data, colWidths=[2.0*inch, 0.8*inch, 1.0*inch, 2.2*inch, 1.5*inch])
        score_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a237e')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'CENTER'),
            ('ALIGN', (2, 0), (2, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('BACKGROUND', (0, 1), (-1, -2), colors.HexColor('#E8EAF6')),
            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#FFECB3')),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('WORDWRAP', (0, 0), (-1, -1), True)
        ]))
        story.append(score_table)
        story.append(Spacer(1, 0.3*inch))

        # Legend
        legend_text = """<para align=center>
<font size=10><b>Level Guide:</b> [A] Awareness (0-25%) | [Ap] Application (26-50%) | [M] Mastery (51-75%) | [I] Influence (76-100%)</font>
</para>"""
        story.append(Paragraph(legend_text, self.styles['Normal']))
        story.append(Spacer(1, 0.3*inch))

        # PAGE 2
        story.append(PageBreak())

        story.append(Paragraph("<b><font size=20 color='#1a237e'>Detailed Competency Analysis</font></b>",
                              self.styles['Title']))
        story.append(Spacer(1, 0.2*inch))

        # Detailed breakdown
        for comp_name, details in competency_scores.items():
            level = details.get('achieved_level', 'N/A')
            icon = self._get_level_icon(level)
            percentage = details.get('percentage', 0)
            score = details.get('total_score', 0)
            max_score = details.get('max_score', 30)
            reasoning = details.get('rubric_reasoning', 'N/A')

            comp_header = f"<b><font size=12 color='#1a237e'>{icon} {comp_name}</font></b>"
            story.append(Paragraph(comp_header, self.styles['Normal']))
            story.append(Spacer(1, 0.08*inch))

            score_info = f"<font size=10><b>Score:</b> {score}/{max_score} ({percentage}%) | <b>Level:</b> {level}</font>"
            story.append(Paragraph(score_info, self.styles['Normal']))
            story.append(Spacer(1, 0.08*inch))

            reasoning_para = f"<font size=10><b>Rubric-Based Reasoning:</b><br/>{reasoning}</font>"
            story.append(Paragraph(reasoning_para, self.styles['Normal']))
            story.append(Spacer(1, 0.08*inch))

            strengths = details.get('strengths', [])
            if strengths:
                story.append(Paragraph("<font size=10><b>Strengths:</b></font>", self.styles['Normal']))
                for strength in strengths[:3]:
                    story.append(Paragraph(f"<font size=9>  • {strength}</font>", self.styles['Normal']))
                story.append(Spacer(1, 0.05*inch))

            improvements = details.get('areas_for_improvement', [])
            if improvements:
                story.append(Paragraph("<font size=10><b>Areas for Improvement:</b></font>", self.styles['Normal']))
                for improvement in improvements[:3]:
                    story.append(Paragraph(f"<font size=9>  • {improvement}</font>", self.styles['Normal']))

            story.append(Spacer(1, 0.15*inch))

        # CV Analysis
        story.append(Paragraph("<b><font size=14 color='#1a237e'>CV Evaluation</font></b>",
                              self.styles['SectionTitle']))
        story.append(Spacer(1, 0.1*inch))

        cv_data = [
            ['Aspect', 'Assessment'],
            ['CV Match Score', f"{cv_score}/15"],
            ['Overall Fit', cv_evaluation.get('recommendation', 'N/A')]
        ]

        cv_strengths = cv_evaluation.get('strengths', [])
        if cv_strengths:
            strengths_text = '; '.join(cv_strengths[:2])
            cv_data.append(['Key Strengths', strengths_text])

        cv_gaps = cv_evaluation.get('gaps', [])
        if cv_gaps:
            gaps_text = '; '.join(cv_gaps[:2])
            cv_data.append(['Gaps Identified', gaps_text])

        cv_table = Table(cv_data, colWidths=[1.8*inch, 5.0*inch])
        cv_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#455A64')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('BACKGROUND', (0, 1), (0, -1), colors.HexColor('#E3F2FD')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('WORDWRAP', (0, 0), (-1, -1), True)
        ]))
        story.append(cv_table)
        story.append(Spacer(1, 0.2*inch))

        # Overall Feedback
        story.append(Paragraph("<b><font size=14 color='#1a237e'>Overall Recommendation & Summary</font></b>",
                              self.styles['SectionTitle']))
        story.append(Spacer(1, 0.1*inch))

        overall_feedback = evaluation.get('overall_feedback', 'No feedback available')
        feedback_para = Paragraph(f"<font size=10>{overall_feedback}</font>", self.styles['Normal'])
        story.append(feedback_para)

        # Footer
        story.append(Spacer(1, 0.2*inch))
        footer = f"""<para align=center>
<font size=8 color="#616161"><i>Report generated by AI-Powered Competency Assessment System<br/>
Date: {datetime.now().strftime('%B %d, %Y at %I:%M %p')} | Report ID: RPT-{datetime.now().strftime('%Y%m%d%H%M%S')}</i></font>
</para>"""
        story.append(Paragraph(footer, self.styles['Normal']))

        doc.build(story)
        print(f" Admin report generated: {output_path}")
