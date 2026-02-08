# Feature: One Click Table Exports

## Metadata
issue_number: `1`
adw_id: `44a44d02`
issue_json: `{"number":1,"title":"One click table exports","body":"Using adw_plan_build_review add one click table exports and one click result export feature to get results as csv files.\n\nCreate two new endpoints to support these features. One exporting tables, one for exporting query results.\n\nPlace a download button directly to the left of the 'x' icon for available tables.\nPlace a download button directly to the left of the 'hide' button for query results.\n\nUse the appropriate download icon."}`

## Feature Description
This feature adds one-click CSV export functionality for both database tables and query results in the Natural Language SQL Interface application. Users will be able to download any available table as a CSV file directly from the tables list, and also export query results to CSV from the results section. The feature includes two new backend API endpoints to handle the CSV generation and two frontend download buttons positioned strategically in the UI.

## User Story
As a data analyst
I want to export tables and query results to CSV files with a single click
So that I can use the data in other applications like Excel or for further analysis

## Problem Statement
Currently, users can query and view data in the Natural Language SQL Interface, but there is no way to export this data for use in other tools. Users who want to use the query results or table data in spreadsheets, reports, or other applications have no straightforward method to do so. This limits the utility of the application for data workflows that require data portability.

## Solution Statement
Implement a two-part export solution:
1. **Table Export**: Add a download button next to each table in the Available Tables section that triggers a GET request to a new `/api/export/table/{table_name}` endpoint, which returns the entire table as a CSV file.
2. **Query Results Export**: Add a download button in the results section header that triggers a POST request to a new `/api/export/results` endpoint, passing the current query results data to generate a CSV file.

Both endpoints will return CSV files with appropriate headers for browser download. The frontend buttons will use a download icon (⬇️ or similar SVG icon) and be positioned as specified: to the left of the 'x' button for tables, and to the left of the 'Hide' button for query results.

## Relevant Files
Use these files to implement the feature:

### Backend Files
- `app/server/server.py` - Main FastAPI server file where new endpoints will be added. Contains existing endpoint patterns to follow for `/api/export/table/{table_name}` and `/api/export/results`.
- `app/server/core/data_models.py` - Pydantic models for request/response types. New models may be needed for the export results request.
- `app/server/core/sql_processor.py` - Contains `execute_sql_safely` and `get_database_schema` functions that can be used for retrieving table data.
- `app/server/core/sql_security.py` - Contains `validate_identifier` and `execute_query_safely` for secure table access.

### Frontend Files
- `app/client/src/main.ts` - Main TypeScript file containing UI logic. Functions to modify: `displayTables()` for table download button, `displayResults()` for results download button.
- `app/client/src/api/client.ts` - API client with existing patterns for API calls. New export methods will be added here.
- `app/client/src/types.d.ts` - TypeScript type definitions. May need new types for export functionality.
- `app/client/src/style.css` - CSS styles. New styles needed for download buttons.
- `app/client/index.html` - HTML structure. May need minor modifications for results section download button placement.

### Test Files
- `app/server/tests/` - Directory for server tests. New test file needed for export endpoints.

### E2E Test References
- `.claude/commands/test_e2e.md` - Instructions for creating E2E tests
- `.claude/commands/e2e/test_basic_query.md` - Example E2E test format

### New Files
- `app/server/tests/test_export.py` - New test file for export endpoint unit tests
- `.claude/commands/e2e/test_one_click_exports.md` - New E2E test file for export functionality

## Implementation Plan
### Phase 1: Foundation
1. Create Pydantic models for the export results request (to accept query results data)
2. Add CSS styles for download buttons that match the existing button styles
3. Create the E2E test file to define expected behavior

### Phase 2: Core Implementation
1. Implement `/api/export/table/{table_name}` endpoint in server.py that:
   - Validates the table name
   - Retrieves all data from the table
   - Converts to CSV format
   - Returns as a downloadable file with proper headers
2. Implement `/api/export/results` endpoint in server.py that:
   - Accepts query results (columns and data) in the request body
   - Converts to CSV format
   - Returns as a downloadable file with proper headers
3. Add API client methods in client.ts for triggering file downloads
4. Add download button to table items in `displayTables()` function
5. Add download button to results section header in `displayResults()` function

### Phase 3: Integration
1. Wire up download buttons to API calls with proper file download handling
2. Add loading states for download buttons
3. Handle errors gracefully with user feedback
4. Write unit tests for the new endpoints
5. Run E2E tests to validate the complete feature

## Step by Step Tasks
IMPORTANT: Execute every step in order, top to bottom.

### Step 1: Create E2E Test File
- Create `.claude/commands/e2e/test_one_click_exports.md` with test steps for:
  - Verifying download button appears next to each table
  - Verifying download button appears in results section
  - Testing table export functionality (click downloads CSV)
  - Testing query results export functionality

### Step 2: Add Export Request/Response Models
- Add `ExportResultsRequest` model to `app/server/core/data_models.py`:
  - `columns: List[str]` - column names
  - `results: List[Dict[str, Any]]` - row data
- No response model needed (returns file stream)

### Step 3: Implement Table Export Endpoint
- Add `GET /api/export/table/{table_name}` endpoint to `app/server/server.py`:
  - Validate table name using `validate_identifier()`
  - Check table exists using `check_table_exists()`
  - Execute `SELECT * FROM {table}` using safe query execution
  - Convert results to CSV using Python's csv module with StringIO
  - Return `StreamingResponse` with `Content-Disposition: attachment; filename="{table_name}.csv"` header
  - Set `Content-Type: text/csv`

### Step 4: Implement Results Export Endpoint
- Add `POST /api/export/results` endpoint to `app/server/server.py`:
  - Accept `ExportResultsRequest` body
  - Convert columns and results to CSV format
  - Return `StreamingResponse` with `Content-Disposition: attachment; filename="query_results.csv"` header
  - Set `Content-Type: text/csv`

### Step 5: Add Download Button Styles
- Add styles to `app/client/src/style.css`:
  - `.download-table-button` - styled similar to `.remove-table-button`
  - `.download-results-button` - styled similar to `.toggle-button`
  - Include hover states with appropriate color (primary color instead of error)

### Step 6: Add API Client Methods
- Add methods to `app/client/src/api/client.ts`:
  - `exportTable(tableName: string): Promise<void>` - triggers file download for table
  - `exportResults(columns: string[], results: Record<string, any>[]): Promise<void>` - triggers file download for results
- Use `window.location.href` or create a hidden anchor element for GET endpoint
- Use `fetch` with blob handling for POST endpoint

### Step 7: Add Download Button to Tables
- Modify `displayTables()` function in `app/client/src/main.ts`:
  - Create download button element with download icon (⬇️ or ↓)
  - Insert button directly to the left of the remove button in `tableHeader`
  - Add click handler that calls `api.exportTable(table.name)` or triggers direct download

### Step 8: Add Download Button to Results Section
- Modify `displayResults()` function in `app/client/src/main.ts`:
  - Store current query response data for export
  - Create download button element with download icon
  - Insert button directly to the left of the Hide button in results header
  - Add click handler that calls `api.exportResults()` with current columns and results

### Step 9: Write Unit Tests for Export Endpoints
- Create `app/server/tests/test_export.py`:
  - Test table export returns valid CSV with correct headers
  - Test table export with invalid table name returns 400
  - Test table export with non-existent table returns 404
  - Test results export returns valid CSV
  - Test results export with empty results
  - Test CSV format is correct (proper escaping, headers)

### Step 10: Run Validation Commands
- Execute all validation commands to ensure the feature works correctly with zero regressions

## Testing Strategy
### Unit Tests
- `test_export_table_success`: Export existing table returns CSV with all rows
- `test_export_table_invalid_name`: Invalid table name returns 400 error
- `test_export_table_not_found`: Non-existent table returns 404 error
- `test_export_results_success`: Export results returns valid CSV
- `test_export_results_empty`: Export empty results returns CSV with only headers
- `test_export_results_special_chars`: Results with commas/quotes are properly escaped
- `test_csv_format_headers`: CSV has correct Content-Type and Content-Disposition headers

### Edge Cases
- Table with special characters in column names
- Results with null/None values
- Results with very large datasets
- Results with unicode characters
- Empty table export
- Table names that could be SQL injection attempts (should be validated)

## Acceptance Criteria
- [ ] Download button appears to the left of the 'x' icon for each table in the Available Tables section
- [ ] Download button appears to the left of the 'Hide' button in the Query Results section
- [ ] Clicking table download button triggers download of that table as CSV file
- [ ] Clicking results download button triggers download of current query results as CSV file
- [ ] Downloaded CSV files are properly formatted with headers and data
- [ ] CSV files have appropriate filenames (`{table_name}.csv` and `query_results.csv`)
- [ ] Download buttons have appropriate download icons
- [ ] All existing functionality continues to work (no regressions)
- [ ] Unit tests pass for new export endpoints
- [ ] E2E tests pass for export functionality

## Validation Commands
Execute every command to validate the feature works correctly with zero regressions.

- Read `.claude/commands/test_e2e.md`, then read and execute `.claude/commands/e2e/test_one_click_exports.md` E2E test file to validate this functionality works.
- `cd app/server && uv run pytest` - Run server tests to validate the feature works with zero regressions
- `cd app/client && bun tsc --noEmit` - Run frontend tests to validate the feature works with zero regressions
- `cd app/client && bun run build` - Run frontend build to validate the feature works with zero regressions

## Notes
- The CSV export uses Python's built-in `csv` module which handles proper escaping of special characters (commas, quotes, newlines)
- For the table export endpoint, we use a GET request since it's idempotent and can be easily triggered via direct URL access
- For the results export endpoint, we use POST since we need to send the results data in the request body
- The download icon should be visually distinct but consistent with the existing UI style - consider using ⬇ or a similar simple icon
- Future enhancement: Add option to export as other formats (JSON, Excel)
- Future enhancement: Add progress indicator for large exports
- The StreamingResponse is used for efficient memory handling with large datasets
