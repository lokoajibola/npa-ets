from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.units import inch, cm
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os
from django.conf import settings
import tempfile
from decimal import Decimal
from datetime import datetime

def generate_boq_pdf(project, stage, boq_items, form_data):
    """Generate BOQ/BEME PDF document"""
    
    # Create temporary file
    temp_dir = tempfile.mkdtemp()
    filename = f"BOQ_{project.project_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    filepath = os.path.join(temp_dir, filename)
    
    # Create document with landscape orientation for wide tables
    doc = SimpleDocTemplate(
        filepath,
        pagesize=landscape(A4),
        rightMargin=0.5*inch,
        leftMargin=0.5*inch,
        topMargin=0.5*inch,
        bottomMargin=0.5*inch
    )
    
    # Register fonts
    try:
        pdfmetrics.registerFont(TTFont('Helvetica', 'Helvetica.ttf'))
        pdfmetrics.registerFont(TTFont('Helvetica-Bold', 'Helvetica-Bold.ttf'))
    except:
        pass  # Use default fonts
    
    # Create styles
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        alignment=TA_CENTER,
        spaceAfter=12,
        fontName='Helvetica-Bold'
    )
    
    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Heading2'],
        fontSize=12,
        alignment=TA_CENTER,
        spaceAfter=6,
        fontName='Helvetica'
    )
    
    header_style = ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontSize=9,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold',
        textColor=colors.white
    )
    
    cell_style = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontSize=8,
        alignment=TA_LEFT,
        fontName='Helvetica'
    )
    
    amount_style = ParagraphStyle(
        'AmountCell',
        parent=styles['Normal'],
        fontSize=8,
        alignment=TA_RIGHT,
        fontName='Helvetica'
    )
    
    section_style = ParagraphStyle(
        'SectionHeader',
        parent=styles['Normal'],
        fontSize=9,
        alignment=TA_LEFT,
        fontName='Helvetica-Bold',
        backColor=colors.lightgrey,
        textColor=colors.black
    )
    
    # Build story
    story = []
    
    # Header with NPA Logo
    header_data = [
        [
            Paragraph("NIGERIAN PORTS AUTHORITY", title_style),
        ],
        [
            Paragraph("ENGINEERING DEPARTMENT", subtitle_style),
        ],
        [
            Paragraph("BILL OF ENGINEERING MEASUREMENT & EVALUATION (BEME)", title_style),
        ],
    ]
    
    header_table = Table(header_data, colWidths=[doc.width])
    story.append(header_table)
    story.append(Spacer(1, 0.2*inch))
    
    # Project Information
    project_info = [
        ["PROJECT TITLE:", project.title],
        ["PROJECT ID:", project.project_id],
        ["LOCATION:", project.location],
        ["BOQ NUMBER:", form_data.get('boq_number', '')],
        ["DATE:", form_data.get('boq_date', datetime.now().strftime('%d-%m-%Y'))],
        ["PREPARED BY:", form_data.get('prepared_by', '')],
    ]
    
    if form_data.get('reviewed_by'):
        project_info.append(["REVIEWED BY:", form_data.get('reviewed_by')])
    if form_data.get('approved_by'):
        project_info.append(["APPROVED BY:", form_data.get('approved_by')])
    
    project_table = Table(project_info, colWidths=[2*inch, 4*inch])
    project_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    
    story.append(project_table)
    story.append(Spacer(1, 0.3*inch))
    
    # BOQ Table Header
    table_header = [
        [
            Paragraph("S/N", header_style),
            Paragraph("DESCRIPTION OF ITEM", header_style),
            Paragraph("QTY", header_style),
            Paragraph("UNIT", header_style),
            Paragraph("RATE (₦)", header_style),
            Paragraph("AMOUNT (₦)", header_style),
            Paragraph("REMARKS", header_style),
        ]
    ]
    
    # Prepare table data
    table_data = table_header.copy()
    current_section = None
    row_index = 1  # Start after header
    
    # Group items by section
    sections = {}
    for item in boq_items:
        section = item.section or 'Main'
        if section not in sections:
            sections[section] = []
        sections[section].append(item)
    
    # Calculate totals
    section_totals = {}
    grand_total = Decimal('0')
    
    for section_name, items in sections.items():
        # Add section header row
        section_total = Decimal('0')
        table_data.append([
            Paragraph("", cell_style),
            Paragraph(f"<b>{section_name.upper()}</b>", section_style),
            Paragraph("", cell_style),
            Paragraph("", cell_style),
            Paragraph("", cell_style),
            Paragraph("", cell_style),
            Paragraph("", cell_style),
        ])
        row_index += 1
        
        # Add items in this section
        for idx, item in enumerate(items, 1):
            amount = item.quantity * item.rate
            section_total += amount
            
            table_data.append([
                Paragraph(str(idx), cell_style),
                Paragraph(item.description, cell_style),
                Paragraph(f"{item.quantity:,.2f}", amount_style),
                Paragraph(item.unit.upper(), cell_style),
                Paragraph(f"{item.rate:,.2f}", amount_style),
                Paragraph(f"{amount:,.2f}", amount_style),
                Paragraph(item.notes or "", cell_style),
            ])
            row_index += 1
        
        section_totals[section_name] = section_total
        grand_total += section_total
        
        # Add section total row
        table_data.append([
            Paragraph("", cell_style),
            Paragraph(f"<b>SUB-TOTAL FOR {section_name.upper()}</b>", cell_style),
            Paragraph("", cell_style),
            Paragraph("", cell_style),
            Paragraph("", cell_style),
            Paragraph(f"<b>{section_total:,.2f}</b>", amount_style),
            Paragraph("", cell_style),
        ])
        row_index += 1
    
    # Add summary section
    story.append(Spacer(1, 0.2*inch))
    
    # Create BOQ table
    col_widths = [0.4*inch, 4.5*inch, 0.6*inch, 0.6*inch, 1.2*inch, 1.2*inch, 1.5*inch]
    boq_table = Table(table_data, colWidths=col_widths, repeatRows=1)
    
    # Apply table styles
    boq_table.setStyle(TableStyle([
        # Header style
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#003087')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('TOPPADDING', (0, 0), (-1, 0), 8),
        
        # Grid lines
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('ALIGN', (2, 1), (2, -1), 'RIGHT'),  # QTY column right aligned
        ('ALIGN', (4, 1), (5, -1), 'RIGHT'),  # Rate and Amount columns right aligned
        
        # Section header background
        ('BACKGROUND', (0, 1), (-1, 1), colors.lightgrey),
        
        # Alternating row colors
        ('ROWBACKGROUNDS', (0, 2), (-1, -1), [colors.white, colors.whitesmoke]),
        
        # Section total rows
        ('BACKGROUND', (0, -len(sections)*2), (-1, -1), colors.HexColor('#e8f5e8')),
        ('FONTNAME', (0, -len(sections)*2), (-1, -1), 'Helvetica-Bold'),
        
        # Cell padding
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        
        # Valign all cells
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    
    story.append(boq_table)
    story.append(Spacer(1, 0.3*inch))
    
    # Financial Summary
    contingency_percent = Decimal('5.0')
    vat_percent = Decimal('7.5')
    
    contingency = grand_total * (contingency_percent / Decimal('100'))
    vat = grand_total * (vat_percent / Decimal('100'))
    grand_total_with_taxes = grand_total + contingency + vat
    
    summary_data = [
        ["SUMMARY", "AMOUNT (₦)"],
        ["Total Cost of Works:", f"{grand_total:,.2f}"],
        [f"Contingency ({contingency_percent}%):", f"{contingency:,.2f}"],
        [f"VAT ({vat_percent}%):", f"{vat:,.2f}"],
        ["<b>GRAND TOTAL:</b>", f"<b>{grand_total_with_taxes:,.2f}</b>"],
    ]
    
    summary_table = Table(summary_data, colWidths=[3*inch, 2*inch])
    summary_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('BACKGROUND', (0, 0), (1, 0), colors.HexColor('#003087')),
        ('TEXTCOLOR', (0, 0), (1, 0), colors.white),
        ('BACKGROUND', (0, -1), (1, -1), colors.HexColor('#d4edda')),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
    ]))
    
    story.append(summary_table)
    story.append(Spacer(1, 0.2*inch))
    
    # Amount in words
    amount_words = number_to_words(grand_total_with_taxes)
    words_para = Paragraph(f"<b>Amount in Words:</b> {amount_words}", 
                          ParagraphStyle('WordsStyle', parent=styles['Normal'], fontSize=9))
    story.append(words_para)
    
    # Footer
    story.append(Spacer(1, 0.5*inch))
    
    footer_data = [
        ["_________________________", "_________________________", "_________________________"],
        ["Prepared By", "Reviewed By", "Approved By"],
        [form_data.get('prepared_by', ''), form_data.get('reviewed_by', ''), form_data.get('approved_by', '')],
        ["", "", f"Date: {datetime.now().strftime('%d-%m-%Y')}"],
    ]
    
    footer_table = Table(footer_data, colWidths=[doc.width/3]*3)
    footer_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    
    story.append(footer_table)
    
    # Disclaimer
    disclaimer = Paragraph(
        "<i>This is a computer-generated document. No signature is required.</i>",
        ParagraphStyle('Disclaimer', parent=styles['Normal'], fontSize=8, alignment=TA_CENTER)
    )
    story.append(Spacer(1, 0.2*inch))
    story.append(disclaimer)
    
    # Build PDF
    doc.build(story)
    
    return filepath, filename

def number_to_words(num):
    """Convert number to words (Nigerian format)"""
    if isinstance(num, Decimal):
        num = float(num)
    
    import math
    
    def convert_to_words(n):
        ones = ["", "One", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine", 
                "Ten", "Eleven", "Twelve", "Thirteen", "Fourteen", "Fifteen", "Sixteen", 
                "Seventeen", "Eighteen", "Nineteen"]
        tens = ["", "", "Twenty", "Thirty", "Forty", "Fifty", "Sixty", "Seventy", "Eighty", "Ninety"]
        
        if n < 20:
            return ones[n]
        elif n < 100:
            return tens[n // 10] + (" " + ones[n % 10] if n % 10 != 0 else "")
        elif n < 1000:
            return ones[n // 100] + " Hundred" + (" " + convert_to_words(n % 100) if n % 100 != 0 else "")
        elif n < 1000000:
            return convert_to_words(n // 1000) + " Thousand" + (" " + convert_to_words(n % 1000) if n % 1000 != 0 else "")
        elif n < 1000000000:
            return convert_to_words(n // 1000000) + " Million" + (" " + convert_to_words(n % 1000000) if n % 1000000 != 0 else "")
        else:
            return convert_to_words(n // 1000000000) + " Billion" + (" " + convert_to_words(n % 1000000000) if n % 1000000000 != 0 else "")
    
    # Separate naira and kobo
    naira = int(num)
    kobo = int(round((num - naira) * 100))
    
    words = ""
    if naira > 0:
        words = convert_to_words(naira) + " Naira"
    if kobo > 0:
        if words:
            words += " "
        words += convert_to_words(kobo) + " Kobo"
    
    if not words:
        words = "Zero Naira"
    
    return words + " Only"

def add_page_number(canvas, doc):
    """Add page numbers to PDF"""
    page_num = canvas.getPageNumber()
    text = f"Page {page_num}"
    canvas.setFont("Helvetica", 8)
    canvas.drawRightString(doc.width + doc.rightMargin, 0.5*inch, text)