# Order Analysis Dashboard

A comprehensive Flask web application for analyzing customer and order data with interactive visualizations.

## Features

### 📊 Summary Statistics
- Total customers, orders, and revenue
- Average order value and order status distribution

### 🗺️ China Map Visualization
- Interactive map showing customer distribution across Chinese provinces
- Heat map display with customer count per province

### 📈 Data Visualizations
- Monthly revenue trends
- Customer age distribution analysis
- Product performance rankings
- Order status distribution charts

## Project Structure

```
data_workflow/
├── app.py                 # Main Flask application
├── run.py                # Startup script
├── requirements.txt      # Python dependencies
├── templates/
│   └── index.html       # Dashboard HTML template
├── customer data.txt     # Customer dataset
├── order data.txt        # Order dataset
└── order_analysis.db     # SQLite database (created on first run)
```

## Quick Start

### Option 1: Automated Startup (Recommended)
```bash
python run.py
```

### Option 2: Manual Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Start the application
python app.py
```

### Option 3: Direct Execution
```bash
python app.py
```

## Access the Dashboard

After starting the application, open your browser and navigate to:

**http://localhost:5000**

## Data Sources

- **Customer Data**: Contains customer information including province, city, and demographic details
- **Order Data**: Contains order details including products, quantities, amounts, and status

## API Endpoints

- `/` - Main dashboard interface
- `/api/summary` - Summary statistics and key metrics
- `/api/map-data` - Customer distribution data for China map
- `/api/charts` - Chart data for revenue trends and age distribution

## Technical Details

### Database
- **SQLite** database with SQLAlchemy ORM
- Automatic data import from CSV files on first run
- Relational structure with Customers and Orders tables

### Visualization Libraries
- **Plotly** for interactive charts and graphs
- **ECharts** for China map visualization
- Responsive design with modern CSS Grid layout

### Key Features
- Real-time data processing and visualization
- Mobile-responsive design
- Interactive map with hover tooltips
- Comprehensive summary statistics
- Product performance analysis

## Data Analysis

The dashboard provides insights into:
- Customer geographic distribution across China
- Revenue trends over time
- Customer demographic analysis
- Product performance and popularity
- Order processing efficiency

## Requirements

- Python 3.7+
- Flask 2.3.3
- SQLAlchemy
- Pandas
- Plotly
- ECharts (loaded via CDN)

## License

This project is created for educational and analytical purposes.