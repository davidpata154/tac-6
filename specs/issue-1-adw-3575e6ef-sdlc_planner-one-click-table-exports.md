# Feature: One Click Table Exports

## Metadata
issue_number: `1`
adw_id: `3575e6ef`
issue_json: `{"number":1,"title":"One click table exports","body":"Using adw_plan_build_review add one click table exports and one click result export feature to get results as csv files.\n\nCreate two new endpoints to support these features. One exporting tables, one for exporting query results.\n\nPlace a download button directly to the left of the 'x' icon for available tables.\nPlace a download button directly to the left of the 'hide' button for query results.\n\nUse the appropriate download icon."}`

## Feature Description
This feature adds CSV export functionality to the Natural Language SQL Interface application. Users will be able to:
1. Export entire database tables as CSV files with a single click
2. Export query results as CSV files with a single click

Download buttons will be strategically placed in the UI:
- For tables: directly to the left of the existing 'x' (remove) icon in the Available Tables section
- For query results: directly to the left of the existing 'Hide' button in the Query Results section

## User Story
As a data analyst
I want to export tables and query results as CSV files with one click
So that I can use the data in spreadsheet applications or share it with colleagues

## Problem Statement
Currently, users can view their data in the application but have no way to export it. If they need to work with the data externally (e.g., in Excel, Google Sheets, or another data tool), they must manually copy and paste the data, which is tedious and error-prone.

## Solution Statement
Implement two new backend API endpoints for CSV export and add download buttons to the frontend:
1. `GET /api/export/table/{table_name}` - Returns entire table contents as a CSV file download
2. `POST /api/export/results` - Returns the provided query results as a CSV file download

The frontend will add download buttons with appropriate download icons that trigger file downloads using these endpoints.

## Relevant Files
Use these files to implement the feature:

### Backend Files
- `app/server/server.py` - Main server file where new export endpoints will be added. Contains existing endpoint patterns to follow.
- `app/server/core/data_models.py` - Pydantic models for request/response. Will need new models for export functionality.
- `app/server/core/sql_processor.py` - Contains `execute_sql_safely()` and `get_database_schema()` functions that will be used to fetch table data.
- `app/server/core/sql_security.py` - Security module with `validate_identifier()` and `check_table_exists()` for safe table name handling.

### Frontend Files
- `app/client/src/main.ts` - Main application logic. Contains `displayTables()` function (line 254) where table download button will be added, and `displayResults()` function (line 184) where results download button will be added.
- `app/client/src/api/client.ts` - API client. New export methods will be added here.
- `app/client/src/types.d.ts` - TypeScript type definitions. May need new types for export functionality.
- `app/client/src/style.css` - Styles for download buttons.
- `app/client/index.html` - HTML structure. Results header section (line 33-35) will need modification.

### Test Files
- `app/server/tests/` - Server test directory for new export endpoint tests.

### Documentation
- Read `.claude/commands/test_e2e.md` and `.claude/commands/e2e/test_basic_query.md` to understand how to create an E2E test file.

### New Files
- `.claude/commands/e2e/test_table_exports.md` - E2E test file for validating the export functionality

## Implementation Plan
### Phase 1: Foundation
- Create Pydantic response model for export operations (simple success/error model not needed since we return StreamingResponse)
- Add export utility function to convert data rows to CSV format
- Set up proper content-disposition headers for file downloads

### Phase 2: Core Implementation
- Implement `GET /api/export/table/{table_name}` endpoint that:
  - Validates the table name using existing security functions
  - Fetches all table data using SQL
  - Converts to CSV format
  - Returns as StreamingResponse with appropriate headers for download
- Implement `POST /api/export/results` endpoint that:
  - Accepts results data (columns and rows) in request body
  - Converts to CSV format
  - Returns as StreamingResponse with appropriate headers for download

### Phase 3: Integration
- Add download buttons to the table items in `displayTables()` function
- Add download button to results header in `displayResults()` function
- Style download buttons to match existing UI patterns
- Implement client-side download triggering using blob URLs or direct fetch

## Step by Step Tasks

### Step 1: Create E2E Test File
- Create `.claude/commands/e2e/test_table_exports.md` that validates:
  - Download button appears next to table 'x' icon
  - Download button appears next to results 'Hide' button
  - Clicking table download triggers file download
  - Clicking results download triggers file download
  - Downloaded files contain correct CSV data

### Step 2: Add Backend Export Endpoint for Tables
- Add `GET /api/export/table/{table_name}` endpoint to `app/server/server.py`
- Validate table name using `validate_identifier()` from `sql_security.py`
- Check table exists using `check_table_exists()`
- Fetch all table data using safe SQL query execution
- Convert results to CSV format using Python's `csv` module with `StringIO`
- Return `StreamingResponse` with:
  - `media_type="text/csv"`
  - `Content-Disposition: attachment; filename="{table_name}.csv"`

### Step 3: Add Backend Export Endpoint for Query Results
- Add `POST /api/export/results` endpoint to `app/server/server.py`
- Create request model in `data_models.py` with `columns: List[str]` and `results: List[Dict[str, Any]]`
- Convert provided results to CSV format
- Return `StreamingResponse` with appropriate headers

### Step 4: Add Server Tests for Export Endpoints
- Create `app/server/tests/test_export.py` with tests for:
  - Table export with valid table name
  - Table export with invalid/nonexistent table name
  - Results export with valid data
  - Results export with empty data
  - CSV format validation

### Step 5: Add Download Buttons to Table Items
- Modify `displayTables()` function in `app/client/src/main.ts`
- Create download button element with download icon (use SVG or unicode download icon `\u2B07` or HTML entity)
- Place button directly to the left of the remove (`x`) button
- Add click handler that triggers CSV download via fetch to `/api/export/table/{table_name}`
- Handle the blob response and trigger browser download

### Step 6: Add Download Button to Results Header
- Modify `displayResults()` function in `app/client/src/main.ts`
- Modify HTML structure in `index.html` results-header to accommodate new button
- Create download button with download icon
- Place directly to the left of the 'Hide' button
- Add click handler that sends current results data to `/api/export/results`
- Trigger browser download with the returned CSV

### Step 7: Add CSS Styles for Download Buttons
- Add `.download-button` class to `app/client/src/style.css`
- Style to match existing `.remove-table-button` aesthetic
- Add hover state with primary color highlight
- Ensure proper alignment in flex containers

### Step 8: Run Validation Commands
- Run all validation commands to ensure the feature works correctly with zero regressions

## Testing Strategy
### Unit Tests
- Test table export endpoint returns valid CSV format
- Test table export with nonexistent table returns 404
- Test table export with invalid table name returns 400
- Test results export with valid data returns CSV
- Test results export handles empty results gracefully
- Test CSV includes proper headers (column names as first row)
- Test special characters in data are properly escaped in CSV

### Edge Cases
- Table with no rows (should return CSV with headers only)
- Table/column names with special characters
- Data containing commas, quotes, or newlines (CSV escaping)
- Very large tables (streaming should handle this)
- Unicode characters in data
- Null values in data

## Acceptance Criteria
- Download button appears directly to the left of 'x' icon for each table in Available Tables section
- Download button appears directly to the left of 'Hide' button in Query Results section
- Clicking table download button downloads `{table_name}.csv` file
- Clicking results download button downloads `query_results.csv` file
- Downloaded CSV files open correctly in spreadsheet applications
- CSV files contain proper headers (column names)
- CSV files contain all data from the table/results
- Special characters in data are properly escaped
- Empty tables/results download as CSV with headers only
- All existing functionality continues to work (no regressions)

## Validation Commands
Execute every command to validate the feature works correctly with zero regressions.

- `cd app/server && uv run pytest` - Run server tests to validate the feature works with zero regressions
- `cd app/client && bun tsc --noEmit` - Run frontend type checking to validate the feature works with zero regressions
- `cd app/client && bun run build` - Run frontend build to validate the feature works with zero regressions
- Read `.claude/commands/test_e2e.md`, then read and execute `.claude/commands/e2e/test_table_exports.md` to validate export functionality works end-to-end

## Notes
- Python's built-in `csv` module with `StringIO` is the recommended approach for CSV generation - no external libraries needed
- FastAPI's `StreamingResponse` is ideal for file downloads as it handles large files efficiently
- Using unicode download arrow `\u2193` (↓) or SVG icon for the download button
- The frontend will use `fetch()` with blob handling for download, creating an object URL and triggering download via a temporary anchor element
- Consider adding a brief loading state for the download buttons during the fetch operation
- Future enhancement could include format options (CSV, JSON, Excel) but CSV is sufficient for this initial implementation
