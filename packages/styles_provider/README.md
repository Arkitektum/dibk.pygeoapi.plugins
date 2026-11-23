# styles_provider

A styles provider for [pygeoapi](https://pygeoapi.io/), serving
[OGC API - Styles](https://ogcapi.ogc.org/styles/) resources.

The styles are declared in the pygeoapi configuration, while the stylesheet
documents themselves live outside of it &ndash; either on the local file system
or behind an HTTP(S) endpoint &ndash; and are fetched on demand.

## Supported stylesheet encodings

| `type`   | Format                          | Media type                                    |
| -------- | ------------------------------- | --------------------------------------------- |
| `mapbox` | Mapbox Style Specification 8    | `application/vnd.mapbox.style+json`           |
| `se11`   | OGC Symbology Encoding 1.1      | `application/vnd.ogc.se+xml;version=1.1`      |
| `sld10`  | OGC Styled Layer Descriptor 1.0 | `application/vnd.ogc.sld+xml;version=1.0`     |

The `type` doubles as the `f` query parameter used to request a style
definition, e.g. `/styles/rpomrade?f=se11`.

## Installation

Into an existing pygeoapi environment, pinned to a release tag:

```bash
uv pip install "styles_provider @ git+https://github.com/Arkitektum/dibk.pygeoapi.plugins@styles_provider-v<version>#subdirectory=packages/styles_provider"
```

For local development, see the [repository README](../../README.md#development).

Requires Python 3.12 or later.

## Configuration

Add the provider to `pygeoapi-config.yml`:

```yaml
- type: style
  name: styles_provider.StyleProvider
  styles:
    - id: rpomrade
      title: RpOmråde
      description: RpOmråde
      stylesheets:
        - type: se11
          uri: /path/to/styles/sld/rpomrade.sld
          native: true
        - type: mapbox
          uri: /path/to/styles/mapbox/rpomrade.json
          native: false
      layers:
        - id: rpomrade
          type: polygon
```

### Provider options

| Key        | Required | Description                                                                                |
| ---------- | -------- | ------------------------------------------------------------------------------------------ |
| `styles`   | yes      | List of style definitions, see below.                                                       |
| `base_uri` | no       | Base URI that every stylesheet `uri` is resolved against. See [Resolving stylesheet URIs](#resolving-stylesheet-uris). |

`server_url` is supplied by pygeoapi itself and is used to build the links in
the responses; it is not set in the provider block.

### Style options

| Key           | Required | Description                                                              |
| ------------- | -------- | ------------------------------------------------------------------------ |
| `id`          | yes      | Identifier of the style, used in the URL path.                            |
| `title`       | yes      | Human readable title.                                                     |
| `stylesheets` | yes      | List of stylesheet encodings available for the style.                     |
| `layers`      | yes      | List of layers the style applies to, each with an `id` and a `type`.      |
| `description` | no       | Longer description, included in the style metadata when present.          |
| `keywords`    | no       | List of keywords, included in the style metadata when present.            |
| `version`     | no       | Version of the style, included in the style metadata when present.        |

### Stylesheet options

| Key      | Required | Description                                                                                   |
| -------- | -------- | --------------------------------------------------------------------------------------------- |
| `type`   | yes      | One of `mapbox`, `se11` or `sld10`.                                                            |
| `uri`    | yes      | Location of the stylesheet document, absolute or relative to `base_uri`.                       |
| `native` | yes      | Whether this encoding is the authoritative one the other encodings were derived from.          |

## Resolving stylesheet URIs

Each stylesheet `uri` may be a file system path, a `file://` URL or an
`http://`/`https://` URL. When `base_uri` is set it determines how the
stylesheets are retrieved, and the individual `uri` values are treated as
relative to it. Without `base_uri`, each `uri` has to stand on its own.

Absolute paths, one style on disk and one on a web server:

```yaml
- type: style
  name: styles_provider.StyleProvider
  styles:
    - id: rpomrade
      title: RpOmråde
      stylesheets:
        - type: se11
          uri: /var/lib/pygeoapi/styles/sld/rpomrade.sld
          native: true
      layers:
        - id: rpomrade
          type: polygon
    - id: rpgrense
      title: RpGrense
      stylesheets:
        - type: mapbox
          uri: https://example.com/styles/mapbox/rpgrense.json
          native: true
      layers:
        - id: rpgrense
          type: line
```

A shared directory on disk:

```yaml
- type: style
  name: styles_provider.StyleProvider
  base_uri: /var/lib/pygeoapi/styles
  styles:
    - id: rpomrade
      title: RpOmråde
      stylesheets:
        - type: se11
          uri: sld/rpomrade.sld
          native: true
        - type: mapbox
          uri: mapbox/rpomrade.json
          native: false
      layers:
        - id: rpomrade
          type: polygon
```

A shared base URL:

```yaml
- type: style
  name: styles_provider.StyleProvider
  base_uri: https://example.com/styles/
  styles:
    - id: rpomrade
      title: RpOmråde
      stylesheets:
        - type: se11
          uri: sld/rpomrade.sld
          native: true
      layers:
        - id: rpomrade
          type: polygon
```

## Endpoints

| Endpoint                      | Provider method          | Response                                                       |
| ----------------------------- | ------------------------ | -------------------------------------------------------------- |
| `/styles`                     | `get_styles`             | All configured styles, with links to metadata and stylesheets. |
| `/styles/{styleId}`           | `get_style_definition`   | The stylesheet document, in the encoding given by `?f=`.       |
| `/styles/{styleId}/metadata`  | `get_style_metadata`     | Style metadata, including stylesheets and layers.              |

A style, an encoding or a stylesheet document that cannot be found yields
`None` from the provider; a stylesheet that cannot be fetched over HTTP is
logged as a warning and treated the same way, so that one broken style does
not break the styles endpoint.

`get_style_preview` is not implemented.

## License

See [LICENSE](LICENSE).
