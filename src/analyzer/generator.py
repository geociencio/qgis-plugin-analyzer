import pathlib
from .utils import logger


class ProjectGenerator:
    """Generates QGIS plugin projects from templates."""

    def __init__(self, target_path: str):
        self.target_path = pathlib.Path(target_path).resolve()
        self.template_dir = pathlib.Path(__file__).parent / "templates"

    def generate(self, plugin_type: str, context: dict):
        """Generates the plugin structure."""
        if not self.target_path.exists():
            self.target_path.mkdir(parents=True)

        logger.info(f"🚀 Generating plugin in: {self.target_path}")

        # 1. Copy base files
        self._copy_and_render("base", context)

        # 2. Copy type-specific files
        self._copy_and_render(plugin_type, context)

        # 3. Handle special name mappings
        self._finalize_structure(plugin_type, context)

        logger.info(f"✅ Plugin '{context['name']}' created successfully!")

    def _copy_and_render(self, template_name: str, context: dict):
        source = self.template_dir / template_name
        if not source.exists():
            logger.warning(f"⚠️ Template '{template_name}' not found.")
            return

        for item in source.iterdir():
            if item.is_file():
                content = item.read_text(encoding="utf-8")
                # Simple variable substitution
                for key, value in context.items():
                    content = content.replace(f"{{{{{key}}}}}", str(value))

                target_name = item.name.replace(".tmpl", "")
                target_file = self.target_path / target_name
                target_file.write_text(content, encoding="utf-8")

    def _finalize_structure(self, plugin_type: str, context: dict):
        # Specific mappings (e.g., algorithm.py -> plugin.py if needed, or keeping them separate)
        if plugin_type == "processing":
            # In processing, we usually have a main file with the algorithm
            # By default copied as algorithm.py, maybe we want to rename it or provide a plugin.py
            pass
        elif plugin_type == "gui":
            # already named plugin.py
            pass
        elif plugin_type == "map_tool":
            # already named plugin.py
            pass

        # Create a dummy icon if not exists
        icon_path = self.target_path / "icon.png"
        if not icon_path.exists():
            with open(icon_path, "wb") as f:
                # 1x1 transparent pixel or similar
                f.write(
                    b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82"
                )
