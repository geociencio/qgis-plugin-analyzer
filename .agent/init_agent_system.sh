#!/bin/bash
# init_agent_system.sh
# Inicializa el framework agentico genérico configurando variables en los workflows.

set -e

echo "============================================================"
echo "    🚀  Antigravity Framework - Initialization Script  🚀   "
echo "============================================================"
echo ""
echo "Este script configurará las variables base en los workflows (.agent/workflows/)."
echo ""

read -p "Ingresa el comando principal para ejecutar tests (ej. 'npm run test', 'make test', 'pytest'): " MASTER_TEST_COMMAND
read -p "Ingresa el comando para reparar/formatear código (ej. 'npm run lint:fix', 'ruff check --fix . && ruff format .'): " LINTER_FIX_COMMAND
read -p "Ingresa el comando para chequear complejidad o ejecución pre-commit (ej. 'npm run build', 'radon cc . -a'): " COMP_CHECK_COMMAND
read -p "Ingresa el comando para sincronizar dependencias (ej. 'npm install', 'uv sync'): " SYNC_COMMAND

echo ""
echo "🔄 Reemplazando variables en workflows..."

find .agent/workflows -type f -name "*.md" -print0 | while IFS= read -r -d '' file; do
    sed -i "s/{{MASTER_TEST_COMMAND}}/${MASTER_TEST_COMMAND//\//\\/}/g" "$file"
    sed -i "s/{{LINTER_FIX_COMMAND}}/${LINTER_FIX_COMMAND//\//\\/}/g" "$file"
    sed -i "s/{{COMPLEXITY_CHECK_COMMAND}}/${COMP_CHECK_COMMAND//\//\\/}/g" "$file"
    sed -i "s/{{SYNC_DEPENDENCIES_COMMAND}}/${SYNC_COMMAND//\//\\/}/g" "$file"
    # Fallbacks de test
    sed -i "s/{{UNIT_TEST_COMMAND}}/${MASTER_TEST_COMMAND//\//\\/}/g" "$file"
    sed -i "s/{{INTEGRATION_TEST_COMMAND}}/${MASTER_TEST_COMMAND//\//\\/}/g" "$file"
    sed -i "s/{{PRE_COMMIT_CHECK_COMMAND}}/${COMP_CHECK_COMMAND//\//\\/}/g" "$file"
done

echo "✅ Inicialización completada."
echo "👉 Recomendación: Edita .agent/skills/project-context/SKILL.md para reflejar tu arquitectura real."
echo "👉 Recomendación: Edita .agent/skills/coding-standards/SKILL.md si quieres estándares estrictos específicos."
