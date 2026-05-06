# Retail Data Pipeline

An AI-powered ETL pipeline for retail e-commerce data analysis.

## Overview

This pipeline processes retail order data to generate business insights:
- Revenue analysis by product category
- Daily sales volume tracking
- Data quality validation and cleaning

## Features

- **Data Cleaning**: Removes duplicates, handles missing values
- **Business Metrics**: Calculates revenue per category and daily sales
- **Performance Optimization**: Memory-efficient processing with filters
- **Error Handling**: Comprehensive logging and validation
- **Testing**: Full test suite with pytest

## Project Structure

```
├── main.py                 # Main ETL pipeline
├── main_optimized.py       # Optimized version with performance improvements
├── test_pipeline.py        # Test suite
├── orders.csv             # Sample input data
├── specification.md        # Business requirements
├── requirements.txt        # Python dependencies
├── README.md              # This file
└── .github/
    └── workflows/
        └── ci.yml         # GitHub Actions workflow
```

## Installation

1. Create virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Basic Pipeline
```bash
python main.py
```

### Optimized Pipeline
```bash
python main_optimized.py
```

### Run Tests
```bash
pytest test_pipeline.py -v
```

## Input Data Format

CSV file with the following columns:
- `order_id`: Unique order identifier
- `customer_id`: Customer identifier
- `product`: Product name
- `category`: Product category
- `price`: Unit price
- `quantity`: Order quantity
- `order_date`: Order date (YYYY-MM-DD)

## Output Files

- `revenue.csv`: Total revenue per category
- `daily_sales.csv`: Daily order counts
- `revenue_optimized.csv`: Optimized version output
- `daily_sales_optimized.csv`: Optimized version output

## Performance Features

- Memory-efficient data types
- Early filtering for large datasets
- Incremental processing support
- Vectorized operations
- Optional compression

## Testing

The pipeline includes comprehensive tests:
- Data validation
- Function unit tests
- Integration tests
- Error handling tests

## CI/CD

Automated testing with GitHub Actions on every push.

## License

MIT License
