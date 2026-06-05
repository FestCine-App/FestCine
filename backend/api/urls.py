from django.urls import path, re_path
from . import views

urlpatterns = [
    path('peliculas/', views.peliculas, name='peliculas-list'),
    re_path(r'^peliculas/(?P<id>\d+)/$', views.peliculas, name='peliculas-detail'),

    path('proyecciones/', views.proyecciones, name='proyecciones-list'),
    re_path(r'^proyecciones/(?P<id>\d+)/$', views.proyecciones, name='proyecciones-detail'),

    path('asistentes/', views.asistentes, name='asistentes-list'),
    re_path(r'^asistentes/(?P<id>\d+)/$', views.asistentes, name='asistentes-detail'),

    path('entradas/', views.entradas, name='entradas'),
    path('abonos/', views.abonos, name='abonos'),

    path('sedes/', views.sedes, name='sedes-list'),
    re_path(r'^sedes/(?P<id>\d+)/$', views.sedes, name='sedes-detail'),

    path('salas/', views.salas, name='salas-list'),
    re_path(r'^salas/(?P<id>\d+)/$', views.salas, name='salas-detail'),

    path('eventos/', views.eventos, name='eventos-list'),
    re_path(r'^eventos/(?P<id>\d+)/$', views.eventos, name='eventos-detail'),

    path('generos/', views.generos, name='generos'),

    path('personal/', views.personal, name='personal-list'),
    re_path(r'^personal/(?P<id>\d+)/$', views.personal, name='personal-detail'),

    path('categorias/', views.categorias, name='categorias-list'),
    re_path(r'^categorias/(?P<id>\d+)/$', views.categorias, name='categorias-detail'),

    path('jurados/', views.jurados, name='jurados-list'),
    re_path(r'^jurados/(?P<id>\d+)/$', views.jurados, name='jurados-detail'),

    path('evaluaciones/', views.evaluaciones, name='evaluaciones-list'),
    re_path(r'^evaluaciones/(?P<id>\d+)/$', views.evaluaciones, name='evaluaciones-detail'),

    path('patrocinadores/', views.patrocinadores, name='patrocinadores-list'),
    re_path(r'^patrocinadores/(?P<id>\d+)/$', views.patrocinadores, name='patrocinadores-detail'),

    path('patrocinios/', views.patrocinios, name='patrocinios'),
    re_path(r'^patrocinios/(?P<id>\d+)/$', views.patrocinios, name='patrocinios-detail'),


    path('ediciones/', views.ediciones, name='ediciones-list'),
    re_path(r'^ediciones/(?P<id>\d+)/$', views.ediciones, name='ediciones-detail'),

    path('hoteles/', views.hoteles, name='hoteles-list'),
    re_path(r'^hoteles/(?P<id>\d+)/$', views.hoteles, name='hoteles-detail'),

    path('alojamientos/', views.alojamientos, name='alojamientos-list'),
    re_path(r'^alojamientos/(?P<id>\d+)/$', views.alojamientos, name='alojamientos-detail'),

    path('traslados/', views.traslados, name='traslados-list'),
    re_path(r'^traslados/(?P<id>\d+)/$', views.traslados, name='traslados-detail'),

    path('premios/', views.premios, name='premios-list'),
    re_path(r'^premios/(?P<id>\d+)/$', views.premios, name='premios-detail'),

    path('competencia/', views.competencia, name='competencia'),
    path('roles/', views.roles_pelicula, name='roles-pelicula'),


    path('tarifas/', views.tarifas, name='tarifas'),
    path('tipos-abono/', views.tiposabono, name='tiposabono'),

    path('reportes/ranking/', views.reporte_ranking, name='reporte-ranking'),
    path('reportes/premiacion/', views.reporte_premiacion, name='reporte-premiacion'),
    path('reportes/financiero/', views.reporte_financiero, name='reporte-financiero'),
    path('reportes/ocupacion-salas/', views.reporte_ocupacion, name='reporte-ocupacion'),
    re_path(r'^reportes/ventas-edicion/(?P<id>\d+)/$', views.reporte_ventas_edicion, name='reporte-ventas'),
]
