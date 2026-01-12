
import click
import pathlib
import shutil
import os
from typing import Optional

from .analyzer.engine import ProjectAnalyzer
from .config.loader import ConfigLoader, list_profiles

@click.group()
def cli():
    """Herramienta CLI para gestión de contexto IA y análisis de proyectos."""
    pass

@cli.command()
@click.option("--profile", "-p", help="Perfil de configuración (ej. qgis-plugin)", default="generic")
@click.option("--path", default=".", help="Ruta del proyecto")
def init(profile: str, path: str):
    """Inicializa la estructura .ai-context en el proyecto."""
    project_path = pathlib.Path(path).resolve()
    ai_context_dir = project_path / ".ai-context"
    agent_workflows_dir = project_path / ".agent" / "workflows"
    
    click.echo(f"🔄 Inicializando AI Context en {project_path} con perfil '{profile}'...")

    # 1. Crear directorios
    ai_context_dir.mkdir(exist_ok=True)
    agent_workflows_dir.mkdir(parents=True, exist_ok=True)

    # 2. Copiar/Generar Config
    loader = ConfigLoader()
    # Cargar config base del perfil para escribirla
    if profile != "generic":
        profile_path = loader.profiles_path / f"{profile}.yaml"
        if profile_path.exists():
            shutil.copy2(profile_path, ai_context_dir / "config.yaml")
            click.echo(f"✅ Configuración de perfil '{profile}' copiada.")
        else:
            click.secho(f"⚠️ Perfil '{profile}' no encontrado. Usando configuración base.", fg="yellow")
    
    # 3. Copiar Workflows
    templates_dir = pathlib.Path(__file__).parent / "templates" / "workflows"
    if templates_dir.exists():
        for wf in templates_dir.glob("*.md"):
            dest = agent_workflows_dir / wf.name
            if not dest.exists():
                shutil.copy2(wf, dest)
                click.echo(f"✅ Workflow instalado: {wf.name}")
            else:
                click.echo(f"ℹ️ Workflow {wf.name} ya existe. Saltando.")

    # 4. Copiar Prompt Inicial
    prompt_src = pathlib.Path(__file__).parent / "templates" / "initial_prompt.md"
    prompt_dest = ai_context_dir / "prompt_inicial.md"
    if prompt_src.exists() and not prompt_dest.exists():
        content = prompt_src.read_text(encoding="utf-8")
        # Reemplazar placeholders básicos
        content = content.replace("{project_name}", project_path.name)
        content = content.replace("{project_type}", profile)
        prompt_dest.write_text(content, encoding="utf-8")
        click.echo("✅ Prompt inicial generado.")

    click.secho("✨ Inicialización completada exitosamente.", fg="green")

@cli.command()
@click.option("--path", default=".", help="Ruta del proyecto")
@click.option("--workers", "-w", default=None, type=int, help="Número de workers paralelos")
@click.option("--no-cache", is_flag=True, help="Deshabilitar caché")
def analyze(path: str, workers: Optional[int], no_cache: bool):
    """Ejecuta el análisis del proyecto y actualiza el contexto."""
    project_path = pathlib.Path(path).resolve()
    
    # Cargar configuración
    loader = ConfigLoader()
    
    # Intentar detectar perfil o cargar config local
    local_config_path = project_path / ".ai-context" / "config.yaml"
    local_config = {}
    profile_name = None
    
    if local_config_path.exists():
        try:
            import yaml
            local_config = yaml.safe_load(local_config_path.read_text()) or {}
            profile_name = local_config.get("profile_name")
        except:
            pass
            
    # Cargar config final
    config = loader.load_config(profile_name=profile_name, override_config=local_config)
    
    # Instanciar analizador
    analyzer = ProjectAnalyzer(
        project_path=str(project_path),
        config=config,
        max_workers=workers
    )
    
    click.echo(f"🚀 Iniciando análisis de {project_path.name}...")
    
    try:
        results = analyzer.analyze()
        
        metrics = results.get("metrics", {})
        quality = metrics.get('quality_score', 0)
        
        click.echo("-" * 40)
        click.secho(f"🏆 Score de Calidad: {quality:.1f}/100", fg="green" if quality > 80 else "yellow")
        click.echo(f"📊 Líneas de Código: {metrics.get('total_lines_code', 0):,}")
        click.echo(f"💡 Optimizaciones: {len(results.get('optimizations', []))}")
        click.echo("-" * 40)
        click.secho("✅ Análisis completado y contexto actualizado.", fg="green")
        
    except Exception as e:
        click.secho(f"❌ Error durante el análisis: {e}", fg="red")
        if os.environ.get("DEBUG"):
            raise e
        import sys
        sys.exit(1)

@cli.command()
def profiles():
    """Lista los perfiles de configuración disponibles."""
    click.echo("Perfiles disponibles:")
    for p in list_profiles():
        click.echo(f" - {p}")

if __name__ == "__main__":
    cli()
