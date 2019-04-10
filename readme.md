# Bananas - Jeff Davidson 310-395-9300 jeff@very-advanced.com

## Usage

All responses will have the form

```json
{
    "message": "Description of what happened",
    "data": "Mixed type holding the content of the response"
}
```

Definitions detail only the expected value of the `data field`:

### update_values

**Definition**

POST /update_values

**Arguments**

- `"sell_price":string` price at which bananas are sold - default 0.35
- `"buy_price":string` cost of bananas for purchase - default - 0.20
- `"days_fresh":string` number of days bananas stay fresh - default 10

This will update the values for buy and sell prices.  If field is NULL, current value will not be updated

### Purchase

**Definition**

POST /purchase`

**Arguments**

- `"total":string` total number of bananas sold
- `"date":string` date bananas were sold with format YYYY-MM-DD

Multiple daily transactions are allowed!  If the date already exists, a second order for the same date will be created

**Response**

- `201 OK` on success

```json
    {
        "total": "100",
        "date": "YYYY-MM-DD",
    },
```

### Sell

**Definition**

`POST /sell

**Arguments**

- `"total":string` total number of bananas sold
- `"date":string` date bananas were sold with format YYYY-MM-DD

Multiple daily transactions are allowed!  If the date already exists, a second order for the same date will be created

**Response**

- `201 Created` on success

```json
    {
        "total": "100",
        "date": "YYYY-MM-DD",
    },
```

## Metrics
`GET /metrics

**Arguments**

- `"start_date":string` date bananas were sold with format YYYY-MM-DD
- `"end_date":string` date bananas were sold with format YYYY-MM-DD

**Response**

- `404 Not Found` date range not found
- `201 OK` on success

```json
{
    "inventory": "50",
    "expired": "10",
    "total_sold": "100",
    "profit": "1200"
}
```

