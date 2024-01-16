```markdown
# TileClipper Downloader

This Streamlit app provides map visualization and bounding box drawing capabilities, allowing users to draw polygons on a map, clip tiles, and download the results.

## Features

- Map Visualization: Use Folium to display maps and draw polygons on them.
- Bounding Box Drawing: Draw polygons and obtain the corresponding bounding box (bbox) coordinates.
- Tile Clipping: Clip tiles based on the drawn bounding box.
- Zip Download: Download the clipped tiles as a zip file.

## Installation

1. Clone the repository:

```bash
git clone <your-repository-url>
cd <repository-folder>
```

2. Create and activate a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Linux/Mac
# or
venv\Scripts\activate  # On Windows
```

3. Install the required packages:

```bash
pip install -r requirements.txt
```

## Usage

Run the Streamlit app:

```bash
streamlit run app.py
```

Visit the Streamlit app in your browser and use the sidebar to draw polygons, input tile URLs, and generate tiles.

## Contributors

- Deepak Pradhan
- Sijan Dhungana

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details.
```
