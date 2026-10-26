# Housing Dataset Documentation

## Overview & Transparency Notice

> **Important Academic / Demonstration Notice**:
> This dataset (`housing_data.csv`) is a benchmark **demonstration dataset** specifically generated for academic, educational, and prototyping purposes. While the distributions, correlations, and valuation rules mirror real-world Indian urban residential property metrics, the data is synthetic. Its predictions should be interpreted as **illustrative approximations** rather than certified real-estate appraisals.

---

## Dataset Schema

The dataset contains **2,500 observations** across 5 independent predictor variables and 1 target variable:

| Column Name | Data Type | Units / Range | Description |
| :--- | :--- | :--- | :--- |
| `area_sqft` | Integer | 500 – 4,500 sq ft | Total built-up / carpet area of the residence. |
| `bedrooms` | Integer | 1 – 6 BHK | Number of dedicated bedrooms. |
| `bathrooms` | Integer | 1 – 5 | Number of completed bathrooms. |
| `floors` | Integer | 1 – 4 | Number of stories/floors of the structure. |
| `age_years` | Float | 0.0 – 40.0 years | Age of the property since construction (0 = brand new). |
| `price_inr` | Integer | ₹23,95,000 – ₹2,45,50,000 | Property sale price in Indian Rupees (target variable). |

---

## Methodology & Feature Relations

The synthetic values were generated using standard economic valuation logic combined with stochastic market variance:
- **Base Intercept**: Baseline land and infrastructure cost foundation (~₹12,00,000).
- **Area Rate**: Positive linear weight (~₹4,800 / sq ft).
- **Bedrooms**: Incremental amenity premium (~₹2,80,000 / room).
- **Bathrooms**: Plumbing, fixtures, and sanitary premium (~₹1,60,000 / bathroom).
- **Floors**: Multi-story vertical build and terrace utility (~₹3,40,000 / floor).
- **Age Depreciation**: Linear structural depreciation (-₹55,000 / year).
- **Market Noise**: Zero-centered Gaussian error ($\sigma \approx ₹2,80,000$) simulating negotiation swings, view quality, and micro-location variations.

---

## Regenerating the Data

To regenerate or adjust parameters:

```bash
python data/generate_dataset.py
```
