from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import UserProfile

def role_required(*allowed_roles):
    """
    Decorador que verifica si el usuario tiene uno de los roles permitidos
    Uso: @role_required('admin', 'registro')
    """
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def _wrapped_view(request, *args, **kwargs):
            try:
                # Intentar obtener el perfil del usuario
                user_profile = UserProfile.objects.get(user=request.user)
                user_role = user_profile.rol
            except UserProfile.DoesNotExist:
                # Si no tiene perfil, crear uno con rol por defecto
                user_profile = UserProfile.objects.create(
                    user=request.user,
                    rol='registro'  # rol por defecto
                )
                user_role = 'registro'
            
            # Verificar si el usuario tiene un rol permitido
            if user_role in allowed_roles:
                return view_func(request, *args, **kwargs)
            else:
                messages.error(
                    request, 
                    f'❌ Acceso denegado. Se requiere rol: {", ".join(allowed_roles)}'
                )
                return redirect('dashboard')
        
        return _wrapped_view
    return decorator

def admin_required(view_func):
    """Decorador específico para administradores"""
    return role_required('admin')(view_func)

def registro_or_admin_required(view_func):
    """Decorador para usuarios de registro o admin"""
    return role_required('admin', 'registro')(view_func)

def escaneo_or_admin_required(view_func):
    """Decorador para usuarios de escaneo o admin"""
    return role_required('admin', 'escaneo')(view_func)