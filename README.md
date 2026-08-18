# 🛰️ Land Use Land Cover (LULC) Classification, Change Detection & Future Prediction

A Machine Learning and Geospatial Analysis project that performs:

- 🌍 Land Use Land Cover (LULC) Classification
- 🔄 Multi-Year Change Detection
- 📊 Percentage & Trend Analysis
- 🔮 Future Land Use Prediction using CA-Markov
- 🖥️ Interactive Streamlit Dashboard

This project uses Landsat satellite imagery and combines MiniBatch K-Means clustering with a Cellular Automata + Markov Chain (CA-Markov) prediction model for environmental monitoring and urban growth analysis.

---

# 📌 Project Overview

Land use patterns continuously change due to:

- Urbanization
- Deforestation
- Agricultural expansion
- Climate change

Manual monitoring of satellite imagery is difficult and time-consuming.

This project automates the entire workflow using Machine Learning and Remote Sensing techniques to:

✅ Classify land cover types  
✅ Detect land changes across years  
✅ Analyze land percentage distribution  
✅ Predict future land use trends  

---

# 🚀 Features

## ✅ LULC Classification

Automatically classifies satellite imagery into:

- Forest
- Water
- Urban
- Grassland
- Desert
- Cropland
- Bare Soil

---

## ✅ Multi-Year Change Detection

Compare land changes between:

- 2017 → 2020
- 2020 → 2024
- 2017 → 2024

Detects:

- Urban expansion
- Vegetation loss
- Land transformation

---

## ✅ NDVI Feature Engineering

Uses:

NDVI = (NIR - Red) / (NIR + Red)

to improve vegetation classification accuracy.

---

## ✅ CA-Markov Future Prediction

Predicts future land cover maps using:

- Transition probabilities
- Spatial neighborhood influence
- Cellular Automata + Markov Chain

---

## ✅ Interactive Streamlit Dashboard

Includes:

- Classification maps
- Change maps
- Comparison charts
- Future prediction interface
- Trend visualization

---

# 🧠 Technologies Used

| Technology | Purpose |
|------------|---------|
| Python | Core programming |
| Rasterio | Satellite image processing |
| NumPy | Numerical operations |
| Scikit-learn | Machine Learning |
| SciPy | Spatial filtering |
| Matplotlib | Visualization |
| Streamlit | Web dashboard |
| Pandas | Data handling |

---

# 📂 Dataset

## Source

- USGS EarthExplorer
- Landsat 8 / Landsat 9 imagery

## Bands Used

| Band | Description |
|------|-------------|
| B2 | Blue |
| B3 | Green |
| B4 | Red |
| B5 | Near Infrared (NIR) |

---

# 🧠 Machine Learning Model

## MiniBatch K-Means Clustering

The project uses MiniBatch K-Means, an optimized version of K-Means designed for large datasets.

### Why MiniBatch K-Means?

✅ Faster than traditional K-Means  
✅ Memory efficient  
✅ Suitable for high-resolution satellite imagery  
✅ Works without labeled data  

---

# 🔬 Project Workflow

```text
Landsat Images
       ↓
Band Extraction
       ↓
NDVI Calculation
       ↓
Feature Stacking
       ↓
MiniBatch K-Means Classification
       ↓
Semantic Label Assignment
       ↓
Change Detection
       ↓
CA-Markov Prediction
       ↓
Visualization & Dashboard
```

---

# 🌱 NDVI Calculation

NDVI helps distinguish vegetation from non-vegetation areas.

```python
ndvi = (nir - red) / (nir + red + 1e-10)
```

---

# 📊 Land Cover Classes

| Class ID | Land Type |
|----------|-----------|
| 0 | Forest |
| 1 | Water |
| 2 | Urban |
| 3 | Grassland |
| 4 | Desert |
| 5 | Cropland |
| 6 | Bare Soil |

---

# 🔄 Change Detection

Pixel-wise comparison is performed between classified images.

```python
change_map = (img1 != img2).astype(np.uint8)
```

This identifies:

- Stable regions
- Changed regions
- Urban growth areas
- Vegetation reduction

---

# 🔮 Future Prediction using CA-Markov

## What is CA-Markov?

CA-Markov combines:

### 🔹 Markov Chain

Models land transition probabilities over time.

### 🔹 Cellular Automata

Adds spatial neighborhood influence.

Together they generate realistic future land cover predictions.

---

# 📈 Prediction Process

1. Compute transition matrix
2. Analyze class conversion probabilities
3. Apply spatial neighborhood rules
4. Generate future land map

---

# 🖥️ Streamlit Dashboard

The project includes a fully interactive dashboard.

## Dashboard Pages

### 🏠 Home

Project overview and workflow

### 📊 Classification Results

View classified maps and statistics

### 📈 Year Comparison

Compare multiple years side-by-side

### 📍 Change Analysis

Visualize land transformation

### 🔮 Future Prediction

Run CA-Markov prediction

### ℹ️ About

Project details and methodology

---

# 📸 Outputs

## Classification Maps

- Multi-year land classification

## Change Maps

- Highlight changed regions

## Bar Charts

- Percentage comparison

## Transition Heatmaps

- Land conversion probabilities

## Trend Graphs

- Area trends across years

---

# 📦 Installation

## Clone Repository

```bash
git clone https://github.com/your-username/LULC_classification.git
cd LULC_classification
```

---

# 📥 Install Dependencies

```bash
pip install -r requirements.txt
```

---

# ▶️ Run Streamlit Dashboard

```bash
streamlit run lulc_app.py
```

---

# 📁 Project Structure

```text
LULC_classification/
│
├── lulc_app.py
├── prediction_model.py
├── requirements.txt
├── README.md
│
├── 2017/
├── 2020/
├── 2024/
│
└── outputs/
```

---

# 📌 Important Notes

- Satellite `.TIF` files are not included due to large size.
- Download Landsat imagery from:
  - https://earthexplorer.usgs.gov/

---

# ⚠️ Limitations

- Limited temporal data
- No ground truth labels
- Unsupervised clustering limitations
- Prediction depends on historical trends

---

# 🚀 Future Scope

- Add more years of data
- Use Random Forest / SVM
- Integrate Deep Learning (CNN/LSTM)
- Real-time monitoring system
- Cloud deployment
- GIS integration

---

# 🎯 Applications

- Urban planning
- Environmental monitoring
- Forest management
- Smart city planning
- Disaster assessment
- Agricultural analysis

---

# 📚 References

- USGS EarthExplorer
- Landsat Documentation
- Scikit-learn Documentation
- Streamlit Documentation
- Remote Sensing Research Papers

---

# 👨‍💻 Author

## Divyansh Sharma

Machine Learning | Remote Sensing | Geospatial Analysis

---

# ⭐ Conclusion

This project demonstrates how Machine Learning and Geospatial Analysis can be combined to:

✅ Classify land cover  
✅ Detect environmental changes  
✅ Predict future land use patterns  

using real satellite imagery and interactive visualization tools.

---

# 🌍 “Understanding Earth Through Data and Machine Learning”
