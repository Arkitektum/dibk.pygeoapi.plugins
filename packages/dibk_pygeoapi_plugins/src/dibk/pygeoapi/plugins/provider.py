"""pygeoapi providers, e.g. ``name: dibk.pygeoapi.plugins.provider.PostgreSQL``."""

from ._lazy import lazy_classes

__getattr__, __dir__ = lazy_classes(__name__, {
    "PostgreSQL": ("postgresql_provider", "PostgreSQLProvider"),
    "MvtPostgreSQL": ("mvt_postgresql_provider", "MVTPostgreSQLProvider"),
    "Styles": ("styles_provider", "StyleProvider"),
})
