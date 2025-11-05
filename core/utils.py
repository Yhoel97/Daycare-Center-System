

from django.contrib.auth.models import Group

def es_admin(user):
    """Verifica si el usuario es admin/staff"""
    return user.is_superuser or user.is_staff

def es_maestro(user):
    """Verifica si el usuario pertenece al grupo Maestro"""
    return user.groups.filter(name='Maestro').exists()

def es_padre(user):
    """Verifica si el usuario pertenece al grupo Padre/Tutor"""
    return user.groups.filter(name='Padre/Tutor').exists()

def obtener_rol(user):
    """Retorna el rol del usuario como string"""
    if es_admin(user):
        return 'admin'
    elif es_maestro(user):
        return 'maestro'
    elif es_padre(user):
        return 'padre'
    return 'sin_rol'

def puede_editar_nino(user):
    """Verifica si el usuario puede editar niños"""
    return es_admin(user)

def puede_ver_todos_los_ninos(user):
    """Verifica si el usuario puede ver todos los niños"""
    return es_admin(user) or es_maestro(user)

def obtener_ninos_permitidos(user):
    """
    Retorna los niños que el usuario puede ver según su rol:
    - Admin: todos
    - Maestro: todos
    - Padre: solo sus hijos
    """
    from core.models import Nino, PadreNino
    
    if es_admin(user) or es_maestro(user):
        return Nino.objects.filter(activo=True)
    elif es_padre(user):
        # Solo los niños asociados a este padre
        return Nino.objects.filter(
            padres__padre=user,
            activo=True
        ).distinct()
    
    return Nino.objects.none()