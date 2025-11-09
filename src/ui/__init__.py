"""UI layer for AI Study Assistant."""

from .styles import apply_custom_styles, render_header
from .components import UIComponents
from .pages import DocumentViewerPage, ChatAssistantPage

__all__ = ["apply_custom_styles", "render_header", "UIComponents", "DocumentViewerPage", "ChatAssistantPage"]
