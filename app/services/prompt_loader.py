from pathlib import Path

import yaml


class PromptLoader:
    """
    Manages AI prompt templates by loading configurations from YAML and
    caching markdown content from the filesystem during initialization.
    """

    def __init__(self):
        # Root-level prompts folder
        self.base_path = Path(__file__).resolve().parent.parent.parent / "prompts"

        # Load yaml
        with open(self.base_path / "prompts.yaml", "r") as f:
            self.config = yaml.safe_load(f)

        # Cache ALL markdown files once at init
        self.cache = {}
        self._preload_files()

    def _preload_files(self):
        """
        Iterates through prompt subdirectories to read and cache markdown
        content into memory using structured keys for quick access.
        """
        for folder in ["base", "core", "rules", "styles", "intensity"]:
            dir_path = self.base_path / folder
            if not dir_path.exists():
                continue

            for file in dir_path.glob("*.md"):
                key = f"{folder}/{file.stem}"
                self.cache[key] = file.read_text().strip()

    def _get(self, path: str) -> str:
        """
        Retrieves a cached prompt string by its path key, returning an empty
        string if the key does not exist.
        """
        return self.cache.get(path, "")

    def build(self, name: str, intensity_override: str | None = None, **kwargs) -> str:
        """
        Assembles a final prompt string by layering base, core, style, and rule
        sections, applying intensity levels, and injecting dynamic keyword arguments.
        """
        cfg = self.config[name]
        parts = []

        # base → core → styles → rules → intensity (last = strongest)

        # Base
        base_name = Path(cfg["base"]).stem
        parts.append(self._get(f"base/{base_name}"))

        # Layered sections
        for section in ["core", "styles", "rules"]:
            for item in cfg.get(section, []):
                parts.append(self._get(f"{section}/{item}"))

        # Intensity
        intensity = intensity_override or cfg.get("intensity", "medium")
        parts.append(self._get(f"intensity/{intensity}"))

        prompt = "\n\n".join(p for p in parts if p)

        return prompt.format(**kwargs)


loader = PromptLoader()
