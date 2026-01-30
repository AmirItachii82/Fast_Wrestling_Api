# Postman Instructions

This guide explains how to import and use the Wrestling Dashboard API Postman collection.

## Prerequisites

- [Postman](https://www.postman.com/downloads/) installed
- Wrestling Dashboard API running locally or on a server

## Importing the Collection

1. Open Postman
2. Click **Import** button (top-left)
3. Select the `postman/Wrestling_Dashboard_API.postman_collection.json` file
4. Click **Import**

## Setting Up Environment Variables

### Create Environment

1. Click the **Environments** tab (left sidebar)
2. Click **+** to create new environment
3. Name it "Wrestling Dashboard - Local"
4. Add the following variables:

| Variable | Initial Value | Current Value |
|----------|--------------|---------------|
| `base_url` | `http://localhost:8000/api/v1` | `http://localhost:8000/api/v1` |
| `accessToken` | (leave empty) | (leave empty) |
| `refreshToken` | (leave empty) | (leave empty) |

5. Click **Save**

### For Production

Create another environment "Wrestling Dashboard - Production" with your production URL.

## Using the Collection

### 1. Authentication

**Login:**
1. Expand the **Auth** folder
2. Select **Login**
3. Check the Body tab has valid credentials:
   ```json
   {
     "email": "admin@wrestling.com",
     "password": "admin123"
   }
   ```
4. Click **Send**
5. The response will contain tokens:
   ```json
   {
     "accessToken": "eyJ...",
     "refreshToken": "eyJ...",
     "user": { ... }
   }
   ```
6. **Important:** The collection has a post-request script that automatically saves the tokens to environment variables

**Token Auto-Save Script:**
```javascript
if (pm.response.code === 200) {
    const response = pm.response.json();
    pm.environment.set("accessToken", response.accessToken);
    pm.environment.set("refreshToken", response.refreshToken);
}
```

### 2. Using Protected Endpoints

After login, all requests will automatically include the access token:

1. Select any request (e.g., **Wrestlers > List Wrestlers**)
2. Check the **Authorization** tab
3. It should show "Bearer Token" with `{{accessToken}}`
4. Click **Send**

### 3. Refresh Token

When access token expires:

1. Go to **Auth > Refresh Token**
2. Click **Send**
3. New access token is automatically saved

### 4. AI Endpoints

**Chart Insight:**
1. Go to **AI > Chart Insight**
2. Modify the body if needed:
   ```json
   {
     "wrestlerId": "your-wrestler-id",
     "chartId": "overview-radar",
     "chartData": {
       "labels": ["A", "B", "C"],
       "values": [80, 85, 90]
     },
     "locale": "fa-IR"
   }
   ```
3. Click **Send**

**AI Training Program:**
1. Go to **AI > Generate Training Program**
2. Modify the body:
   ```json
   {
     "wrestlerId": "your-wrestler-id",
     "goal": "strength",
     "date": "2025-02-01"
   }
   ```
3. Click **Send**

## Collection Structure

```
Wrestling Dashboard API
├── Auth
│   ├── Login
│   ├── Refresh Token
│   └── Logout
├── Wrestlers
│   ├── List Wrestlers
│   ├── Get Wrestler
│   └── Get Overview
├── Body Composition
│   ├── Get Metrics
│   ├── Get Trends
│   └── Get InBody
├── Bloodwork
│   ├── Get Metrics
│   └── Get Charts
├── Recovery
│   ├── Get Metrics
│   └── Get Charts
├── Supplements
│   ├── Get Metrics
│   └── Get Charts
├── Performance
│   ├── Get Metrics
│   └── Get Charts
├── Training
│   ├── Get Program
│   └── Submit Program
├── Calendar
│   └── Get Calendar
├── Teams
│   ├── Get Stats
│   └── Get Athletes
├── AI
│   ├── Chart Insight
│   ├── Advanced Insight
│   └── Generate Training Program
├── Scores
│   ├── Overall Score
│   ├── Domain Scores
│   └── Score Explanation
└── Legacy Data
    ├── List Athletes
    ├── List Sessions
    ├── List Metrics
    ├── Body Composition (Freestyle)
    ├── Body Composition (Greco-Roman)
    ├── Chestbelt Heart Rate
    ├── Fitness
    └── Urion Analysis
```

## Legacy Data Endpoints

The Legacy Data folder contains endpoints for accessing data from the original Fittechno database.

### Key Features

- **Session Date Resolution**: All responses include session dates automatically
- **Filtering**: Filter by athlete name, metric name, session ID, and date range
- **Pagination**: All endpoints support pagination with `page` and `perPage` parameters

### Example: List Body Composition (Freestyle)

1. Go to **Legacy Data > Body Composition (Freestyle)**
2. Check/modify query parameters:
   - `athleteName`: Filter by athlete (partial match)
   - `metricName`: Filter by metric (partial match)
   - `sessionId`: Filter by exact session
   - `dateFrom`: Start date (YYYY-MM-DD)
   - `dateTo`: End date (YYYY-MM-DD)
3. Click **Send**

**Example Response:**
```json
{
  "data": [
    {
      "id": 1,
      "sessionId": "1001",
      "athleteName": "حسن یزدانی",
      "metricName": "Weight",
      "nvalue": 86.5,
      "tvalue": null,
      "sessionDate": "2025-01-15",
      "sessionDateShamsi": "1403-10-26"
    }
  ],
  "pagination": {
    "page": 1,
    "perPage": 50,
    "total": 100,
    "totalPages": 2
  },
  "style": "freestyle"
}
```

## Tips

### View Response Time
- Check the response time in the upper-right of the response panel
- Use this to monitor API performance

### Save Examples
- After a successful request, click **Save Response > Save as Example**
- This saves response examples for documentation

### Run Collection
1. Click the collection name
2. Click **Run**
3. Select environment
4. Click **Run Wrestling Dashboard API**
5. View test results

### Export Updated Collection
After making changes:
1. Right-click the collection
2. Select **Export**
3. Choose format (v2.1 recommended)
4. Save the file

## Troubleshooting

### "Unauthorized" Error
- Token may have expired
- Run the **Login** request again
- Check that environment is selected

### "Connection Refused"
- Ensure the API is running
- Check the `base_url` variable
- Verify port number (default: 8000)

### "Invalid Request Body"
- Check JSON syntax
- Verify required fields are present
- Check field types match schema

### Environment Not Working
- Ensure correct environment is selected (top-right dropdown)
- Check variable names match exactly
- Verify variables have "Current Value" set
