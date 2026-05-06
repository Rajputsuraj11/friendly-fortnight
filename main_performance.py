import pandas as pd
import numpy as np
import logging
import time
from typing import Tuple, Optional
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def load_data_optimized(file_path: str, chunk_size: Optional[int] = None) -> pd.DataFrame:
    """
    Load large dataset with memory optimization.
    
    Args:
        file_path: Path to the CSV file
        chunk_size: If provided, load in chunks
        
    Returns:
        DataFrame containing order data
    """
    start_time = time.time()
    logger.info(f"Loading large dataset from {file_path}")
    
    # Optimize data types for memory efficiency
    dtype_dict = {
        'order_id': 'int32',
        'customer_id': 'int32',
        'price': 'float32',
        'quantity': 'float32',  # Keep as float to handle NaN
        'discount': 'float32'
    }
    
    # Category columns as category type for memory efficiency
    categorical_cols = ['product', 'category']
    
    try:
        if chunk_size:
            # Load in chunks for very large files
            chunks = []
            for chunk in pd.read_csv(file_path, dtype=dtype_dict, chunksize=chunk_size):
                for col in categorical_cols:
                    if col in chunk.columns:
                        chunk[col] = chunk[col].astype('category')
                chunks.append(chunk)
            df = pd.concat(chunks, ignore_index=True)
        else:
            # Load all at once with optimizations
            df = pd.read_csv(file_path, dtype=dtype_dict)
            
            # Convert categorical columns
            for col in categorical_cols:
                if col in df.columns:
                    df[col] = df[col].astype('category')
        
        load_time = time.time() - start_time
        memory_usage = df.memory_usage(deep=True).sum() / 1024 / 1024
        
        logger.info(f"Loaded {len(df)} records in {load_time:.2f}s")
        logger.info(f"Memory usage: {memory_usage:.2f} MB")
        
        return df
        
    except Exception as e:
        logger.error(f"Error loading data: {e}")
        raise

def clean_data_optimized(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean large dataset with vectorized operations.
    
    Args:
        df: Input DataFrame
        
    Returns:
        Cleaned DataFrame
    """
    start_time = time.time()
    logger.info("Starting optimized data cleaning")
    initial_count = len(df)
    
    # Remove duplicates efficiently
    df = df.drop_duplicates(keep='first')
    duplicates_removed = initial_count - len(df)
    logger.info(f"Removed {duplicates_removed} duplicate records")
    
    # Vectorized missing value handling
    df["quantity"] = df["quantity"].fillna(1).astype('int32')
    df["price"] = df["price"].fillna(0).astype('float32')
    df["discount"] = df["discount"].fillna(0).astype('float32')
    
    # Validate and clean data ranges
    df = df[df["price"] >= 0]  # No negative prices
    df = df[df["quantity"] > 0]  # No zero/negative quantities
    df["discount"] = df["discount"].clip(0, 1)  # Discount between 0-1
    
    cleaning_time = time.time() - start_time
    logger.info(f"Data cleaning completed in {cleaning_time:.2f}s. Final count: {len(df)}")
    
    return df

def transform_data_optimized(df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Transform large dataset with optimized aggregations.
    
    Args:
        df: Cleaned DataFrame
        
    Returns:
        Tuple of (revenue_by_category, daily_sales) DataFrames
    """
    start_time = time.time()
    logger.info("Starting optimized data transformation")
    
    # Vectorized calculations
    df["total"] = df["price"] * df["quantity"] * (1 - df["discount"])
    
    # Optimized aggregations using categorical data
    revenue_by_category = (df.groupby("category", observed=True)["total"]
                          .sum()
                          .reset_index()
                          .sort_values("total", ascending=False))
    revenue_by_category.columns = ["category", "total_revenue"]
    
    # Optimized daily sales with date parsing
    df["order_date"] = pd.to_datetime(df["order_date"])
    daily_sales = (df.groupby(df["order_date"].dt.date)["order_id"]
                  .count()
                  .reset_index()
                  .sort_values("order_date"))
    daily_sales.columns = ["order_date", "sales_count"]
    
    # Additional performance metrics
    daily_sales["order_date"] = daily_sales["order_date"].astype(str)
    
    transform_time = time.time() - start_time
    logger.info(f"Data transformation completed in {transform_time:.2f}s")
    
    return revenue_by_category, daily_sales

def performance_benchmark(df: pd.DataFrame, operation_name: str) -> None:
    """
    Benchmark memory usage and performance.
    
    Args:
        df: DataFrame to benchmark
        operation_name: Name of the operation
    """
    memory_usage = df.memory_usage(deep=True).sum() / 1024 / 1024
    logger.info(f"[BENCHMARK] {operation_name}: {len(df)} rows, {memory_usage:.2f} MB")

def run_performance_pipeline(file_path: str = "orders_large.csv") -> None:
    """
    Execute the performance-optimized pipeline.
    
    Args:
        file_path: Path to the input file
    """
    total_start_time = time.time()
    logger.info("Starting performance-optimized retail data pipeline")
    
    try:
        # Load data with optimizations
        df = load_data_optimized(file_path)
        performance_benchmark(df, "After Loading")
        
        # Clean data
        df = clean_data_optimized(df)
        performance_benchmark(df, "After Cleaning")
        
        # Transform data
        revenue, daily = transform_data_optimized(df)
        performance_benchmark(revenue, "Revenue DataFrame")
        performance_benchmark(daily, "Daily Sales DataFrame")
        
        # Save results
        save_start = time.time()
        revenue.to_csv("revenue_performance.csv", index=False)
        daily.to_csv("daily_sales_performance.csv", index=False)
        save_time = time.time() - save_start
        
        total_time = time.time() - total_start_time
        logger.info(f"Results saved in {save_time:.2f}s")
        logger.info(f"Pipeline completed successfully in {total_time:.2f}s")
        
        # Performance summary
        print("\n" + "="*60)
        print("PERFORMANCE PIPELINE SUMMARY")
        print("="*60)
        print(f"Total records processed: {len(df):,}")
        print(f"Categories analyzed: {len(revenue)}")
        print(f"Days covered: {len(daily)}")
        print(f"Total processing time: {total_time:.2f}s")
        print(f"Records per second: {len(df)/total_time:.0f}")
        
        print(f"\nTop 5 Categories by Revenue:")
        print(revenue.head().to_string(index=False))
        
        print(f"\nSample Daily Sales:")
        print(daily.head().to_string(index=False))
        
        # Memory efficiency metrics
        final_memory = df.memory_usage(deep=True).sum() / 1024 / 1024
        print(f"\nMemory Usage: {final_memory:.2f} MB")
        print(f"Memory per record: {final_memory * 1024 / len(df):.2f} KB")
        
    except Exception as e:
        logger.error(f"Performance pipeline failed: {e}")
        raise

def compare_performance() -> None:
    """
    Compare performance between basic and optimized pipelines.
    """
    print("\n" + "="*60)
    print("PERFORMANCE COMPARISON")
    print("="*60)
    
    # Test with optimized pipeline
    start_time = time.time()
    run_performance_pipeline("orders_large.csv")
    optimized_time = time.time() - start_time
    
    print(f"\nOptimized Pipeline Time: {optimized_time:.2f}s")
    
    # Performance metrics
    df = pd.read_csv("orders_large.csv")
    print(f"Dataset Size: {len(df):,} records")
    print(f"Dataset Memory (unoptimized): {df.memory_usage(deep=True).sum() / 1024 / 1024:.2f} MB")

if __name__ == "__main__":
    # Run performance comparison
    compare_performance()
