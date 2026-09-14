from urllib.parse import urljoin, urlparse
from urllib.request import url2pathname
from pathlib import Path
import logging
from typing import Any, Dict, List
import requests
from .uri_type import UriType

_logger = logging.getLogger(__name__)

# Supported stylesheet encodings, keyed by the 'type' used in the provider
# configuration. Each entry holds the metadata that OGC API - Styles expects to
# be advertised for a stylesheet, plus the 'format' value used as the ?f=
# query parameter when linking to the style definition.
_stylesheet_types = {
    'mapbox': {
        'title': 'Mapbox Style',
        'mime_type': 'application/vnd.mapbox.style+json',
        'version': '8',
        'spec': 'https://docs.mapbox.com/style-spec/guides',
        'format': 'mapbox'
    },
    'se11': {
        'title': 'OGC SE',
        'mime_type': 'application/vnd.ogc.se+xml;version=1.1',
        'version': '1.1',
        'spec': 'https://www.ogc.org/standards/se',
        'format': 'se11'
    },
    'sld10': {
        'title': 'OGC SLD',
        'mime_type': 'application/vnd.ogc.sld+xml;version=1.0',
        'version': '1.0',
        'spec': 'https://www.ogc.org/standards/sld',
        'format': 'sld10'
    }
}

   
class StyleProvider:
    """Provider serving OGC API - Styles resources from a static configuration.

    The styles themselves are declared in the pygeoapi configuration; the
    stylesheet definitions live outside of it and are fetched on demand from
    either the local file system or an HTTP(S) endpoint.
    """

    def __init__(self, provider_def: Dict):
        """
        :param provider_def: provider definition from the pygeoapi
                             configuration. Expects a `styles` list, a
                             `server_url` (injected by pygeoapi) and an
                             optional `base_uri` that stylesheet URIs are
                             resolved against.
        """
        self.styles: List[Dict[str, Any]] = provider_def['styles']
        self.server_url: str = provider_def['server_url']
        self.base_uri: str | None = provider_def.get('base_uri')

    def get_styles(self) -> Dict[str, Any]:
        """Return all configured styles with links to their metadata and to
        each of their stylesheet encodings.

        :returns: dict matching the OGC API - Styles `styles` response
        """
        styles: List[Dict[str, Any]] = []

        for style in self.styles:
            id: str = style['id']

            links = [
                {
                    'rel': 'describedby',
                    'title': 'Style metadata',
                    'href': f'{self.server_url}/styles/{id}/metadata'
                }
            ]

            stylesheets: List[Dict] = style['stylesheets']

            # one stylesheet link per configured encoding, e.g. ?f=se11
            for styleheet in stylesheets:
                type = styleheet['type']

                links.append({
                    'rel': 'stylesheet',
                    'type': _stylesheet_types[type]['mime_type'],
                    'title': f'Style in {_stylesheet_types[type]["title"]} format',
                    'href': f'{self.server_url}/styles/{id}?f={_stylesheet_types[type]["format"]}'
                })

            styles.append({
                'id': id,
                'title': style.get('title'),
                'links': links
            })

        return {
            'styles': styles
        }

    def get_style(self, style_id: str) -> Dict[str, Any] | None:
        """Return a single style entry, as it appears in `get_styles()`.

        :param style_id: identifier of the style
        :returns: the style dict, or None if no such style is configured
        """
        styles: List[Dict] = self.get_styles().get('styles', [])
        style = next(
            (style for style in styles if style['id'] == style_id), None)

        return style

    def get_style_metadata(self, style_id: str) -> Dict[str, Any] | None:
        """Return the style metadata document for a style.

        Optional configuration keys (description, keywords, version) are only
        included when present, so that the response stays free of null values.

        :param style_id: identifier of the style
        :returns: dict matching the OGC API - Styles style metadata response,
                  or None if no such style is configured
        """
        style = next(
            (style for style in self.styles if style['id'] == style_id), None)

        if not style:
            return None

        metadata = {
            'id': style['id'],
            'title': style['title']
        }

        description = style.get('description')

        if description:
            metadata['description'] = description

        keywords = style.get('keywords')

        if keywords:
            metadata['keywords'] = keywords

        metadata['scope'] = 'style'

        version = style.get('version')

        if version:
            metadata['version'] = version

        stylesheets: List[Dict[str, Any]] = style['stylesheets']
        metadata['stylesheets'] = []

        for styleheet in stylesheets:
            type = _stylesheet_types[styleheet['type']]

            metadata['stylesheets'].append({
                'title': type['title'],
                'version': type['version'],
                'specification': type['spec'],
                'native': styleheet['native'],
                'link': {
                    'href': f'{self.server_url}/styles/{style_id}?f={type["format"]}',
                    'rel': 'stylesheet',
                    'type': type['mime_type']
                }
            })

        layers: List[Dict[str, Any]] = style['layers']
        metadata['layers'] = []

        for layer in layers:
            metadata['layers'].append({
                'id': layer['id'],
                'type': layer['type']
            })

        return metadata

    def get_style_definition(self, style_id: str, format_: str) -> str | None:
        """Fetch the raw stylesheet document for a style in a given encoding.

        :param style_id: identifier of the style
        :param format_: stylesheet type, i.e. one of the keys of
                        `_stylesheet_types` ('mapbox', 'se11', 'sld10')
        :returns: the stylesheet as text, or None if the style, the requested
                  encoding or the underlying document could not be found
        """
        style = next(
            (style for style in self.styles if style['id'] == style_id), None)

        if not style:
            return None

        stylesheets: List[Dict[str, Any]] = style.get('stylesheets', [])
        stylesheet = next(
            (stylesheet for stylesheet in stylesheets if stylesheet['type'] == format_), None)

        if not stylesheet:
            return None

        uri: str = stylesheet['uri']

        # `base_uri` decides how the stylesheet is retrieved when configured;
        # the stylesheet URI is then expected to be relative to it. Without a
        # base URI the stylesheet URI has to be absolute and decides on its own.
        uri_type = self._get_uri_type(
            self.base_uri) if self.base_uri else self._get_uri_type(uri)

        if uri_type == UriType.HTTP_URL:
            return self._get_style_from_http(self.base_uri, uri)

        base_uri = self.base_uri

        # file:// URLs have to be turned into native file system paths before
        # they can be opened; whichever of the two is absolute is the one to
        # convert.
        if uri_type == UriType.FILE_URL:
            if self.base_uri:
                parsed_url = urlparse(self.base_uri)
                base_uri = url2pathname(parsed_url.path)
            else:
                parsed_url = urlparse(uri)
                uri = url2pathname(parsed_url.path)

        return self._get_style_from_path(base_uri, uri)

    def get_style_preview(self, style_id: str):
        """Not implemented: rendering a preview image of a style."""
        raise NotImplementedError()

    def _get_style_from_path(self, base_uri: str | None, uri: str) -> str | None:
        """Read a stylesheet from the local file system."""
        path = Path(base_uri).joinpath(uri) if base_uri else Path(uri)

        if not path.exists():
            return None

        with open(path, 'r') as file:
            return file.read()

    def _get_style_from_http(self, base_uri: str | None, uri: str) -> str | None:
        """Fetch a stylesheet over HTTP(S).

        A missing or unreachable stylesheet is logged and treated as absent
        rather than raised, so that a single broken style does not take down
        the styles endpoint.
        """
        # the trailing slash keeps urljoin from dropping the last path segment
        # of the base URI
        url = urljoin(base_uri.rstrip('/') + '/', uri) if base_uri else uri

        try:
            response = requests.get(url)
            response.raise_for_status()

            return response.text
        except Exception as err:
            _logger.warning(f'Could not fetch style definition: {url}: {err}')
            return None

    def _get_uri_type(self, uri: str) -> UriType:
        """Classify a URI as an HTTP(S) URL, a file URL or a plain path."""
        parsed = urlparse(uri)

        if parsed.scheme in ('http', 'https'):
            return UriType.HTTP_URL

        if parsed.scheme == 'file':
            return UriType.FILE_URL

        return UriType.PATH
