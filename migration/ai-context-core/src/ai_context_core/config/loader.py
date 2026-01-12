
import yaml
import pathlib
from typing import Dict, Any, Optional

class ConfigLoader:
    """Carga y gestiona la configuración del analizador."""

    def __init__(self):
        self.base_path = pathlib.Path(__file__).parent
        self.defaults_path = self.base_path / "defaults.yaml"
        self.profiles_path = self.base_path / "profiles"

    def load_config(self, profile_name: Optional[str] = None, override_config: Optional[Dict] = None) -> Dict[str, Any]:
        """Carga la configuración combinando defaults, perfil y overrides."""
        
        # 1. Cargar defaults
        config = self._load_yaml(self.defaults_path)

        # 2. Cargar perfil si se especificó
        if profile_name:
            profile_file = self.profiles_path / f"{profile_name}.yaml"
            if profile_file.exists():
                profile_config = self._load_yaml(profile_file)
                config = self._merge_dicts(config, profile_config)
            else:
                print(f"⚠️ Perfil '{profile_name}' no encontrado en {self.profiles_path}. Usando defaults.")

        # 3. Aplicar overrides (ej. desde CLI)
        if override_config:
            config = self._merge_dicts(config, override_config)

        return config

    def _load_yaml(self, path: pathlib.Path) -> Dict[str, Any]:
        """Carga un archivo YAML de forma segura."""
        try:
            return yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        except Exception as e:
            print(f"❌ Error cargando config {path}: {e}")
            return {}

    def _merge_dicts(self, base: Dict, update: Dict) -> Dict:
        """Combina dos diccionarios recursivamente."""
        for key, value in update.items():
            if isinstance(value, dict) and key in base and isinstance(base[key], dict):
                base[key] = self._merge_dicts(base[key], value)
            else:
                base[key] = value
        return base

def list_profiles() -> list[str]:
    """Lista los perfiles disponibles."""
    profiles_dir = pathlib.Path(__file__).parent / "profiles"
    if not profiles_dir.exists():
        return []
    return [p.stem for p in profiles_dir.glob("*.yaml")]
