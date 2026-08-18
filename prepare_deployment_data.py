from pathlib import Path
import rasterio
from rasterio.enums import Resampling

BASE_DIR = Path(__file__).resolve().parent

YEARS = [2017, 2020, 2024]

for year in YEARS:
    input_dir = BASE_DIR / str(year)
    output_dir = BASE_DIR / "deployment_data" / str(year)
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"\nProcessing {year}...")

    for band in [2, 3, 4, 5]:
        files = list(input_dir.glob(f"*SR_B{band}.TIF"))

        if not files:
            print(f"❌ B{band} not found")
            continue

        input_file = files[0]
        output_file = output_dir / input_file.name

        print(f"  B{band}: {input_file.name}")

        with rasterio.open(input_file) as src:

            new_width = src.width // 2
            new_height = src.height // 2

            profile = src.profile.copy()
            profile.update(
                width=new_width,
                height=new_height,
                transform=src.transform * src.transform.scale(
                    src.width / new_width,
                    src.height / new_height
                ),
                compress="deflate",
                predictor=2
            )

            with rasterio.open(output_file, "w", **profile) as dst:
                data = src.read(
                    1,
                    out_shape=(new_height, new_width),
                    resampling=Resampling.bilinear
                )

                dst.write(data, 1)

        print(f"  ✅ Saved: {output_file}")

print("\n🎉 Done!")
print(f"Output folder: {BASE_DIR / 'deployment_data'}")