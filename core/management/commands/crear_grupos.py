

from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from core.models import Nino, Maestro, Aula, Seccion, PermisoAusencia, Asistencia

class Command(BaseCommand):
    help = 'Crea los grupos de usuarios: Maestro y Padre/Tutor'

    def handle(self, *args, **kwargs):
        # ========== GRUPO: MAESTRO ==========
        maestro_group, created = Group.objects.get_or_create(name='Maestro')
        if created:
            self.stdout.write(self.style.SUCCESS('✓ Grupo "Maestro" creado'))
        
        # Permisos para Maestro (solo ver)
        permisos_maestro = [
            'view_nino',
            'view_maestro',
            'view_aula',
            'view_seccion',
            'view_asistencia',
            'add_asistencia',
            'change_asistencia',
        ]
        
        for perm_codename in permisos_maestro:
            try:
                perm = Permission.objects.get(codename=perm_codename)
                maestro_group.permissions.add(perm)
            except Permission.DoesNotExist:
                self.stdout.write(self.style.WARNING(f'⚠ Permiso {perm_codename} no existe'))
        
        self.stdout.write(self.style.SUCCESS(f'✓ Permisos asignados al grupo Maestro: {maestro_group.permissions.count()}'))

        # ========== GRUPO: PADRE/TUTOR ==========
        padre_group, created = Group.objects.get_or_create(name='Padre/Tutor')
        if created:
            self.stdout.write(self.style.SUCCESS('✓ Grupo "Padre/Tutor" creado'))
        
        # Permisos para Padre/Tutor
        permisos_padre = [
            'view_nino',
            'view_responsableautorizado',
            'add_responsableautorizado',
            'change_responsableautorizado',
            'view_permisoausencia',
            'add_permisoausencia',
        ]
        
        for perm_codename in permisos_padre:
            try:
                perm = Permission.objects.get(codename=perm_codename)
                padre_group.permissions.add(perm)
            except Permission.DoesNotExist:
                self.stdout.write(self.style.WARNING(f'⚠ Permiso {perm_codename} no existe'))
        
        self.stdout.write(self.style.SUCCESS(f'✓ Permisos asignados al grupo Padre/Tutor: {padre_group.permissions.count()}'))
        
        self.stdout.write(self.style.SUCCESS('\n========== RESUMEN =========='))
        self.stdout.write(self.style.SUCCESS('Grupos creados exitosamente'))
        self.stdout.write(self.style.SUCCESS('Ahora puedes asignar usuarios a estos grupos desde el admin'))