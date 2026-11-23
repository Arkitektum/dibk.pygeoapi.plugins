"""SOSI-GML Reguleringsplan 20190401 formatter."""

from .._lazy import lazy_classes

__getattr__, __dir__ = lazy_classes(__name__, {
    "Reguleringsplan": (
        "gml_npad_formatter.reguleringsplan_20190401", "ReguleringsplanFormatter"),
})
