import rasterio
import numpy as np
import matplotlib.pyplot as plt
from sklearn.cluster import MiniBatchKMeans
from scipy.ndimage import zoom
import matplotlib.colors as mcolors

land_types = {
    0: "forest", 1: "water", 2: "urban", 3: "grassland",
    4: "desert", 5: "cropland", 6: "bare soil"
}
colors = [
    "#228B22", "#1E90FF", "#A9A9A9", "#7CFC00",
    "#EDC9AF", "#FFD700", "#D2B48C"
]

def load_landsat_features(band_paths, downscale_factor=0.5):
    bands = []
    for path in band_paths:
        with rasterio.open(path) as src:
            band = src.read(1).astype(float)
            if downscale_factor < 1.0:
                band = zoom(band, downscale_factor, order=1)
            bands.append(band)
    red, nir = bands[2], bands[3]
    ndvi = (nir - red) / (nir + red + 1e-10)
    return np.stack([bands[0], bands[1], bands[2], ndvi], axis=0)

def classify(features):
    pixels = features.reshape(features.shape[0], -1).T
    kmeans = MiniBatchKMeans(n_clusters=7, random_state=42, batch_size=10000, n_init=3)
    labels = kmeans.fit_predict(pixels)
    return labels.reshape(features.shape[1], features.shape[2])

def compute_percentage_summary(classified_image):
    total = classified_image.size
    unique, counts = np.unique(classified_image, return_counts=True)
    return {land_types[i]: round((c / total) * 100, 2) for i, c in zip(unique, counts)}

def compute_change_map(img1, img2):
    if img1.shape != img2.shape:
        img2 = zoom(img2, (img1.shape[0] / img2.shape[0], img1.shape[1] / img2.shape[1]), order=0)
    return (img1 != img2).astype(np.uint8)

def plot_classification(image, title):
    cmap = mcolors.ListedColormap(colors)
    plt.figure(figsize=(8, 8))
    plt.imshow(image, cmap=cmap, interpolation='nearest')
    handles = [plt.Line2D([0], [0], color=colors[i], lw=4, label=land_types[i]) for i in range(7)]
    plt.legend(handles=handles, loc="lower left", fontsize=8)
    plt.title(title)
    plt.axis("off")
    plt.tight_layout()
    plt.show()

def plot_bar_chart(percentages_2020, percentages_2017):
    labels = list(land_types.values())
    vals_2020 = [percentages_2020.get(label, 0) for label in labels]
    vals_2017 = [percentages_2017.get(label, 0) for label in labels]

    x = np.arange(len(labels))
    width = 0.35

    plt.figure(figsize=(10, 6))
    plt.bar(x - width/2, vals_2017, width, label='2017', color='lightblue')
    plt.bar(x + width/2, vals_2020, width, label='2020', color='green')
    plt.xticks(x, labels, rotation=45)
    plt.ylabel("Percentage (%)")
    plt.title("Land Use Percentage Comparison (2017 vs 2020)")
    plt.legend()
    plt.grid(True, axis='y', linestyle='--', alpha=0.5)
    plt.tight_layout()
    plt.show()

def plot_change_bar(percentages_2020, percentages_2017):
    labels = list(land_types.values())
    vals_2020 = [percentages_2020.get(label, 0) for label in labels]
    vals_2017 = [percentages_2017.get(label, 0) for label in labels]
    change = [round(v20 - v17, 2) for v20, v17 in zip(vals_2020, vals_2017)]

    colors_change = ['green' if c >= 0 else 'red' for c in change]

    plt.figure(figsize=(10, 6))
    plt.bar(labels, change, color=colors_change)
    plt.axhline(0, color='black', linewidth=0.8)
    plt.title("Change in Land Use Percentage (2020 - 2017)")
    plt.ylabel("Percentage Change (%)")
    plt.xticks(rotation=45)
    plt.grid(True, axis='y', linestyle='--', alpha=0.5)
    plt.tight_layout()
    plt.show()

def plot_change_map(change_map):
    plt.figure(figsize=(8, 8))
    plt.imshow(change_map, cmap='Reds')
    plt.title("Change Map (Red = Change)")
    plt.colorbar()
    plt.axis("off")
    plt.tight_layout()
    plt.show()

def main():
    print("🔄 Loading images with downsampling (50%)...")
    band_paths_2020 = [
        "D:\\python\\2020\LC08_L2SP_140047_20150101_20200910_02_T2_SR_B2.TIF",
        "D:\\python\\2020\LC08_L2SP_140047_20150101_20200910_02_T2_SR_B3.TIF",
        "D:\\python\\2020\LC08_L2SP_140047_20150101_20200910_02_T2_SR_B4.TIF",
        "D:\\python\\2020\LC08_L2SP_140047_20150101_20200910_02_T2_SR_B5.TIF"
    ]
    band_paths_2017 = [
        "D:\\python\\2017\LC08_L2SP_140047_20170428_20200904_02_T1_SR_B2.TIF",
        "D:\\python\\2017\LC08_L2SP_140047_20170428_20200904_02_T1_SR_B3.TIF",
        "D:\\python\\2017\LC08_L2SP_140047_20170428_20200904_02_T1_SR_B4.TIF",
        "D:\\python\\2017\LC08_L2SP_140047_20170428_20200904_02_T1_SR_B5.TIF"
    ]
    features_2020 = load_landsat_features(band_paths_2020, downscale_factor=0.5)
    features_2017 = load_landsat_features(band_paths_2017, downscale_factor=0.5)

    print("🔍 Classifying images...")
    classified_2020 = classify(features_2020)
    classified_2017 = classify(features_2017)

    print("🧮 Performing change detection...")
    change_map = compute_change_map(classified_2020, classified_2017)

    print("\n📊 Land Use Percentages:")
    perc_2020 = compute_percentage_summary(classified_2020)
    perc_2017 = compute_percentage_summary(classified_2017)

    print("🔹 2020:")
    for k, v in perc_2020.items():
        print(f"{k}: {v}%")
    print("🔹 2017:")
    for k, v in perc_2017.items():
        print(f"{k}: {v}%")

    print("\n🖼️ Displaying visualizations...")
    plot_classification(classified_2020, "Land Use Classification - 2020")
    plot_classification(classified_2017, "Land Use Classification - 2017")

    plot_bar_chart(perc_2020, perc_2017)
    plot_change_bar(perc_2020, perc_2017)

    plot_change_map(change_map)

if __name__ == "__main__":
    main()
