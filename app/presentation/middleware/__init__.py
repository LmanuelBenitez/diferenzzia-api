"""Presentation middleware package.

Exposes helpers to configure CORS and global error handling.
"""

from app.presentation.middleware.cors import configure_cors
from app.presentation.middleware.error_handler import register_exception_handlers

__all__ = ["configure_cors", "register_exception_handlers"]
