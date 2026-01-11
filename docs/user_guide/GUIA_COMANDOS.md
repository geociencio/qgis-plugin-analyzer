# 🛡️ Guía Detallada de Comandos (GIS) - QGIS Plugin Analyzer

El **QGIS Plugin Analyzer** es una herramienta de auditoría avanzada diseñada para garantizar que los complementos de QGIS (PyQGIS) cumplan con los más altos estándares de calidad, seguridad y mantenibilidad. Esta guía detalla cada comando disponible, sus parámetros y los escenarios recomendados de uso.

---

## � Instalación

Puedes instalar el **QGIS Plugin Analyzer** de varias formas, dependiendo de tu flujo de trabajo:

### A. Usando `uv` (Recomendado - Aislado y Rápido)
Si usas [uv](https://github.com/astral-sh/uv), puedes instalarlo como una herramienta global aislada:

```bash
# Instalación global (recomendado para uso frecuente)
uv tool install git+https://github.com/geociencio/qgis-plugin-analyzer.git
```

### B. Usando `pip`
Ideal para entornos virtuales estándar o instalaciones directas:

```bash
# Desde el repositorio de GitHub
pip install git+https://github.com/geociencio/qgis-plugin-analyzer.git

# Si tienes el código descargado localmente
pip install .
```

### C. Instalación para Desarrollo (Local)
Si deseas contribuir o modificar el código:

```bash
git clone https://github.com/geociencio/qgis-plugin-analyzer
cd qgis-plugin-analyzer
uv sync
```

---

## �📋 Referencia de Comandos CLI

El comando principal es `qgis-analyzer`. A continuación, se detallan sus subcomandos:

### 1. `analyze` (El Motor de Auditoría)
Analiza un proyecto de forma exhaustiva, generando métricas de complejidad, estabilidad y detección de problemas específicos de QGIS.

**Uso base:**
```bash
qgis-analyzer analyze /ruta/al/plugin
```

**Parámetros principales:**
- `-o, --output`: Directorio para los reportes (por defecto: `./analysis_results`).
- `-r, --report`: Genera reportes detallados en HTML y Markdown.
- `-p, --profile`: Especifica el perfil de configuración en `pyproject.toml` (ej. `default`, `release`).

> [!TIP]
> Si ejecutas `qgis-analyzer /ruta/al/plugin` sin subcomando, el sistema asumirá automáticamente el comando `analyze`.

---

### 2. `fix` (Corrección Automatizada)
El "Ángel Guardián" de tu código. Permite corregir automáticamente problemas comunes detectados por las reglas de auditoría.

**Uso base:**
```bash
qgis-analyzer fix /ruta/al/plugin
```

**Opciones de control:**
- `--dry-run`: (Activado por defecto) Muestra los cambios propuestos sin aplicarlos.
- `--apply`: Ejecuta las modificaciones directamente en los archivos.
- `--auto-approve`: Aplica todos los cambios sin pedir confirmación interactiva.
- `--rules`: Permite filtrar qué reglas arreglar (ej. `--rules QGS101,QGS105`).

---

### 3. `summary` (Resumen Ejecutivo)
Ideal para obtener una visión rápida de la salud del proyecto directamente en la terminal sin abrir reportes externos.

**Uso base:**
```bash
qgis-analyzer summary
```

**Niveles de granularidad (`-b, --by`):**
- `total`: (Por defecto) Un resumen general de todo el proyecto.
- `modules`: Desglose por archivos Python.
- `classes`: Análisis de la complejidad de las clases.
- `functions`: Identificación de funciones con alta deuda técnica.

---

### 4. `list-rules` (Catálogo de Reglas)
Muestra la lista completa de reglas de auditoría implementadas, su severidad y el mensaje de error asociado.

**Uso:**
```bash
qgis-analyzer list-rules
```

---

### 5. `init` (Configuración Rápida)
Crea un archivo `.analyzerignore` en el directorio actual con los patrones de exclusión recomendados por la comunidad (venvs, caches, builds, etc.).

**Uso:**
```bash
qgis-analyzer init
```

---

## 🚀 Escenarios de Uso (Casos Prácticos)

### A. Auditoría previa a Publicación
Antes de subir tu complemento al [Repositorio Oficial de QGIS](https://plugins.qgis.org/), utiliza el perfil `release` para asegurar el cumplimiento estricto.

```bash
qgis-analyzer analyze . -p release -r
```
*   **Qué busca:** Binarios prohibidos, tamaño del paquete, validez de URLs en `metadata.txt` y cumplimiento estricto de estándares.

### B. Integración Continua (CI/CD)
Puedes integrar el analizador en GitHub Actions para bloquear PRs que introduzcan dependencias circulares o alta complejidad.

```yaml
- name: Run Quality Check
  run: qgis-analyzer analyze . --profile release
```

### C. Refactorización de Código Heredado
Si estás trabajando en un plugin antiguo, usa `summary --by functions` para identificar rápidamente las partes más complejas del código.

```bash
qgis-analyzer summary --by functions
```

---

## ⚙️ Personalización Avanzada

### Archivo `pyproject.toml`
Puedes definir perfiles personalizados para adaptar el rigor del análisis:

```toml
[tool.qgis-analyzer.profiles.mi_perfil]
strict = true
fail_on_error = true
[tool.qgis-analyzer.profiles.mi_perfil.rules]
QGS101 = "error"   # Prohibir absolutamente importaciones de GDAL directas
QGS303 = "ignore"  # Ignorar validación de iconos por ahora
```

### Archivo `.analyzerignore`
Usa este archivo para excluir carpetas que no deben ser analizadas (ej. librerías externas o archivos de datos comprimidos).

---
*Documentación generada para la comunidad PyQGIS.*
