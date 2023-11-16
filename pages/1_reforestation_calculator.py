# import libraries
import streamlit as st
import geemap.foliumap as geemap
import ee
import json
import pandas as pd
import matplotlib.pyplot as plt 
import geopandas as gpd
import tempfile
import zipfile
import datetime
import os
import shutil
from PIL import Image
import time

def cleanup_temp_directory(temp_dir):
    try:
        import shutil
        shutil.rmtree(temp_dir)
        st.success("Temporary directory cleaned up successfully.")
    except Exception as e:
        st.error(f"Error cleaning up temporary directory: {e}")

# Create a function to mask clouds using the Sentinel-2 QA60 band
def mask_clouds(image):
    # Select the QA60 band from the image
    QA60 = image.select(['QA60'])
    
    # Create a cloud mask by checking if the QA60 band is 0 (indicating no cloud)
    cloud_mask = QA60.bitwiseAnd(1 << 10).eq(0)
    
    # Update the image mask with the cloud mask
    return image.updateMask(cloud_mask)

# Customize the sidebar
markdown = """
Web App URL: <https://land-screening-tool.streamlit.app>
"""
st.sidebar.title("About")
st.sidebar.info(markdown)

# Preparing values
json_data = st.secrets["json_data"]
service_account = st.secrets["service_account"]
json_object = json.loads(json_data, strict=False)
json_object = json.dumps(json_object)

# Authorizing the app
credentials = ee.ServiceAccountCredentials(service_account, key_data=json_object)
ee.Initialize(credentials)

# Create a temporary directory
temp_dir = tempfile.TemporaryDirectory()

# Upload a JSON file for ROI
st.sidebar.header("Upload a GeoJSON")
geojson_file = st.sidebar.file_uploader("Upload a GeoJSON", type=["geojson"])

if geojson_file is not None:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".geojson") as temp_geojson_file:
    
        temp_geojson_file.write(geojson_file.read())
        temp_geojson_file_path = temp_geojson_file.name
    
    with open(temp_geojson_file_path, "r") as temp_geojson_file:
        geojson_content = temp_geojson_file.read()
    
    # Parse the GeoJSON content as a JSON object
    try:
        cleaned_content = geojson_content.strip()
        
        if cleaned_content:

            json_object = json.loads(cleaned_content.encode('utf-8').decode('utf-8'))
            print("GeoJSON loaded successfully.")

        else:
            print("GeoJSON file is empty.")
            
    except json.JSONDecodeError as e:
        
        print(f"Error decoding JSON: {e}")

# Upload a shapefile
st.sidebar.header("Upload Shapefile")
shapefile = st.sidebar.file_uploader("Upload a shapefile (ZIP)", type=["zip"])

if shapefile is not None:
    # Extract the uploaded shapefile to the temporary directory
    with open(f"{temp_dir.name}/shapefile.zip", "wb") as f:
        f.write(shapefile.read())
    with zipfile.ZipFile(f"{temp_dir.name}/shapefile.zip", 'r') as zip_ref:
        zip_ref.extractall(temp_dir.name)

    # Read the shapefile using GeoPandas
    gdf = gpd.read_file(temp_dir.name)

    # # Add the shapefile as a layer on the map
    # map = geemap.Map()
    # map.add_gdf(gdf, layer_name="Uploaded Shapefile")


# Allow the user to upload a GeoTIFF file
st.sidebar.header("Upload Geotiff")
tiff = st.sidebar.file_uploader("Upload a GeoTIFF file", type=["tif", "tiff"])

if tiff is not None:
    # Create a temporary directory
    temp_dir = tempfile.mkdtemp()

    # Save the uploaded file to the temporary directory
    temp_file_path = os.path.join(temp_dir, tiff.name)
    with open(temp_file_path, "wb") as temp_file:
        temp_file.write(tiff.read())

    # Read the image
    image = Image.open(temp_file_path)
    # st.image(image)
    # Read the uploaded GeoTIFF file
    # Add the GeoTIFF to the map
    # m.add_raster(temp_file_path, colormap='gray', layer_name='Uploaded GeoTIFF')

# Initialize NLCD legends
nlcd_class_names = [
    'Open Water',
    'Perennial Ice/Snow',
    'Developed - Open Space',
    'Developed - Low Intensity',
    'Developed - Medium Intensity',
    'Developed - High Intensity',
    'Barren Land (Rock/Sand/Clay)',
    'Deciduous Forest',
    'Evergreen Forest',
    'Mixed Forest',
    'Dwarf Scrub',
    'Shrub/Scrub',
    'Grassland/Herbaceous',
    'Sedge/Herbaceous',
    'Lichens',
    'Moss',
    'Pasture/Hay',
    'Cultivated Crops',
    'Woody Wetlands',
    'Emergent Herbaceous Wetlands'
]
nlcd_legend = {
    'Class_11': 'Open Water',
    'Class_12': 'Perennial Ice/Snow',
    'Class_21': 'Developed - Open Space',
    'Class_22': 'Developed - Low Intensity',
    'Class_23': 'Developed - Medium Intensity',
    'Class_24': 'Developed - High Intensity',
    'Class_31': 'Barren Land (Rock/Sand/Clay)',
    'Class_41': 'Deciduous Forest',
    'Class_42': 'Evergreen Forest',
    'Class_43': 'Mixed Forest',
    'Class_51': 'Dwarf Scrub',
    'Class_52': 'Shrub/Scrub',
    'Class_71': 'Grassland/Herbaceous',
    'Class_72': 'Sedge/Herbaceous',
    'Class_73': 'Lichens',
    'Class_74': 'Moss',
    'Class_81': 'Pasture/Hay',
    'Class_82': 'Cultivated Crops',
    'Class_90': 'Woody Wetlands',
    'Class_95': 'Emergent Herbaceous Wetlands'
}       
nlcd_colors = {
    'Open Water': '#466b9f',
    'Perennial Ice/Snow': '#d1def8',
    'Developed - Open Space': '#dec5c5',
    'Developed - Low Intensity': '#d99282',
    'Developed - Medium Intensity': '#eb0000',
    'Developed - High Intensity': '#ab0000',
    'Barren Land (Rock/Sand/Clay)': '#b3ac9f',
    'Deciduous Forest': '#68ab5f',
    'Evergreen Forest': '#1c5f2c',
    'Mixed Forest': '#b5c58f',
    'Dwarf Scrub': '#af963c',
    'Shrub/Scrub': '#ccb879',
    'Grassland/Herbaceous': '#dfdfc2',
    'Sedge/Herbaceous': '#d1d182',
    'Lichens': '#a3cc51',
    'Moss': '#82ba9e',
    'Pasture/Hay': '#dcd939',
    'Cultivated Crops': '#ab6c28',
    'Woody Wetlands': '#b8d9eb',
    'Emergent Herbaceous Wetlands': '#6c9fb8',
}

color_mapping_esa = {
    10: "#006400",  # Tree cover
    20: "#ffbb22",  # Shrubland
    30: "#ffff4c",  # Grassland
    40: "#f096ff",  # Cropland
    50: "#fa0000",  # Built-up
    60: "#b4b4b4",  # Bare / sparse vegetation
    70: "#f0f0f0",  # Snow and ice
    80: "#0064c8",  # Permanent water bodies
    90: "#0096a0",  # Herbaceous wetland
    95: "#00cf75",  # Mangroves
    100: "#fae6a0"  # Moss and lichen
}

# Print title label
st.title("Reforestation Calculator")

# Create a Map
m0 = geemap.Map()
m1 = geemap.Map()
m2 = geemap.Map()
ms = geemap.Map()

# Initialize df
df = pd.DataFrame()

# Add a selectbox for choosing the slope threshold
st.header("1. Define the slope threshold for your reforestation project")
slope_threshold_options = [30, 20, 10]
slope_threshold = st.selectbox("Select Slope Threshold (%)", slope_threshold_options)

# Allow the user to input start and end dates
st.header("2. Enter the start/end date for a satellite overlaid image")
start_date = st.text_input("Enter the start date (e.g., YYYY-MM-DD):", "2021-01-01")
end_date = st.text_input("Enter the end date (e.g., YYYY-MM-DD):","2021-12-31")

# Add the selected basemap for m1 and m2
m1.add_basemap("SATELLITE")
m2.add_basemap("TERRAIN")
ms.add_basemap("TERRAIN")

st.header("3. Define ROI")
st.write(f"Visit GeoJson.io to copy the JSON of your region of interest (ROI):")
url = "https://geojson.io/#map=7.17/38.451/-80.677"
st.markdown(f'<a href="{url}" target="_blank">Open GeoJSON.io</a>', unsafe_allow_html=True)

geojson_json = st.text_area("Paste JSON script of the ROI here:", "")

if geojson_json != "":
    custom_geojson = json.loads(geojson_json)
    st.success("GeoJSON loaded successfully.")
    
    coordinates = custom_geojson['features'][0]['geometry']['coordinates']
    roi_geometry = ee.Geometry.Polygon(coordinates)
    
    # Convert the ROI to an ee.FeatureCollection
    # roi_fc = ee.FeatureCollection(ee.Geometry(roi_geometry))
    m0.centerObject(roi_geometry)

    m0.addLayer(roi_geometry, {}, "ROI")

    # Load Sentinel-2 imagery for the specified date range and ROI
    collection = ee.ImageCollection('COPERNICUS/S2') \
        .filterBounds(roi_geometry) \
        .filterDate(start_date, end_date) \
        .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 10)) \
        # .map(mask_clouds) \

    esa = ee.ImageCollection('ESA/WorldCover/v100').first().clip(roi_geometry)

    m0.add_layer(esa, color_mapping_esa, 'ESA Landcover')

    image_count = int(collection.size().getInfo())

    # Sort the image collection by cloud coverage, with the least cloudy images first
    sorted_collection = collection.sort('CLOUDY_PIXEL_PERCENTAGE', True)

    if image_count > 5:
        # Limit the collection to the first 5 clearest images
        limited_collection = sorted_collection.limit(5)
    else:
        limited_collection = sorted_collection.limit(image_count)

    # Select the first (clearest) image from the sorted collection
    clearest_image = limited_collection.median().clip(roi_geometry)

    m0.addLayer(clearest_image, {'bands': ['B4', 'B3', 'B2'],  # True color bands
                'min': 0,
                'max': 2000,
                }, 'Satellite Imagery')

    col1, col2 = st.columns(2)

    with col1:
        m0.to_streamlit(height=500)

        if tiff is not None:
            st.header("Landcover from PEARL landcover.io:")
            st.image(image)

            with open(temp_file_path, "rb") as file:
                btn = st.download_button(label="Download image",  
                                    data = file, 
                                    file_name = "landcoverio_download", 
                                    mime="image/png"
                                )
                
    with col2:
        
        st.write(f'Number of images in the range provided: {image_count}')

        st.write("Satellite imagery (clearest dates):")

        # Iterate through the collection and extract timestamps
        timestamps = []
        for image in limited_collection.getInfo()['features']:
            timestamp_ms = image['properties']['system:time_start']
            datetime_obj = datetime.datetime.fromtimestamp(timestamp_ms / 1000)
            formatted_date = datetime_obj.strftime('%m-%d-%Y')
            timestamps.append(formatted_date)

        # Convert the list to a Pandas DataFrame for a table format
        dates_df = pd.DataFrame({'Date': timestamps})

        # Print the DataFrame
        st.write(dates_df)

    # Button to set the selected geometry as ROI
    if st.button("Calculate"):

        # Convert ROI to GeoJSON
        roi_geojson = roi_geometry.getInfo()
        custom_geojson_json = json.dumps(roi_geojson, indent=2)

        # Create an Earth Engine Feature from the GeoJSON and add it to the map
        roi_feature= ee.Feature(ee.Geometry(roi_geojson))
        roi = roi_feature.geometry()
        m1.addLayer(roi, {'color': 'FF0000'}, 'ROI')
        
        # Create a map and add the clipped elevation image
        m1.centerObject(roi)
        m2.centerObject(roi)

        # Add NLCD 2021 and clip to the user-defined ROI
        nlcd = ee.Image('USGS/NLCD_RELEASES/2021_REL/NLCD/2021').select('landcover').clip(roi)
        m1.addLayer(nlcd, {}, 'NLCD 2021')

        # Add a legend for the NLCD data
        m1.add_legend(builtin_legend='NLCD')

        # Define forested areas (NLCD class 41, 42, and 43) and slope threshold
        forested = nlcd.eq(41).And(nlcd.eq(42)).And(nlcd.eq(43))

        # Create a binary mask for non-forested areas and other features
        non_forested = nlcd.neq(41).And(nlcd.neq(42)).And(nlcd.neq(43))  \
        .And(nlcd.neq(11)).And(nlcd.neq(12)).And(nlcd.neq(21))  \
        .And(nlcd.neq(22)).And(nlcd.neq(23)).And(nlcd.neq(24))   \
        .And(nlcd.neq(90)).And(nlcd.neq(95)).And(nlcd.neq(82)) \
        .And(nlcd.neq(81))

        # Clip the elevation image to ROI
        elevation = ee.Image('CGIAR/SRTM90_V4').clip(roi)

        # Apply an algorithm to an image to compute the slope
        slope = ee.Terrain.slope(elevation)
        slope_vis = {'min':0, 'max':40, 'palette': 'rainbow'}
        ms.addLayer(slope, slope_vis, "Slope")
        ms.centerObject(roi)
        
        # Add a colorbar for the slope layer
        ms.add_colorbar(
            vis_params = slope_vis,
            label = "Slope"
        )

        col1, col2 = st.columns(2)   
        with col1:
            st.header("NLCD Lancover Types")
            m1.to_streamlit(height = 500, add_layer_control = True)
        with col2: 
            st.header("Slope Map")
            ms.to_streamlit(height=500)

            # Create a binary mask for slopes less than threshold
            slope_lt_threshold_mask = slope.lt(slope_threshold)

            # Create a binary mask for slopes greater than or equal to threshold
            slope_ge_threshold_mask = slope.gte(slope_threshold)

            # Apply masking to show slopes less than threshold in blue
            blue_slope = slope.updateMask(slope_lt_threshold_mask)

            # Apply masking to show slopes greater than or equal to threshold in red
            red_slope = slope.updateMask(slope_ge_threshold_mask)

            # Define the palette for slope layers
            slope_palette = '0000FF'  # Default palette for slopes < 30 degrees
            if slope_threshold == 20:
                slope_palette = '00FF00'  # Change palette for slopes < 20 degrees
            elif slope_threshold == 10:
                slope_palette = 'FFFF00'  # Change palette for slopes < 10 degrees

            # Add the slope layers with the dynamic legend
            m2.addLayer(blue_slope, {'min': 0, 'max': 60, 'palette': slope_palette}, f'Slope < {slope_threshold} degrees', False)
            m2.addLayer(red_slope, {'min': 0, 'max': 60, 'palette': 'FF0000'}, f'Slope >= {slope_threshold} degrees', False)

            # Apply masking to show only non-forested areas
            masked_non_forested_nlcd = nlcd.updateMask(non_forested).updateMask(slope_lt_threshold_mask)

            # Add the masked layers to the map
            m2.addLayer(masked_non_forested_nlcd, {}, 'NLCD 2021 Non-Forested')

            # Calculate zonal statistics within the defined ROI
            nlcd_stats = nlcd.reduceRegion(
                reducer=ee.Reducer.frequencyHistogram(),
                geometry=roi,
                scale=30,
            )

            nlcd_dict = nlcd_stats.getInfo()
            df = pd.DataFrame(nlcd_dict['landcover'].items(), columns=['Class', 'Sum'])
            df['Sum'] = (df['Sum'] / 1000000*900 )
            total_area = df['Sum'].sum()
            df['Percentage'] = ((df['Sum'] / total_area) * 100).apply(lambda x: "{:.2f}%".format(x))
            df['Sum'] = df['Sum'].apply(lambda x: "{:.2f}".format(x))
            df['Description'] = df['Class'].apply(lambda x: nlcd_legend.get('Class_' + str(x), 'Unknown'))
            df['Sum'] = pd.to_numeric(df['Sum'])
            df = df.sort_values(by='Sum', ascending = False)
            
            # Calculate the total areas for forested and non-forested areas
            forested_area = df[df['Description'].isin(['Deciduous Forest', 'Evergreen Forest', 'Mixed Forest'])]['Sum'].sum()
            non_forested_area = df[df['Description'].isin(['Developed - Open Space', 'Developed - Low Intensity', 'Developed - Medium Intensity', 'Developed - High Intensity',
                                                            'Barren Land (Rock/Sand/Clay)', 'Dwarf Scrub', 'Shrub/Scrub', 'Grassland/Herbaceous', 'Sedge/Herbaceous',
                                                            'Lichens', 'Moss', 'Pasture/Hay', 'Cultivated Crops', 'Woody Wetlands', 'Emergent Herbaceous Wetlands'])]['Sum'].sum()

            total_area = forested_area + non_forested_area
        
        col1, col2 = st.columns(2)   
        
        with col1:
            
            st.header("Landcover Class Breakdown")
            
            # Display the total areas for forested and non-forested areas with percentages
            st.write(f"Total Forested Area: {forested_area:.2f} Sq. Km ({(forested_area / total_area * 100):.2f}%)")
            st.write(f"Total Non-Forested Area: {non_forested_area:.2f} Sq. Km ({(non_forested_area / total_area * 100):.2f}%)")

            # Create a horizontal bar plot with specified colors and percentages
            plt.figure(figsize=(8, 4))
            df = df.sort_values(by='Sum', ascending = True)
            bars = plt.barh(df['Description'], df['Sum'].astype(float), color=[nlcd_colors.get(nlcd_legend['Class_' + str(class_val)], '#FFFFFF') for class_val in df['Class']])  # Use the nlcd_colors dictionary to get colors

            # Add percentages as text labels to the bars
            for bar, percentage in zip(bars, df['Sum']):
                plt.text(float(bar.get_width()), bar.get_y() + bar.get_height() / 2, percentage, ha='left', va='center')

            plt.xlabel('Area (Sq. Km)')
            plt.title('NLCD Landcover Types')
            plt.tight_layout()  # To adjust the spacing

            st.pyplot(plt)

        with col2:
            st.markdown(" \
                            \
                            \
                        ")
            # Create a pie plot
            fig, ax = plt.subplots(figsize=(2,2))
            labels = ['Forested', 'Non-Forested']
            sizes = [forested_area, non_forested_area]
            colors = ['#68ab5f', '#b3ac9f']  # Forested in green, Non-Forested in gray
            ax.pie(
                sizes, 
                labels=labels, 
                colors=colors, 
                autopct='%1.1f%%', 
                startangle=90,
            )
            ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.

            # Display the pie plot in Streamlit
            st.pyplot(fig)

            # Calculate zonal statistics within the defined ROI
            nlcd_stats = masked_non_forested_nlcd.reduceRegion(
                reducer=ee.Reducer.frequencyHistogram(),
                geometry=roi,
                scale=30,
            )

            nlcd_dict = nlcd_stats.getInfo()
            df = pd.DataFrame(nlcd_dict['landcover'].items(), columns=['Class', 'Sum'])
            df['Sum'] = (df['Sum'] / 1000000*900 )
            total_area_nf = df['Sum'].sum()
            df['Percentage'] = ((df['Sum'] / total_area_nf) * 100).apply(lambda x: "{:.2f}%".format(x))
            df['Sum'] = df['Sum'].apply(lambda x: "{:.2f}".format(x))
            df['Description'] = df['Class'].apply(lambda x: nlcd_legend.get('Class_' + str(x), 'Unknown'))
            df['Sum'] = pd.to_numeric(df['Sum'])
            df = df.sort_values(by='Sum', ascending = False)
        
        col1, col2 = st.columns(2)

        with col1:

            st.header("Non-Forested Landcover Class Breakdown")

            df = df.sort_values(by='Sum', ascending = True)

            # Create a horizontal bar plot with specified colors and percentages
            plt.figure(figsize=(8, 4))
            bars = plt.barh(df['Description'], df['Sum'].astype(float), color=[nlcd_colors.get(nlcd_legend['Class_' + str(class_val)], '#FFFFFF') for class_val in df['Class']])  # Use the nlcd_colors dictionary to get colors

            # Add percentages as text labels to the bars
            for bar, percentage in zip(bars, df['Sum']):
                plt.text(float(bar.get_width()), bar.get_y() + bar.get_height() / 2, percentage, ha='left', va='center')

            plt.xlabel('Area (Sq. Km)')
            plt.title('NLCD Landcover Types')
            plt.tight_layout()  # To adjust the spacing

            # Display the plot in Streamlit
            st.pyplot(plt)

        with col2:
            # Create a pie plot
            fig, ax = plt.subplots(figsize=(2,2))
            labels = df['Description']
            colors = [nlcd_colors.get(class_name, '#FFFFFF') for class_name in labels]
            ax.pie(
                df['Sum'], 
                labels=labels, 
                colors=colors, 
                autopct='%1.1f%%', 
                startangle=90
            )
            ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.

            # Display the pie plot in Streamlit
            st.pyplot(fig)
        
        st.header("Potential for Reforestation Map")
        st.write(f"Total plantable areas that are non-forested and within slope threshold:  {total_area_nf:.2f} sq. km ({(total_area_nf / total_area * 100):.2f}% of total ROI)")

        m3 = geemap.Map()
        m3.centerObject(roi)
        m3.add_basemap("TERRAIN")
        
        # # Add Satellite Imagery
        # m3.addLayer(clearest_image, {'bands': ['B4', 'B3', 'B2'],  # True color bands
        #                             'min': 0,
        #                             'max': 2000,
        #             }, 'Satellite Imagery')

        m3.addLayer(masked_non_forested_nlcd, {'palette': 'green'}, 'Plantable Areas')
        m3.addLayerControl()
        m3.to_streamlit()

        # Export button
        if st.button("Download Shapefile"):
            try:
                st.write(os.path.exists(temp_dir.name))
    
                # Export the shapefile
                output_shp = "Result.shp"
                geemap.ee_export_vector(masked_non_forested_nlcd, output_shp, temp_dir, crs='EPSG:4326')
                
                # Display a download link
                shapefile_path = os.path.join(temp_dir, output_shp)
                
                st.markdown(f"Download the Plantable Area shapefile [here]({shapefile_path}).")
            except Exception as e:
                st.exception("Error during shapefile export:")
else:
    st.error("Please input a GeoJSON in JSON format above or upload a GeoJSON file.")