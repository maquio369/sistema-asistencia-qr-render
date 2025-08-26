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
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from .forms import CustomLoginForm
from .forms import InvitadoForm
from django.contrib import messages
import pytz
from django.db import transaction


def login_view(request):
    """Vista para el login"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = CustomLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            
            # Redirigir según el usuario
            next_url = request.GET.get('next', 'dashboard')
            messages.success(request, f'¡Bienvenido {user.get_full_name() or user.username}!')
            return redirect(next_url)
        else:
            messages.error(request, 'Usuario o contraseña incorrectos.')
    else:
        form = CustomLoginForm()
    
    context = {
        'form': form,
        'titulo': 'Iniciar Sesión - Sistema QR'
    }
    
    return render(request, 'invitados/login.html', context)

def logout_view(request):
    """Vista para cerrar sesión"""
    logout(request)
    messages.success(request, 'Sesión cerrada exitosamente.')
    return redirect('login')

@login_required
def dashboard(request):
    """Panel principal después del login"""
    # Estadísticas generales
    total_invitados = Invitado.objects.count()
    total_asistentes = Invitado.objects.filter(asistio=True).count()
    porcentaje_asistencia = (total_asistentes / total_invitados * 100) if total_invitados > 0 else 0
    
    # Invitados recientes
    invitados_recientes = Invitado.objects.order_by('-fecha_creacion')[:3]
 
    
    context = {
        'titulo': 'Dashboard - Sistema QR',
        'total_invitados': total_invitados,
        'total_asistentes': total_asistentes,
        'porcentaje_asistencia': round(porcentaje_asistencia, 1),
        'invitados_recientes': invitados_recientes,
        'usuario': request.user,
    }
    
    return render(request, 'invitados/dashboard.html', context)


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

        if not request.body:
         return JsonResponse({
            'success': False,
            'error': 'BODY_VACIO',
            'message': 'El cuerpo de la petición está vacío'
        }, status=400)


        data = json.loads(request.body)
        token_qr = data.get('token_qr', '').strip()
        dispositivo = data.get('dispositivo', 'Dispositivo desconocido')
            
        if not token_qr:
            return JsonResponse({
                'success': False,
                'error': 'Token QR vacío',
                'message': 'No se pudo leer el código QR'
            })
        
        if len(token_qr) < 30 or len(token_qr) > 50:
            return JsonResponse({
                'success': False,
                'error': 'TOKEN_FORMATO_INVALIDO',
                'message': 'Formato de código QR inválido'
            })






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
    mexico_tz = pytz.timezone('America/Mexico_City')
    for invitado in ultimas_llegadas:
        try:
            if invitado.fecha_hora_entrada:
                if invitado.fecha_hora_entrada.tzinfo is None:
                    utc_time = pytz.UTC.localize(invitado.fecha_hora_entrada)
                    hora_local = utc_time.astimezone(mexico_tz)
                else:
                    hora_local = invitado.fecha_hora_entrada.astimezone(mexico_tz)
                hora_formateada = hora_local.strftime('%d/%m/%Y %H:%M:%S')
            else:
                hora_formateada = "No registrada"
        except Exception as e:
            print(f"Error al formatear hora para {invitado.nombre_completo}: {e}")
            hora_formateada = invitado.hora_entrada_formateada
        
        # CORREGIDO: Siempre agregar el invitado a la lista
        llegadas_data.append({
            'nombre': invitado.nombre_completo,
            'puesto': invitado.puesto_cargo,
            'hora': hora_formateada,
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
@login_required
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

@login_required
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


@login_required
def crear_invitado(request):
    """Vista para crear nuevo invitado via formulario web"""
    if request.method == 'POST':
        form = InvitadoForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                invitado = form.save()
                messages.success(
                    request, 
                    f'✅ Invitado "{invitado.nombre_completo}" creado exitosamente. QR generado automáticamente.'
                )
                return redirect('crear_invitado')
            except Exception as e:
                messages.error(request, f'❌ Error al crear invitado: {str(e)}')
        else:
            messages.error(request, '❌ Por favor corrige los errores en el formulario.')
    else:
        form = InvitadoForm()
    
    # Estadísticas para mostrar en la página
    total_invitados = Invitado.objects.count()
    invitados_recientes = Invitado.objects.order_by('-fecha_creacion')[:3]  # ← Solo 3 registros
    
    context = {
        'form': form,
        'titulo': 'Registrar Nuevo Invitado',
        'total_invitados': total_invitados,
        'invitados_recientes': invitados_recientes,
    }
    
    return render(request, 'invitados/crear_invitado.html', context)

def ver_invitado_qr(request, invitado_id):
    """Vista para ver el QR de un invitado específico por ID"""
    invitado = get_object_or_404(Invitado, id=invitado_id)
    
    context = {
        'invitado': invitado,
        'titulo': f'QR - {invitado.nombre_completo}'
    }
    
    return render(request, 'invitados/mostrar_qr.html', context)
@csrf_exempt
@require_POST
@login_required
def marcar_asistencia_manual(request):
    """Vista para marcar asistencia manualmente desde la lista de invitados - VERSIÓN CORREGIDA"""
    
    # NUEVA VALIDACIÓN: Verificar que el body no esté vacío
    if not request.body:
        return JsonResponse({
            'success': False,
            'error': 'BODY_VACIO',
            'message': 'El cuerpo de la petición está vacío'
        }, status=400)
    
    try:
        data = json.loads(request.body)
        invitado_id = data.get('invitado_id')
        accion = data.get('accion', 'marcar')  # 'marcar' o 'desmarcar'
        
        if not invitado_id:
            return JsonResponse({
                'success': False,
                'error': 'ID de invitado requerido',
                'message': 'No se proporcionó el ID del invitado'
            })
        
        # NUEVA VALIDACIÓN: Verificar formato UUID
        try:
            import uuid
            uuid.UUID(invitado_id)
        except (ValueError, TypeError):
            return JsonResponse({
                'success': False,
                'error': 'ID_INVALIDO',
                'message': 'ID de invitado inválido'
            })
        
        # NUEVA VALIDACIÓN: Verificar acción válida
        if accion not in ['marcar', 'desmarcar']:
            return JsonResponse({
                'success': False,
                'error': 'ACCION_INVALIDA',
                'message': 'Acción no válida'
            })
        
        # CORRECCIÓN PRINCIPAL: Usar transacciones atómicas para evitar condiciones de carrera
        from django.db import transaction
        
        try:
            with transaction.atomic():
                # Usar select_for_update() para evitar condiciones de carrera
                invitado = Invitado.objects.select_for_update().get(id=invitado_id)
                
                if accion == 'marcar':
                    # Verificar si ya está marcado (con datos frescos de la DB)
                    if invitado.asistio:
                        return JsonResponse({
                            'success': False,
                            'error': 'YA_MARCADO',
                            'message': f'{invitado.nombre_completo} ya tiene su asistencia marcada',
                            'invitado': {
                                'id': str(invitado.id),
                                'nombre': invitado.nombre_completo,
                                'puesto': invitado.puesto_cargo,
                                'asistio': invitado.asistio,
                                'hora_entrada': invitado.hora_entrada_formateada,
                                'foto': invitado.fotografia.url if invitado.fotografia else None
                            }
                        })
                    
                    # Marcar asistencia manualmente usando el método del modelo (que ya es thread-safe)
                    dispositivo = f"Registro Manual - {request.user.username} - {timezone.now().strftime('%d/%m/%Y %H:%M:%S')}"
                    
                    if invitado.marcar_asistencia(dispositivo):
                        return JsonResponse({
                            'success': True,
                            'message': f'✅ Asistencia marcada para {invitado.nombre_completo}',
                            'invitado': {
                                'id': str(invitado.id),
                                'nombre': invitado.nombre_completo,
                                'puesto': invitado.puesto_cargo,
                                'asistio': invitado.asistio,
                                'hora_entrada': invitado.hora_entrada_formateada,
                                'foto': invitado.fotografia.url if invitado.fotografia else None
                            }
                        })
                    else:
                        return JsonResponse({
                            'success': False,
                            'error': 'ERROR_MARCADO',
                            'message': 'Error al marcar la asistencia'
                        })
                        
                elif accion == 'desmarcar':
                    # Verificar si no está marcado (con datos frescos de la DB)
                    if not invitado.asistio:
                        return JsonResponse({
                            'success': False,
                            'error': 'NO_MARCADO',
                            'message': f'{invitado.nombre_completo} no tiene asistencia marcada'
                        })
                    
                    # Desmarcar asistencia de forma atómica
                    invitado.asistio = False
                    invitado.fecha_hora_entrada = None
                    invitado.escaneado_por = f"Desmarcado por {request.user.username} - {timezone.now().strftime('%d/%m/%Y %H:%M:%S')}"
                    invitado.save()
                    
                    return JsonResponse({
                        'success': True,
                        'message': f'❌ Asistencia desmarcada para {invitado.nombre_completo}',
                        'invitado': {
                            'id': str(invitado.id),
                            'nombre': invitado.nombre_completo,
                            'puesto': invitado.puesto_cargo,
                            'asistio': invitado.asistio,
                            'hora_entrada': invitado.hora_entrada_formateada,
                            'foto': invitado.fotografia.url if invitado.fotografia else None
                        }
                    })
                    
        except Invitado.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'INVITADO_NO_ENCONTRADO',
                'message': 'Invitado no encontrado'
            })
        except Exception as e:
            print(f"Error en transacción de asistencia manual: {e}")
            return JsonResponse({
                'success': False,
                'error': 'ERROR_TRANSACCION',
                'message': 'Error al procesar la operación'
            }, status=500)
            
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'JSON_ERROR',
            'message': 'Datos inválidos recibidos'
        }, status=400)
    except Exception as e:
        print(f"Error inesperado en marcar_asistencia_manual: {e}")
        return JsonResponse({
            'success': False,
            'error': 'ERROR_SERVIDOR',
            'message': 'Error interno del servidor'
        }, status=500)