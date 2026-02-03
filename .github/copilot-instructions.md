# Copilot / AI Agent Instructions for Proyecto_qome

Purpose: quick, actionable guidance so an AI coding agent can be productive immediately in this repository.

- **Repo type:** Django web app (SQLite by default) with utility scripts in `ZZ_acciones/`.
- **Entry points:** run web app with `python manage.py runserver`, manage DB with `python manage.py migrate`, load seed data with `python manage.py loaddata recetas_seed.json`.

Key architecture notes
- The Django project settings live in `qome_backend/settings.py` and the main app is `core/`.
- Models and domain logic are concentrated in `core/models.py` (ingredients, productos reales, recetas, planes semanales).
- Templates are under `core/templates/core/` and follow standard Django template usage.

Important project-specific patterns
- We store weights and recipe amounts in grams everywhere: `RecetaIngrediente.cantidad_gramos` and `ProductoReal.peso_gramos`.
- `ProductoReal.save()` contains specialized weight-extraction logic (math via `precio_por_unidad_medida` then regex). See `core/models.py` methods `_extraer_peso_regex()` and `_convertir_a_gramos()` — prefer preserving this logic when changing product ingestion.
- `PlanSemanal.lista_compra_generada` is JSON stored in a `TextField` (not a JSONField). When producing or consuming it, convert to/from string explicitly.
- Nutritional values are per-100g on `IngredienteBase` (e.g., `calorias` is kcal per 100g). `Receta.calorias_totales()` multiplies by grams accordingly.

Developer workflows & commands
- Run dev server: `python manage.py runserver`.
- Apply migrations: `python manage.py migrate`.
- Create superuser: `python manage.py createsuperuser`.
- Run tests: `python manage.py test` (limit to `core` when iterating: `python manage.py test core`).
- Load seed data: `python manage.py loaddata recetas_seed.json` (file at repo root).

Utility & integration points
- One-off scripts and scrapers live in `ZZ_acciones/` (e.g., `scraper_mercadona.py`, `sembrar_nutricion.py`). These are not packaged Django management commands — inspect each script before running. Prefer running them in the Django context via the shell if they import models:

  python manage.py shell
  >>> exec(open('ZZ_acciones/sembrar_nutricion.py').read())

- DB: `db.sqlite3` in repo root — local development only.

Conventions and pitfalls to watch
- Units: treat `tipo_unidad` values `KG`, `L`, `UD` with care. Conversions assume 1L ≈ 1000g for recipe calculations.
- When editing product ingestion, preserve the save() heuristics: math-based PUM first, then regex fallback, then default 1000g.
- Avoid changing the `lista_compra_generada` storage type without migrating existing data (it's free-form JSON-in-text today).
- Tests are lightweight; add focused unit tests for parsing logic (e.g., regex weight extraction) if you change `ProductoReal`.

Useful files to inspect
- `core/models.py` — domain model and important parsing/save logic
- `qome_backend/settings.py` — Django configuration (databases, installed apps)
- `manage.py` — standard Django CLI
- `recetas_seed.json` — initial data set for recipes
- `ZZ_acciones/` — utilities, scrapers, and seed helpers

When editing code
- Keep changes minimal and preserve database-backed field semantics.
- If adding new data fields used in templates or serialization, add a migration and update any seed scripts under `ZZ_acciones/`.

If you need clarification
- Ask for the intended runtime (local vs production) and whether running `ZZ_acciones/` scripts in-process is acceptable. When unsure, prefer safe, read-only analysis and tests rather than executing scrapers.

Feedback request: If any areas are unclear (e.g., which scrapers are safe to run, or expected production config), tell me and I'll expand the instructions.
