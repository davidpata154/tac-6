# E2E Test: One-Click Table Exports

Test the one-click CSV export functionality for tables and query results in the Natural Language SQL Interface application.

## User Story

As a data analyst
I want to export tables and query results to CSV files with a single click
So that I can use the data in other applications like Excel or for further analysis

## Prerequisites

- Application is running at the `Application URL`
- At least one table is loaded in the database (e.g., users table from sample data)

## Test Steps

### Part 1: Verify Download Buttons Appear

1. Navigate to the `Application URL`
2. Take a screenshot of the initial state
3. **Verify** the Available Tables section is visible
4. **Verify** each table item has a download button (↓) to the left of the remove (×) button
5. Take a screenshot showing the download button for tables

### Part 2: Test Table Export

6. Click the download button for the first table (e.g., "users")
7. **Verify** a CSV file download is triggered
8. **Verify** the downloaded file is named "{table_name}.csv"
9. Take a screenshot after clicking the download button

### Part 3: Test Query Results Export

10. Enter a query: "Show me all users"
11. Click the Query button
12. **Verify** the results section appears with data
13. **Verify** a download button appears to the left of the "Hide" button in the results header
14. Take a screenshot of the results section showing the download button
15. Click the results download button
16. **Verify** a CSV file download is triggered with filename "query_results.csv"

### Part 4: Verify CSV Content

17. **Verify** the downloaded table CSV contains:
    - A header row with column names
    - Data rows matching the table content
18. **Verify** the downloaded results CSV contains:
    - A header row matching the query columns
    - Data rows matching the query results

## Success Criteria

- Download button (↓) appears to the left of remove button (×) for each table
- Download button appears to the left of Hide button for query results
- Clicking table download button triggers CSV file download
- Clicking results download button triggers CSV file download
- Downloaded CSV files have correct filenames
- Downloaded CSV files contain proper headers and data
- 4 screenshots are taken
