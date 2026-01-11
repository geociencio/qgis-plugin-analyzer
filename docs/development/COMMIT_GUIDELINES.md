# Commit Guidelines 📜

Este proyecto sigue el estándar de **Conventional Commits** para mantener un historial de cambios legible, profesional y fácil de automatizar.

## Estructura del Mensaje

```text
<tipo>(<alcance>): <descripción corta>

[cuerpo opcional]

[pie de página opcional]
```

## Tipos de Commit

| Tipo | Descripción | Ejemplo |
| :--- | :--- | :--- |
| `feat` | Una nueva funcionalidad para el usuario. | `feat(api): add export to GeoJSON` |
| `fix` | Corrección de un error (bug). | `fix(engine): resolve null reference in scanner` |
| `docs` | Cambios solo en la documentación. | `docs: add installation instructions` |
| `style` | Cambios que no afectan el significado del código (espacios, formato). | `style: run black formatter` |
| `refactor` | Cambio en el código que ni corrige un error ni añade una funcionalidad. | `refactor: simplify rule detection logic` |
| `perf` | Cambio en el código que mejora el rendimiento. | `perf: optimize AST traversal` |
| `test` | Añadir o corregir pruebas existentes. | `test: add cases for circular dependencies` |
| `chore` | Cambios en el proceso de construcción o herramientas auxiliares. | `chore: update dependencies` |

## Reglas de Oro

1.  **Idioma**: Los mensajes de commit deben escribirse en **inglés**.
2.  **Modo Imperativo**: Usa "Add" en lugar de "Added".
3.  **Sin punto final**: No termines la descripción con un punto.
4.  **Minúsculas**: La descripción debe empezar en minúsculas después del tipo.
5.  **Concisión**: Mantén la primera línea por debajo de los 72 caracteres.

---
*Mantener estas reglas ayuda a generar Changelogs automáticos y facilita la colaboración.*
