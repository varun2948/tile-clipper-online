import streamlit as st
from streamlit_folium import st_folium
import folium
from shapely.geometry import Polygon
from tileclipper import TileClipper
import copy
import base64
import shutil
import os
import requests
import time
import datetime

# bbox = [xmin, ymin, xmax, ymax]
output_folder = "./output"
max_workers = 10
post_url = "http://13.234.106.125:8000/predict"

def get_bbox(coordinates):
    polygon = Polygon(coordinates)
    bboxy = polygon.bounds
    return bboxy
def main():
    st.set_page_config(
        page_title="TileClipper Downloader",
        page_icon="🧙‍♂️",
        layout="wide",
    )
    bbox= None
    # st.title("Map Visualization and Bounding Box Drawing")
    nominatum_search = st.text_input('Address', None)
    
    # Create a Folium map centered at a default location
    m = folium.Map(location=[0, 0], zoom_start=2)
    def boundtobox(city):
        try:
            response = requests.get(f"https://nominatim.openstreetmap.org/search.php?q={city}&format=jsonv2")
            data = response.json()

            bboxt = [(float(data[0]["boundingbox"][0]), float(data[0]["boundingbox"][2])),
                (float(data[0]["boundingbox"][1]), float(data[0]["boundingbox"][3]))
            ]
            print(bboxt,'banepa')
            folium.map.FitBounds(bboxt).add_to(m)
        except Exception as e:
            st.sidebar.error(f"Error: {e}")

    if nominatum_search:
        boundtobox(nominatum_search)
    st.sidebar.header("Draw Polygon and Get Tile Clipped for Bounding Box")
    tile_url = st.sidebar.text_input('Enter Tile URl', 'https://tiles.openaerialmap.org/62d85d11d8499800053796c1/0/62d85d11d8499800053796c2/{z}/{x}/{y}')
    values = st.sidebar.slider(
    'Select a range of zoom values',
    1, 25, (18, 22))
    st.write('Zoom Levels:', values)
    drawn_features = m.add_child(folium.plugins.Draw(export=True,
        draw_options={"polygon": True,"polyline": False,"circle":False,"marker":False,"circlemarker":False},))
    fg1 = folium.FeatureGroup(name='g1')
    

    tilelayer = folium.raster_layers.TileLayer(tiles=tile_url, attr="<a href=https://endless-sky.github.io/>Endless Sky</a>")
    tilelayer.add_to(fg1)
    m.add_child(fg1)

    # m.add_child(tilelayer)
    
    # Display the Folium map in Streamlit
    st_data = st_folium(m,width=1000)

    def request_post_api(url):
        dt_text = datetime.datetime.now().strftime("%d%m%Y%H%M%S")
        # The data you want to send in the POST request (in this example, a dictionary)
        payload = {
            "baseUrl": "https://tiles.openaerialmap.org/62d85d11d8499800053796c1/0/62d85d11d8499800053796c2/{z}/{x}/{y}",
            "bbox": list(bbox),
            "input_folder": "tiles",
            "output_folder": dt_text,
            "max_workers": max_workers,
            "zoom_level": [
                values[0],
                values[1]
            ]
        }
        print("payload",payload)
        # Make the POST request
        response = requests.post(url, json=payload)

        # Print the response
        print("Status Code:", response.status_code)
        print("Response Content:", response.text)
        print("Response ContentJSON:", response.json())
        # new_tilelayer = folium.raster_layers.TileLayer(tiles=response.json()[0]["url"], attr="<a href=https://deepakpradhan.com.np/>Varun</a>")
        # new_tilelayer.add_to(m)
        # m.add_child(new_tilelayer)
        return dt_text

        # tilelayer.
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


    def request_nominatum_api():
        response = requests.get("https://nominatim.openstreetmap.org/search.php?q=banepa&format=jsonv2")
        data = response.json()
        
        bboxt = [(float(data[0]["boundingbox"][0]), float(data[0]["boundingbox"][2])),
            (float(data[0]["boundingbox"][1]), float(data[0]["boundingbox"][3]))
        ]
        # [(27,85),(27,86)]
        print(bboxt,'bboxt')
        # rect=folium.Rectangle(bounds=bboxt, color='blue', fill=True, fill_color='blue', fill_opacity=0.2).add_to(m)
        folium.map.FitBounds(bboxt).add_to(m)
        return m
    # print(nominatum_search,'search')
    # # if nominatum_search:
    # request_nominatum_api()

    bbox = copy.deepcopy(bbox)
    def tile_download_click():
        print("bbox",bbox)
        # try:
        #     if os.path.exists(output_folder):
        #         shutil.rmtree(output_folder)
        #     tileclipper = TileClipper(tile_url, bbox, output_folder, max_workers)
        #     tileclipper.download_tiles(values[0], values[1])
        # except Exception as e:
        #     st.sidebar.error(f"Error: {e}")
        st.sidebar.success("Tiles Generated Successfully")
        
        output_folder= request_post_api(post_url)
        if output_folder:
            while True:
                check_tile_response = requests.get(f"https://solidwasteapi.naxa.com.np/check/{output_folder}")
                print(check_tile_response.json(), 'check_tile_response')
                status = check_tile_response.json()[1]
                
                if status == 202:
                    st.sidebar.info("Tiles are processing...")
                    time.sleep(2)  # Adjust the sleep duration as needed
                elif status == 200:
                    st.sidebar.success(f"Tiles are ready for download{check_tile_response.json()[0]['url']}")
                    fg2 = folium.FeatureGroup(name='g2')
                    new_tilelayer = folium.TileLayer(tiles=check_tile_response.json()[0]["url"], attr="<a href=https://deepakpradhan.com.np/>Varun</a>")
                    # new_tilelayer.add_to(m)
                    
                    folium.LayerControl(collapsed=False).add_to(m)
                    new_tilelayer.add_to(fg2)
                    m.add_child(fg2)
                    time.sleep(5)  # Adjust the sleep duration as needed
                    break
                else:
                    st.sidebar.error(f"Error: Unexpected status {status}")
                    break
        # try:
        #     create_download_zip(output_folder, "./output.zip", "example.zip")
        # except Exception as e:
        #     st.sidebar.error(f"Error: {e}")
        
        
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