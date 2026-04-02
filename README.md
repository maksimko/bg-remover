# Remove Background

Batch background removal tool for images. Uses [rembg](https://github.com/danielgatis/rembg) to remove backgrounds, cleans up white fringe around edges, and auto-crops the result.

## Setup

### 1. Install Python

Download and install Python 3.10+ from [python.org](https://www.python.org/downloads/). During installation, check **"Add Python to PATH"**.

### 2. Create a virtual environment (recommended)

```
python3 -m venv venv
source venv/bin/activate   # macOS/Linux
venv\Scripts\activate      # Windows
```

### 3. Install dependencies

```
pip install "rembg[gpu]" Pillow numpy scipy
```

If you don't have an NVIDIA GPU, use:

```
pip install "rembg[cpu]" Pillow numpy scipy
```

### 4. Prepare images

Place your input images (`.png`, `.jpg`, `.jpeg`) into the `raw_images` folder.

### 5. Run

```
python test.py
```

Processed images will appear in the `processed_images` folder.

## GUI App

`app.py` is a standalone GUI version with folder pickers and configurable settings. Run it with:

```
python app.py
```

## Building a standalone .exe (no Python required for end users)

### 1. Install build dependencies

```
pip install pyinstaller "rembg[cpu]" Pillow numpy scipy
```

### 2. Download the model (if not already cached)

```
python -c "from rembg import new_session; new_session('isnet-general-use')"
```

### 3. Build

```
pyinstaller remove_bg.spec
```

The resulting `RemoveBackground.exe` will be in the `dist` folder. It bundles Python, all dependencies, and the AI model -- no installation needed on the target machine.

## Configuration

You can tune the edge cleanup in `test.py` by editing the `clean_white_edges()` call, or use the settings panel in the GUI app:

- `border_size` (default `3`) -- how many pixels from the edge to clean. Increase if white fringe remains.
- `white_threshold` (default `240`) -- what counts as "white". Lower values clean more aggressively.
