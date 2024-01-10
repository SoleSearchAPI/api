# SoleSearch: Ingest

# Endpoints

# Filtering

# Sorting

By default, all queries are sorted in reverse chronological order by release date. You can sort on other fields using the `sort` query paramter.

## Query Parameters

### sort

The `sort` query parameter allows you to specify the field by which you want to sort the results of your query.

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

### sortOrder

The `sortOrder` query parameter is used in conjunction with the `sort` parameter to determine the direction of the sorting. It allows you to specify whether you want the results to be sorted in ascending or descending order. If not specified, results are sorted in descending order.

#### Possible Values:

- `asc` (Ascending): This will sort the results in ascending order.
- `desc` (Descending): This will sort the results in descending order.

#### Example:

```
GET /sneakers?sort=name&sortOrder=asc
```

Returns results sorted in alphabetical order based on the "name" field.
