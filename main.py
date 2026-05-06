import pandas as pd
import logging
from typing import Tuple

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def load_data(file_path: str) -> pd.DataFrame:
    """
    Load order data from CSV file.
    
    Args:
        file_path: Path to the CSV file
        
    Returns:
        DataFrame containing order data
        
    Raises:
        FileNotFoundError: If file doesn't exist
        Exception: For other file reading errors
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
    Clean the dataset by removing duplicates and handling missing values.
    
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
    
    # Ensure proper data types
    df["quantity"] = df["quantity"].astype(int)
    df["price"] = df["price"].astype(float)
    
    logger.info(f"Data cleaning completed. Final record count: {len(df)}")
    return df

def transform_data(df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Generate business metrics from cleaned data.
    
    Args:
        df: Cleaned DataFrame
        
    Returns:
        Tuple of (revenue_by_category, daily_sales) DataFrames
    """
    logger.info("Starting data transformation")
    
    # Calculate total revenue per order
    df["total"] = df["price"] * df["quantity"]
    
    # Calculate revenue by category
    revenue_by_category = df.groupby("category")["total"].sum().reset_index()
    revenue_by_category.columns = ["category", "total_revenue"]
    revenue_by_category = revenue_by_category.sort_values("total_revenue", ascending=False)
    
    # Calculate daily sales count
    daily_sales = df.groupby("order_date")["order_id"].count().reset_index()
    daily_sales.columns = ["order_date", "sales_count"]
    daily_sales = daily_sales.sort_values("order_date")
    
    logger.info(f"Generated {len(revenue_by_category)} category revenue records")
    logger.info(f"Generated {len(daily_sales)} daily sales records")
    
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
    Execute the complete ETL pipeline.
    """
    logger.info("Starting retail data pipeline")
    
    try:
        # Load data
        df = load_data("orders.csv")
        
        # Clean data
        df = clean_data(df)
        
        # Transform data
        revenue, daily = transform_data(df)
        
        # Save results
        save_data(revenue, "revenue.csv")
        save_data(daily, "daily_sales.csv")
        
        logger.info("Pipeline completed successfully")
        
        # Print summary
        print("\n=== Pipeline Summary ===")
        print(f"Total orders processed: {len(df)}")
        print(f"Categories analyzed: {len(revenue)}")
        print(f"Days covered: {len(daily)}")
        print(f"\nRevenue by Category:")
        print(revenue.to_string(index=False))
        
    except Exception as e:
        logger.error(f"Pipeline failed: {e}")
        raise

if __name__ == "__main__":
    run_pipeline()
