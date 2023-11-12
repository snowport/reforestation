# import necessary libraries
import streamlit as st
import geemap.foliumap as geemap
import ee
import json
import pandas as pd
import matplotlib.pyplot as plt 

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

# Print title label
st.title("Land Screening Application")

# Create a Map
m0 = geemap.Map()
m1 = geemap.Map()
m2 = geemap.Map()

# Initialize df
df = pd.DataFrame()

# Create two columns
col1, col2 = st.columns(2)

with col1:
    # Create a button to open the URL in a new tab
    st.write("Head over to GeoJson.io to get a JSON of your region of interest (ROI):")
    url = "https://geojson.io/#map=7.17/38.451/-80.677"
    st.markdown(f'<a href="{url}" target="_blank">Open GeoJSON.io</a>', unsafe_allow_html=True)
    
    # User input for GeoJSON coordinates
    custom_geojson_json = st.text_area("Enter your GeoJSON here as JSON:", "")

    if custom_geojson_json:
        try:
            custom_geojson_data = json.loads(custom_geojson_json)
            coordinates = custom_geojson_data['features'][0]['geometry']['coordinates']
            roi_geometry = ee.Geometry.Polygon(coordinates)
            m0.centerObject(roi_geometry)
            m0.addLayer(roi_geometry, {}, "ROI")
            st.write("Successfully added ROI to the map!")

        except json.JSONDecodeError:
            st.warning("Invalid JSON format. Please enter a valid GeoJSON.")
    else:
        st.warning("Please enter your GeoJSON in the text area above and press 'Ctrl' + 'Enter'.")

with col2:
    # Create a selection box for the basemap
    # basemap_options = list(geemap.basemaps.keys())
    # basemap_selection_m1 = st.selectbox("Select a basemap for map1:", basemap_options, index=basemap_options.index("SATELLITE"))
    # basemap_selection_m2 = st.selectbox("Select a basemap for map2:", basemap_options, index=basemap_options.index("TERRAIN"))

    # Add a selectbox for choosing the slope threshold
    slope_threshold_options = [30, 20, 10]
    selected_slope_threshold = st.selectbox("Select Slope Threshold (%)", slope_threshold_options)

    # Define the selected slope threshold
    slope_threshold = selected_slope_threshold

    # Add the selected basemap for m1 and m2
    m1.add_basemap("SATELLITE")
    m2.add_basemap("TERRAIN")

m0.to_streamlit()

# Button to set the selected geometry as ROI
if st.button("Calculate NLCD") and roi_geometry:
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

    st.header("NLCD Map")

    # Display the map
    m1.to_streamlit(height = 500, add_layer_control = True)

    # Define forested areas (NLCD class 41, 42, and 43) and slope threshold
    forested = nlcd.eq(41).And(nlcd.eq(42)).And(nlcd.eq(43))

    # Create a binary mask for non-forested areas and other features
    non_forested = nlcd.neq(41).And(nlcd.neq(42)).And(nlcd.neq(43))  \
    .And(nlcd.neq(11)).And(nlcd.neq(12)).And(nlcd.neq(21))  \
    .And(nlcd.neq(22)).And(nlcd.neq(23)).And(nlcd.neq(24))   \
    .And(nlcd.neq(90)).And(nlcd.neq(95))

    # Clip the elevation image to ROI
    elevation = ee.Image('CGIAR/SRTM90_V4').clip(roi)

    # Apply an algorithm to an image to compute the slope
    slope = ee.Terrain.slope(elevation)

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

    # Add layer control to the map
    m2.addLayerControl()

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

    # Create two columns
    col1, col2 = st.columns(2)

    # with col1:

    #     st.header("Landcover Area:")
    #     st.dataframe(df[['Description','Sum']], use_container_width=True)

    with col1:
        
        st.header("Landcover Class Breakdown")
        
        # Create a horizontal bar plot with specified colors and percentages
        plt.figure(figsize=(8, 4))
        df = df.sort_values(by='Sum', ascending = True)
        bars = plt.barh(df['Description'], df['Sum'].astype(float), color=[nlcd_colors.get(nlcd_legend['Class_' + str(class_val)], '#FFFFFF') for class_val in df['Class']])  # Use the nlcd_colors dictionary to get colors

        # Add percentages as text labels to the bars
        for bar, percentage in zip(bars, df['Percentage']):
            plt.text(float(bar.get_width()), bar.get_y() + bar.get_height() / 2, percentage, ha='left', va='center')

        plt.xlabel('Area (Sq. Km)')
        plt.title('NLCD Landcover Types')
        plt.tight_layout()  # To adjust the spacing

        st.pyplot(plt)

    with col2:

        # Create a pie plot
        fig, ax = plt.subplots(figsize=(8,4))
        labels = ['Forested', 'Non-Forested']
        sizes = [forested_area, non_forested_area]
        colors = ['#68ab5f', '#b3ac9f']  # Forested in green, Non-Forested in gray
        ax.pie(
            sizes, 
            labels=labels, 
            colors=colors, 
            autopct='%1.1f%%', 
            startangle=90
        )
        ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.

        # Display the pie plot in Streamlit
        st.pyplot(fig)

        # Display the total areas for forested and non-forested areas with percentages
        st.write(f"Total Forested Area: {forested_area:.2f} Sq. Km ({(forested_area / total_area * 100):.2f}%)")
        st.write(f"Total Non-Forested Area: {non_forested_area:.2f} Sq. Km ({(non_forested_area / total_area * 100):.2f}%)")

    # Calculate zonal statistics within the defined ROI
    nlcd_stats = masked_non_forested_nlcd.reduceRegion(
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

    st.header("Non-Forested Landcover Class Breakdown")

    # Create two columns
    col1, col2 = st.columns(2)
    
    with col1:
        # st.dataframe(df[['Description','Sum']], use_container_width=True)
        st.write(f"Total Plantable Area (non-forested) within {slope_threshold}% slope threshold: {total_area:.2f} Sq. Km")

        df = df.sort_values(by='Sum', ascending = True)

        # Create a horizontal bar plot with specified colors and percentages
        plt.figure(figsize=(8, 4))
        bars = plt.barh(df['Description'], df['Sum'].astype(float), color=[nlcd_colors.get(nlcd_legend['Class_' + str(class_val)], '#FFFFFF') for class_val in df['Class']])  # Use the nlcd_colors dictionary to get colors

        # Add percentages as text labels to the bars
        for bar, percentage in zip(bars, df['Percentage']):
            plt.text(float(bar.get_width()), bar.get_y() + bar.get_height() / 2, percentage, ha='left', va='center')

        plt.xlabel('Area (Sq. Km)')
        plt.title('NLCD Landcover Types')
        plt.tight_layout()  # To adjust the spacing

        # Display the plot in Streamlit
        st.pyplot(plt)

    with col2:
        # m2.to_streamlit()
        # Create a pie plot
        fig, ax = plt.subplots(figsize=(8,4))
        labels = df['Description']
        colors = [nlcd_colors.get(class_name, '#FFFFFF') for class_name in labels]
        ax.pie(
            df['Sum'], 
            labels=None, 
            colors=colors, 
            # autopct='%1.1f%%', 
            startangle=90
        )
        ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.

        # Display the pie plot in Streamlit
        st.pyplot(fig)
    
    st.header("Plantable Areas Map")

    m3 = geemap.Map()
    m3.centerObject(roi, 11)
    m3.add_basemap("TERRAIN")
    m3.addLayer(masked_non_forested_nlcd, {'palette': 'green'}, 'Plantable Areas')
    m3.addLayerControl()
    m3.to_streamlit()

    # Export button
    if st.button("Export Image"):
        # Define export options
        export_options = {
            "region": m3.get_bounds(),  # Export the current map extent
            "scale": 30,  # Resolution in meters per pixel
            "fileFormat": "GeoTIFF",  # Export format
        }

        # Export the image
        export_task = geemap.export_image(masked_non_forested_nlcd, **export_options)

        # Wait for the export to finish
        st.info("Exporting image. Please wait...")

        # Get the export link
        export_link = geemap.get_download_url(export_task)

        # Display the link to download the exported file
        st.markdown(f'[Download Exported Image]({export_link})')