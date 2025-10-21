from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.contrib import messages
from django.core.paginator import Paginator
from .models import Nino, ResponsableAutorizado
from .forms import NinoForm, ResponsableAutorizadoForm

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

