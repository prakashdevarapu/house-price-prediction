"""
Script to generate a benchmark demonstration dataset for House Price Prediction.

This dataset models residential property pricing in Indian urban/suburban markets
based on standard appraisal metrics: Area, Bedrooms, Bathrooms, Floors, and Age.
Seed is fixed for 100% reproducibility.
"""

import numpy as np
import pandas as pd
from pathlib import Path


def generate_housing_data(num_samples: int = 2500, random_seed: int = 42) -> pd.DataFrame:
    np.random.seed(random_seed)

    # 1. Area in square feet (lognormal/clipped to reflect realistic residential stock: 450 - 5500 sq ft)
    area = np.random.normal(loc=1750, scale=650, size=num_samples)
    area = np.clip(area, 500, 5000).round()

    # 2. Bedrooms: correlated with area
    # Roughly: ~1 BHK for < 700 sqft, 2 BHK for 700-1400, 3 BHK for 1400-2400, 4+ for larger
    bedrooms = np.round((area / 650) + np.random.normal(0, 0.4, size=num_samples))
    bedrooms = np.clip(bedrooms, 1, 6).astype(int)

    # 3. Bathrooms: typically <= bedrooms + 1, min 1
    bathrooms = np.round(bedrooms * 0.85 + np.random.normal(0, 0.35, size=num_samples))
    bathrooms = np.clip(bathrooms, 1, 5).astype(int)

    # 4. Floors: 1 to 4 stories (independent house, villa, or duplex/triplex)
    floors = np.random.choice([1, 2, 3, 4], size=num_samples, p=[0.45, 0.35, 0.15, 0.05])

    # 5. Age of property in years (0 = brand new, up to 40 years)
    age = np.random.exponential(scale=10, size=num_samples)
    age = np.clip(age, 0, 40).round(1)

    # 6. Realistic Price Calculation in Indian Rupees (INR)
    # Base intercept: 12,00,000 INR
    # Area rate: ~4,800 INR per sq ft
    # Bedroom premium: 2,80,000 INR per bedroom
    # Bathroom premium: 1,60,000 INR per bathroom
    # Floor premium: 3,40,000 INR per floor
    # Age depreciation: -55,000 INR per year of age
    base_price = (
        1200000
        + (area * 4800)
        + (bedrooms * 280000)
        + (bathrooms * 160000)
        + (floors * 340000)
        - (age * 55000)
    )

    # Add realistic market variance (Gaussian noise ~ 5% - 8% of value)
    noise = np.random.normal(loc=0, scale=280000, size=num_samples)
    price = np.round(base_price + noise)

    # Ensure price does not drop below a sensible minimum for small older properties
    price = np.maximum(price, 1500000)

    df = pd.DataFrame({
        "area_sqft": area.astype(int),
        "bedrooms": bedrooms,
        "bathrooms": bathrooms,
        "floors": floors,
        "age_years": age,
        "price_inr": price.astype(int)
    })

    return df


if __name__ == "__main__":
    output_dir = Path(__file__).resolve().parent
    output_file = output_dir / "housing_data.csv"
    
    print("Generating synthetic residential housing dataset...")
    df = generate_housing_data(num_samples=2500, random_seed=42)
    df.to_csv(output_file, index=False)
    
    print(f"Successfully saved {len(df)} samples to {output_file}")
    print("\nDataset Summary Statistics:")
    print(df.describe().to_string())
