#### List All Athletes
```bash
GET /api/athletes/athletes/
Authorization: Token abc123xyz...

Response:
{
  "count": 78,
  "next": "http://localhost:8000/api/athletes/profiles/?page=2",
  "previous": null,
  "results": [
    {
      "athlete_id": 101,
      "full_name": "Jordan Wrestler",
      "gender": "M",
      "age": 24,
      "created_at": "2024-10-01T09:00:00Z",
      "updated_at": "2024-10-01T09:00:00Z"
    },
    ...
  ]
}
```

#### Get Single Athlete
```bash
GET /api/athletes/profiles/101/
Authorization: Token abc123xyz...

Response:
{
  "athlete_id": 101,
  "full_name": "Jordan Wrestler",
  "gender": "M",
  "age": 24,
  "created_at": "2024-10-01T09:00:00Z",
  "updated_at": "2024-10-01T09:00:00Z"
}
```

#### Search Athletes
```bash
GET /api/athletes/profiles/?search=Jordan
Authorization: Token abc123xyz...
```

#### Filter Athletes by Gender
```bash
GET /api/athletes/profiles/?gender=M
Authorization: Token abc123xyz...
```

#### Get Specific Athlete's Data
```bash
GET /api/athletes/profiles/?athlete_id=101
Authorization: Token abc123xyz...
```

### Session Data

#### List Sessions for Athlete
```bash
GET /api/athletes/sessions/?athlete_id=101
Authorization: Token abc123xyz...

Response:
{
  "count": 5,
  "next": null,
  "previous": null,
  "results": [
    {
      "session_id": 7001.0,
      "athlete_id": 101,
      "athlete_name": "Jordan Wrestler",
      "miladi_date": "2024-10-01",
      "shamsi_date": "1403-07-10",
      "start_time": "09:00:00",
      "test_category": "Body Composition",
      "created_at": "2024-10-01T09:00:00Z",
      "updated_at": "2024-10-01T09:00:00Z"
    },
    ...
  ]
}
```

### Metrics

#### List All Metrics
```bash
GET /api/athletes/metrics/
Authorization: Token abc123xyz...

Response:
{
  "count": 664,
  "next": "http://localhost:8000/api/athletes/metrics/?page=2",
  "previous": null,
  "results": [
    {
      "metric_id": 5001,
      "name": "Body Fat %",
      "method": "DXA",
      "category": "Body_Composition",
      "field": "composition"
    },
    ...
  ]
}
```

#### Filter Metrics by Category
```bash
GET /api/athletes/metrics/?category=Body_Composition
Authorization: Token abc123xyz...
```

### Devices

#### List All Devices
```bash
GET /api/athletes/devices/
Authorization: Token abc123xyz...

Response:
{
  "count": 5,
  "next": null,
  "previous": null,
  "results": [
    {
      "code": "body_comp_fs",
      "name": "Body composition (FS device)",
      "description": "Data imported from body_composition_fs"
    },
    ...
  ]
}
```

### Measurements (Fact Table)

#### Get All Measurements for Athlete
```bash
GET /api/athletes/measurements/?athlete_id=101
Authorization: Token abc123xyz...

Response:
{
  "count": 150,
  "next": "http://localhost:8000/api/athletes/measurements/?athlete_id=101&page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "athlete_id": 101,
      "athlete_name": "Jordan Wrestler",
      "session_id": 7001.0,
      "metric_id": 5001,
      "metric_name": "Body Fat %",
      "metric_category": "Body_Composition",
      "device_code": "body_comp_fs",
      "numeric_value": 12.5,
      "text_value": "12.5",
      "source_table": "body_composition_fs",
      "source_row_id": 1,
      "recorded_at": "2024-10-01T09:00:00Z",
      "created_at": "2024-10-01T09:00:00Z",
      "updated_at": "2024-10-01T09:00:00Z"
    },
    ...
  ]
}
```

#### Filter Measurements by Source Table
```bash
GET /api/athletes/measurements/?athlete_id=101&source_table=body_composition_fs
Authorization: Token abc123xyz...
```

#### Filter Measurements by Metric
```bash
GET /api/athletes/measurements/?athlete_id=101&metric_id=5001
Authorization: Token abc123xyz...
```

#### Filter Measurements by Category
```bash
GET /api/athletes/measurements/?athlete_id=101&category=Body_Composition
Authorization: Token abc123xyz...
```

### Specialized Measurement Feeds

#### Body Composition Data
```bash
GET /api/athletes/body-composition/?athlete_id=101
Authorization: Token abc123xyz...
```
Returns only measurements with category containing "body"

#### Fitness Test Data
```bash
GET /api/athletes/fitness/?athlete_id=101
Authorization: Token abc123xyz...
```
Returns only measurements with category containing "fitness"

#### Heart-Rate (Chest Belt) Data
```bash
GET /api/athletes/chestbelt/?athlete_id=101
Authorization: Token abc123xyz...
```
Returns only measurements from chest belt device

#### Urion Analysis Data
```bash
GET /api/athletes/urion/?athlete_id=101
Authorization: Token abc123xyz...
```
Returns only measurements from urion_analysis_gr table