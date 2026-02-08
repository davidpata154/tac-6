# Feature: One Click Table Exports

## Metadata
issue_number: `1`
adw_id: `54e3696f`
issue_json: `{"number":1,"title":"One click table exports","body":"Using adw_plan_build_review add one click table exports and one click result export feature to get results as csv files.\n\nCreate two new endpoints to support these features. One exporting tables, one for exporting query results.\n\nPlace a download button directly to the left of the 'x' icon for available tables.\nPlace a download button directly to the left of the 'hide' button for query results.\n\nUse the appropriate download icon."}`

## Feature Description
This feature adds the ability to export data as CSV files directly from the UI with a single click. Users can export:
1. **Table exports** - Export any table from the Available Tables section to a CSV file
2. **Query result exports** - Export the results of any query execution to a CSV file

This provides a seamless way to extract data from the Natural Language SQL Interface without having to manually copy data or use external tools.

## User Story
As a data analyst
I want to export tables and query results to CSV with one click
So that I can easily share data or use it in other applications like Excel or Google Sheets

## Problem Statement
Currently, users can query their data and view results in the UI, but there is no way to export this data. Users who want to share their data or use it in other applications must manually copy the data from the interface, which is tedious and error-prone for large datasets.

## Solution Statement
Add two new API endpoints and corresponding UI buttons to enable one-click CSV exports:
1. A `GET /api/table/{table_name}/export` endpoint that exports all rows from a table as CSV
2. A `POST /api/export-results` endpoint that accepts query results and returns them as a CSV file
3. Download buttons in the UI placed according to the specification:
   - Table export button: directly to the left of the '×' (remove) icon for each table
   - Query results export button: directly to the left of the 'Hide' button in the results header

## Relevant Files
Use these files to implement the feature:

### Server Files
- `app/server/server.py` - Main FastAPI server where new export endpoints will be added. Contains existing endpoint patterns to follow.
- `app/server/core/data_models.py` - Pydantic models for request/response types. New export-related models will be added here.
- `app/server/core/sql_processor.py` - Contains `execute_sql_safely()` and `get_database_schema()` which will be used to fetch table data for export.
- `app/server/core/sql_security.py` - Security utilities for validating identifiers and executing safe queries. Must use `validate_identifier()` and `execute_query_safely()` for table name validation.
- `app/server/tests/test_sql_injection.py` - Existing test patterns to follow for unit tests.

### Client Files
- `app/client/src/main.ts` - Main TypeScript file containing UI logic. The `displayTables()` function creates table items where download buttons will be added. The `displayResults()` function creates the results section where the query results download button will be added.
- `app/client/src/api/client.ts` - API client module. New export methods will be added here.
- `app/client/src/types.d.ts` - TypeScript type definitions. May need new types for export functionality.
- `app/client/src/style.css` - CSS styles. May need styles for the download button.
- `app/client/index.html` - HTML template. The results section header already exists here with the Hide button.

### E2E Test References
- `.claude/commands/test_e2e.md` - Instructions for running E2E tests
- `.claude/commands/e2e/test_basic_query.md` - Example E2E test format to follow

### New Files
- `app/server/tests/test_export.py` - Unit tests for the new export endpoints
- `.claude/commands/e2e/test_one_click_exports.md` - E2E test for validating export functionality

## Implementation Plan

### Phase 1: Foundation
1. Add Pydantic models for export requests/responses in `data_models.py`
2. Create unit tests for export endpoints (test-driven approach)
3. Add TypeScript types for export functionality

### Phase 2: Core Implementation
1. Implement `GET /api/table/{table_name}/export` endpoint
   - Validate table name using security module
   - Fetch all table data using safe query execution
   - Convert data to CSV format
   - Return as downloadable file with proper headers
2. Implement `POST /api/export-results` endpoint
   - Accept columns and results data from request body
   - Convert to CSV format
   - Return as downloadable file with proper headers
3. Add API client methods for export functionality
4. Add download button UI for tables
5. Add download button UI for query results

### Phase 3: Integration
1. Wire up download buttons to API calls
2. Handle file downloads in the browser (using blob URLs)
3. Add loading states for export buttons
4. Test end-to-end flow
5. Create E2E test file

## Step by Step Tasks
IMPORTANT: Execute every step in order, top to bottom.

### Step 1: Create E2E Test File
- Create `.claude/commands/e2e/test_one_click_exports.md` with test steps for validating the export functionality
- Define test steps for:
  - Uploading sample data
  - Clicking download button on a table
  - Verifying CSV download works for tables
  - Running a query
  - Clicking download button on query results
  - Verifying CSV download works for query results
- Include screenshots for each major step

### Step 2: Add Data Models
- Add `ExportResultsRequest` model to `app/server/core/data_models.py`:
  - `columns: List[str]` - Column names
  - `results: List[Dict[str, Any]]` - Row data
  - `filename: Optional[str]` - Optional custom filename

### Step 3: Create Unit Tests for Export Endpoints
- Create `app/server/tests/test_export.py` with tests for:
  - Valid table export returns CSV with correct content
  - Invalid table name returns 400 error
  - Non-existent table returns 404 error
  - Query results export returns valid CSV
  - Empty results return valid empty CSV with headers
  - SQL injection attempts are blocked for table names

### Step 4: Implement Table Export Endpoint
- Add `GET /api/table/{table_name}/export` endpoint to `server.py`:
  - Validate table name using `validate_identifier()` from `sql_security`
  - Check table exists using `check_table_exists()`
  - Execute `SELECT * FROM {table}` using `execute_query_safely()`
  - Convert results to CSV using Python's `csv` module
  - Return as `StreamingResponse` with:
    - Content-Type: `text/csv`
    - Content-Disposition: `attachment; filename="{table_name}.csv"`
- Handle errors appropriately with proper HTTP status codes

### Step 5: Implement Query Results Export Endpoint
- Add `POST /api/export-results` endpoint to `server.py`:
  - Accept `ExportResultsRequest` body
  - Convert columns and results to CSV format
  - Return as `StreamingResponse` with:
    - Content-Type: `text/csv`
    - Content-Disposition: `attachment; filename="query_results.csv"` (or custom filename if provided)
- Handle empty results gracefully (return CSV with headers only)

### Step 6: Add TypeScript Types
- Add to `app/client/src/types.d.ts`:
  - `ExportResultsRequest` interface matching the Pydantic model

### Step 7: Add API Client Methods
- Add to `app/client/src/api/client.ts`:
  - `exportTable(tableName: string): Promise<void>` - Downloads table as CSV
  - `exportResults(request: ExportResultsRequest): Promise<void>` - Downloads query results as CSV
- Use `fetch` with blob handling to trigger file downloads
- Include proper error handling

### Step 8: Add Download Button Styles
- Add to `app/client/src/style.css`:
  - `.download-table-button` class styled similarly to `.remove-table-button`
  - Use a download icon or appropriate styling
  - Hover state with blue tint (similar to primary color)
  - Position it to work inline with the remove button

### Step 9: Add Table Download Button to UI
- Modify `displayTables()` function in `app/client/src/main.ts`:
  - Create download button element before the remove button
  - Use a download icon (SVG or Unicode character like ⬇ or use an actual download icon)
  - Add click handler that calls `api.exportTable(table.name)`
  - Add to `tableHeader` before `removeButton`

### Step 10: Add Query Results Download Button to UI
- Modify `displayResults()` function in `app/client/src/main.ts`:
  - Store current results and columns in module-level variables for export access
  - Create download button element before the toggle (Hide) button
  - Add click handler that calls `api.exportResults()` with stored results
  - Update the results header HTML structure

### Step 11: Run Unit Tests
- Execute `cd app/server && uv run pytest tests/test_export.py -v` to validate export endpoints
- Fix any failing tests

### Step 12: Run Validation Commands
- Execute all validation commands to ensure the feature works correctly with zero regressions

## Testing Strategy

### Unit Tests
- Test table export endpoint:
  - Returns valid CSV for existing table
  - Returns 400 for invalid table name (SQL injection attempt)
  - Returns 404 for non-existent table
  - CSV contains correct headers and data
- Test results export endpoint:
  - Returns valid CSV with provided data
  - Handles empty results (returns headers only)
  - Handles special characters in data
  - Returns proper Content-Type and Content-Disposition headers

### Edge Cases
- Empty table (should return CSV with headers only)
- Empty query results (should return CSV with headers only)
- Table with special characters in column names
- Data containing commas, quotes, or newlines (CSV escaping)
- Very large tables (streaming response should handle efficiently)
- Table names that look like SQL injection attempts

## Acceptance Criteria
- [ ] Download button appears to the left of the '×' icon for each table in Available Tables
- [ ] Download button appears to the left of the 'Hide' button in Query Results header
- [ ] Clicking table download button downloads a CSV file named `{table_name}.csv`
- [ ] Clicking query results download button downloads a CSV file named `query_results.csv`
- [ ] CSV files contain correct headers matching column names
- [ ] CSV files contain all row data
- [ ] CSV files are properly formatted (proper escaping of special characters)
- [ ] Invalid table names return appropriate error
- [ ] All existing tests pass
- [ ] New unit tests pass
- [ ] TypeScript compiles without errors
- [ ] Frontend builds successfully

## Validation Commands
Execute every command to validate the feature works correctly with zero regressions.

- Read `.claude/commands/test_e2e.md`, then read and execute `.claude/commands/e2e/test_one_click_exports.md` E2E test file to validate this functionality works
- `cd app/server && uv run pytest` - Run server tests to validate the feature works with zero regressions
- `cd app/server && uv run pytest tests/test_export.py -v` - Run export-specific tests
- `cd app/client && bun tsc --noEmit` - Run frontend tests to validate the feature works with zero regressions
- `cd app/client && bun run build` - Run frontend build to validate the feature works with zero regressions

## Notes
- The CSV export uses Python's built-in `csv` module which handles proper escaping of special characters
- For large tables, consider using `StreamingResponse` with a generator to avoid memory issues
- The download is triggered client-side by creating a blob URL and programmatically clicking a hidden anchor element
- Unicode download icon options: ⬇ (U+2B07), ⤓ (U+2913), or an SVG icon
- Consider using the same icon styling pattern as the remove button for visual consistency
