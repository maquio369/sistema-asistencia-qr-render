import os
import uuid
import qrcode
from io import BytesIO
from django.db import models
from django.utils import timezone
from django.core.files.base import ContentFile
from PIL import Image, ImageDraw
from django.conf import settings

class Invitado(models.Model):
    # Campos principales
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nombre_completo = models.CharField(max_length=200, verbose_name="Nombre completo")
    puesto_cargo = models.CharField(max_length=150, verbose_name="Puesto o cargo")
    fotografia = models.ImageField(
        upload_to='fotos_invitados/', 
        verbose_name="Fotografía",
        help_text="Sube una foto del invitado"
    )
    
    # Campos para QR y control
    token_qr = models.CharField(max_length=100, unique=True, blank=True)
    qr_generado = models.BooleanField(default=False, verbose_name="QR generado")
    qr_imagen = models.ImageField(
        upload_to='qr_codes/', 
        blank=True, 
        null=True,
        verbose_name="Código QR"
    )
    
    # Campos de asistencia
    asistio = models.BooleanField(default=False, verbose_name="¿Asistió?")
    fecha_hora_entrada = models.DateTimeField(
        null=True, 
        blank=True,
        verbose_name="Fecha y hora de entrada"
    )
    escaneado_por = models.CharField(
        max_length=100, 
        blank=True,
        verbose_name="Escaneado por (dispositivo/usuario)"
    )
    
    # Campos de auditoría
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Invitado"
        verbose_name_plural = "Invitados"
        ordering = ['nombre_completo']
    
    def __str__(self):
        return f"{self.nombre_completo} - {self.puesto_cargo}"
    
    def save(self, *args, **kwargs):
        # Generar token único si no existe
        if not self.token_qr:
            self.token_qr = str(uuid.uuid4())
            print(f"🔧 Token generado: {self.token_qr}")
        
        # Guardar primero para obtener el ID
        super().save(*args, **kwargs)
        
        # Generar QR automáticamente si no existe
        if not self.qr_generado or not self.qr_imagen:
            try:
                print(f"🔧 Generando QR para {self.nombre_completo}")
                self.generar_qr()
                print("✅ QR generado exitosamente")
                # Guardar nuevamente para actualizar el campo QR
                super().save(*args, **kwargs)
            except Exception as e:
                print(f"❌ Error al generar QR: {e}")
        
        # Redimensionar imagen si es muy grande
        if self.fotografia:
            try:
                img = Image.open(self.fotografia.path)
                if img.height > 300 or img.width > 300:
                    img.thumbnail((300, 300))
                    img.save(self.fotografia.path)
            except Exception as e:
                print(f"❌ Error al redimensionar imagen: {e}")

    def generar_qr(self):
        """Método para generar código QR con logo personalizado"""
        if not self.token_qr:
            self.token_qr = str(uuid.uuid4())
        
        print("🔧 Iniciando generación de QR...")
        
        # Crear el código QR con configuración optimizada para logo
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,  # Máxima corrección de errores
            box_size=10,
            border=4,
        )
        
        # Agregar el token como datos del QR
        qr.add_data(self.token_qr)
        qr.make(fit=True)
        
        # Crear la imagen del QR base
        qr_img = qr.make_image(fill_color="black", back_color="white").convert('RGB')
        print(f"📐 Tamaño del QR: {qr_img.size}")
        
        # Intentar agregar logo al centro
        logo_agregado = False
        try:
            # Buscar logo en diferentes ubicaciones
            possible_paths = [
                os.path.join(settings.BASE_DIR, 'static', 'images', 'logo-qr.png'),
                os.path.join(settings.STATICFILES_DIRS[0], 'images', 'logo-qr.png') if settings.STATICFILES_DIRS else None,
            ]
            
            logo_path = None
            for path in possible_paths:
                if path and os.path.exists(path):
                    logo_path = path
                    break
            
            if logo_path:
                print(f"🎯 Logo encontrado en: {logo_path}")
                
                # Abrir y procesar el logo
                logo = Image.open(logo_path)
                print(f"📐 Tamaño original del logo: {logo.size}")
                
                # Calcular tamaño del logo (20% del QR)
                qr_width, qr_height = qr_img.size
                logo_size = int(min(qr_width, qr_height) * 0.2)  # 20% del tamaño del QR
                
                # Redimensionar logo manteniendo aspecto
                logo = logo.resize((logo_size, logo_size), Image.Resampling.LANCZOS)
                print(f"📐 Logo redimensionado a: {logo.size}")
                
                # Convertir a RGBA si no lo está
                if logo.mode != 'RGBA':
                    logo = logo.convert('RGBA')
                
                # Crear fondo blanco circular para el logo
                background_size = logo_size + 10
                background = Image.new('RGBA', (background_size, background_size), (255, 255, 255, 255))
                
                # Crear máscara circular para el fondo
                bg_mask = Image.new('L', (background_size, background_size), 0)
                bg_draw = ImageDraw.Draw(bg_mask)
                bg_draw.ellipse((0, 0, background_size, background_size), fill=255)
                background.putalpha(bg_mask)
                
                # Calcular posición central
                bg_pos = ((qr_width - background_size) // 2, (qr_height - background_size) // 2)
                logo_pos = ((background_size - logo_size) // 2, (background_size - logo_size) // 2)
                
                # Pegar fondo blanco primero
                qr_img.paste(background, bg_pos, background)
                
                # Pegar logo sobre el fondo
                final_logo_pos = (bg_pos[0] + logo_pos[0], bg_pos[1] + logo_pos[1])
                qr_img.paste(logo, final_logo_pos, logo)
                
                logo_agregado = True
                print("✅ Logo agregado exitosamente al QR")
                
            else:
                print("⚠️ Logo no encontrado en ninguna ubicación:")
                for path in possible_paths:
                    if path:
                        print(f"   - {path} (existe: {os.path.exists(path)})")
                
        except Exception as e:
            print(f"❌ Error al agregar logo al QR: {e}")
            import traceback
            traceback.print_exc()
        
        # Convertir a bytes
        buffer = BytesIO()
        qr_img.save(buffer, format='PNG', quality=95)
        buffer.seek(0)
        
        # Nombre del archivo
        filename = f"qr_{self.token_qr[:8]}_{'con_logo' if logo_agregado else 'sin_logo'}.png"
        
        # Guardar en el campo qr_imagen
        self.qr_imagen.save(
            filename,
            ContentFile(buffer.getvalue()),
            save=False
        )
        
        # Marcar como QR generado
        self.qr_generado = True
        buffer.close()
        
        print(f"💾 QR guardado como: {filename}")
        return True

    def marcar_asistencia(self, dispositivo=""):
        """Método para marcar asistencia del invitado"""
        if not self.asistio:
            self.asistio = True
            self.fecha_hora_entrada = timezone.now()
            self.escaneado_por = dispositivo
            self.save()
            return True
        return False
    
    @property
    def estado_asistencia(self):
        """Retorna el estado de asistencia del invitado"""
        if self.asistio:
            return "Asistió"
        return "No asistió"
    
    @property
    def hora_entrada_formateada(self):
        """Retorna la hora de entrada formateada"""
        if self.fecha_hora_entrada:
            return self.fecha_hora_entrada.strftime("%d/%m/%Y %H:%M:%S")
        return "No registrada"