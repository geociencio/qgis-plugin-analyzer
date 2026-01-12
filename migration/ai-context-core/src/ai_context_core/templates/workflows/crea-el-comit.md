
---
description: Crea el comit asegurando calidad (Ruff), métricas y changelog.
---

# Workflow: Crea el Comit (Enhanced)

Este workflow es el estándar de oro para guardar cambios. No solo hace commit, sino que limpia el código, actualiza la memoria del proyecto y asegura documentación.

## Pasos del Workflow

1.  **Higiene de Código (Automático)**:
    Antes de nada, asegura que el código esté limpio y formateado para evitar rechazos del CI.
    // turbo
    ```bash
    uv run ruff check --fix .
    uv run ruff format .
    ```

2.  **Sincronización de Impacto (IA)**:
    Actualiza las métricas para entender cómo estos cambios afectan la complejidad del proyecto.
    // turbo
    ```bash
    ai-ctx analyze
    ```

3.  **Actualizar CHANGELOG.md**:
    *   Revisa `git status`.
    *   Inserta una línea concisa en la sección `[Unreleased]` de `CHANGELOG.md` describiendo el valor aportado.

4.  **Generar Mensaje de Commit**:
    Redacta un mensaje siguiendo las directrices en `docs/development/COMMIT_GUIDELINES.md`.
    *   **Formato**: `<tipo>: <descripción en inglés>`
    *   **Tipos**: `feat`, `fix`, `docs`, `chore`, `refactor`, `test`.

5.  **Ejecución**:
    Consolida los cambios.
    // turbo
    ```bash
    git add .
    git commit -m "<mensaje_generado>"
    ```

## Notas Importantes
- Si `ruff` modificó archivos en el paso 1, esos cambios se incluirán automáticamente en el commit.
- Si el mensaje generado no te convence, edítalo antes de aprobar el comando final.
