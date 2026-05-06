import pandas as pd
import logging
from typing import Tuple

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def load_data(file_path: str) -> pd.DataFrame:
    """
    Load order data from CSV file with error handling for missing columns.
    
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
        logger.info(f"Columns found: {list(df.columns)}")
        return df
    except FileNotFoundError:
        logger.error(f"File not found: {file_path}")
        raise
    except Exception as e:
        logger.error(f"Error loading data: {e}")
        raise

def validate_schema(df: pd.DataFrame) -> bool:
    """
    Validate that the DataFrame has the required columns.
    
    Args:
        df: DataFrame to validate
        
    Returns:
        True if schema is valid, False otherwise
    """
    logger.info("Validating data schema")
    
    required_columns = ['order_id', 'customer_id', 'product', 'category', 'quantity', 'order_date']
    optional_columns = ['price', 'discount']
    
    missing_required = [col for col in required_columns if col not in df.columns]
    
    if missing_required:
        logger.error(f"Missing required columns: {missing_required}")
        return False
    
    # Check for price column specifically
    if 'price' not in df.columns:
        logger.warning("Price column is missing - this will cause calculation errors")
        return False
    
    logger.info("Schema validation passed")
    return True

def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean the dataset with robust error handling.
    
    Args:
        df: Input DataFrame
        
    Returns:
        Cleaned DataFrame
        
    Raises:
        ValueError: If critical columns are missing
    """
    logger.info("Starting data cleaning")
    
    # Validate schema first
    if not validate_schema(df):
        raise ValueError("Schema validation failed - cannot proceed with cleaning")
    
    # Remove duplicates
    initial_count = len(df)
    df = df.drop_duplicates()
    duplicates_removed = initial_count - len(df)
    logger.info(f"Removed {duplicates_removed} duplicate records")
    
    # Handle missing values in quantity
    if "quantity" in df.columns:
        df["quantity"] = df["quantity"].fillna(1)
        df["quantity"] = df["quantity"].astype(int)
    
    # Handle missing values in price
    if "price" in df.columns:
        df["price"] = df["price"].fillna(0)
        df["price"] = df["price"].astype(float)
    else:
        logger.error("Price column is missing - cannot calculate revenue")
        raise ValueError("Price column is required for revenue calculations")
    
    # Handle discount column if present
    if "discount" in df.columns:
        df["discount"] = df["discount"].fillna(0)
        df["discount"] = df["discount"].clip(0, 1)
    else:
        df["discount"] = 0.0
    
    logger.info(f"Data cleaning completed. Final record count: {len(df)}")
    return df

def transform_data(df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Generate business metrics with error handling.
    
    Args:
        df: Cleaned DataFrame
        
    Returns:
        Tuple of (revenue_by_category, daily_sales) DataFrames
        
    Raises:
        ValueError: If required columns are missing
    """
    logger.info("Starting data transformation")
    
    # Check for required columns
    if "price" not in df.columns:
        raise ValueError("Price column is required for revenue calculations")
    if "quantity" not in df.columns:
        raise ValueError("Quantity column is required for revenue calculations")
    
    try:
        # Calculate total revenue
        df["total"] = df["price"] * df["quantity"]
        
        # Apply discount if present
        if "discount" in df.columns:
            df["total"] = df["total"] * (1 - df["discount"])
        
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
        
    except KeyError as e:
        logger.error(f"Missing required column for transformation: {e}")
        raise ValueError(f"Missing required column: {e}")
    except Exception as e:
        logger.error(f"Error during transformation: {e}")
        raise

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

def run_pipeline_with_debug(file_path: str = "orders_buggy.csv") -> None:
    """
    Execute the pipeline with comprehensive debugging and error handling.
    
    Args:
        file_path: Path to the input file
    """
    logger.info(f"Starting retail data pipeline with debugging for {file_path}")
    
    try:
        # Load data
        df = load_data(file_path)
        
        # Print data info for debugging
        print("\n=== Data Debug Info ===")
        print(f"Shape: {df.shape}")
        print(f"Columns: {list(df.columns)}")
        print(f"Data types:\n{df.dtypes}")
        print(f"First few rows:\n{df.head()}")
        print(f"Missing values:\n{df.isnull().sum()}")
        
        # Clean data (this will fail if price is missing)
        df = clean_data(df)
        
        # Transform data
        revenue, daily = transform_data(df)
        
        # Save results
        save_data(revenue, "revenue_debug.csv")
        save_data(daily, "daily_sales_debug.csv")
        
        logger.info("Pipeline completed successfully")
        
        # Print summary
        print("\n=== Pipeline Summary (Debug) ===")
        print(f"Total orders processed: {len(df)}")
        print(f"Categories analyzed: {len(revenue)}")
        print(f"Days covered: {len(daily)}")
        print(f"\nRevenue by Category:")
        print(revenue.to_string(index=False))
        
    except Exception as e:
        logger.error(f"Pipeline failed with error: {e}")
        print(f"\n=== ERROR DEBUG INFO ===")
        print(f"Error Type: {type(e).__name__}")
        print(f"Error Message: {str(e)}")
        print("\nPossible Solutions:")
        print("1. Check if 'price' column exists in the input file")
        print("2. Ensure all required columns are present")
        print("3. Verify data types are correct")
        print("4. Check for missing values that need to be handled")
        raise

if __name__ == "__main__":
    # Try to run with buggy data
    try:
        run_pipeline_with_debug("orders_buggy.csv")
    except Exception as e:
        print(f"\n=== PIPELINE FAILED ===")
        print(f"The pipeline failed as expected due to missing price column.")
        print(f"Error: {e}")
        
        print(f"\n=== ATTEMPTING RECOVERY ===")
        print("Let's try to fix the issue by adding a default price...")
        
        # Create a fixed version
        try:
            df_buggy = pd.read_csv("orders_buggy.csv")
            # Add a default price column
            df_buggy["price"] = 100.0  # Default price
            df_buggy.to_csv("orders_fixed.csv", index=False)
            print("Created orders_fixed.csv with default price column")
            
            # Run with fixed data
            run_pipeline_with_debug("orders_fixed.csv")
            
        except Exception as fix_error:
            print(f"Recovery also failed: {fix_error}")
