import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import rasterio
from rasterio.merge import merge
from sklearn.cluster import MiniBatchKMeans
from scipy.ndimage import zoom
import os
from pathlib import Path

# Page configuration
st.set_page_config(
    page_title="LULC Classification Dashboard",
    page_icon="🛰️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main {
        padding: 0rem 0rem;
    }
    .metric-container {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
    }
    </style>
    """, unsafe_allow_html=True)

# Constants
LAND_TYPES = {
    0: "Forest", 1: "Water", 2: "Urban", 3: "Grassland",
    4: "Desert", 5: "Cropland", 6: "Bare Soil"
}

COLORS = [
    "#228B22", "#1E90FF", "#A9A9A9", "#7CFC00",
    "#EDC9AF", "#FFD700", "#D2B48C"
]

PROJECT_ROOT = Path(__file__).resolve().parent / "deployment_data"

# Sidebar configuration
st.sidebar.markdown("# 🛰️ LULC Classification")
st.sidebar.markdown("---")

page = st.sidebar.radio(
    "Select Page",
    ["🏠 Home", "📊 Classification Results", "📈 Year Comparison", "📍 Change Analysis", "ℹ️ About"]
)

# Utility functions
@st.cache_resource
def load_band_files(year):
    """Load band files for a given year"""
    year_path = PROJECT_ROOT / str(year)
    if not year_path.exists():
        return None
    
    bands = {}
    for band_num in [2, 3, 4, 5]:
        files = list(year_path.glob(f"*SR_B{band_num}.TIF"))
        if files:
            bands[band_num] = str(files[0])
    
    return bands if len(bands) == 4 else None

@st.cache_data
def load_landsat_features(band_paths, downscale_factor=0.5):
    """Load Landsat bands and compute NDVI"""
    bands = []
    for band_num in [2, 3, 4, 5]:
        if band_num in band_paths:
            with rasterio.open(band_paths[band_num]) as src:
                band = src.read(1).astype(float)
                if downscale_factor < 1.0:
                    band = zoom(band, downscale_factor, order=1)
                bands.append(band)
    
    if len(bands) < 4:
        return None
    
    red, nir = bands[2], bands[3]
    ndvi = (nir - red) / (nir + red + 1e-10)
    return np.stack([bands[0], bands[1], bands[2], ndvi], axis=0)

@st.cache_data
def classify_image(features):
    """Classify image using KMeans clustering"""
    pixels = features.reshape(features.shape[0], -1).T
    kmeans = MiniBatchKMeans(n_clusters=7, random_state=42, batch_size=10000, n_init=3)
    labels = kmeans.fit_predict(pixels)
    return labels.reshape(features.shape[1], features.shape[2])

def compute_percentage_summary(classified_image):
    """Compute percentage of each land type"""
    total = classified_image.size
    unique, counts = np.unique(classified_image, return_counts=True)
    return {LAND_TYPES[i]: round((c / total) * 100, 2) for i, c in zip(unique, counts)}

def compute_change_map(img1, img2):
    """Compute change map between two images"""
    if img1.shape != img2.shape:
        img2 = zoom(img2, (img1.shape[0] / img2.shape[0], img1.shape[1] / img2.shape[1]), order=0)
    return (img1 != img2).astype(np.uint8)

def plot_classification(image, title="Classification Map"):
    """Plot classification with legend"""
    cmap = mcolors.ListedColormap(COLORS)
    fig, ax = plt.subplots(figsize=(10, 8))
    im = ax.imshow(image, cmap=cmap, interpolation='nearest')
    handles = [plt.Line2D([0], [0], color=COLORS[i], lw=4, label=LAND_TYPES[i]) for i in range(7)]
    ax.legend(handles=handles, loc="upper left", fontsize=10)
    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.axis("off")
    plt.tight_layout()
    return fig

def plot_percentage_bar(percentages, title="Land Cover Distribution"):
    """Plot percentage bar chart"""
    fig, ax = plt.subplots(figsize=(10, 6))
    labels = list(LAND_TYPES.values())
    values = [percentages.get(label, 0) for label in labels]
    bars = ax.bar(labels, values, color=COLORS, edgecolor='black', linewidth=1.5)
    
    # Add value labels on bars
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.1f}%', ha='center', va='bottom', fontsize=10, fontweight='bold')
    
    ax.set_ylabel("Percentage (%)", fontsize=12)
    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.set_ylim(0, max(values) * 1.15)
    plt.xticks(rotation=45, ha='right')
    plt.grid(True, axis='y', linestyle='--', alpha=0.3)
    plt.tight_layout()
    return fig

def plot_comparison_bars(perc1, perc2, year1, year2):
    """Plot comparison bar chart"""
    fig, ax = plt.subplots(figsize=(12, 6))
    labels = list(LAND_TYPES.values())
    vals1 = [perc1.get(label, 0) for label in labels]
    vals2 = [perc2.get(label, 0) for label in labels]
    
    x = np.arange(len(labels))
    width = 0.35
    
    bars1 = ax.bar(x - width/2, vals1, width, label=f'{year1}', color='lightblue', edgecolor='black', linewidth=1.5)
    bars2 = ax.bar(x + width/2, vals2, width, label=f'{year2}', color='green', edgecolor='black', linewidth=1.5)
    
    ax.set_ylabel("Percentage (%)", fontsize=12)
    ax.set_title(f"Land Cover Comparison: {year1} vs {year2}", fontsize=14, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=45, ha='right')
    ax.legend(fontsize=11)
    ax.grid(True, axis='y', linestyle='--', alpha=0.3)
    plt.tight_layout()
    return fig

def plot_change_bar(perc1, perc2, year1, year2):
    """Plot change in land cover"""
    fig, ax = plt.subplots(figsize=(12, 6))
    labels = list(LAND_TYPES.values())
    vals1 = [perc1.get(label, 0) for label in labels]
    vals2 = [perc2.get(label, 0) for label in labels]
    change = [round(v2 - v1, 2) for v2, v1 in zip(vals2, vals1)]
    
    colors_change = ['green' if c >= 0 else 'red' for c in change]
    
    bars = ax.bar(labels, change, color=colors_change, edgecolor='black', linewidth=1.5)
    
    # Add value labels
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.1f}%', ha='center', va='bottom' if height >= 0 else 'top', fontsize=10, fontweight='bold')
    
    ax.axhline(0, color='black', linewidth=1.5)
    ax.set_ylabel("Percentage Change (%)", fontsize=12)
    ax.set_title(f"Change in Land Cover: {year2} - {year1}", fontsize=14, fontweight='bold')
    ax.set_xticklabels(labels, rotation=45, ha='right')
    ax.grid(True, axis='y', linestyle='--', alpha=0.3)
    plt.tight_layout()
    return fig

def plot_change_map(change_map, title="Change Detection Map"):
    """Plot change map"""
    fig, ax = plt.subplots(figsize=(10, 8))
    im = ax.imshow(change_map, cmap='RdYlGn_r', interpolation='nearest', vmin=0, vmax=1)
    ax.set_title(title, fontsize=14, fontweight='bold')
    cbar = plt.colorbar(im, ax=ax, label='Change Detected')
    ax.axis("off")
    plt.tight_layout()
    return fig

# Home Page
if page == "🏠 Home":
    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown("# 🛰️ Land Use/Land Cover Classification")
        st.markdown("### Satellite Image Analysis Dashboard")
    with col2:
        st.image("https://images.unsplash.com/photo-1446776653964-20c1d3a81b06?w=400", use_column_width=True)
    
    st.markdown("---")
    
    st.markdown("""
    ## About This Project
    
    This dashboard analyzes **satellite imagery** from Landsat satellites to classify land cover types 
    and track changes over time.
    
    ### Key Features:
    - 🎯 **7 Land Type Classification**: Forest, Water, Urban, Grassland, Desert, Cropland, Bare Soil
    - 📊 **Multi-Year Analysis**: Compare classifications across different years
    - 📈 **Statistical Summaries**: View percentage distribution and trends
    - 🗺️ **Change Detection**: Identify areas where land cover has changed
    - 🛰️ **Satellite Data**: Uses Landsat 8 and 9 data with spectral band analysis
    
    ### How It Works:
    1. **Data Loading**: Loads multispectral Landsat satellite bands
    2. **Feature Extraction**: Computes NDVI (Normalized Difference Vegetation Index)
    3. **Classification**: Uses K-Means clustering to classify pixels into 7 land types
    4. **Analysis**: Generates statistics and comparisons across years
    5. **Visualization**: Creates detailed maps and charts
    
    ### Technology Stack:
    - **Rasterio**: Geospatial data handling
    - **Scikit-learn**: Machine learning classification
    - **Matplotlib**: Data visualization
    - **Streamlit**: Interactive dashboard
    """)
    
    st.markdown("---")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.info("📁 **Available Years**: 2017, 2020, 2024")
    with col2:
        st.success("🎯 **Land Types**: 7 Classes")
    with col3:
        st.warning("🔧 **Status**: Active")

# Classification Results Page
elif page == "📊 Classification Results":
    st.title("📊 Classification Results")
    
    col1, col2 = st.columns(2)
    with col1:
        selected_year = st.selectbox("Select Year", [2017, 2020, 2024], key="year_select")
    
    if selected_year:
        st.markdown(f"### Analysis for {selected_year}")
        
        # Load and classify
        with st.spinner(f"Loading satellite data for {selected_year}..."):
            bands = load_band_files(selected_year)
            if bands:
                features = load_landsat_features(bands, downscale_factor=0.5)
                if features is not None:
                    classified = classify_image(features)
                    percentages = compute_percentage_summary(classified)
                    
                    # Display results
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.subheader("Classification Map")
                        fig = plot_classification(classified, f"Land Cover Classification - {selected_year}")
                        st.pyplot(fig, use_container_width=True)
                    
                    with col2:
                        st.subheader("Land Cover Distribution")
                        fig = plot_percentage_bar(percentages)
                        st.pyplot(fig, use_container_width=True)
                    
                    # Detailed statistics
                    st.markdown("### Detailed Statistics")
                    
                    cols = st.columns(4)
                    sorted_items = sorted(percentages.items(), key=lambda x: x[1], reverse=True)
                    
                    for idx, (land_type, percentage) in enumerate(sorted_items):
                        with cols[idx % 4]:
                            st.metric(
                                land_type,
                                f"{percentage}%",
                                delta=f"{percentage:.2f}% of total area"
                            )
                    
                    # Data table
                    st.markdown("### Statistics Table")
                    import pandas as pd
                    df = pd.DataFrame([
                        {"Land Type": k, "Percentage (%)": v} 
                        for k, v in sorted(percentages.items(), key=lambda x: x[1], reverse=True)
                    ])
                    st.dataframe(df, use_container_width=True)
                else:
                    st.error("Failed to load and process satellite imagery.")
            else:
                st.error(f"No satellite data found for {selected_year}")

# Year Comparison Page
elif page == "📈 Year Comparison":
    st.title("📈 Year-to-Year Comparison")
    
    col1, col2 = st.columns(2)
    with col1:
        year1 = st.selectbox("Select First Year", [2017, 2020, 2024], index=0)
    with col2:
        year2 = st.selectbox("Select Second Year", [2017, 2020, 2024], index=2)
    
    if year1 != year2:
        with st.spinner(f"Loading and processing data for {year1} and {year2}..."):
            # Load first year
            bands1 = load_band_files(year1)
            features1 = load_landsat_features(bands1, downscale_factor=0.5) if bands1 else None
            
            # Load second year
            bands2 = load_band_files(year2)
            features2 = load_landsat_features(bands2, downscale_factor=0.5) if bands2 else None
            
            if features1 is not None and features2 is not None:
                classified1 = classify_image(features1)
                classified2 = classify_image(features2)
                perc1 = compute_percentage_summary(classified1)
                perc2 = compute_percentage_summary(classified2)
                
                # Comparison chart
                st.subheader("Land Cover Comparison")
                fig = plot_comparison_bars(perc1, perc2, year1, year2)
                st.pyplot(fig, use_container_width=True)
                
                # Change chart
                st.subheader("Change Analysis")
                fig = plot_change_bar(perc1, perc2, year1, year2)
                st.pyplot(fig, use_container_width=True)
                
                # Detailed comparison
                st.markdown("### Detailed Comparison Table")
                import pandas as pd
                
                comparison_data = []
                for land_type in LAND_TYPES.values():
                    v1 = perc1.get(land_type, 0)
                    v2 = perc2.get(land_type, 0)
                    change = v2 - v1
                    comparison_data.append({
                        "Land Type": land_type,
                        f"{year1} (%)": v1,
                        f"{year2} (%)": v2,
                        "Change (%)": round(change, 2),
                        "Trend": "📈 Increase" if change > 0 else ("📉 Decrease" if change < 0 else "➡️ No Change")
                    })
                
                df = pd.DataFrame(comparison_data)
                st.dataframe(df, use_container_width=True)
                
                # Key insights
                st.markdown("### Key Insights")
                col1, col2, col3, col4 = st.columns(4)
                
                largest_increase = max([(lt, perc2.get(lt, 0) - perc1.get(lt, 0)) 
                                       for lt in LAND_TYPES.values()], key=lambda x: x[1])
                largest_decrease = min([(lt, perc2.get(lt, 0) - perc1.get(lt, 0)) 
                                       for lt in LAND_TYPES.values()], key=lambda x: x[1])
                
                with col1:
                    st.success(f"📈 Biggest Increase: {largest_increase[0]} ({largest_increase[1]:+.2f}%)")
                with col2:
                    st.error(f"📉 Biggest Decrease: {largest_decrease[0]} ({largest_decrease[1]:+.2f}%)")
                with col3:
                    total_change = abs(sum(perc2.values()) - sum(perc1.values()))
                    st.info(f"🔄 Overall Change: {total_change:.2f}%")
                with col4:
                    years_diff = year2 - year1
                    st.metric("Year Difference", f"{years_diff} years")
            else:
                st.error(f"Could not load data for the selected years")
    else:
        st.warning("Please select two different years for comparison.")

# Change Analysis Page
elif page == "📍 Change Analysis":
    st.title("📍 Change Detection Analysis")
    
    col1, col2 = st.columns(2)
    with col1:
        year1 = st.selectbox("Select First Year", [2017, 2020, 2024], index=0, key="change_year1")
    with col2:
        year2 = st.selectbox("Select Second Year", [2017, 2020, 2024], index=2, key="change_year2")
    
    if year1 != year2:
        with st.spinner("Computing change detection..."):
            bands1 = load_band_files(year1)
            bands2 = load_band_files(year2)
            
            features1 = load_landsat_features(bands1, downscale_factor=0.5) if bands1 else None
            features2 = load_landsat_features(bands2, downscale_factor=0.5) if bands2 else None
            
            if features1 is not None and features2 is not None:
                classified1 = classify_image(features1)
                classified2 = classify_image(features2)
                
                # Align dimensions
                if classified1.shape != classified2.shape:
                    classified2 = zoom(classified2, 
                                      (classified1.shape[0] / classified2.shape[0], 
                                       classified1.shape[1] / classified2.shape[1]), order=0)
                
                change_map = compute_change_map(classified1, classified2)
                
                # Display change map
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader("Change Detection Map")
                    fig = plot_change_map(change_map, f"Change Detection: {year1} vs {year2}")
                    st.pyplot(fig, use_container_width=True)
                
                with col2:
                    st.subheader("Change Statistics")
                    total_pixels = change_map.size
                    changed_pixels = np.sum(change_map)
                    unchanged_pixels = total_pixels - changed_pixels
                    change_percentage = (changed_pixels / total_pixels) * 100
                    
                    st.metric("Total Pixels Analyzed", f"{total_pixels:,}")
                    st.metric("Pixels with Change", f"{changed_pixels:,} ({change_percentage:.2f}%)")
                    st.metric("Stable Pixels", f"{unchanged_pixels:,} ({100-change_percentage:.2f}%)")
                
                # Additional info
                st.info(
                    f"🗺️ **Interpretation**: Red areas show locations where land cover "
                    f"classification changed between {year1} and {year2}. "
                    f"Higher intensity indicates change detection areas."
                )
            else:
                st.error("Could not load data for change detection")
    else:
        st.warning("Please select two different years for change analysis.")

# About Page
elif page == "ℹ️ About":
    st.title("ℹ️ About This Project")
    
    st.markdown("""
    ## Project Overview
    
    The **Land Use/Land Cover (LULC) Classification** project is designed to analyze satellite imagery
    and automatically classify different types of land cover across temporal periods.
    
    ### Objectives
    - Monitor changes in land use over time
    - Identify areas of significant land cover change
    - Provide statistical analysis of land cover distribution
    - Support environmental and urban planning decisions
    
    ### Data Sources
    
    This project utilizes satellite data from:
    - **Landsat 8**: Operational Land Imager (OLI)
    - **Landsat 9**: Continuation of Landsat 8 with improved sensors
    
    #### Spectral Bands Used:
    - **Band 2 (Blue)**: Coastal/Aerosol (0.43-0.45 µm)
    - **Band 3 (Green)**: Visible light (0.53-0.59 µm)
    - **Band 4 (Red)**: Visible light (0.64-0.67 µm)
    - **Band 5 (NIR)**: Near-Infrared (0.85-0.88 µm)
    
    ### Classification Methodology
    
    1. **Data Preprocessing**
       - Load multispectral bands at 30m resolution
       - Normalize reflectance values
       - Downscale for computational efficiency
    
    2. **Feature Engineering**
       - Compute NDVI (Normalized Difference Vegetation Index)
       - Stack bands with NDVI for classification features
    
    3. **Unsupervised Classification**
       - K-Means clustering (k=7)
       - MiniBatch gradient descent for efficiency
       - 7 land cover classes identified
    
    4. **Post-Processing**
       - Calculate percentage distribution
       - Generate change detection maps
       - Compute temporal comparisons
    
    ### Land Cover Classes
    
    | Class | Description | Color | Indicators |
    |-------|-------------|-------|-----------|
    | Forest | Dense vegetation | 🟢 Green | High NDVI, dense trees |
    | Water | Water bodies | 🔵 Blue | Reflective surfaces |
    | Urban | Built-up areas | ⚫ Gray | Hard surfaces, buildings |
    | Grassland | Open grass/shrub | 🟡 Yellow-Green | Medium NDVI |
    | Desert | Arid regions | 🟫 Tan | Low NDVI, bare soil |
    | Cropland | Agricultural areas | 🟨 Gold | Regular patterns, seasonal |
    | Bare Soil | Exposed soil | 🟤 Brown | Minimal vegetation |
    
    ### Technical Stack
    
    **Libraries & Tools:**
    - `rasterio`: GeoTIFF file I/O and processing
    - `numpy`: Numerical array operations
    - `scikit-learn`: Machine learning algorithms
    - `matplotlib`: Data visualization
    - `scipy`: Scientific computing
    - `streamlit`: Interactive web interface
    
    ### Key Advantages
    
    ✅ **Automated Analysis** - No manual classification needed
    
    ✅ **Multi-temporal** - Track changes over years
    
    ✅ **High Resolution** - 30m pixel resolution
    
    ✅ **Comprehensive** - Covers large geographical areas
    
    ✅ **Scientifically Grounded** - Uses spectral indices like NDVI
    
    ### Limitations & Future Work
    
    ⚠️ **Cloud Cover** - Satellite imagery affected by cloud cover
    
    ⚠️ **Seasonal Variation** - Image dates matter for accuracy
    
    ⚠️ **Resolution** - 30m pixels may miss fine-scale features
    
    **Future Enhancements:**
    - Supervised classification with training data
    - Integration of additional spectral indices (EVI, BSI, NDMI)
    - Cloud masking and atmospheric correction
    - Real-time monitoring dashboard
    - Export capabilities for GIS software
    
    ### Data Availability
    
    Landsat imagery is freely available from:
    - [USGS Earth Explorer](https://earthexplorer.usgs.gov/)
    - [Google Earth Engine](https://earthengine.google.com/)
    
    ### Contact & Support
    
    For questions or suggestions about this project, please refer to the project documentation.
    """)
    
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: gray; padding: 20px;">
    <p>🛰️ LULC Classification Dashboard v1.0</p>
    <p>Built with Streamlit & Open GIS Tools</p>
    </div>
    """, unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown(
    """
    <div style="text-align: center; color: gray; font-size: 0.8rem; padding: 10px;">
    Land Use/Land Cover Classification Dashboard | Powered by Streamlit & Geospatial Analysis
    </div>
    """,
    unsafe_allow_html=True
)
