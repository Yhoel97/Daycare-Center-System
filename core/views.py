from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.contrib import messages
from django.core.paginator import Paginator
from .models import Nino, ResponsableAutorizado, Maestro, Aula, Seccion, HorarioAula, AsignacionAula, Asistencia, PermisoAusencia
from .forms import NinoForm, ResponsableAutorizadoForm, AsignarAulaForm, AsistenciaForm, PermisoAusenciaForm
from django.contrib.auth.models import User
from django.contrib.admin.views.decorators import staff_member_required
from django.utils import timezone
import os
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import json
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.utils import timezone
from .models import Nino, Asistencia
from .email import enviar_notificacion_inasistencia, enviar_confirmacion_solicitud_permiso, enviar_notificacion_permiso_aprobado

@login_required
def actualizar_asistencia_ajax(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Método no permitido'}, status=405)
    if not request.content_type == 'application/json':
        return JsonResponse({'success': False, 'error': 'Tipo de contenido debe ser JSON'}, status=400)

    try:
        data = json.loads(request.body)
        nino_id = data.get('nino_id')
        presente = data.get('presente', True)
        motivo = data.get('motivo', '').strip() if not presente else ''

        if not nino_id:
            return JsonResponse({'success': False, 'error': 'ID de niño requerido'}, status=400)

        nino = get_object_or_404(Nino, pk=nino_id)
        print(f"DEBUG: Procesando asistencia para {nino.nombre_completo}")
        print(f"DEBUG: presente={presente}, motivo='{motivo}'")
        print(f"DEBUG: email_responsable={nino.email_responsable}")

        hoy = timezone.now().date()
        asistencia, created = Asistencia.objects.get_or_create(
            nino=nino,
            fecha=hoy,
            defaults={'registrado_por': request.user}
        )

        asistencia.presente = presente
        if not presente:
            asistencia.motivo_inasistencia = motivo
        asistencia.registrado_por = request.user
        asistencia.save()

        notificacion_enviada = False
        if not presente and not motivo:
            if nino.email_responsable:
                print("DEBUG: Intentando enviar notificación...")
                from .email import enviar_notificacion_inasistencia
                exito = enviar_notificacion_inasistencia(nino.email_responsable, nino.nombre_completo)
                print(f"DEBUG: Resultado de envío = {exito}")
                if exito:
                    notificacion_enviada = True
            else:
                print("DEBUG: No hay email, omitiendo notificación.")
        else:
            print("DEBUG: Asistencia justificada o presente, no se envía notificación.")

        return JsonResponse({
            'success': True,
            'motivo': motivo,
            'notificacion_enviada': notificacion_enviada,
            'nombre_nino': nino.nombre_completo
        })

    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'JSON inválido'}, status=400)
    except Exception as e:
        print(f"ERROR EN VISTA AJAX: {str(e)}")
        return JsonResponse({'success': False, 'error': str(e)}, status=400)



def cerrar_sesion(request):
    """Vista personalizada para cerrar sesión"""
    logout(request)
    messages.success(request, '¡Has cerrado sesión exitosamente!')
    return redirect('inicio')

def inicio(request):
    """Vista de la página de inicio"""
    return render(request, 'inicio.html')

def acerca_de(request):
    """Vista de la página Acerca de Nosotros"""
    return render(request, 'acerca_de.html')

def contacto(request):
    """Vista de la página de Contacto"""
    if request.method == 'POST':
        # Aquí podrías procesar el formulario de contacto
        nombre = request.POST.get('nombre')
        email = request.POST.get('email')
        mensaje = request.POST.get('mensaje')
        
        # Por ahora solo mostramos un mensaje de éxito
        messages.success(request, '¡Gracias por contactarnos! Responderemos pronto.')
        return redirect('contacto')
    
    return render(request, 'contacto.html')

@login_required
def lista_ninos(request):
    """Vista para listar todos los niños registrados"""
    ninos_list = Nino.objects.filter(activo=True).order_by('-fecha_registro')
    
    # Búsqueda
    query = request.GET.get('q')
    if query:
        ninos_list = ninos_list.filter(nombre_completo__icontains=query)
    
    # Paginación
    paginator = Paginator(ninos_list, 10)  # 10 niños por página
    page_number = request.GET.get('page')
    ninos = paginator.get_page(page_number)
    
    context = {
        'ninos': ninos,
        'query': query
    }
    return render(request, 'lista_ninos.html', context)

@login_required
def detalle_nino(request, pk):
    """Vista para ver el detalle completo de un niño"""
    nino = get_object_or_404(Nino, pk=pk)
    
    context = {
        'nino': nino
    }
    return render(request, 'detalle_nino.html', context)

@login_required
def registrar_nino(request):
    """Vista para registrar un nuevo niño"""
    if request.method == 'POST':
        form = NinoForm(request.POST, request.FILES)
        if form.is_valid():
            nino = form.save(commit=False)
            nino.usuario_registro = request.user
            nino.save()
            messages.success(request, f'¡Niño/a {nino.nombre_completo} registrado exitosamente!')
            return redirect('lista_ninos')
        else:
            messages.error(request, 'Por favor corrija los errores en el formulario.')
    else:
        form = NinoForm()
    
    context = {
        'form': form,
        'titulo': 'Registrar Nuevo Niño/a'
    }
    return render(request, 'form_nino.html', context)

@login_required
def editar_nino(request, pk):
    """Vista para editar información de un niño existente"""
    nino = get_object_or_404(Nino, pk=pk)
    
    if request.method == 'POST':
        form = NinoForm(request.POST, request.FILES, instance=nino)
        if form.is_valid():
            form.save()
            messages.success(request, f'Información de {nino.nombre_completo} actualizada exitosamente!')
            return redirect('detalle_nino', pk=nino.pk)
        else:
            messages.error(request, 'Por favor corrija los errores en el formulario.')
    else:
        form = NinoForm(instance=nino)
    
    context = {
        'form': form,
        'nino': nino,
        'titulo': f'Editar: {nino.nombre_completo}'
    }
    return render(request, 'form_nino.html', context)

@login_required
def eliminar_nino(request, pk):
    """Vista para eliminar (desactivar) un niño"""
    nino = get_object_or_404(Nino, pk=pk)
    
    if request.method == 'POST':
        # En lugar de eliminar, lo desactivamos
        nino.activo = False
        nino.save()
        messages.success(request, f'{nino.nombre_completo} ha sido dado de baja.')
        return redirect('lista_ninos')
    
    context = {
        'nino': nino
    }
    return render(request, 'eliminar_nino.html', context)


# Bloque de Aulas
@login_required
def asignar_aula(request, nino_pk):
    nino = get_object_or_404(Nino, pk=nino_pk)
    asignacion = getattr(nino, 'asignacion_aula', None)

    if request.method == 'POST':
        form = AsignarAulaForm(request.POST)
        if form.is_valid():
            if asignacion:
                asignacion.seccion = form.cleaned_data['seccion']
                asignacion.save()
            else:
                AsignacionAula.objects.create(nino=nino, seccion=form.cleaned_data['seccion'])
            messages.success(request, f'Aula, sección y maestro asignados a {nino.nombre_completo}.')
            return redirect('detalle_nino', pk=nino.pk)
    else:
        form = AsignarAulaForm(initial={'seccion': asignacion.seccion.pk if asignacion else None})

    return render(request, 'asignar_aula.html', {
        'form': form,
        'nino': nino,
        'titulo': f'Asignar Aula y Maestro a {nino.nombre_completo}'
    })

# ===== VISTAS PARA AULAS =====

@login_required
def lista_aulas(request):
    aulas = Aula.objects.all().order_by('nombre')
    return render(request, 'lista_aulas.html', {'aulas': aulas})

@login_required
def crear_aula(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        capacidad = request.POST.get('capacidad')
        activo = request.POST.get('activo') == 'on'
        if nombre and capacidad:
            Aula.objects.create(nombre=nombre, capacidad=capacidad, activo=activo)
            messages.success(request, 'Aula creada exitosamente.')
            return redirect('lista_aulas')
    return render(request, 'form_aula.html', {'titulo': 'Crear Aula'})

@login_required
def editar_aula(request, pk):
    aula = get_object_or_404(Aula, pk=pk)
    if request.method == 'POST':
        aula.nombre = request.POST.get('nombre')
        aula.capacidad = request.POST.get('capacidad')
        aula.activo = request.POST.get('activo') == 'on'
        aula.save()
        messages.success(request, 'Aula actualizada.')
        return redirect('lista_aulas')
    return render(request, 'form_aula.html', {'aula': aula, 'titulo': 'Editar Aula'})

@login_required
def eliminar_aula(request, pk):
    aula = get_object_or_404(Aula, pk=pk)
    if request.method == 'POST':
        aula.delete()
        messages.success(request, 'Aula eliminada.')
        return redirect('lista_aulas')
    return render(request, 'eliminar_aula.html', {'aula': aula})


# ===== VISTAS PARA MAESTROS =====

@staff_member_required
def lista_maestros(request):
    maestros = Maestro.objects.all().order_by('nombre_completo')
    return render(request, 'lista_maestros.html', {'maestros': maestros})

@staff_member_required
def crear_maestro(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre_completo')
        telefono = request.POST.get('telefono')
        email = request.POST.get('email')
        activo = request.POST.get('activo') == 'on'
        if nombre:
            Maestro.objects.create(
                nombre_completo=nombre,
                telefono=telefono,
                email=email,
                activo=activo
            )
            messages.success(request, 'Maestro creado exitosamente.')
            return redirect('lista_maestros')
    return render(request, 'form_maestro.html', {
        'titulo': 'Crear Maestro'
    })

@staff_member_required
def editar_maestro(request, pk):
    maestro = get_object_or_404(Maestro, pk=pk)
    if request.method == 'POST':
        maestro.nombre_completo = request.POST.get('nombre_completo')
        maestro.telefono = request.POST.get('telefono')
        maestro.email = request.POST.get('email')
        maestro.activo = request.POST.get('activo') == 'on'
        maestro.save()
        messages.success(request, 'Maestro actualizado.')
        return redirect('lista_maestros')
    return render(request, 'form_maestro.html', {
        'maestro': maestro,
        'titulo': 'Editar Maestro'
    })

@staff_member_required
def eliminar_maestro(request, pk):
    maestro = get_object_or_404(Maestro, pk=pk)
    if request.method == 'POST':
        maestro.delete()
        messages.success(request, 'Maestro eliminado.')
        return redirect('lista_maestros')
    return render(request, 'eliminar_maestro.html', {'maestro': maestro})


# ===== VISTAS PARA SECCIONES =====

@staff_member_required
def lista_secciones(request):
    secciones = Seccion.objects.select_related('aula', 'maestro').all().order_by('aula__nombre', 'nombre')
    return render(request, 'lista_secciones.html', {'secciones': secciones})

@login_required
def crear_seccion(request):
    if request.method == 'POST':
        aula_id = request.POST.get('aula')
        maestro_id = request.POST.get('maestro') or None
        nombre = request.POST.get('nombre')
        activo = request.POST.get('activo') == 'on'
        if aula_id and nombre:
            seccion = Seccion.objects.create(
                aula_id=aula_id,
                maestro_id=maestro_id,
                nombre=nombre,
                activo=activo
            )
            # Procesar horarios
            idx = 0
            while True:
                dia = request.POST.get(f'horario_{idx}_dia')
                if not dia:
                    break
                inicio = request.POST.get(f'horario_{idx}_inicio')
                fin = request.POST.get(f'horario_{idx}_fin')
                if dia and inicio and fin:
                    HorarioAula.objects.create(
                        seccion=seccion,
                        dia=dia,
                        hora_inicio=inicio,
                        hora_fin=fin
                    )
                idx += 1
            messages.success(request, 'Sección creada exitosamente.')
            return redirect('lista_secciones')
    aulas = Aula.objects.filter(activo=True)
    maestros = Maestro.objects.filter(activo=True)
    return render(request, 'form_seccion.html', {
        'aulas': aulas,
        'maestros': maestros,
        'titulo': 'Crear Sección'
    })

@login_required
def editar_seccion(request, pk):
    seccion = get_object_or_404(Seccion, pk=pk)
    if request.method == 'POST':
        seccion.aula_id = request.POST.get('aula')
        seccion.maestro_id = request.POST.get('maestro') or None
        seccion.nombre = request.POST.get('nombre')
        seccion.activo = request.POST.get('activo') == 'on'
        seccion.save()
        # Eliminar horarios anteriores
        seccion.horarios.all().delete()
        # Crear nuevos horarios
        idx = 0
        while True:
            dia = request.POST.get(f'horario_{idx}_dia')
            if not dia:
                break
            inicio = request.POST.get(f'horario_{idx}_inicio')
            fin = request.POST.get(f'horario_{idx}_fin')
            if dia and inicio and fin:
                HorarioAula.objects.create(
                    seccion=seccion,
                    dia=dia,
                    hora_inicio=inicio,
                    hora_fin=fin
                )
            idx += 1
        messages.success(request, 'Sección actualizada.')
        return redirect('lista_secciones')
    aulas = Aula.objects.filter(activo=True)
    maestros = Maestro.objects.filter(activo=True)
    # Cargar horarios existentes para el template
    horarios = seccion.horarios.all()
    return render(request, 'form_seccion.html', {
        'seccion': seccion,
        'aulas': aulas,
        'maestros': maestros,
        'horarios': horarios,
        'titulo': 'Editar Sección'
    })

@staff_member_required
def eliminar_seccion(request, pk):
    seccion = get_object_or_404(Seccion, pk=pk)
    if request.method == 'POST':
        seccion.delete()
        messages.success(request, 'Sección eliminada.')
        return redirect('lista_secciones')
    return render(request, 'eliminar_seccion.html', {'seccion': seccion})


# ==========================================
# VISTAS PARA RESPONSABLES AUTORIZADOS
# ==========================================

@login_required
def lista_responsables(request, nino_pk):
    """Vista para listar todos los responsables de un niño"""
    nino = get_object_or_404(Nino, pk=nino_pk)
    responsables = ResponsableAutorizado.objects.filter(nino=nino).order_by('-activo', 'nombre_completo')
    
    context = {
        'nino': nino,
        'responsables': responsables
    }
    return render(request, 'lista_responsables.html', context)

@login_required
def registrar_responsable(request, nino_pk):
    """Vista para registrar un nuevo responsable autorizado"""
    nino = get_object_or_404(Nino, pk=nino_pk)
    
    if request.method == 'POST':
        form = ResponsableAutorizadoForm(request.POST, request.FILES)
        if form.is_valid():
            responsable = form.save(commit=False)
            responsable.nino = nino
            responsable.usuario_registro = request.user
            responsable.save()
            messages.success(
                request, 
                f'¡Responsable {responsable.nombre_completo} registrado exitosamente!'
            )
            return redirect('lista_responsables', nino_pk=nino.pk)
        else:
            messages.error(request, 'Por favor corrija los errores en el formulario.')
    else:
        form = ResponsableAutorizadoForm()
    
    context = {
        'form': form,
        'nino': nino,
        'titulo': f'Registrar Responsable para {nino.nombre_completo}'
    }
    return render(request, 'form_responsable.html', context)

@login_required
def detalle_responsable(request, pk):
    """Vista para ver el detalle de un responsable"""
    responsable = get_object_or_404(ResponsableAutorizado, pk=pk)
    
    context = {
        'responsable': responsable,
        'nino': responsable.nino
    }
    return render(request, 'detalle_responsable.html', context)

@login_required
def editar_responsable(request, pk):
    """Vista para editar un responsable autorizado"""
    responsable = get_object_or_404(ResponsableAutorizado, pk=pk)
    
    if request.method == 'POST':
        form = ResponsableAutorizadoForm(request.POST, request.FILES, instance=responsable)
        if form.is_valid():
            form.save()
            messages.success(
                request, 
                f'Información de {responsable.nombre_completo} actualizada exitosamente!'
            )
            return redirect('detalle_responsable', pk=responsable.pk)
        else:
            messages.error(request, 'Por favor corrija los errores en el formulario.')
    else:
        form = ResponsableAutorizadoForm(instance=responsable)
    
    context = {
        'form': form,
        'responsable': responsable,
        'nino': responsable.nino,
        'titulo': f'Editar: {responsable.nombre_completo}'
    }
    return render(request, 'form_responsable.html', context)

@login_required
def eliminar_responsable(request, pk):
    """Vista para eliminar un responsable autorizado"""
    responsable = get_object_or_404(ResponsableAutorizado, pk=pk)
    nino = responsable.nino
    
    if request.method == 'POST':
        nombre = responsable.nombre_completo
        responsable.delete()
        messages.success(request, f'Responsable {nombre} eliminado exitosamente.')
        return redirect('lista_responsables', nino_pk=nino.pk)
    
    context = {
        'responsable': responsable,
        'nino': nino
    }
    return render(request, 'eliminar_responsable.html', context)


# ===== VISTAS PARA AULAS =====

@login_required
def lista_aulas(request):
    aulas = Aula.objects.all().order_by('nombre')
    return render(request, 'lista_aulas.html', {'aulas': aulas})

@login_required
def crear_aula(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        capacidad = request.POST.get('capacidad')
        activo = request.POST.get('activo') == 'on'
        if nombre and capacidad:
            Aula.objects.create(nombre=nombre, capacidad=capacidad, activo=activo)
            messages.success(request, 'Aula creada exitosamente.')
            return redirect('lista_aulas')
    return render(request, 'form_aula.html', {'titulo': 'Crear Aula'})

@login_required
def editar_aula(request, pk):
    aula = get_object_or_404(Aula, pk=pk)
    if request.method == 'POST':
        aula.nombre = request.POST.get('nombre')
        aula.capacidad = request.POST.get('capacidad')
        aula.activo = request.POST.get('activo') == 'on'
        aula.save()
        messages.success(request, 'Aula actualizada.')
        return redirect('lista_aulas')
    return render(request, 'form_aula.html', {'aula': aula, 'titulo': 'Editar Aula'})

@login_required
def eliminar_aula(request, pk):
    aula = get_object_or_404(Aula, pk=pk)
    if request.method == 'POST':
        aula.delete()
        messages.success(request, 'Aula eliminada.')
        return redirect('lista_aulas')
    return render(request, 'eliminar_aula.html', {'aula': aula})



@login_required
def registrar_asistencia(request, nino_pk):
    nino = get_object_or_404(Nino, pk=nino_pk)
    hoy = timezone.now().date()

    # Obtener o crear registro de hoy
    asistencia, created = Asistencia.objects.get_or_create(
        nino=nino,
        fecha=hoy,
        defaults={'registrado_por': request.user}
    )

    if request.method == 'POST':
        form = AsistenciaForm(request.POST, instance=asistencia)
        if form.is_valid():
            asistencia = form.save(commit=False)
            asistencia.nino = nino
            asistencia.fecha = hoy
            asistencia.registrado_por = request.user
            asistencia.save()

            # Dentro de registrar_asistencia, después de guardar la asistencia
            if not asistencia.presente and not asistencia.justificado():
                if nino.email_responsable:
                    print(">>> Enviando notificación a:", nino.email_responsable)
                    print(">>> BREVO_API_KEY disponible:", bool(os.getenv("BREVO_API_KEY")))
                    from .email import enviar_notificacion_inasistencia
                    exito = enviar_notificacion_inasistencia(nino.email_responsable, nino.nombre_completo)
                    if exito:
                        messages.warning(request, f"Notificación enviada al responsable de {nino.nombre_completo}.")
                    else:
                        messages.error(request, "No se pudo enviar la notificación. Verifique la configuración.")
                else:
                    messages.warning(request, f"{nino.nombre_completo} no tiene email registrado.")

            return redirect('detalle_nino', pk=nino.pk)
    else:
        form = AsistenciaForm(instance=asistencia)

    return render(request, 'registrar_asistencia.html', {
        'form': form,
        'nino': nino,
        'hoy': hoy,
    })




# core/views.py







@login_required
def enviar_notificacion_manual(request, nino_pk):
    if request.method != 'POST':
        return HttpResponseForbidden()
    
    nino = get_object_or_404(Nino, pk=nino_pk)
    
    # Verificar que hoy el niño esté ausente y sin justificar
    hoy = timezone.now().date()
    asistencia = Asistencia.objects.filter(nino=nino, fecha=hoy).first()
    
    if not asistencia or asistencia.presente or asistencia.justificado():
        messages.error(request, f"{nino.nombre_completo} no tiene una inasistencia no justificada hoy.")
        return redirect('detalle_nino', pk=nino.pk)
    
    if not nino.email_responsable:
        messages.warning(request, f"{nino.nombre_completo} no tiene email registrado.")
        return redirect('detalle_nino', pk=nino.pk)
    
    # Enviar notificación
    exito = enviar_notificacion_inasistencia(nino.email_responsable, nino.nombre_completo)
    if exito:
        messages.success(request, f"✅ Notificación enviada al responsable de {nino.nombre_completo}.")
    else:
        messages.error(request, "❌ No se pudo enviar la notificación. Verifique la configuración de Brevo.")
    
    return redirect('detalle_nino', pk=nino.pk)

@login_required
def reporte_asistencia_diario(request):
    hoy = timezone.now().date()
    if request.user.is_superuser:
        ninos_asignados = Nino.objects.filter(
            activo=True,
            asignacion_aula__isnull=False
        ).select_related('asignacion_aula__seccion__aula', 'asignacion_aula__seccion__maestro')
    else:
        ninos_asignados = Nino.objects.filter(
            activo=True,
            asignacion_aula__seccion__maestro__usuario=request.user
        ).select_related('asignacion_aula__seccion__aula', 'asignacion_aula__seccion__maestro')

    # Asegurar orden para regroup
    ninos_asignados = ninos_asignados.order_by(
        'asignacion_aula__seccion__aula__nombre',
        'asignacion_aula__seccion__nombre'
    )

    asistencias_hoy = {}
    for nino in ninos_asignados:
        asistencia, created = Asistencia.objects.get_or_create(
            nino=nino,
            fecha=hoy,
            defaults={'registrado_por': request.user}
        )
        asistencias_hoy[nino.id] = asistencia

    # ✅ Agregar asistencias_json al contexto
    asistencias_dict = {
        nino.id: {
            'presente': asistencia.presente,
            'motivo_inasistencia': asistencia.motivo_inasistencia or ''
        }
        for nino in ninos_asignados
        for asistencia in [asistencias_hoy[nino.id]]
    }

    context = {
        'ninos_asignados': ninos_asignados,
        'asistencias_hoy': asistencias_hoy,
        'asistencias_json': json.dumps(asistencias_dict),
        'hoy': hoy,
    }
    return render(request, 'reporte_diario.html', context)


# ========== PBI 05: PERMISOS DE AUSENCIA ==========

@login_required
def solicitar_permiso_ausencia(request, nino_pk):
    """Vista para que padres/tutores soliciten permisos de ausencia"""
    nino = get_object_or_404(Nino, pk=nino_pk, activo=True)
    
    if request.method == 'POST':
        form = PermisoAusenciaForm(request.POST, request.FILES)
        if form.is_valid():
            permiso = form.save(commit=False)
            permiso.nino = nino
            permiso.solicitante = request.user
            permiso.save()
            
            # Enviar confirmación al responsable
            if nino.email_responsable:
                enviar_confirmacion_solicitud_permiso(
                    nino.email_responsable,
                    nino.nombre_completo,
                    permiso.fecha_inicio.strftime('%d/%m/%Y'),
                    permiso.get_tipo_display()
                )
            
            messages.success(
                request,
                f'Permiso de ausencia solicitado exitosamente para {nino.nombre_completo}. '
                f'Será revisado por el personal administrativo.'
            )
            return redirect('detalle_nino', pk=nino.pk)
    else:
        form = PermisoAusenciaForm()
    
    context = {
        'form': form,
        'nino': nino,
        'titulo': f'Solicitar Permiso de Ausencia - {nino.nombre_completo}'
    }
    return render(request, 'solicitar_permiso.html', context)


@staff_member_required
def lista_permisos_ausencia(request):
    """Vista para que el staff vea y filtre permisos de ausencia"""
    # Obtener filtro por estado
    estado_filtro = request.GET.get('estado', 'pendiente')
    
    # Filtrar permisos según el estado
    if estado_filtro == 'todos':
        permisos = PermisoAusencia.objects.all()
    else:
        permisos = PermisoAusencia.objects.filter(estado=estado_filtro)
    
    # Ordenar por fecha de solicitud (más recientes primero)
    permisos = permisos.select_related('nino', 'solicitante', 'aprobado_por').order_by('-fecha_solicitud')
    
    # Paginación
    paginator = Paginator(permisos, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Contar permisos por estado
    total_pendientes = PermisoAusencia.objects.filter(estado='pendiente').count()
    total_aprobados = PermisoAusencia.objects.filter(estado='aprobado').count()
    total_rechazados = PermisoAusencia.objects.filter(estado='rechazado').count()
    
    context = {
        'page_obj': page_obj,
        'estado_filtro': estado_filtro,
        'total_pendientes': total_pendientes,
        'total_aprobados': total_aprobados,
        'total_rechazados': total_rechazados,
    }
    return render(request, 'lista_permisos.html', context)


@staff_member_required
def gestionar_permiso_ausencia(request, pk):
    """Vista para que el staff apruebe o rechace permisos"""
    permiso = get_object_or_404(PermisoAusencia, pk=pk)
    
    if request.method == 'POST':
        accion = request.POST.get('accion')
        notas = request.POST.get('notas_gestion', '').strip()
        
        if accion in ['aprobar', 'rechazar']:
            permiso.estado = 'aprobado' if accion == 'aprobar' else 'rechazado'
            permiso.aprobado_por = request.user
            permiso.fecha_gestion = timezone.now()
            permiso.notas_gestion = notas
            permiso.save()
            
            # Si se aprueba, notificar al maestro
            if accion == 'aprobar':
                try:
                    # Obtener el maestro del niño
                    asignacion = permiso.nino.asignacion_aula
                    maestro = asignacion.seccion.maestro
                    
                    if maestro and maestro.email:
                        # Formatear fechas
                        fecha_inicio = permiso.fecha_inicio.strftime('%d/%m/%Y')
                        fecha_fin = permiso.fecha_fin.strftime('%d/%m/%Y') if permiso.fecha_fin else None
                        
                        # Enviar notificación al maestro
                        enviar_notificacion_permiso_aprobado(
                            maestro.email,
                            permiso.nino.nombre_completo,
                            fecha_inicio,
                            fecha_fin,
                            permiso.get_tipo_display(),
                            permiso.motivo,
                            permiso.horario_ausencia()
                        )
                        messages.success(
                            request,
                            f'Permiso aprobado exitosamente. Se ha notificado al maestro {maestro.nombre_completo}.'
                        )
                    else:
                        messages.warning(
                            request,
                            'Permiso aprobado, pero el niño no tiene maestro asignado o el maestro no tiene email.'
                        )
                except Exception as e:
                    messages.warning(
                        request,
                        f'Permiso aprobado, pero no se pudo enviar la notificación al maestro: {str(e)}'
                    )
            else:
                messages.success(request, 'Permiso rechazado exitosamente.')
            
            return redirect('lista_permisos_ausencia')
    
    context = {
        'permiso': permiso,
    }
    return render(request, 'gestionar_permiso.html', context)