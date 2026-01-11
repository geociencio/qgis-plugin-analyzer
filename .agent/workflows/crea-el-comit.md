---
description: Crea el commit y actualiza CHANGELOG.md automáticamente
---

# Workflow: Crea el Comit

Este workflow automatiza la actualización del historial de cambios y la realización del commit siguiendo los estándares del proyecto.

## Pasos del Workflow

1.  **Analizar Cambios**:
    Analiza los archivos modificados en el área de preparación (staging) o en el directorio de trabajo.
    ```bash
    git status
    ```

2.  **Actualizar CHANGELOG.md**:
    Inserta una breve descripción de los cambios en la sección `[Unreleased]` del archivo `CHANGELOG.md`. 
    > [!IMPORTANT]
    > Si la sección `[Unreleased]` no existe, se debe crear debajo de la cabecera.

3.  **Generar Mensaje de Commit**:
    Redacta un mensaje siguiendo las directrices en `docs/development/COMMIT_GUIDELINES.md`. El formato debe ser: `<tipo>: <descripción en inglés>`.

4.  **Ejecutar Commit**:
    Ejecuta los comandos de git para consolidar los cambios.
    // turbo
    ```bash
    git add .
    git commit -m "<mensaje_generado>"
    ```

## Reglas Críticas
- El mensaje **DEBE** estar en inglés.
- El tipo debe ser uno de los definidos (feat, fix, docs, chore, etc.).
- La actualización del `CHANGELOG.md` es obligatoria antes del commit.
