import os
from io import BytesIO
from django.http import HttpResponse
from django.conf import settings
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, mm
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from PIL import Image as PILImage
from .models import Invitado

def generar_pdf_qr_invitados():
    """
    Genera un PDF con todos los códigos QR de los invitados
    organizados en un grid de 5 columnas
    """
    # Crear buffer en memoria
    buffer = BytesIO()
    
    # Configurar documento PDF
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=10*mm,
        leftMargin=10*mm,
        topMargin=15*mm,
        bottomMargin=10*mm
    )
    
    # Lista para elementos del PDF
    elements = []
    
    # Estilos
    styles = getSampleStyleSheet()
    
    # Estilo personalizado para el título
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        spaceAfter=20,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#00A693')
    )
    
    # Estilo para subtítulo
    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Normal'],
        fontSize=12,
        spaceAfter=15,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#666666')
    )
    
    # Agregar título
    title = Paragraph("CÓDIGOS QR - CONTROL DE ASISTENCIA", title_style)
    elements.append(title)
    
    # Agregar subtítulo
    subtitle = Paragraph("Gobierno de Chiapas - Fiestas Patrias", subtitle_style)
    elements.append(subtitle)
    
    # Espacio

    elements.append(Spacer(1, 5*mm))
    
    # Obtener todos los invitados ordenados por nombre
    invitados = Invitado.objects.all().order_by('nombre_completo')
    
    if not invitados:
        # Si no hay invitados
        no_data = Paragraph("No hay invitados registrados", styles['Normal'])
        elements.append(no_data)
    else:
        # Crear datos para la tabla (5 columnas)
        data = []
        row = []
        
        for i, invitado in enumerate(invitados):
            # Crear celda para cada invitado
            cell_content = crear_celda_invitado(invitado)
            row.append(cell_content)
            
            # Si completamos 5 columnas o es el último invitado
            if len(row) == 5 or i == len(invitados) - 1:
                # Completar fila con celdas vacías si es necesario
                while len(row) < 5:
                    row.append("")
                
                data.append(row)
                row = []
        
        # Crear tabla
        table = Table(
            data,
            colWidths=[38*mm] * 5,  # 5 columnas de 35mm cada una
            rowHeights=40*mm  # Altura de cada filz
        )
        
        # Estilo de la tabla
        table.setStyle(TableStyle([
        # Bordes más sutiles (opcional)
        ('GRID', (0, 0), (-1, -1), 0.25, colors.lightgrey),  # antes 0.5
        # Alineación
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        # Paddings más pequeños
        ('LEFTPADDING', (0, 0), (-1, -1), 0.5*mm),   # antes 2*mm
        ('RIGHTPADDING', (0, 0), (-1, -1), 0.5*mm),  # antes 2*mm
        ('TOPPADDING', (0, 0), (-1, -1), 0.5*mm),    # antes 2*mm
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0.5*mm), # antes 2*mm
    ]))

        
        elements.append(table)
    
    # Generar PDF
    doc.build(elements)
    
    # Obtener contenido del buffer
    pdf_content = buffer.getvalue()
    buffer.close()
    
    return pdf_content

def crear_celda_invitado(invitado):
    """
    Crea el contenido de una celda individual para un invitado
    """
    from reportlab.platypus import Paragraph
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.lib.enums import TA_CENTER
    from reportlab.lib import colors
    
    # Verificar si el QR existe
    if invitado.qr_imagen and os.path.exists(invitado.qr_imagen.path):
        try:
            # Crear imagen QR
            qr_img = Image(
                invitado.qr_imagen.path,
                width=32*mm,
                height=32*mm
            )
            
            # Estilo para el nombre
            name_style = ParagraphStyle(
                'InvitadoName',
                fontSize=8,
                alignment=TA_CENTER,
                spaceAfter=2,
                textColor=colors.black,
                leading=8
            )
            
            # Crear párrafo con el nombre (máximo 2 líneas)
            nombre_texto = invitado.nombre_completo.upper()
            if len(nombre_texto) > 25:  # Si es muy largo, truncar
                nombre_texto = nombre_texto[:22] + "..."
            
            nombre_p = Paragraph(nombre_texto, name_style)
            
            # Combinar QR y nombre en una tabla vertical
            cell_data = [
                [qr_img],
                [nombre_p]
            ]
            
            cell_table = Table(
                cell_data,
                colWidths=[36*mm],
                  rowHeights=[30*mm, 10*mm]
            )
            
            cell_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (0, 0), 'MIDDLE'),
            ('VALIGN', (0, 1), (0, 1), 'TOP'),
            # Paddings internos mínimos
            ('LEFTPADDING', (0, 0), (-1, -1), 0.25*mm),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0.25*mm),
            ('TOPPADDING', (0, 0), (-1, -1), 0.25*mm),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 0.25*mm),
        ]))
            
            return cell_table
            
        except Exception as e:
            print(f"Error al procesar QR de {invitado.nombre_completo}: {e}")
            # Fallback: solo texto
            return Paragraph(f"SIN QR\n{invitado.nombre_completo}", ParagraphStyle(
                'Error',
                fontSize=8,
                alignment=TA_CENTER,
                textColor=colors.red
            ))
    else:
        # Sin QR, mostrar solo texto
        return Paragraph(f"SIN QR\n{invitado.nombre_completo}", ParagraphStyle(
            'NoQR',
            fontSize=8,
            alignment=TA_CENTER,
            textColor=colors.grey
        ))