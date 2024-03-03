# SoleSearch: Ingest

[Read the Docs](https://api.solesearch.io/docs)

[OpenAPI Schema](https://api.solesearch.io/openapi.json)

# Endpoints

## `/sneakers/{product_id}`

Returns a single sneaker found by the specified product_id. Product IDs are guaranteed to be unique in the SoleSearch database.

## `/sneakers/sku/{sku}`

Returns a single sneaker found by the specified SKU.

SKU format differs by manufacturer, however, some brands may have overlapping SKUs. To ensure you find the correct product, either use the `/sneakers/product_id` endpoint, or specify the `brand` in the query params. Example:

`/sneakers/sku/ABCDEF-123?brand=Nike`

## `/sneakers`

### Filtering

By default, all products in the database are returned when calling `/sneakers`. You can filter with the following query parameters:

- brand
- name
- audience
- colorway
- releaseDate
- released

Filtering is case insensitive, but the search will start from the beginning of each field. For example, a search `/sneakers?brand=jordan` will return all sneakers with a brand starting with `Jordan`, `jordan`, `JOrdan`, etc... but a search `/sneakers?brand=ordan` will not find any `Jordan`s.

### Sorting

By default, all queries are sorted in reverse chronological order by release date. You can sort on other fields using the `sort` query paramter.

#### Sortable Fields:

- `brand`
- `sku`
- `name`
- `colorway`
- `releaseDate`
- `price`

#### Example:

```
GET /sneakers?sort=price
```

Returns results starting from the highest retail price.

#### sortOrder

The `sortOrder` query parameter is used in conjunction with the `sort` parameter to determine the direction of the sorting. It allows you to specify whether you want the results to be sorted in ascending or descending order. If not specified, results are sorted in descending order.

#### Possible Values:

- `asc` (Ascending): This will sort the results in ascending order.
- `desc` (Descending): This will sort the results in descending order.

#### Example:

```
GET /sneakers?sort=name&sortOrder=asc
```

Returns results sorted in alphabetical order based on the "name" field.
