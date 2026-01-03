# Task 2.7 - Recipe Search and Data Visualization

## Search Implementation Thoughts

### Search Criteria

Users should be able to search for recipes based on the following criteria:

1. **Recipe Name/Title** - Search by the recipe title using partial matching (wildcards)
2. **Ingredient** - Find recipes that contain a specific ingredient
3. **Category** - Filter recipes by their category (e.g., Breakfast, Italian, Mexican)
4. **Maximum Cooking Time** - Filter by total time (prep + cook) in minutes

### Search Format

- **Input Form**: A user-friendly form with:
  - Text input for recipe name (supports partial/wildcard search)
  - Dropdown for ingredient selection
  - Dropdown for category selection
  - Number input for maximum total time
  - "Search" button to apply filters
  - "Show All" button to display all recipes without filters

### Output Format

- Results displayed as a **pandas DataFrame converted to HTML table**
- Table columns:
  - Recipe ID (hidden but used for linking)
  - Recipe Name (clickable link to detail page)
  - Category
  - Ingredients Count
  - Total Time (prep + cook)
  - Author
- Table should be sortable and clearly formatted
- Display count of results found
- Show active filter tags for clarity

### Partial/Wildcard Search

- Implement case-insensitive partial matching using Django's `__icontains` lookup
- Example: Searching "chick" will return "Chicken Parmesan", "Grilled Chicken Salad", etc.
- Example: Searching "spa" will return "Spaghetti Carbonara", "Spanish Omelette", etc.

---

## Data Analysis

### Chart 1: Bar Chart - Recipes per Category

- **Purpose**: Show the distribution of recipes across different categories
- **X-axis**: Category names (Breakfast, Italian, Mexican, etc.)
- **Y-axis**: Number of recipes (count)
- **Labels**: Category name on each bar, count value on top
- **Display**: Always shown on the search/visualization page
- **Use Case**: Helps users understand what types of recipes are available

### Chart 2: Pie Chart - Recipe Distribution by Difficulty (based on time)

- **Purpose**: Show proportion of recipes by time complexity
- **Categories**:
  - Quick (≤15 min total)
  - Medium (16-45 min total)
  - Long (>45 min total)
- **Labels**: Percentage and count for each segment
- **Display**: Always shown - provides quick overview of recipe complexity
- **Use Case**: Users can quickly see if most recipes are quick or time-intensive

### Chart 3: Line Chart - Recipes Created Over Time

- **Purpose**: Show the trend of recipe additions over time
- **X-axis**: Date (month/year or specific dates)
- **Y-axis**: Cumulative number of recipes
- **Labels**: Date markers on x-axis, recipe count on y-axis
- **Display**: Always shown - demonstrates platform growth
- **Use Case**: Track how the recipe collection has grown

---

## Implementation Notes

### Technologies Used

- **Django**: Web framework for views and URL routing
- **pandas**: DataFrame creation and manipulation
- **matplotlib**: Chart generation
- **Base64 encoding**: Embed charts as images in HTML

### Security Considerations

- Search page requires user authentication (login protection)
- Input sanitization for search queries
- CSRF protection on forms

### Testing Approach

- Test form field validation
- Test search functionality with various queries
- Test partial/wildcard matching
- Test login protection for views
- Test chart generation
- Test edge cases (empty results, special characters)
