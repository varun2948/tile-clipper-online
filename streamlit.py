import streamlit as st
from streamlit_folium import st_folium
import folium
from shapely.geometry import Polygon
from tileclipper import TileClipper
import copy
import base64
import shutil
import os

# bbox = [xmin, ymin, xmax, ymax]
output_folder = "./output"
max_workers = 10

def get_bbox(coordinates):
    polygon = Polygon(coordinates)
    bbox = polygon.bounds
    return bbox
def main():
    st.set_page_config(
        page_title="TileClipper Downloader",
        page_icon="🧙‍♂️",
        layout="wide",
    )
    st.title("Map Visualization and Bounding Box Drawing")
    bbox=None
    # Create a Folium map centered at a default location
    m = folium.Map(location=[0, 0], zoom_start=2)
    st.sidebar.header("Draw Polygon and Get Tile Clipped for Bounding Box")
    tile_url = st.sidebar.text_input('Enter Tile URl', 'https://tiles.openaerialmap.org/62d85d11d8499800053796c1/0/62d85d11d8499800053796c2/{z}/{x}/{y}')
    values = st.sidebar.slider(
    'Select a range of zoom values',
    1, 20, (18, 20))
    st.write('Zoom Levels:', values)
    drawn_features = m.add_child(folium.plugins.Draw(export=True,
        draw_options={"polygon": True,"polyline": False,"circle":False,"marker":False,"circlemarker":False},))
    tilelayer = folium.raster_layers.TileLayer(tiles=tile_url, attr="<a href=https://endless-sky.github.io/>Endless Sky</a>")
    tilelayer.add_to(m)
    m.add_child(tilelayer)
    # Display the Folium map in Streamlit
    st_data = st_folium(m,width=1000)


    def create_download_zip(zip_directory, zip_path, filename="export.zip"):
        """ 
            zip_directory (str): path to directory  you want to zip 
            zip_path (str): where you want to save zip file
            filename (str): download filename for user who download this
        """
        shutil.make_archive('output', 'zip', zip_directory)
        with open(zip_path,'rb') as f:
            bytes = f.read()
            b64 = base64.b64encode(bytes).decode()
            href = f'<a href="data:file/zip;base64,{b64}" download=\'{filename}\'>\
                Download file \
            </a>'
            st.markdown(href, unsafe_allow_html=True)


    bbox = copy.deepcopy(bbox)
    def tile_download_click():
        print("bbox",bbox)
        try:
            if os.path.exists(output_folder):
                shutil.rmtree(output_folder)
            tileclipper = TileClipper(tile_url, bbox, output_folder, max_workers)
            tileclipper.download_tiles(values[0], values[1])
        except Exception as e:
            st.sidebar.error(f"Error: {e}")
        st.sidebar.success("Tiles Generated Successfully")
        try:
            create_download_zip(output_folder, "./output.zip", "example.zip")
        except Exception as e:
            st.sidebar.error(f"Error: {e}")
        
    st.sidebar.button("Generate Tiles", type="secondary",disabled=not st_data["last_active_drawing"], on_click=(tile_download_click))


    if st_data:
        if(st_data["last_active_drawing"]):
            # Get the coordinates of the drawn polygon
            coordinates = st_data["last_active_drawing"]["geometry"]["coordinates"][0]

            # Display the drawn polygon on the map
            folium.Polygon(locations=coordinates, color='blue', fill=True, fill_color='blue').add_to(m)

            # Get the bounding box (bbox) of the drawn polygon
            bbox = get_bbox(coordinates)
            print("-----bbox",bbox)
            
            list_bbox=list(bbox)
            print(list_bbox)
            
            st.sidebar.success(f"Bounding Box (bbox): {list_bbox}")

if __name__ == "__main__":
    main()