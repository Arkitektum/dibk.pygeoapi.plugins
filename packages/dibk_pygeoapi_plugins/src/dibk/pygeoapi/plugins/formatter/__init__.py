"""pygeoapi formatters, e.g. ``name: dibk.pygeoapi.plugins.formatter.JsonFG``.

The SOSI-GML formatters live in one submodule per product specification
version, e.g. ``reguleringsplan_20190401.Reguleringsplan``.
"""

from .._lazy import lazy_classes

__getattr__, __dir__ = lazy_classes(__name__, {
    "JsonFG": ("jsonfg_formatter", "JsonFgFormatter"),
})
