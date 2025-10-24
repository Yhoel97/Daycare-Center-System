from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.contrib import messages
from django.core.paginator import Paginator
from .models import Nino, ResponsableAutorizado, Maestro, Aula, Seccion, HorarioAula, AsignacionAula
from .forms import NinoForm, ResponsableAutorizadoForm, AsignarAulaForm
from django.contrib.auth.models import User
from django.contrib.admin.views.decorators import staff_member_required



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



