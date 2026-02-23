from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, Image
)
from reportlab.lib import colors
from datetime import datetime
from typing import Dict
import os
import logging

logger = logging.getLogger(__name__)


class PDFReportGenerator:
    """
    Court-ready PDF report generator
    
    This is your competitive advantage in DomainIntel
    Police officers LOVE professional reports
    """
    
    def __init__(self, output_dir: str = "./reports"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Define custom styles for the report"""
        
        # Title style
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=18,
            textColor=colors.HexColor('#1a1a1a'),
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        # Section header
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#2c3e50'),
            spaceAfter=12,
            spaceBefore=12,
            fontName='Helvetica-Bold'
        ))
        
        # Subsection
        self.styles.add(ParagraphStyle(
            name='SubSection',
            parent=self.styles['Heading3'],
            fontSize=12,
            textColor=colors.HexColor('#34495e'),
            spaceAfter=8,
            fontName='Helvetica-Bold'
        ))
        
        # Risk label styles
        self.styles.add(ParagraphStyle(
            name='RiskHigh',
            parent=self.styles['Normal'],
            fontSize=14,
            textColor=colors.HexColor('#e74c3c'),
            fontName='Helvetica-Bold'
        ))
        
        self.styles.add(ParagraphStyle(
            name='RiskMedium',
            parent=self.styles['Normal'],
            fontSize=14,
            textColor=colors.HexColor('#f39c12'),
            fontName='Helvetica-Bold'
        ))
        
        self.styles.add(ParagraphStyle(
            name='RiskLow',
            parent=self.styles['Normal'],
            fontSize=14,
            textColor=colors.HexColor('#27ae60'),
            fontName='Helvetica-Bold'
        ))
    
    def generate_report(self, analysis_data: Dict, filename: str = None) -> str:
        """
        Generate comprehensive PDF report
        
        Args:
            analysis_data: Complete analysis result from API
            filename: Optional custom filename
        
        Returns:
            Path to generated PDF file
        """
        try:
            # Generate filename if not provided
            if not filename:
                domain = analysis_data.get('domain', 'unknown')
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"{domain.replace('.', '_')}_{timestamp}.pdf"
            
            filepath = os.path.join(self.output_dir, filename)
            
            # Create PDF document
            doc = SimpleDocTemplate(
                filepath,
                pagesize=A4,
                rightMargin=2*cm,
                leftMargin=2*cm,
                topMargin=2*cm,
                bottomMargin=2*cm
            )
            
            # Build story (content)
            story = []
            
            # Header
            story.extend(self._build_header(analysis_data))
            
            # Executive Summary
            story.extend(self._build_executive_summary(analysis_data))
            
            # Domain Information
            story.extend(self._build_domain_section(analysis_data))
            
            # Hosting Information
            story.extend(self._build_hosting_section(analysis_data))
            
            # Security Analysis
            story.extend(self._build_security_section(analysis_data))
            
            # Risk Assessment (MOST IMPORTANT)
            story.extend(self._build_risk_section(analysis_data))
            
            # Footer
            story.extend(self._build_footer(analysis_data))
            
            # Build PDF
            doc.build(story)
            
            logger.info(f"PDF report generated: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"PDF generation failed: {str(e)}")
            raise
    
    def _build_header(self, data: Dict) -> list:
        """Build report header"""
        content = []
        
        # Title
        title = Paragraph(
            "DOMAIN INTELLIGENCE REPORT",
            self.styles['CustomTitle']
        )
        content.append(title)
        content.append(Spacer(1, 0.5*cm))
        
        # Case information table
        case_data = [
            ['Domain Analyzed:', data.get('domain', 'N/A')],
            ['Case ID:', data.get('case_id', 'N/A')],
            ['Analyst:', data.get('analyst_name', 'N/A')],
            ['Report Date:', datetime.now().strftime('%Y-%m-%d %H:%M:%S')],
        ]
        
        case_table = Table(case_data, colWidths=[5*cm, 12*cm])
        case_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#ecf0f1')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
            ('RIGHTPADDING', (0, 0), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        
        content.append(case_table)
        content.append(Spacer(1, 1*cm))
        
        return content
    
    def _build_executive_summary(self, data: Dict) -> list:
        """Build executive summary section"""
        content = []
        
        content.append(Paragraph("EXECUTIVE SUMMARY", self.styles['SectionHeader']))
        
        risk = data.get('risk_assessment', {})
        risk_level = risk.get('risk_level', 'UNKNOWN')
        risk_score = risk.get('risk_score', 0)
        
        # Risk level with color
        risk_style = f'Risk{risk_level.title()}' if risk_level in ['HIGH', 'MEDIUM', 'LOW'] else 'Normal'
        risk_text = f"Risk Level: {risk_level} (Safety Score: {risk_score}/10)"
        content.append(Paragraph(risk_text, self.styles.get(risk_style, self.styles['Normal'])))
        content.append(Spacer(1, 0.3*cm))
        
        # Risk explanation
        explanation = risk.get('explanation', 'No explanation available.')
        content.append(Paragraph(explanation, self.styles['Normal']))
        content.append(Spacer(1, 0.5*cm))
        
        return content
    
    def _build_domain_section(self, data: Dict) -> list:
        """Build domain information section"""
        content = []
        
        content.append(Paragraph("1. DOMAIN REGISTRATION DETAILS", self.styles['SectionHeader']))
        
        domain_info = data.get('domain_info', {})
        
        # Format status codes - clean up WHOIS status URLs
        raw_status = domain_info.get('status', [])
        if isinstance(raw_status, list) and raw_status:
            # Extract just the status name (before any URL)
            cleaned_status = []
            for s in raw_status[:5]:  # Limit to 5 statuses
                if isinstance(s, str):
                    # Take only the status name (e.g., "clientTransferProhibited" from "clientTransferProhibited https://...")
                    status_name = s.split()[0] if ' ' in s else s
                    cleaned_status.append(f"• {status_name}")
            status_display = Paragraph('<br/>'.join(cleaned_status), self.styles['Normal'])
        else:
            status_display = 'N/A'
        
        # Format nameservers as bullet list
        nameservers = domain_info.get('nameservers', [])
        if nameservers:
            ns_formatted = [f"• {ns}" for ns in nameservers[:4]]  # Limit to 4 nameservers
            nameservers_display = Paragraph('<br/>'.join(ns_formatted), self.styles['Normal'])
        else:
            nameservers_display = 'N/A'
        
        domain_data = [
            ['Field', 'Value'],
            ['Registrar', domain_info.get('registrar', 'N/A')],
            ['Registration Date', domain_info.get('creation_date', 'N/A')],
            ['Expiry Date', domain_info.get('expiry_date', 'N/A')],
            ['Domain Age', f"{domain_info.get('domain_age_days', 'N/A')} days"],
            ['Status', status_display],
            ['Nameservers', nameservers_display],
        ]
        
        domain_table = Table(domain_data, colWidths=[5*cm, 12*cm])
        domain_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#34495e')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ]))
        
        content.append(domain_table)
        content.append(Spacer(1, 0.5*cm))
        
        return content
    
    def _build_hosting_section(self, data: Dict) -> list:
        """Build hosting information section"""
        content = []
        
        content.append(Paragraph("2. HOSTING & NETWORK INFORMATION", self.styles['SectionHeader']))
        
        hosting_info = data.get('hosting_info', {})
        
        hosting_data = [
            ['Field', 'Value'],
            ['IP Address', hosting_info.get('ip_address', 'N/A')],
            ['Country', hosting_info.get('country', 'N/A')],
            ['City', hosting_info.get('city', 'N/A')],
            ['ISP/Provider', hosting_info.get('isp', 'N/A')],
            ['ASN', hosting_info.get('asn', 'N/A')],
            ['Organization', hosting_info.get('organization', 'N/A')],
            ['Hosting Type', hosting_info.get('hosting_type', 'Unknown').title()],
        ]
        
        hosting_table = Table(hosting_data, colWidths=[5*cm, 12*cm])
        hosting_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#34495e')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ]))
        
        content.append(hosting_table)
        content.append(Spacer(1, 0.5*cm))
        
        return content
    
    def _build_security_section(self, data: Dict) -> list:
        """Build security analysis section"""
        content = []
        
        content.append(Paragraph("3. SECURITY ANALYSIS", self.styles['SectionHeader']))
        
        security_info = data.get('security_info', {})
        
        security_data = [
            ['Field', 'Status'],
            ['HTTPS Enabled', '✓ Yes' if security_info.get('https_enabled') else '✗ No'],
            ['SSL Certificate Valid', '✓ Yes' if security_info.get('ssl_valid') else '✗ No'],
            ['SSL Issuer', security_info.get('ssl_issuer', 'N/A')],
            ['Blacklisted', '⚠ Yes' if security_info.get('blacklisted') else '✓ No'],
        ]
        
        security_table = Table(security_data, colWidths=[5*cm, 12*cm])
        security_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#34495e')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ]))
        
        content.append(security_table)
        content.append(Spacer(1, 0.5*cm))
        
        return content
    
    def _build_risk_section(self, data: Dict) -> list:
        """Build risk assessment section - MOST IMPORTANT"""
        content = []
        
        content.append(Paragraph("4. RISK ASSESSMENT", self.styles['SectionHeader']))
        
        risk = data.get('risk_assessment', {})
        
        # Risk level summary
        content.append(Paragraph("Assessment Method", self.styles['SubSection']))
        content.append(Paragraph(
            "This assessment is based on rule-based analysis of domain characteristics. "
            "No artificial intelligence or machine learning predictions are used. "
            "All factors are transparently evaluated against established cybercrime indicators.",
            self.styles['Normal']
        ))
        content.append(Spacer(1, 0.3*cm))
        
        # Risk factors
        reasons = risk.get('reasons', [])
        if reasons:
            content.append(Paragraph("Contributing Risk Factors:", self.styles['SubSection']))
            
            for i, reason in enumerate(reasons, 1):
                content.append(Paragraph(f"{i}. {reason}", self.styles['Normal']))
            
            content.append(Spacer(1, 0.3*cm))
        
        # Confidence level
        confidence = risk.get('confidence', 'unknown')
        content.append(Paragraph(
            f"Assessment Confidence: {confidence.upper()}",
            self.styles['SubSection']
        ))
        content.append(Spacer(1, 0.5*cm))
        
        return content
    
    def _build_footer(self, data: Dict) -> list:
        """Build report footer"""
        content = []
        
        content.append(Spacer(1, 1*cm))
        content.append(Paragraph("_" * 80, self.styles['Normal']))
        content.append(Spacer(1, 0.3*cm))
        
        footer_text = (
            "<i>This report is generated by DomainIntel, an automated domain intelligence system. "
            "The information provided is based on publicly available data and should be verified "
            "through additional investigation methods. This report is intended for law enforcement "
            "use only.</i>"
        )
        content.append(Paragraph(footer_text, self.styles['Normal']))
        
        return content