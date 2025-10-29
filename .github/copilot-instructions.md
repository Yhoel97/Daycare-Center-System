# Daycare Center System - AI Agent Instructions

## Project Overview
Django-based daycare management system tracking children, authorized guardians, classroom assignments, teachers, and daily attendance with automated email notifications via Brevo API.

## Architecture & Data Flow

### Core Domain Models (`core/models.py`)
- **Nino**: Central entity with medical profile, guardian info, and one-to-many relationships to `ResponsableAutorizado` and `Asistencia`
- **ResponsableAutorizado**: Guardian authorization with time-based permissions, electronic signatures, and photo verification
- **Academic Models**: `Aula` → `Seccion` → `HorarioAula` hierarchy; `AsignacionAula` links child to section (one-to-one)
- **Asistencia**: Daily attendance tracking with auto-email for unjustified absences

### Request Flow Pattern
1. All CRUD views use function-based views with `@login_required` decorator
2. Staff operations (maestros, secciones) require `@staff_member_required`
3. Forms handle all validation in `core/forms.py` with Bootstrap 5 styling
4. Success redirects to detail/list views with `messages.success()` feedback
5. Soft deletes: `activo=False` instead of `.delete()` for `Nino` model

### Email Integration (`core/email.py`)
- Uses **Brevo (Sendinblue) API v3 SDK** not SMTP
- `enviar_notificacion_inasistencia()` triggered for absences without `motivo_inasistencia`
- API key loaded from environment: `os.getenv("BREVO_API_KEY")`
- Error handling logs to console with `ApiException` catch blocks

## Key Development Patterns

### Database Configuration
- **Production**: PostgreSQL via Neon (hardcoded connection string in `settings.py`)
- **Local**: Falls back to SQLite `db.sqlite3`
- Always check `DEBUG` mode: database selection depends on `dj_database_url.parse()`

### Environment Variables (.env file)
```bash
SECRET_KEY=your-secret-key
DEBUG=True  # String comparison: 'True' == 'True'
ALLOWED_HOSTS=localhost 127.0.0.1
BREVO_API_KEY=xkeysib-...
```

### Forms & Validation
- All fields use Bootstrap classes: `form-control`, `form-select`, `form-check-input`
- Custom validation in `clean()` methods (e.g., `ResponsableAutorizadoForm` validates date ranges)
- Electronic signatures stored as base64 in `firma_electronica` hidden field
- File uploads: images to `media/fotos_ninos/`, documents to `media/documentos_medicos/`

### Template Structure
- **Base Template**: `base.html` includes Bootstrap 5, Bootstrap Icons CDN
- **Conditional Navigation**: Authenticated users see "Niños", "Académico" dropdown, "Asistencia"
- **Messages**: Django messages mapped to Bootstrap alerts via `MESSAGE_TAGS` in settings
- **Dynamic Dropdowns**: `AsignarAulaForm` shows "Aula - Sección - Maestro: Nombre" format

### AJAX Patterns (`reporte_diario.html`)
- Attendance updates via `actualizar_asistencia_ajax` endpoint (POST JSON)
- Expects: `{nino_id, presente, motivo}`
- Returns: `{success, motivo, notificacion_enviada, nombre_nino}`
- Auto-triggers email if `presente=False` and no `motivo` provided

## Development Commands

### Setup & Run
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Database migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Run development server
python manage.py runserver
```

### Static Files (Production)
```bash
python manage.py collectstatic --noinput
```
Uses **WhiteNoise** for serving static files with compression (`CompressedManifestStaticFilesStorage`)

## URL Routing Conventions

- Nested resources: `/ninos/<int:nino_pk>/responsables/`
- CRUD pattern: `lista_*`, `registrar_*`, `detalle_*`, `editar_*`, `eliminar_*`
- AJAX endpoints: suffix `-ajax` (e.g., `actualizar_asistencia_ajax`)

### Example URL Structure
```
/ninos/                           → lista_ninos
/ninos/registrar/                 → registrar_nino
/ninos/5/                         → detalle_nino (pk=5)
/ninos/5/editar/                  → editar_nino
/ninos/5/responsables/            → lista_responsables
/ninos/5/asignar-aula/            → asignar_aula
/asistencia/reporte/              → reporte_asistencia_diario
```

## Testing Strategy
- No automated tests currently in codebase
- Manual testing via Django admin (`/admin/`) and UI
- Check email delivery in Brevo dashboard (https://app.brevo.com)

## Common Pitfalls

1. **Email not sending**: Verify `BREVO_API_KEY` in environment, check `DEFAULT_FROM_EMAIL='ra16004@ues.edu.sv'`
2. **Static files 404**: Run `collectstatic` and ensure `STATIC_ROOT = BASE_DIR / 'staticfiles'`
3. **Migration conflicts**: Delete `db.sqlite3` and re-run migrations in development
4. **Form validation errors**: Hidden field `firma_electronica` must be populated via JavaScript (not in this codebase)
5. **Permission errors**: Views like `lista_maestros` require staff status; non-staff users get 403

## Project-Specific Quirks

- **Spanish language**: All UI text, model verbose names, and comments in Spanish
- **Custom template tag**: `dict_extras.py` provides `|get_item` filter for dictionary access in templates
- **Attendance logic**: Children auto-created in `Asistencia` table with `get_or_create()` on report page load
- **Soft delete pattern**: Only `Nino` uses `activo=False`; other models use hard deletes
- **Date formatting**: `DATE_FORMAT = 'd/m/Y'` (day/month/year) with `USE_L10N = False`

## When Adding Features

- **New model**: Add to `core/models.py`, create migration, update admin registration
- **New view**: Follow pattern: form class → view function → URL pattern → template
- **Email notifications**: Extend `core/email.py` with new Brevo transactional email function
- **Authentication required**: Always use `@login_required` decorator on views
- **File uploads**: Add `enctype="multipart/form-data"` to forms, use `request.FILES` in views
