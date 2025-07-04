from django.urls import path
from . import views

urlpatterns = [
    path('', views.lista_invitados, name='lista_invitados'),
    path('qr/<str:token>/', views.mostrar_qr, name='mostrar_qr'),
    path('escaner/', views.escaner_qr, name='escaner_qr'),
    path('procesar-qr/', views.procesar_qr, name='procesar_qr'),
    path('estadisticas/', views.estadisticas_tiempo_real, name='estadisticas'),
    path('panel/', views.panel_control, name='panel_control'),
    path('exportar-csv/', views.exportar_asistencia_csv, name='exportar_csv'),
    path('offline/', views.offline_page, name='offline'),
]