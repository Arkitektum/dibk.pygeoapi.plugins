"""The dibk.pygeoapi.plugins.* names resolve to the plugin classes."""

import importlib
import importlib.util
import subprocess
import sys

import pytest
from pygeoapi.plugin import load_plugin

HAS_GDAL = importlib.util.find_spec("osgeo") is not None
needs_gdal = pytest.mark.skipif(not HAS_GDAL, reason="requires the GDAL Python bindings")

NAMES = [
    pytest.param(
        "dibk.pygeoapi.plugins.provider.PostgreSQL",
        "postgresql_provider", "PostgreSQLProvider", marks=needs_gdal),
    pytest.param(
        "dibk.pygeoapi.plugins.provider.MvtPostgreSQL",
        "mvt_postgresql_provider", "MVTPostgreSQLProvider"),
    pytest.param(
        "dibk.pygeoapi.plugins.provider.Styles",
        "styles_provider", "StyleProvider"),
    pytest.param(
        "dibk.pygeoapi.plugins.formatter.JsonFG",
        "jsonfg_formatter", "JsonFgFormatter", marks=needs_gdal),
    pytest.param(
        "dibk.pygeoapi.plugins.formatter.reguleringsplan_20190401.Reguleringsplan",
        "gml_npad_formatter.reguleringsplan_20190401", "ReguleringsplanFormatter"),
    pytest.param(
        "dibk.pygeoapi.plugins.formatter.kommuneplan_20190401.Kommuneplan",
        "gml_npad_formatter.kommuneplan_20190401", "KommuneplanFormatter"),
]


def _resolve(name: str):
    # The same lookup pygeoapi.plugin.load_plugin does for dotted names.
    module_name, class_name = name.rsplit(".", 1)
    return getattr(importlib.import_module(module_name), class_name)


@pytest.mark.parametrize(("name", "module", "class_name"), NAMES)
def test_name_resolves_to_plugin_class(name, module, class_name):
    expected = getattr(importlib.import_module(module), class_name)

    assert _resolve(name) is expected


def test_pygeoapi_loads_plugin_by_name():
    formatter = load_plugin("formatter", {
        "name": "dibk.pygeoapi.plugins.formatter.reguleringsplan_20190401.Reguleringsplan",
        "feature_type": "RpOmråde",
    })

    assert type(formatter).__name__ == "ReguleringsplanFormatter"


def test_plugin_packages_are_imported_on_first_access():
    # A fresh interpreter, so earlier tests have not imported anything yet.
    code = (
        "import sys\n"
        "import dibk.pygeoapi.plugins.provider as p\n"
        "assert 'styles_provider' not in sys.modules\n"
        "p.Styles\n"
        "assert 'styles_provider' in sys.modules\n"
        "assert 'postgresql_provider' not in sys.modules\n"
    )

    subprocess.run([sys.executable, "-c", code], check=True)


def test_unknown_name_raises_attribute_error():
    from dibk.pygeoapi.plugins import provider

    with pytest.raises(AttributeError, match="Postgres"):
        provider.Postgres


def test_dir_lists_public_names():
    from dibk.pygeoapi.plugins import formatter, provider

    assert dir(provider) == ["MvtPostgreSQL", "PostgreSQL", "Styles"]
    assert dir(formatter) == ["JsonFG"]
