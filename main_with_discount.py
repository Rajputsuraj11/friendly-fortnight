import pandas as pd
import logging
from typing import Tuple

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def load_data(file_path: str) -> pd.DataFrame:
    """
    Load order data from CSV file with discount support.
    
    Args:
        file_path: Path to the CSV file
        
    Returns:
        DataFrame containing order data with discount column
    """
    try:
        logger.info(f"Loading data from {file_path}")
        df = pd.read_csv(file_path)
        logger.info(f"Successfully loaded {len(df)} records")
        return df
    except FileNotFoundError:
        logger.error(f"File not found: {file_path}")
        raise
    except Exception as e:
        logger.error(f"Error loading data: {e}")
        raise

def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean the dataset with discount handling.
    
    Args:
        df: Input DataFrame
        
    Returns:
        Cleaned DataFrame
    """
    logger.info("Starting data cleaning")
    
    # Remove duplicates
    initial_count = len(df)
    df = df.drop_duplicates()
    duplicates_removed = initial_count - len(df)
    logger.info(f"Removed {duplicates_removed} duplicate records")
    
    # Handle missing values
    df["quantity"] = df["quantity"].fillna(1)
    df["price"] = df["price"].fillna(0)
    
    # Handle discount column - default to 0 if missing
    if "discount" in df.columns:
        df["discount"] = df["discount"].fillna(0)
        # Ensure discount is between 0 and 1
        df["discount"] = df["discount"].clip(0, 1)
    else:
        df["discount"] = 0.0
        logger.warning("Discount column not found, using 0.0 for all records")
    
    # Ensure proper data types
    df["quantity"] = df["quantity"].astype(int)
    df["price"] = df["price"].astype(float)
    df["discount"] = df["discount"].astype(float)
    
    logger.info(f"Data cleaning completed. Final record count: {len(df)}")
    return df

def transform_data(df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Generate business metrics with discount calculations.
    
    Args:
        df: Cleaned DataFrame
        
    Returns:
        Tuple of (revenue_by_category, daily_sales) DataFrames
    """
    logger.info("Starting data transformation")
    
    # Calculate discounted price and total revenue
    df["discounted_price"] = df["price"] * (1 - df["discount"])
    df["total"] = df["discounted_price"] * df["quantity"]
    
    # Calculate revenue by category (after discount)
    revenue_by_category = df.groupby("category")["total"].sum().reset_index()
    revenue_by_category.columns = ["category", "total_revenue"]
    revenue_by_category = revenue_by_category.sort_values("total_revenue", ascending=False)
    
    # Calculate daily sales count
    daily_sales = df.groupby("order_date")["order_id"].count().reset_index()
    daily_sales.columns = ["order_date", "sales_count"]
    daily_sales = daily_sales.sort_values("order_date")
    
    # Additional metrics: total discount amount by category
    original_total = (df["price"] * df["quantity"]).sum()
    discounted_total = df["total"].sum()
    total_discount = original_total - discounted_total
    
    logger.info(f"Generated {len(revenue_by_category)} category revenue records")
    logger.info(f"Generated {len(daily_sales)} daily sales records")
    logger.info(f"Total discount amount: ${total_discount:.2f}")
    
    return revenue_by_category, daily_sales

def save_data(df: pd.DataFrame, path: str) -> None:
    """
    Save DataFrame to CSV file.
    
    Args:
        df: DataFrame to save
        path: Output file path
    """
    try:
        logger.info(f"Saving data to {path}")
        df.to_csv(path, index=False)
        logger.info(f"Successfully saved {len(df)} records to {path}")
    except Exception as e:
        logger.error(f"Error saving data to {path}: {e}")
        raise

def run_pipeline() -> None:
    """
    Execute the complete ETL pipeline with discount support.
    """
    logger.info("Starting retail data pipeline with discount support")
    
    try:
        # Load data with discount
        df = load_data("orders_with_discount.csv")
        
        # Clean data
        df = clean_data(df)
        
        # Transform data
        revenue, daily = transform_data(df)
        
        # Save results
        save_data(revenue, "revenue_with_discount.csv")
        save_data(daily, "daily_sales_with_discount.csv")
        
        logger.info("Pipeline completed successfully")
        
        # Print summary
        print("\n=== Pipeline Summary (With Discounts) ===")
        print(f"Total orders processed: {len(df)}")
        print(f"Categories analyzed: {len(revenue)}")
        print(f"Days covered: {len(daily)}")
        print(f"\nRevenue by Category (After Discount):")
        print(revenue.to_string(index=False))
        
        # Show discount impact
        original_revenue = (df["price"] * df["quantity"]).sum()
        discounted_revenue = df["total"].sum()
        total_discount_amount = original_revenue - discounted_revenue
        discount_percentage = (total_discount_amount / original_revenue) * 100
        
        print(f"\nDiscount Impact:")
        print(f"Original Revenue: ${original_revenue:.2f}")
        print(f"Discounted Revenue: ${discounted_revenue:.2f}")
        print(f"Total Discount Amount: ${total_discount_amount:.2f}")
        print(f"Average Discount Rate: {discount_percentage:.1f}%")
        
    except Exception as e:
        logger.error(f"Pipeline failed: {e}")
        raise

if __name__ == "__main__":
    run_pipeline()
