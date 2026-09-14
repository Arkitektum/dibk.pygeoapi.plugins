from enum import Enum


class UriType(Enum):
    """How a configured stylesheet URI should be resolved."""

    HTTP_URL = 1  # http:// or https://, fetched with an HTTP request
    FILE_URL = 2  # file://, converted to a file system path before reading
    PATH = 3      # plain file system path, absolute or relative to base_uri
