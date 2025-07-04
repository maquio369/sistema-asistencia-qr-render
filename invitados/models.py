import os
import uuid
import qrcode
from io import BytesIO
from django.db import models
from django.utils import timezone
from django.core.files.base import ContentFile
from PIL import Image

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
        """Método para generar código QR"""
        if not self.token_qr:
            self.token_qr = str(uuid.uuid4())
        
        # Crear el código QR
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        
        # Agregar el token como datos del QR
        qr.add_data(self.token_qr)
        qr.make(fit=True)
        
        # Crear la imagen del QR
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Convertir a bytes
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        
        # Nombre del archivo
        filename = f"qr_{self.token_qr[:8]}.png"
        
        # Guardar en el campo qr_imagen
        self.qr_imagen.save(
            filename,
            ContentFile(buffer.getvalue()),
            save=False
        )
        
        # Marcar como QR generado
        self.qr_generado = True
        buffer.close()
        
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