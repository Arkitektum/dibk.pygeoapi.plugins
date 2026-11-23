"""SOSI-GML Kommuneplan 20190401 formatter."""

from .._lazy import lazy_classes

__getattr__, __dir__ = lazy_classes(__name__, {
    "Kommuneplan": (
        "gml_npad_formatter.kommuneplan_20190401", "KommuneplanFormatter"),
})
