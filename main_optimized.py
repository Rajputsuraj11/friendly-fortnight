import pandas as pd
import logging
from typing import Tuple, Optional
import time
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def load_data(file_path: str, min_price: float = 0.0, incremental_date: Optional[str] = None) -> pd.DataFrame:
    """
    Load order data from CSV file with performance optimizations.
    
    Args:
        file_path: Path to the CSV file
        min_price: Filter out orders with price below this threshold
        incremental_date: Only load orders after this date (YYYY-MM-DD)
        
    Returns:
        DataFrame containing filtered order data
        
    Raises:
        FileNotFoundError: If file doesn't exist
        Exception: For other file reading errors
    """
    try:
        logger.info(f"Loading data from {file_path}")
        
        # Use dtype optimization for memory efficiency
        dtype_dict = {
            'order_id': 'int32',
            'customer_id': 'int32', 
            'price': 'float32'
            # quantity will be handled later due to missing values
        }
        
        df = pd.read_csv(file_path, dtype=dtype_dict)
        
        # Apply performance filters early
        initial_count = len(df)
        
        # Filter by minimum price
        if min_price > 0:
            df = df[df["price"] > min_price]
            logger.info(f"Filtered {initial_count - len(df)} records with price <= {min_price}")
        
        # Incremental processing
        if incremental_date:
            df = df[df["order_date"] > incremental_date]
            logger.info(f"Filtered {initial_count - len(df)} records before {incremental_date}")
        
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
    Clean the dataset with optimized operations.
    
    Args:
        df: Input DataFrame
        
    Returns:
        Cleaned DataFrame
    """
    logger.info("Starting data cleaning")
    start_time = time.time()
    
    # Use more efficient duplicate detection
    initial_count = len(df)
    df = df.drop_duplicates(keep='first')
    duplicates_removed = initial_count - len(df)
    logger.info(f"Removed {duplicates_removed} duplicate records")
    
    # Vectorized operations for missing values
    df["quantity"] = df["quantity"].fillna(1).astype('int32')
    df["price"] = df["price"].fillna(0).astype('float32')
    
    # Remove rows with invalid data
    df = df[df["price"] >= 0]  # No negative prices
    df = df[df["quantity"] > 0]  # No zero/negative quantities
    
    cleaning_time = time.time() - start_time
    logger.info(f"Data cleaning completed in {cleaning_time:.2f}s. Final record count: {len(df)}")
    return df

def transform_data(df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Generate business metrics with optimized aggregations.
    
    Args:
        df: Cleaned DataFrame
        
    Returns:
        Tuple of (revenue_by_category, daily_sales) DataFrames
    """
    logger.info("Starting data transformation")
    start_time = time.time()
    
    # Vectorized calculation
    df["total"] = df["price"].astype('float32') * df["quantity"].astype('int32')
    
    # Optimized aggregations using categorical data types
    df['category'] = df['category'].astype('category')
    
    revenue_by_category = (df.groupby("category", observed=True)["total"]
                          .sum()
                          .reset_index()
                          .sort_values("total", ascending=False))
    revenue_by_category.columns = ["category", "total_revenue"]
    
    # Optimized daily sales
    daily_sales = (df.groupby("order_date")["order_id"]
                  .count()
                  .reset_index()
                  .sort_values("order_date"))
    daily_sales.columns = ["order_date", "sales_count"]
    
    transform_time = time.time() - start_time
    logger.info(f"Data transformation completed in {transform_time:.2f}s")
    logger.info(f"Generated {len(revenue_by_category)} category revenue records")
    logger.info(f"Generated {len(daily_sales)} daily sales records")
    
    return revenue_by_category, daily_sales

def save_data(df: pd.DataFrame, path: str, compression: bool = False) -> None:
    """
    Save DataFrame to CSV file with optional compression.
    
    Args:
        df: DataFrame to save
        path: Output file path
        compression: Whether to use compression
    """
    try:
        logger.info(f"Saving data to {path}")
        
        if compression:
            df.to_csv(path, index=False, compression='gzip')
            path += '.gz'
        else:
            df.to_csv(path, index=False)
            
        logger.info(f"Successfully saved {len(df)} records to {path}")
        
    except Exception as e:
        logger.error(f"Error saving data to {path}: {e}")
        raise

def validate_data_quality(df: pd.DataFrame) -> bool:
    """
    Validate data quality before processing.
    
    Args:
        df: DataFrame to validate
        
    Returns:
        True if data passes validation, False otherwise
    """
    logger.info("Validating data quality")
    
    # Check for required columns
    required_columns = ['order_id', 'customer_id', 'product', 'category', 'price', 'quantity', 'order_date']
    missing_columns = [col for col in required_columns if col not in df.columns]
    
    if missing_columns:
        logger.error(f"Missing required columns: {missing_columns}")
        return False
    
    # Check for empty dataset
    if len(df) == 0:
        logger.error("Dataset is empty")
        return False
    
    # Check for negative values
    if (df['price'] < 0).any():
        logger.warning("Found negative prices")
    
    if (df['quantity'] <= 0).any():
        logger.warning("Found non-positive quantities")
    
    logger.info("Data quality validation passed")
    return True

def run_pipeline(min_price: float = 0.0, incremental_date: Optional[str] = None, 
                use_compression: bool = False) -> None:
    """
    Execute the optimized ETL pipeline.
    
    Args:
        min_price: Filter orders with price below this threshold
        incremental_date: Only process orders after this date
        use_compression: Whether to compress output files
    """
    start_time = time.time()
    logger.info("Starting optimized retail data pipeline")
    
    try:
        # Load data with filters
        df = load_data("orders.csv", min_price=min_price, incremental_date=incremental_date)
        
        # Validate data quality
        if not validate_data_quality(df):
            raise ValueError("Data quality validation failed")
        
        # Clean data
        df = clean_data(df)
        
        # Transform data
        revenue, daily = transform_data(df)
        
        # Save results
        save_data(revenue, "revenue_optimized.csv", use_compression)
        save_data(daily, "daily_sales_optimized.csv", use_compression)
        
        total_time = time.time() - start_time
        logger.info(f"Pipeline completed successfully in {total_time:.2f}s")
        
        # Print summary
        print("\n=== Optimized Pipeline Summary ===")
        print(f"Total orders processed: {len(df)}")
        print(f"Categories analyzed: {len(revenue)}")
        print(f"Days covered: {len(daily)}")
        print(f"Processing time: {total_time:.2f}s")
        print(f"\nRevenue by Category:")
        print(revenue.to_string(index=False))
        
    except Exception as e:
        logger.error(f"Pipeline failed: {e}")
        raise

if __name__ == "__main__":
    # Example usage with optimizations
    run_pipeline(
        min_price=0.0,  # Filter out free orders
        incremental_date=None,  # Process all data
        use_compression=False  # No compression for this demo
    )
