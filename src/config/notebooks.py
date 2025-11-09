"""Notebook configuration and metadata."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class NotebookConfig:
    """Configuration for a single notebook/document."""

    name: str
    local_path: str
    description: str
    category: str = "general"
    gdrive_id: Optional[str] = None  # Deprecated: kept for backwards compatibility

    def __post_init__(self):
        """Validate configuration after initialization."""
        if not self.local_path:
            raise ValueError(f"local_path is required for notebook '{self.name}'")


# Notebook database - centralized configuration
NOTEBOOKS = {
    "Apuntes de Análisis Real": NotebookConfig(
        name="Apuntes de Análisis Real",
        local_path="data/notebooks/Analisis_Real.pdf",
        description="Usa esta herramienta para buscar información sobre Análisis Real, matemáticas, límites, continuidad, derivadas, integrales y teoremas matemáticos.",
        category="mathematics"
    ),
    "Lógica Computacional": NotebookConfig(
        name="Lógica Computacional",
        local_path="data/notebooks/Lógica_Computacional.pdf",
        description="Usa esta herramienta para buscar información sobre Lógica Computacional, lógica proposicional, lógica de predicados, cálculo lógico, teoremas de computación.",
        category="computer_science"
    ),
    "Disposiciones Generales (Ejemplo)": NotebookConfig(
        name="Disposiciones Generales (Ejemplo)",
        local_path="data/notebooks/2._Libro_1___Disposiciones_Generales.pdf",
        description="Usa esta herramienta para buscar información sobre disposiciones generales, definiciones y explicaciones del RETIE (Reglamento Técnico de Instalaciones Eléctricas).",
        category="regulations"
    )
}


def get_notebook_by_name(name: str) -> Optional[NotebookConfig]:
    """Get notebook configuration by name."""
    return NOTEBOOKS.get(name)


def get_all_notebooks() -> dict[str, NotebookConfig]:
    """Get all configured notebooks."""
    return NOTEBOOKS


def get_notebooks_by_category(category: str) -> dict[str, NotebookConfig]:
    """Get notebooks filtered by category."""
    return {
        name: config
        for name, config in NOTEBOOKS.items()
        if config.category == category
    }
