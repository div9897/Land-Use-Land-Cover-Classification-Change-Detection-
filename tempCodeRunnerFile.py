import rasterio
import numpy as np
from sklearn.cluster import KMeans
import pyttsx3
import os
import matplotlib.pyplot as plt
from rasterio.merge import merge

# Optional imports for voice input
try:
    import speech_recognition as sr
    VOICE_AVAILABLE = True 
except ImportError:
    VOICE_AVAILABLE = False

# Global variables to store the last classified coordinates, stats, and land type
last_x = None
last_y = None
last_stats = None
last_land_type = None

# Function to merge multiple TIFF files
def merge_tiff_files(tiff_files):
    try: 
        src_files = [rasterio.open(f) for f in tiff_files]
        mosaic, out_transform = merge(src_files)
        out_meta = src_files[0].meta.copy()
        out_meta.update({"height": mosaic.shape[1], "width": mosaic.shape[2], "transform": out_transform})
        merged_path = "D:\\LULC_voice\\merged_image.tif"
        with rasterio.open(merged_path, "w", **out_meta) as dest:
            dest.write(mosaic)
        for src in src_files:
            src.close()
        print("TIFF files merged successfully into 'merged_image.tif'!")
        return merged_path
    except Exception as e:
        print(f"Error merging TIFF files: {e}. Proceeding with single file or fake data.")
        return tiff_files[0] if tiff_files else None

# Function to load and classify an image with preprocessing
def classify_image(image_path):
    try:
        with rasterio.open(image_path) as src:
            image = src.read()
            image = image / (image.max() + 1e-10)
            if image.shape[0] > 3:
                red = image[0].astype(float)
                nir = image[3].astype(float)
                ndvi = (nir - red) / (nir + red + 1e-10)
                features = np.stack([image[0], image[1], image[2], ndvi], axis=0)
            else:
                features = image
            pixels = features.reshape(features.shape[0], -1).T
            kmeans = KMeans(n_clusters=7, random_state=42)
            labels = kmeans.fit_predict(pixels)
            classified_image = labels.reshape(features.shape[1], features.shape[2])
            print("Classification successful!")
            return classified_image
    except Exception as e:
        print(f"Error loading image: {e}. Using fake data instead.")
        image = np.random.randint(0, 255, (3, 10, 10))
        pixels = image.reshape(3, -1).T
        kmeans = KMeans(n_clusters=7, random_state=42)
        labels = kmeans.fit_predict(pixels)
        return labels.reshape(10, 10)

# Voice output function using pyttsx3
def speak(text):
    try:
        engine = pyttsx3.init()
        engine.say(text)
        engine.runAndWait()
        print(f"Spoke: {text}")
    except Exception as e:
        print(f"Error in voice output: {e}")

# Voice input function
def listen_command():
    if not VOICE_AVAILABLE:
        print("Voice input not available. Install 'speechrecognition' and 'pyaudio'.")
        return None
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Say something (e.g., 'classify', 'stats', 'save', 'exit')...")
        recognizer.adjust_for_ambient_noise(source, duration=1)
        audio = recognizer.listen(source, timeout=5)
        try:
            command = recognizer.recognize_google(audio).lower()
            print(f"You said: {command}")
            return command
        except sr.UnknownValueError:
            print("Sorry, I didn’t understand.")
            return None
        except sr.RequestError:
            print("Couldn’t connect to the speech service.")
            return None
        except sr.WaitTimeoutError:
            print("Timed out waiting for input.")
            return None

# Text input function
def text_command():
    return input("Enter command (e.g., 'classify', 'stats', 'save', 'exit'): ").lower()

# Function to choose input mode
def choose_input_mode():
    print("Choose input mode:")
    print("1. Voice input (requires microphone and additional libraries)")
    print("2. Text input (type commands)")
    while True:
        mode = input("Enter 1 or 2: ").strip()
        if mode == "1" and VOICE_AVAILABLE:
            print("Voice assistant ready! Say 'classify', 'stats', 'save', or 'exit'.")
            speak("Voice assistant ready! Say classify, stats, save, or exit.")
            return listen_command
        elif mode == "2" or (mode == "1" and not VOICE_AVAILABLE):
            if mode == "1" and not VOICE_AVAILABLE:
                print("Voice input unavailable. Switching to text mode.")
            print("Text assistant ready! Type 'classify', 'stats', 'save', 'exit'.")
            speak("Text assistant ready! Type classify, stats, save, or exit.")
            return text_command
        else:
            print("Invalid choice. Please enter 1 or 2.")

# Function to save classified image as TIFF and show it with coordinates, stats, and land type
def save_as_tiff(classified_image, original_path, output_path="D:\\LULC_voice\\classified.tif"):
    global last_x, last_y, last_stats, last_land_type
    try:
        with rasterio.open(original_path) as src:
            meta = src.meta.copy()
            meta.update(count=1, dtype='uint8')
        with rasterio.open(output_path, "w", **meta) as dest:
            dest.write(classified_image.astype(np.uint8), 1)
        print(f"Classified map saved as {output_path}!")

        with rasterio.open(output_path) as saved_src:
            saved_image = saved_src.read(1)
            plt.figure(figsize=(10, 10))
            plt.imshow(saved_image, cmap='viridis')
            plt.title("Saved Classified Map")
            plt.colorbar(label="Land Type")
            
            # Annotate last classified coordinates and land type if available
            if last_x is not None and last_y is not None and last_land_type is not None:
                plt.scatter(last_x, last_y, color='red', s=100, 
                            label=f'Last Classified: ({last_x}, {last_y}) - {last_land_type}')
            
            # Display stats if available
            if last_stats is not None:
                stats_text = "Land Type Distribution:\n" + "\n".join(f"{k}: {v} pixels" for k, v in last_stats.items())
                plt.text(0.05, 0.95, stats_text, transform=plt.gca().transAxes, 
                         fontsize=10, verticalalignment='top', bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
            
            if last_x is not None or last_stats is not None:
                plt.legend()
            plt.show()
    except Exception as e:
        print(f"Error saving or showing TIFF: {e}")

# Main program
def main():
    global last_x, last_y, last_stats, last_land_type
    tiff_files = ["D:\\LULC_voice\\image_2019-10-01_2020-10-01.tif"]
    if len(tiff_files) > 1:
        image_path = merge_tiff_files(tiff_files)
    else:
        image_path = tiff_files[0]

    classified_image = classify_image(image_path)
    land_types = {0: "forest", 1: "water", 2: "urban", 3: "grassland", 
                  4: "desert", 5: "cropland", 6: "bare soil"}

    plt.imshow(classified_image, cmap='viridis')
    plt.title("LULC Classification Map")
    plt.colorbar(label="Land Type")
    plt.show()

    get_command = choose_input_mode()

    while True:
        command = get_command()
        if command:
            if "classify" in command:
                try:
                    x = int(input("Enter x coordinate: "))
                    y = int(input("Enter y coordinate: "))
                    if 0 <= x < classified_image.shape[1] and 0 <= y < classified_image.shape[0]:
                        label = classified_image[y, x]
                        result = f"Area at ({x}, {y}) is classified as {land_types[label]}."
                        # Store the coordinates and land type
                        last_x = x
                        last_y = y
                        last_land_type = land_types[label]
                    else:
                        result = "Invalid coordinates!"
                except ValueError:
                    result = "Please enter valid numbers for coordinates!"
                print(result)
                speak(result)
            elif "stats" in command:
                unique, counts = np.unique(classified_image, return_counts=True)
                stats = dict(zip([land_types[u] for u in unique], counts))
                last_stats = stats
                result = "Land type distribution: " + ", ".join(f"{k}: {v} pixels" for k, v in stats.items())
                print(result)
                speak(result)
            elif "save" in command:
                save_as_tiff(classified_image, image_path)
                speak("Classification saved as TIFF and displayed!")
            elif "exit" in command:
                print("Shutting down...")
                speak("Classification Completed")
                break
            else:
                print("I can only understand 'classify', 'stats', 'save', or 'exit'.")
                speak("I can only understand classify, stats, save, or exit.")

if __name__ == "__main__":
    main()