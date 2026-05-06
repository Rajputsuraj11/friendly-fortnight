import pandas as pd
import pytest
import os
from main import load_data, clean_data, transform_data, save_data

def test_orders_not_empty():
    """Test that orders.csv contains data"""
    df = pd.read_csv("orders.csv")
    assert df.shape[0] > 0, "orders.csv should not be empty"
    assert df.shape[1] == 7, "orders.csv should have 7 columns"

def test_load_data():
    """Test load_data function"""
    df = load_data("orders.csv")
    assert isinstance(df, pd.DataFrame), "load_data should return DataFrame"
    assert len(df) > 0, "Loaded DataFrame should not be empty"

def test_clean_data():
    """Test clean_data function"""
    # Create test data with duplicates and missing values
    test_data = pd.DataFrame({
        'order_id': [1, 2, 2, 3],
        'customer_id': [101, 102, 102, 103],
        'product': ['Laptop', 'Phone', 'Phone', 'Shoes'],
        'category': ['Electronics', 'Electronics', 'Electronics', 'Fashion'],
        'price': [800, 500, 500, None],
        'quantity': [1, 2, 2, None],
        'order_date': ['2024-01-01', '2024-01-01', '2024-01-01', '2024-01-02']
    })
    
    cleaned = clean_data(test_data)
    
    # Test duplicates removed
    assert len(cleaned) == 3, "Should remove duplicates"
    
    # Test missing values handled
    assert cleaned['quantity'].isna().sum() == 0, "No missing values in quantity"
    assert cleaned['price'].isna().sum() == 0, "No missing values in price"
    
    # Test data types
    assert cleaned['quantity'].dtype == 'int', "Quantity should be integer"
    assert cleaned['price'].dtype == 'float', "Price should be float"

def test_transform_data():
    """Test transform_data function"""
    test_data = pd.DataFrame({
        'order_id': [1, 2, 3],
        'customer_id': [101, 102, 103],
        'product': ['Laptop', 'Phone', 'Shoes'],
        'category': ['Electronics', 'Electronics', 'Fashion'],
        'price': [800, 500, 100],
        'quantity': [1, 2, 1],
        'order_date': ['2024-01-01', '2024-01-01', '2024-01-02']
    })
    
    revenue, daily = transform_data(test_data)
    
    # Test revenue calculation
    assert isinstance(revenue, pd.DataFrame), "Revenue should be DataFrame"
    assert len(revenue) == 2, "Should have 2 categories"
    assert 'total_revenue' in revenue.columns, "Should have total_revenue column"
    
    # Test electronics revenue: (800*1) + (500*2) = 1800
    electronics_revenue = revenue[revenue['category'] == 'Electronics']['total_revenue'].iloc[0]
    assert electronics_revenue == 1800, "Electronics revenue should be 1800"
    
    # Test daily sales
    assert isinstance(daily, pd.DataFrame), "Daily sales should be DataFrame"
    assert len(daily) == 2, "Should have 2 days"
    assert 'sales_count' in daily.columns, "Should have sales_count column"
    
    # Test 2024-01-01 has 2 sales
    jan1_sales = daily[daily['order_date'] == '2024-01-01']['sales_count'].iloc[0]
    assert jan1_sales == 2, "Jan 1 should have 2 sales"

def test_no_nulls_in_price():
    """Test that cleaned data has no nulls in price column"""
    df = load_data("orders.csv")
    cleaned = clean_data(df)
    assert cleaned['price'].isna().sum() == 0, "No null values in price after cleaning"

def test_no_duplicates():
    """Test that cleaned data has no duplicates"""
    df = load_data("orders.csv")
    cleaned = clean_data(df)
    assert len(cleaned) == len(cleaned.drop_duplicates()), "No duplicates in cleaned data"

def test_correct_totals():
    """Test that total calculations are correct"""
    df = load_data("orders.csv")
    cleaned = clean_data(df)
    
    # Calculate expected total for first row: 800 * 1 = 800
    expected_total = cleaned.iloc[0]['price'] * cleaned.iloc[0]['quantity']
    assert expected_total == 800, "First row total should be 800"

def test_save_data():
    """Test save_data function"""
    test_df = pd.DataFrame({
        'category': ['Electronics', 'Fashion'],
        'total_revenue': [1800, 100]
    })
    
    test_file = "test_output.csv"
    save_data(test_df, test_file)
    
    # Verify file was created
    assert os.path.exists(test_file), "Output file should be created"
    
    # Verify content
    saved_df = pd.read_csv(test_file)
    assert len(saved_df) == 2, "Saved file should have 2 rows"
    assert list(saved_df.columns) == ['category', 'total_revenue'], "Columns should match"
    
    # Cleanup
    os.remove(test_file)

def test_pipeline_integration():
    """Integration test for the entire pipeline"""
    # Run the main pipeline functions
    df = load_data("orders.csv")
    cleaned = clean_data(df)
    revenue, daily = transform_data(cleaned)
    
    # Verify outputs are created
    assert len(revenue) > 0, "Revenue data should not be empty"
    assert len(daily) > 0, "Daily sales data should not be empty"
    
    # Verify revenue totals make sense
    total_revenue = revenue['total_revenue'].sum()
    assert total_revenue > 0, "Total revenue should be positive"
