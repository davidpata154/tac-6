# E2E Test: One-Click Table Exports

Test the one-click export functionality for tables and query results in the Natural Language SQL Interface application.

## User Story

As a data analyst
I want to export tables and query results to CSV with one click
So that I can easily share data or use it in other applications like Excel or Google Sheets

## Prerequisites

- Application is running at the `Application URL`
- Sample data is available for testing

## Test Steps

### Part 1: Setup and Initial State

1. Navigate to the `Application URL`
2. Take a screenshot of the initial state
3. **Verify** the page title is "Natural Language SQL Interface"
4. **Verify** core UI elements are present:
   - Query input textbox
   - Query button
   - Upload Data button
   - Available Tables section

### Part 2: Load Sample Data

5. Click "Upload Data" button to open the modal
6. Take a screenshot of the upload modal
7. Click on "Users" sample data button to load users data
8. Wait for the upload to complete
9. **Verify** the "users" table appears in the Available Tables section
10. Take a screenshot showing the users table loaded

### Part 3: Verify Table Download Button

11. **Verify** there is a download button (⬇) to the left of the '×' (remove) icon for the users table
12. Take a screenshot highlighting the download button location

### Part 4: Test Table Export

13. Click the download button for the users table
14. **Verify** a CSV file download is triggered
15. **Verify** the downloaded file is named "users.csv"
16. Take a screenshot after clicking the download button
17. **Verify** the CSV file contains:
    - Header row with column names
    - Data rows matching the table contents

### Part 5: Execute a Query

18. Enter the query: "Show me all users"
19. Take a screenshot of the query input
20. Click the Query button
21. Wait for results to appear
22. **Verify** the query results section is displayed
23. Take a screenshot of the query results

### Part 6: Verify Query Results Download Button

24. **Verify** there is a download button (⬇) to the left of the 'Hide' button in the Results header
25. Take a screenshot highlighting the query results download button location

### Part 7: Test Query Results Export

26. Click the download button for the query results
27. **Verify** a CSV file download is triggered
28. **Verify** the downloaded file is named "query_results.csv"
29. Take a screenshot after clicking the download button
30. **Verify** the CSV file contains:
    - Header row matching the query result columns
    - Data rows matching the displayed results

### Part 8: Test Edge Cases

31. Run a query that returns no results (e.g., "Show users where age > 1000")
32. **Verify** the download button for empty results still works
33. **Verify** the downloaded CSV contains only headers

## Success Criteria

- Download button appears to the left of the '×' icon for each table in Available Tables
- Download button appears to the left of the 'Hide' button in Query Results header
- Clicking table download button downloads a CSV file named `{table_name}.csv`
- Clicking query results download button downloads a CSV file named `query_results.csv`
- CSV files contain correct headers matching column names
- CSV files contain all row data
- CSV files are properly formatted (proper escaping of special characters)
- Empty results produce a valid CSV with headers only
- All existing functionality continues to work

## Screenshots Required

1. Initial application state
2. Upload modal
3. Table loaded with download button visible
4. Download button location for table
5. Query input with text
6. Query results displayed
7. Download button location for query results
8. After table export
9. After query results export
