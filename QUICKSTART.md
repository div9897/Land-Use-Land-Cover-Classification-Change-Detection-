# 🚀 Quick Start Guide

## Option 1: Quick Start (Windows - Easiest)

### Step 1: Double-click the batch file
```
run.bat
```
This will:
- Create a virtual environment (if not exists)
- Install all dependencies
- Start the dashboard automatically

The app will open in your browser at `http://localhost:8501`

---

## Option 2: Manual Setup (Windows Command Prompt)

### Step 1: Navigate to project directory
```bash
cd D:\LULC_voice
```

### Step 2: Create virtual environment
```bash
python -m venv venv
```

### Step 3: Activate virtual environment
```bash
venv\Scripts\activate
```

### Step 4: Install dependencies
```bash
pip install -r requirements.txt
```

### Step 5: Run the application
```bash
streamlit run streamlit_app.py
```

---

## Option 3: Using Python directly (MacOS/Linux)

### Step 1: Navigate to project
```bash
cd /path/to/LULC_voice
```

### Step 2: Create and activate environment
```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install and run
```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
```

---

## ✅ Verification

After starting the app, you should see:

```
  You can now view your Streamlit app in your browser.
  
  Local URL: http://localhost:8501
  Network URL: http://xxx.xxx.xxx.xxx:8501
```

Open `http://localhost:8501` in your web browser.

---

## 📊 Dashboard Interface

Once open, you'll see:

### **Sidebar Navigation**
- 🏠 Home
- 📊 Classification Results
- 📈 Year Comparison
- 📍 Change Analysis
- ℹ️ About

### **Main Features**

#### Classification Results
1. Select a year (2017, 2020, 2024)
2. View classification map
3. See percentage distribution
4. Review statistics table

#### Year Comparison
1. Select first year
2. Select second year
3. View comparison charts
4. See change trends and insights

#### Change Analysis
1. Select two years to compare
2. View change detection map
3. Review pixel statistics
4. Analyze change percentages

---

## 🔧 Troubleshooting

### **Problem: "streamlit: command not found"**
**Solution:**
```bash
# Try full path to streamlit
venv\Scripts\streamlit run streamlit_app.py
```

### **Problem: Port 8501 already in use**
**Solution:**
```bash
streamlit run streamlit_app.py --server.port 8502
```

### **Problem: "No module named 'rasterio'"**
**Solution:**
```bash
pip install --upgrade rasterio
```

### **Problem: "No satellite data found"**
**Solution:**
- Verify TIF files exist in `2017/`, `2020/`, `2024/` folders
- Check that files match naming pattern: `*_SR_B2.TIF`, `*_SR_B3.TIF`, etc.
- Ensure files are valid GeoTIFF format

### **Problem: App crashes or runs slowly**
**Solution:**
- Reduce image resolution by editing `streamlit_app.py`:
  ```python
  downscale_factor=0.25  # Lower value = faster
  ```

---

## 📝 Using the Application

### Home Page
- Overview of the project
- Feature highlights
- Available years and land types

### Classification Results
**Steps:**
1. Open "📊 Classification Results"
2. Select year from dropdown
3. Wait for processing (10-30 seconds)
4. View classification map and statistics
5. Review detailed percentage table

**Information displayed:**
- Color-coded classification map
- Bar chart of land cover percentages
- Detailed metrics for each land type
- Data table with rankings

### Year Comparison
**Steps:**
1. Open "📈 Year Comparison"
2. Select first year
3. Select second year (must be different)
4. Wait for analysis
5. Review comparison charts

**Information displayed:**
- Side-by-side bar comparison
- Change magnitude chart
- Comparison table with trends
- Key insights (biggest increases/decreases)

### Change Analysis
**Steps:**
1. Open "📍 Change Analysis"
2. Select first year
3. Select second year
4. Wait for analysis
5. Review change map

**Information displayed:**
- Change detection heatmap (red = change)
- Total pixels analyzed
- Count of changed pixels
- Percentage of area with change

### About
- Complete technical documentation
- Classification methodology
- Land cover class descriptions
- Data sources
- Limitations and future work

---

## ⚡ Performance Tips

### Make it Faster
```python
# In streamlit_app.py, line ~75:
downscale_factor=0.25  # Default 0.5, lower = faster
```

### Make it More Detailed
```python
# In streamlit_app.py, line ~75:
downscale_factor=0.75  # Higher = more detail but slower
```

---

## 🎨 Customization

### Change Colors
Edit `COLORS` list in `streamlit_app.py`:
```python
COLORS = [
    "#228B22",  # Forest (green)
    "#1E90FF",  # Water (blue)
    "#A9A9A9",  # Urban (gray)
    "#7CFC00",  # Grassland (lime)
    "#EDC9AF",  # Desert (tan)
    "#FFD700",  # Cropland (gold)
    "#D2B48C"   # Bare Soil (brown)
]
```

### Change Land Type Names
Edit `LAND_TYPES` dictionary:
```python
LAND_TYPES = {
    0: "Your Name Here",
    1: "...",
    # etc.
}
```

---

## 📊 Expected Output Examples

### Classification Map
- Color-coded image showing 7 land types
- Legend on map
- Same resolution as input data

### Distribution Chart
- Horizontal/vertical bar chart
- Shows percentage for each land type
- Bars colored by land type

### Comparison Chart
- Two bars side-by-side per land type
- Different color for each year
- Easy to spot differences

### Change Map
- Red heatmap showing changes
- Darker red = more change detection
- White = no change

---

## 🔄 Common Workflows

### Workflow 1: Analyze Single Year
1. Open "Classification Results"
2. Select year
3. View map and statistics
4. Review "About" for interpretation help

### Workflow 2: Compare Two Years
1. Open "Year Comparison"
2. Select two years
3. Review comparison bar chart
4. Check largest increases/decreases
5. View change table for details

### Workflow 3: Detect Changes
1. Open "Change Analysis"
2. Select base year
3. Select comparison year
4. View red change map
5. Review statistics

### Workflow 4: Full Analysis
1. View each year individually
2. Compare all year combinations
3. Analyze changes
4. Read "About" for methodology
5. Export/document findings

---

## 💾 Stopping the Application

### Method 1: Keyboard
```
Press Ctrl + C in the terminal
```

### Method 2: Browser
- Close the browser tab (app continues running in terminal)

### Method 3: Terminal
- Type `exit()` and press Enter
- Or close the terminal window

---

## 📚 Additional Resources

### Understanding Satellite Data
- [Landsat Overview](https://www.usgs.gov/faqs/what-are-band-designations-landsat-satellites)
- [NDVI Explanation](https://en.wikipedia.org/wiki/Normalized_difference_vegetation_index)
- [Remote Sensing Basics](https://en.wikipedia.org/wiki/Remote_sensing)

### Getting More Data
- [USGS Earth Explorer](https://earthexplorer.usgs.gov/)
- [Google Earth Engine](https://earthengine.google.com/)
- [Copernicus Hub](https://scihub.copernicus.eu/)

### Learning Streamlit
- [Streamlit Docs](https://docs.streamlit.io/)
- [Streamlit Cheatsheet](https://docs.streamlit.io/library/cheatsheet)

---

## 📞 Support

If you encounter issues:
1. Check the "Troubleshooting" section above
2. Review the README.md file
3. Check that all TIF files exist
4. Verify Python version (3.8+)
5. Try reinstalling dependencies

---

**Enjoy your LULC Classification Dashboard! 🛰️📊**
