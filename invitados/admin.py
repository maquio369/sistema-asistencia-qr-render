from django.contrib import admin
from django.utils.html import format_html
from .models import Invitado, UserProfile

@admin.register(Invitado)
class InvitadoAdmin(admin.ModelAdmin):
    list_display = [
        'nombre_completo', 
        'puesto_cargo', 
        'mostrar_foto_miniatura',
        'qr_generado',
        'estado_asistencia_admin',
        'fecha_hora_entrada',
        'fecha_creacion'
    ]
    
    list_filter = [
        'asistio', 
        'qr_generado', 
        'fecha_creacion',
        'fecha_hora_entrada'
    ]
    
    search_fields = [
        'nombre_completo', 
        'puesto_cargo', 
        'token_qr'
    ]
    
    readonly_fields = [
        'id', 
        'token_qr', 
        'fecha_creacion', 
        'fecha_modificacion',
        'mostrar_foto_completa',
        'mostrar_qr_completo'
    ]
    
    fieldsets = (
        ('Información del Invitado', {
            'fields': (
                'nombre_completo', 
                'puesto_cargo', 
                'fotografia',
                'mostrar_foto_completa'
            )
        }),
        ('Código QR', {
            'fields': (
                'token_qr',
                'qr_generado',
                'qr_imagen',
                'mostrar_qr_completo'
            )
        }),
        ('Control de Asistencia', {
            'fields': (
                'asistio',
                'fecha_hora_entrada',
                'escaneado_por'
            )
        }),
        ('Información del Sistema', {
            'fields': (
                'id',
                'fecha_creacion',
                'fecha_modificacion'
            ),
            'classes': ('collapse',)
        })
    )
    
    def mostrar_foto_miniatura(self, obj):
        if obj.fotografia:
            return format_html(
                '<img src="{}" width="50" height="50" style="border-radius: 5px;" />',
                obj.fotografia.url
            )
        return "Sin foto"
    mostrar_foto_miniatura.short_description = "Foto"
    
    def mostrar_foto_completa(self, obj):
        if obj.fotografia:
            return format_html(
                '<img src="{}" width="200" height="200" style="border-radius: 10px;" />',
                obj.fotografia.url
            )
        return "Sin foto"
    mostrar_foto_completa.short_description = "Fotografía actual"
    
    def mostrar_qr_completo(self, obj):
        if obj.qr_imagen:
            return format_html(
                '<img src="{}" width="150" height="150" />',
                obj.qr_imagen.url
            )
        return "QR no generado"
    mostrar_qr_completo.short_description = "Código QR"
    
    def estado_asistencia_admin(self, obj):
        if obj.asistio:
            return format_html(
                '<span style="color: green; font-weight: bold;">✓ Asistió</span>'
            )
        return format_html(
            '<span style="color: red; font-weight: bold;">✗ No asistió</span>'
        )
    estado_asistencia_admin.short_description = "Estado"
    
    actions = ['marcar_como_asistido', 'marcar_como_no_asistido', 'regenerar_qr_codes']
    
    def marcar_como_asistido(self, request, queryset):
        count = 0
        for invitado in queryset:
            if invitado.marcar_asistencia("Admin"):
                count += 1
        self.message_user(request, f"{count} invitado(s) marcado(s) como asistido(s).")
    marcar_como_asistido.short_description = "Marcar como asistido"
    
    def marcar_como_no_asistido(self, request, queryset):
        count = queryset.update(asistio=False, fecha_hora_entrada=None)
        self.message_user(request, f"{count} invitado(s) marcado(s) como no asistido(s).")
    marcar_como_no_asistido.short_description = "Marcar como no asistido"
    
    def regenerar_qr_codes(self, request, queryset):
        count = 0
        for invitado in queryset:
            try:
                invitado.generar_qr()
                invitado.save()
                count += 1
            except Exception as e:
                self.message_user(
                    request, 
                    f"Error al generar QR para {invitado.nombre_completo}: {e}",
                    level='ERROR'
                )
        
        self.message_user(
            request, 
            f"Se generaron {count} código(s) QR correctamente."
        )
    regenerar_qr_codes.short_description = "Regenerar códigos QR"


    @admin.register(UserProfile)
    class UserProfileAdmin(admin.ModelAdmin):
        list_display = ['user', 'rol', 'fecha_creacion']
        list_filter = ['rol', 'fecha_creacion']
        search_fields = ['user__username', 'user__first_name', 'user__last_name']
        
        def get_readonly_fields(self, request, obj=None):
            if obj:  # Editando
                return ['user', 'fecha_creacion']
            return ['fecha_creacion']