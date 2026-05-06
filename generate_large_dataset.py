import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

def generate_large_dataset(num_rows: int = 10000) -> pd.DataFrame:
    """
    Generate a large retail dataset for performance testing.
    
    Args:
        num_rows: Number of rows to generate
        
    Returns:
        DataFrame with generated data
    """
    print(f"Generating {num_rows} rows of retail data...")
    
    # Product and category data
    products = [
        'Laptop', 'Phone', 'Tablet', 'Headphones', 'Mouse', 'Keyboard',
        'Monitor', 'Camera', 'Speaker', 'Router', 'Shoes', 'Shirt', 
        'Pants', 'Jacket', 'Hat', 'Watch', 'Bag', 'Belt', 'Sunglasses',
        'Wallet', 'Book', 'Pen', 'Notebook', 'Desk', 'Chair'
    ]
    
    categories = {
        'Electronics': ['Laptop', 'Phone', 'Tablet', 'Headphones', 'Mouse', 'Keyboard', 'Monitor', 'Camera', 'Speaker', 'Router'],
        'Fashion': ['Shoes', 'Shirt', 'Pants', 'Jacket', 'Hat', 'Watch', 'Bag', 'Belt', 'Sunglasses', 'Wallet'],
        'Office': ['Book', 'Pen', 'Notebook', 'Desk', 'Chair']
    }
    
    # Generate data
    np.random.seed(42)  # For reproducibility
    random.seed(42)
    
    data = []
    
    for i in range(num_rows):
        # Generate order ID
        order_id = i + 1
        
        # Generate customer ID (1000-9999)
        customer_id = random.randint(1000, 9999)
        
        # Select product and category
        product = random.choice(products)
        category = 'Electronics' if product in categories['Electronics'] else \
                  'Fashion' if product in categories['Fashion'] else 'Office'
        
        # Generate price based on category
        if category == 'Electronics':
            price = round(random.uniform(50, 2000), 2)
        elif category == 'Fashion':
            price = round(random.uniform(10, 500), 2)
        else:  # Office
            price = round(random.uniform(5, 200), 2)
        
        # Generate quantity (1-5, with higher probability for 1)
        quantity_weights = [0.6, 0.25, 0.1, 0.04, 0.01]  # weights for quantities 1-5
        quantity = random.choices([1, 2, 3, 4, 5], weights=quantity_weights)[0]
        
        # Generate order date (last 365 days)
        start_date = datetime.now() - timedelta(days=365)
        random_days = random.randint(0, 365)
        order_date = (start_date + timedelta(days=random_days)).strftime('%Y-%m-%d')
        
        # Generate discount (0-30% chance)
        discount = round(random.uniform(0, 0.3), 3) if random.random() < 0.3 else 0.0
        
        data.append([order_id, customer_id, product, category, price, quantity, discount, order_date])
    
    # Create DataFrame
    df = pd.DataFrame(data, columns=[
        'order_id', 'customer_id', 'product', 'category', 
        'price', 'quantity', 'discount', 'order_date'
    ])
    
    # Add some duplicates (about 5%)
    duplicate_indices = np.random.choice(len(df), size=int(len(df) * 0.05), replace=False)
    duplicates = df.iloc[duplicate_indices].copy()
    df = pd.concat([df, duplicates], ignore_index=True)
    
    # Add some missing values (about 2% for quantity, 1% for price)
    missing_qty_indices = np.random.choice(len(df), size=int(len(df) * 0.02), replace=False)
    df.loc[missing_qty_indices, 'quantity'] = np.nan
    
    missing_price_indices = np.random.choice(len(df), size=int(len(df) * 0.01), replace=False)
    df.loc[missing_price_indices, 'price'] = np.nan
    
    print(f"Generated dataset with {len(df)} rows")
    print(f"Categories distribution:")
    print(df['category'].value_counts())
    print(f"Missing values: {df.isnull().sum().sum()}")
    print(f"Duplicates: {df.duplicated().sum()}")
    
    return df

if __name__ == "__main__":
    # Generate large dataset
    large_df = generate_large_dataset(10000)
    
    # Save to CSV
    large_df.to_csv("orders_large.csv", index=False)
    print(f"Saved large dataset to orders_large.csv")
    
    # Show sample
    print(f"\nSample data:")
    print(large_df.head())
    print(f"\nData types:")
    print(large_df.dtypes)
    print(f"\nDataset info:")
    print(f"Shape: {large_df.shape}")
    print(f"Memory usage: {large_df.memory_usage(deep=True).sum() / 1024 / 1024:.2f} MB")
