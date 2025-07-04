from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from .models import Invitado
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.utils import timezone
import json
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Count
from django.http import HttpResponse
import csv
from datetime import datetime




def mostrar_qr(request, token):
    """Vista para mostrar QR individual"""
    invitado = get_object_or_404(Invitado, token_qr=token)
    
    context = {
        'invitado': invitado,
        'titulo': f'QR - {invitado.nombre_completo}'
    }
    
    return render(request, 'invitados/mostrar_qr.html', context)

def lista_invitados(request):
    """Vista para listar todos los invitados"""
    invitados = Invitado.objects.all().order_by('nombre_completo')
    
    context = {
        'invitados': invitados,
        'titulo': 'Lista de Invitados'
    }
    
    return render(request, 'invitados/lista_invitados.html', context)

def escaner_qr(request):
    """Vista principal del escáner QR"""
    context = {
        'titulo': 'Escáner QR - Control de Acceso'
    }
    return render(request, 'invitados/escaner_qr.html', context)

@csrf_exempt
@require_POST

@csrf_exempt
@require_POST
def procesar_qr(request):
    """Vista para procesar el QR escaneado vía AJAX"""
    try:
        data = json.loads(request.body)
        token_qr = data.get('token_qr', '').strip()
        dispositivo = data.get('dispositivo', 'Dispositivo desconocido')
        
        if not token_qr:
            return JsonResponse({
                'success': False,
                'error': 'Token QR vacío',
                'message': 'No se pudo leer el código QR'
            })
        
        # Buscar el invitado por token
        try:
            invitado = Invitado.objects.get(token_qr=token_qr)
        except Invitado.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'TOKEN_NO_ENCONTRADO',
                'message': 'Código QR no válido o no encontrado'
            })
        
        # Verificar si ya asistió
        if invitado.asistio:
            return JsonResponse({
                'success': False,
                'error': 'YA_ESCANEADO',
                'message': f'{invitado.nombre_completo} ya registró su entrada',
                'invitado': {
                    'nombre': invitado.nombre_completo,
                    'puesto': invitado.puesto_cargo,
                    'hora_entrada': invitado.hora_entrada_formateada,
                    'foto': invitado.fotografia.url if invitado.fotografia else None
                }
            })
        
        # Marcar asistencia
        if invitado.marcar_asistencia(dispositivo):
            return JsonResponse({
                'success': True,
                'message': f'¡Bienvenido {invitado.nombre_completo}!',
                'invitado': {
                    'nombre': invitado.nombre_completo,
                    'puesto': invitado.puesto_cargo,
                    'hora_entrada': invitado.hora_entrada_formateada,
                    'foto': invitado.fotografia.url if invitado.fotografia else None
                }
            })
        else:
            return JsonResponse({
                'success': False,
                'error': 'ERROR_ASISTENCIA',
                'message': 'Error al registrar la asistencia'
            })
            
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'JSON_ERROR',
            'message': 'Datos inválidos recibidos'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': 'ERROR_SERVIDOR',
            'message': f'Error del servidor: {str(e)}'
        })

def estadisticas_tiempo_real(request):
    """Vista para obtener estadísticas en tiempo real"""
    total_invitados = Invitado.objects.count()
    total_asistentes = Invitado.objects.filter(asistio=True).count()
    porcentaje_asistencia = (total_asistentes / total_invitados * 100) if total_invitados > 0 else 0
    
    # Últimas 5 llegadas
    ultimas_llegadas = Invitado.objects.filter(
        asistio=True
    ).order_by('-fecha_hora_entrada')[:5]
    
    llegadas_data = []
    for invitado in ultimas_llegadas:
        llegadas_data.append({
            'nombre': invitado.nombre_completo,
            'puesto': invitado.puesto_cargo,
            'hora': invitado.hora_entrada_formateada,
            'foto': invitado.fotografia.url if invitado.fotografia else None
        })
    
    return JsonResponse({
        'total_invitados': total_invitados,
        'total_asistentes': total_asistentes,
        'porcentaje_asistencia': round(porcentaje_asistencia, 1),
        'ultimas_llegadas': llegadas_data
    })

def mostrar_qr(request, token):
    """Vista para mostrar QR individual"""
    invitado = get_object_or_404(Invitado, token_qr=token)
    
    context = {
        'invitado': invitado,
        'titulo': f'QR - {invitado.nombre_completo}'
    }
    
    return render(request, 'invitados/mostrar_qr.html', context)

def lista_invitados(request):
    """Vista para listar todos los invitados"""
    invitados = Invitado.objects.all().order_by('nombre_completo')
    
    context = {
        'invitados': invitados,
        'titulo': 'Lista de Invitados'
    }
    
    return render(request, 'invitados/lista_invitados.html', context)
# Agregar estas importaciones al inicio del archivo
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Count
from django.http import HttpResponse
import csv
from datetime import datetime

# Agregar esta vista
@staff_member_required
def panel_control(request):
    """Panel de control administrativo"""
    # Estadísticas generales
    total_invitados = Invitado.objects.count()
    total_asistentes = Invitado.objects.filter(asistio=True).count()
    total_no_asistentes = total_invitados - total_asistentes
    porcentaje_asistencia = (total_asistentes / total_invitados * 100) if total_invitados > 0 else 0
    
    # Invitados recientes (últimos 10)
    asistentes_recientes = Invitado.objects.filter(
        asistio=True
    ).order_by('-fecha_hora_entrada')[:10]
    
    # Invitados que no han llegado
    no_asistentes = Invitado.objects.filter(asistio=False).order_by('nombre_completo')
    
    context = {
        'titulo': 'Panel de Control - Evento',
        'total_invitados': total_invitados,
        'total_asistentes': total_asistentes,
        'total_no_asistentes': total_no_asistentes,
        'porcentaje_asistencia': round(porcentaje_asistencia, 1),
        'asistentes_recientes': asistentes_recientes,
        'no_asistentes': no_asistentes,
    }
    
    return render(request, 'invitados/panel_control.html', context)

@staff_member_required
def exportar_asistencia_csv(request):
    """Exportar lista de asistencia a CSV"""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="asistencia_evento_{datetime.now().strftime("%Y%m%d_%H%M")}.csv"'
    response.write('\ufeff')  # BOM para UTF-8
    
    writer = csv.writer(response)
    
    # Encabezados
    writer.writerow([
        'Nombre Completo',
        'Puesto/Cargo', 
        'Asistió',
        'Fecha y Hora de Entrada',
        'Escaneado Por',
        'Token QR'
    ])
    
    # Datos de todos los invitados
    invitados = Invitado.objects.all().order_by('nombre_completo')
    
    for invitado in invitados:
        writer.writerow([
            invitado.nombre_completo,
            invitado.puesto_cargo,
            'Sí' if invitado.asistio else 'No',
            invitado.hora_entrada_formateada if invitado.asistio else '',
            invitado.escaneado_por if invitado.asistio else '',
            invitado.token_qr
        ])
    
    return response

def offline_page(request):
    """Página para mostrar cuando no hay conexión"""
    return render(request, 'pwa/offline.html')