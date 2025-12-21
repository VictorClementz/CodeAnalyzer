"""
Configuration package for language-specific settings.
"""

from .thresholds import LANGUAGE_CONFIGS, get_language_config, get_supported_languages

__all__ = ['LANGUAGE_CONFIGS', 'get_language_config', 'get_supported_languages']
