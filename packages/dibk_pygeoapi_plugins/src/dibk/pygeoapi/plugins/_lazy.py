from importlib import import_module
from typing import Any, Callable


def lazy_classes(
    module_name: str, classes: dict[str, tuple[str, str]]
) -> tuple[Callable[[str], Any], Callable[[], list[str]]]:
    """Build a module-level ``__getattr__`` and ``__dir__`` (PEP 562).

    *classes* maps each public name to the module and class implementing
    it. The implementing module is imported on first access, so a missing
    plugin package only fails for the names that need it.
    """

    def __getattr__(name: str) -> Any:
        try:
            module, class_name = classes[name]
        except KeyError:
            raise AttributeError(
                f"module {module_name!r} has no attribute {name!r}") from None

        return getattr(import_module(module), class_name)

    def __dir__() -> list[str]:
        return sorted(classes)

    return __getattr__, __dir__
