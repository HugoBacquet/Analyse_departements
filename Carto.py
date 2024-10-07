import geopandas as gpd
import pandas as pd
import folium
from shapely.geometry import Polygon
import streamlit as st
from streamlit_folium import st_folium
import base64
import os

# Paths to the data files
excel_file_path = os.path.abspath('Extraction_données_comptable_2023.xlsx')
geojson_file_path = os.path.abspath('a-dep2021.json')
comparison_excel_path = os.path.abspath('Eléments_de_comparaison.xlsx')

# Set the Streamlit page configuration
st.set_page_config(layout="wide")

# Load data from the Excel files
bdd_data = pd.read_excel(excel_file_path, sheet_name='Feuil2')
comparison_data = pd.read_excel(comparison_excel_path, sheet_name='Comparaison ensemble métropole', usecols="A:AT")

# Load the GeoJSON file with department geometries
departments = gpd.read_file(geojson_file_path)

# List of departments to display
departments_of_interest = ['74', '73', '38', '63', '15', '12', '65', '09', '66', '04', '05', '84', '13', '83']

# Ensure department codes are in string format for merging
bdd_data['Numéro Département'] = bdd_data['Numéro Département'].astype(str)
departments['dep'] = departments['dep'].astype(str)

# Merge data with department geometries
merged_final = pd.merge(departments, bdd_data, left_on='dep', right_on='Numéro Département')
comparison_data['Département'] = comparison_data['Département'].astype(str)
merged_final = pd.merge(merged_final, comparison_data, on='Département', how='left')

# Filter results to include only the departments of interest
filtered_results = merged_final[merged_final['dep'].isin(departments_of_interest)]

# Create a DataFrame that includes all departments for the top table calculation
all_departments = merged_final.copy()

# Define individual positions for each department
department_positions = {
    '74': (2.8, 4.5),
    '73': (3.0, 3.3),
    '38': (-1.1, 5.8),
    '63': (-3.4, 5.3),
    '15': (-5.5, 4.3),
    '12': (-6.8, 3.3),
    '09': (-8, 2.8),
    '65': (-6.7, 0.85),
    '66': (-7.3, -0.6),
    '04': (3.0, 1),
    '05': (3.0, 2.3),
    '13': (-5.2, -1.6),
    '84': (-0.6, -1.5),
    '83': (3, -0.3)
}

# Columns where a positive evolution is desired
growth_positive_columns = [
    'Taux d\'épargne brute', 
    'Délai de désendettement',
    'Dette encours',
    'Population INSEE',
    'Population DGF',
    'Produits de fonctionnement',
    'Epargne brute',
    'Epargne nette',
    'Dépenses directes équipement',
    'Dépenses de fonctionnement',
    'Subventions d\'équipement',
    'Dépenses réelles de fonctionnement par habitant (INSEE)'
    'Epargne brute par habitant (INSEE)',
    'Epargne nette par habitant (INSEE)',
    'Produits de fonctionnement par habitant (INSEE)',
    'Dépenses directes équipement par habitant (INSEE)',
    'Subventions d\'équipement par habitant (INSEE)',
    'Moyenne dépenses d\'investissement par habitant 2021/2023 (INSEE)',
    'Moyenne dépenses d\'équipement par habitant 2021/2023 (INSEE)',
    'Moyenne subventions versées par habitant 2021/2023 (INSEE)',
    'Moyenne dépenses d\'investissement par habitant 2018/2023 (INSEE)',
    'Moyenne dépenses d\'équipement par habitant 2018/2023 (INSEE)',
    'Moyenne subventions versées par habitant 2018/2023 (INSEE)',
    'Prestation compensation handicap (+20 ans) : 6511211 par habitant (INSEE)',
    'Autres matériels informatiques : 21838',
    'Charges générales : Total 011',
    'Charges générales : Total 011 par habitant (DGF)',
    'Dotation colleges publics :655111',
    'Dotation collège privés : 655112',
    'Frais de séjour adultes handicapé : 65242',
    'Frais de séjour pers. Âgées : 65243',
    'Frais de séjour pers. Âgées : 65243 par habitant (INSEE)',
    'Frais de séjour adultes handicapé : 65242 par habitant (INSEE)',
    'Lieux de vie et d’accueil : 652413',
    'Lieux de vie et d’accueil : 652413 par habitant (INSEE)',
    'MECS :652412',
    'MECS :652412 par habitant (INSEE)',
    'Masse salariale :Total 012',
    'Matériel informatique scolaire : 21831',
    'APA : 016',
    'APA : 016 par habitant (INSEE)',
    'Subvention collectivités statut particulier : 65735',
    'Subvention communes : 65734',
    'Subvention communes membres du GFP : 657341',
    'Subvention entreprises : 65742',
    'Subvention ménages : 65741',
    'Subvention organismes publics divers : 657382',
    'Voirie : 2151',
    'Voirie : 2151 par habitant (DGF)'

]

# Columns where a decline is positive (e.g., less debt)
decline_positive_columns = [
    'Dette encours',
    'Dette par habitant (INSEE)'
]

# Columns where only evolution should be displayed
evolution_columns = [
    'Taux d\'épargne brute', 
    'Délai de désendettement',
    'Dette encours',
    'Population INSEE',
    'Population DGF',
    'Produits de fonctionnement',
    'Epargne brute',
    'Epargne nette',
    'Dépenses directes équipement',
    'Subventions d\'équipement',
    'Dépenses de fonctionnement'
]

# Columns where only the 2023 value should be displayed
value_2023_columns = [
    'Epargne brute par habitant (INSEE)',
    'Epargne nette par habitant (INSEE)',
    'Produits de fonctionnement par habitant (INSEE)',
    'Dépenses directes équipement par habitant (INSEE)',
    'Dépenses réelles de fonctionnement par habitant (INSEE)'
    'Subventions d\'équipement par habitant (INSEE)',
    'Moyenne dépenses d\'investissement par habitant 2021/2023 (INSEE)',
    'Moyenne dépenses d\'équipement par habitant 2021/2023 (INSEE)',
    'Moyenne subventions versées par habitant 2021/2023 (INSEE)',
    'Moyenne dépenses d\'investissement par habitant 2018/2023 (INSEE)',
    'Moyenne dépenses d\'équipement par habitant 2018/2023 (INSEE)',
    'Moyenne subventions versées par habitant 2018/2023 (INSEE)',
    'Dette par habitant (INSEE)',
    'Prestation compensation handicap (+20 ans) : 6511211 par habitant (INSEE)',
    'Autres matériels informatiques : 21838',
    'Charges générales : Total 011',
    'Charges générales : Total 011 par habitant (DGF)',
    'Dotation colleges publics :655111',
    'Dotation collège privés : 655112',
    'Frais de séjour adultes handicapé : 65242',
    'Frais de séjour pers. Âgées : 65243',
    'Frais de séjour pers. Âgées : 65243 par habitant (INSEE)',
    'Frais de séjour adultes handicapé : 65242 par habitant (INSEE)',
    'Lieux de vie et d’accueil : 652413',
    'Lieux de vie et d’accueil : 652413 par habitant (INSEE)',
    'MECS :652412',
    'MECS :652412 par habitant (INSEE)',
    'Masse salariale :Total 012',
    'Matériel informatique scolaire : 21831',
    'APA : 016',
    'APA : 016 par habitant (INSEE)',
    'Subvention collectivités statut particulier : 65735',
    'Subvention communes : 65734',
    'Subvention communes membres du GFP : 657341',
    'Subvention entreprises : 65742',
    'Subvention ménages : 65741',
    'Subvention organismes publics divers : 657382',
    'Voirie : 2151',
    'Voirie : 2151 par habitant (DGF)'

]

# Function to get the sorting order based on the selected column
def get_sorting_order(column):
    if column in growth_positive_columns:
        return False  # Descending order for positive growth
    elif column in decline_positive_columns:
        return True  # Ascending order for decline being positive
    else:
        return False  # Default to descending order

# --- Helper function to get image as base64 ---
def get_image_base64(image_path):
    with open(image_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode()
    return encoded_string

# --- Function to Create and Display the Main Map ---
def create_map(selected_column):
    # Create a base map
    m = folium.Map(
        location=[47.5, -1.2],
        zoom_start=6,
        tiles='Stamen Toner',
        attr=" "
    )

    # Add department boundaries
    folium.GeoJson(
        filtered_results,
        style_function=lambda feature: {
            'fillColor': '#FF6961' if feature['properties']['dep'] == '05' else 'orange',  # Red for 'Hautes-Alpes'
            'color': 'black',
            'weight': 1,
            'fillOpacity': 0.6,
        }
    ).add_to(m)

    # Mask surrounding countries
    world_polygon = Polygon([[-90, -180], [-90, 180], [90, 180], [90, -180], [-90, -180]])
    france_geometry = departments.union_all()
    mask_polygon = world_polygon.difference(france_geometry)
    mask_gdf = gpd.GeoDataFrame(geometry=[mask_polygon], crs="EPSG:4326")

    folium.GeoJson(
        mask_gdf,
        style_function=lambda feature: {
            'fillColor': 'white',
            'color': 'white',
            'weight': 0,
            'fillOpacity': 1.0,
        }
    ).add_to(m)


    # --- Add title table to the map ---
    def add_title_table(title, offset_x, offset_y):
        table_html = f"""
        <table style="border-collapse: collapse; background-color: white; width: 1200px;">
            <thead style="background-color: white;">
                <tr><th style="text-align: center; font-style:italic; font-size: 28px; color: black;">{title}</th></tr>
            </thead>
        </table>
        """
        table_location = (offset_y, offset_x)
        folium.Marker(
            location=table_location,
            icon=folium.DivIcon(html=table_html)
        ).add_to(m)

    # --- Add department tables and lines ---
    def add_table(department_code, row, offset_x, offset_y):
        centroid = row['geometry'].centroid
        department_name = row['Département']

        # Determine the background color based on department code
        header_bg_color = "#D6F0F7"  # Default background color

        if department_code == "05":  # Apply red background for Hautes-Alpes
            header_bg_color = "#FF6961"

        # Handle specific columns for percentage and others
        column_mapping = {
            'Taux d\'épargne brute': ('Taux d\'épargne brute 2022', 'Taux d\'épargne brute 2023'),
            'Délai de désendettement': ('Délai de désendettement 2022', 'Délai de désendettement 2023'),
            'Epargne brute par habitant (INSEE)': ('Epargne brute par habitant 2022', 'Epargne brute par habitant 2023'),
            'Epargne nette par habitant (INSEE)': ('Epargne nette par habitant 2022', 'Epargne nette par habitant 2023'),
            'Produits de fonctionnement par habitant (INSEE)': ('Produits de fonctionnement par habitant 2022', 'Produits de fonctionnement par habitant 2023'),
            'Dépenses réelles de fonctionnement par habitant (INSEE)': ('Dépenses réelles de fonctionnement par habitant 2022', 'Dépenses réelles de fonctionnement par habitant 2023'),
            'Population INSEE': ('Population INSEE 2022', 'Population INSEE 2023'),
            'Population DGF': ('Population DGF 2022', 'Population DGF 2023'),
            'Produits de fonctionnement': ('Produits de fonctionnement 2022', 'Produits de fonctionnement 2023'),
            'Dépenses de fonctionnement': ('Dépenses de fonctionnement 2022', 'Dépenses de fonctionnement 2023'),
            'Epargne brute': ('Epargne brute 2022', 'Epargne brute 2023'),
            'Epargne nette': ('Epargne nette 2022', 'Epargne nette 2023'),
            'Dette encours': ('Dette encours 2022', 'Dette encours 2023'),
            'Dette par habitant (INSEE)': ('Dette par habitant 2022', 'Dette par habitant 2023'),
            'Dépenses directes équipement': ('Dépenses directes équipement 2022', 'Dépenses directes équipement 2023'),
            'Dépenses directes équipement par habitant (INSEE)': ('Dépenses directes équipement par habitant 2022', 'Dépenses directes équipement par habitant 2023'),
            'Subventions d\'équipement': ('Subventions d\'équipement 2022', 'Subventions d\'équipement 2023'),
            'Subventions d\'équipement par habitant (INSEE)': ('Subventions d\'équipement par habitant 2022', 'Subventions d\'équipement par habitant 2023')
        }

        if selected_column in column_mapping:
            column_2022, column_2023 = column_mapping[selected_column]
            # Handle values and formats for percentage or raw numbers
            if 'Taux' in selected_column:
                value_2022 = f"{row[column_2022] * 100:,.0f} %".replace(",", " ").replace(".", ",") if pd.notna(row[column_2022]) else "0,00 %"
                value_2023 = f"{row[column_2023] * 100:,.0f} %".replace(",", " ").replace(".", ",") if pd.notna(row[column_2023]) else "0,00 %"
                evolution = f"{(row[column_2023] - row[column_2022]) / row[column_2022] * 100:,.2f} %".replace(",", " ").replace(".", ",") if pd.notna(row[column_2023]) and pd.notna(row[column_2022]) and row[column_2022] != 0 else "N/A"
            else:
                value_2022 = f"{row[column_2022]:,.0f}".replace(",", " ").replace(".", ",") if pd.notna(row[column_2022]) else "0,00"
                value_2023 = f"{row[column_2023]:,.0f}".replace(",", " ").replace(".", ",") if pd.notna(row[column_2023]) else "0,00"
                evolution = f"{(row[column_2023] - row[column_2022]) / row[column_2022] * 100:,.2f} %".replace(",", " ").replace(".", ",") if pd.notna(row[column_2023]) and pd.notna(row[column_2022]) and row[column_2022] != 0 else "N/A"
            # Create the HTML table
            table_html = f"""
            <table style="border: 1px solid black; border-collapse: collapse; background-color: white; width: 200px;">
                <thead style="background-color: {header_bg_color}; color: black;">
                    <tr><th colspan="2" style="text-align: center; font-size: 16px; color: black;">{department_name}</th></tr>
                </thead>
                <tbody>
                    <tr style="border-top: 1px solid black;">
                        <td style="text-align: center; font-size: 16px; font-weight: bold; border-right: 1px solid black; color: black;">2022</td>
                        <td style="text-align: center; font-size: 16px; font-weight: bold; color: black;">{value_2022} €</td>
                    </tr>
                    <tr style="border-top: 1px solid black;">
                        <td style="text-align: center; font-size: 16px; font-weight: bold; border-right: 1px solid black; color:black;">2023</td>
                        <td style="text-align: center; font-size: 16px; font-weight: bold; color:black;">{value_2023} €</td>
                    </tr>
                    <tr style="border-top: 1px solid black;">
                        <td style="text-align: center; font-size: 16px; font-weight: bold; border-right: 1px solid black; color: black;">Evolution</td>
                        <td style="text-align: center; font-size: 16px; font-weight: bold; color: black;">{evolution}</td>
                    </tr>
                </tbody>
            </table>
            """
        else:
            # For other columns, handle as a single value for 2023
            value = f"{int(row[selected_column]):,}".replace(",", " ") if pd.notna(row[selected_column]) else '0'
            table_html = f"""
            <table style="border: 1px solid black; border-collapse: collapse; background-color: white; width: 200px;">
                <thead style="background-color: {header_bg_color}; color: black;">
                    <tr><th colspan="2" style="text-align: center; font-size: 16px; color: black;">{department_name}</th></tr>
                </thead>
                <tbody>
                    <tr style="border-top: 1px solid black;">
                        <td style="text-align: center; font-size: 16px; font-weight: bold; color: black;">{value} €</td>
                    </tr>
                </tbody>
            </table>
            """

        table_location = (centroid.y + offset_y, centroid.x + offset_x)
        folium.Marker(
            location=table_location,
            icon=folium.DivIcon(html=table_html)
        ).add_to(m)

        # Draw line connecting the centroid of the department to the table
        folium.PolyLine(
            locations=[(centroid.y, centroid.x), (table_location[0], table_location[1] + 1.2)],
            color="grey",
            weight=2
        ).add_to(m)

    # Add title
    add_title_table(f"{selected_column}", -14.2, 52)

    # Add tables for each department using the positions specified in department_positions
    for department_code, (offset_x, offset_y) in department_positions.items():
        row = filtered_results[filtered_results['dep'] == department_code].iloc[0]
        add_table(department_code, row, offset_x, offset_y)

    # Add the top table to the map
    create_top_table(selected_column, m)

    # Add logo to the map
    add_logo(m, './logo.png', offset_x=-750, offset_y=50)

    # Display the map in Streamlit
    st_folium(m, width=1400, height=1000)

def create_top_table(selected_column, m):
    # Get all departments for the top table calculation
    all_departments = merged_final.copy()

    column_mapping = {
            'Taux d\'épargne brute': ('Taux d\'épargne brute 2022', 'Taux d\'épargne brute 2023'),
            'Délai de désendettement': ('Délai de désendettement 2022', 'Délai de désendettement 2023'),
            'Epargne brute par habitant (INSEE)': ('Epargne brute par habitant 2022', 'Epargne brute par habitant 2023'),
            'Epargne nette par habitant (INSEE)': ('Epargne nette par habitant 2022', 'Epargne nette par habitant 2023'),
            'Produits de fonctionnement par habitant (INSEE)': ('Produits de fonctionnement par habitant 2022', 'Produits de fonctionnement par habitant 2023'),
            'Dépenses réelles de fonctionnement par habitant (INSEE)': ('Dépenses réelles de fonctionnement par habitant 2022', 'Dépenses réelles de fonctionnement par habitant 2023'),
            'Population INSEE': ('Population INSEE 2022', 'Population INSEE 2023'),
            'Population DGF': ('Population DGF 2022', 'Population DGF 2023'),
            'Produits de fonctionnement': ('Produits de fonctionnement 2022', 'Produits de fonctionnement 2023'),
            'Dépenses de fonctionnement': ('Dépenses de fonctionnement 2022', 'Dépenses de fonctionnement 2023'),
            'Epargne brute': ('Epargne brute 2022', 'Epargne brute 2023'),
            'Epargne nette': ('Epargne nette 2022', 'Epargne nette 2023'),
            'Dette encours': ('Dette encours 2022', 'Dette encours 2023'),
            'Dette par habitant (INSEE)': ('Dette par habitant 2022', 'Dette par habitant 2023'),
            'Dépenses directes équipement': ('Dépenses directes équipement 2022', 'Dépenses directes équipement 2023'),
            'Dépenses directes équipement par habitant (INSEE)': ('Dépenses directes équipement par habitant 2022', 'Dépenses directes équipement par habitant 2023'),
            'Subventions d\'équipement': ('Subventions d\'équipement 2022', 'Subventions d\'équipement 2023'),
            'Subventions d\'équipement par habitant (INSEE)': ('Subventions d\'équipement par habitant 2022', 'Subventions d\'équipement par habitant 2023')
        }

    # Check if the selected column requires evolution calculation
    if selected_column in column_mapping:
        column_2022, column_2023 = column_mapping[selected_column]

        # Calculate the evolution for each department
        all_departments['Metric'] = all_departments.apply(
            lambda row: (row[column_2023] - row[column_2022]) / row[column_2022] * 100 if pd.notna(row[column_2023]) and pd.notna(row[column_2022]) and row[column_2022] != 0 else None,
            axis=1
        )
    else:
        # If it's not an evolution column, just use the 2023 value
        all_departments['Metric'] = all_departments[selected_column]

    # Remove rows with NaN values in the Metric column before ranking
    all_departments = all_departments.dropna(subset=['Metric'])

    # Determine sorting order based on the selected column
    ascending = get_sorting_order(selected_column)

    # Rank departments based on the Metric column
    all_departments['Rank'] = all_departments['Metric'].rank(ascending=ascending, method='min')

    # Get the top 5 departments
    top_5 = all_departments[['Département', 'Metric', 'Rank']].sort_values(by='Metric', ascending=ascending).head(5)
    bottom_3 = all_departments[['Département', 'Metric', 'Rank']].sort_values(by='Metric', ascending=ascending).tail(3)

    # Check if 'Hautes-Alpes' exists in the DataFrame
    if 'Hautes-Alpes' in all_departments['Département'].values:
        hautes_alpes_metric = all_departments.loc[all_departments['Département'] == 'Hautes-Alpes', 'Metric'].values[0]
        hautes_alpes_rank = all_departments.loc[all_departments['Département'] == 'Hautes-Alpes', 'Rank'].values[0]

        # Add 'Hautes-Alpes' to the top 5 DataFrame if it's not already there
    if 'Hautes-Alpes' not in top_5['Département'].values and 'Hautes-Alpes' not in bottom_3['Département'].values:
            top_5 = pd.concat([top_5, pd.DataFrame({'Département': ['Hautes-Alpes'], 'Metric': [hautes_alpes_metric], 'Rank': [hautes_alpes_rank]})], ignore_index=True)

    # Get the bottom 3 departments

    # Create HTML table for the top results
    table_html = f"""
    <table style="border: 1px solid black; border-collapse: collapse; background-color: white; width: 400px;">
        <thead style="background-color: #f0f0f0; color: black;">
            <tr>
                <th style="text-align: center; font-size: 16px; color: black; border-right: 1px solid grey;">Position</th>
                <th style="text-align: center; font-size: 16px; color: black; border-right: 1px solid grey;">Département</th>
                <th style="text-align: center; font-size: 16px; color: black;">{'Evolution' if selected_column in evolution_columns else '2023' if selected_column in value_2023_columns else '2023'}</th>
            </tr>
        </thead>
        <tbody>
    """

    # Add top 5 departments
    for i, row in top_5.iterrows():
        position = int(row['Rank'])
        department_name = row['Département']
        value_to_display = f"{row['Metric']:,.2f} %".replace(",", " ").replace(".", ",") if selected_column in column_mapping else f"{row['Metric']:,.2f}".replace(",", " ").replace(".", ",")
        # Determine row background color (red for 'Hautes-Alpes')
        row_bg_color = "#FF6961" if department_name == 'Hautes-Alpes' else "white"

        table_html += f"""
        <tr style="border-top: 1px solid grey; background-color: {row_bg_color};">
            <td style="text-align: center; font-size: 14px; font-weight: bold; color: black; padding: 2px; border-right: 1px solid grey;">{position}</td>
            <td style="text-align: center; font-size: 14px; font-weight: bold; color: black; padding: 2px; border-right: 1px solid grey;">{department_name}</td>
            <td style="text-align: center; font-size: 14px; font-weight: bold; color: black; padding: 2px;">{value_to_display}</td>
        </tr>
        """

    # Add bottom 3 departments
    for i, row in bottom_3.iterrows():
        position = int(row['Rank'])
        department_name = row['Département']
        value_to_display = f"{row['Metric']:.2f} %".replace(",", " ").replace(".", ",") if selected_column in column_mapping else f"{row['Metric']:,.2f}".replace(",", " ").replace(".", ",")
        row_bg_color = "#FF6961" if department_name == 'Hautes-Alpes' else "white"
        table_html += f"""
        <tr style="border-top: 1px solid grey; background-color: {row_bg_color};">
            <td style="text-align: center; font-size: 14px; font-weight: bold; color: black; padding: 2px; border-right: 1px solid grey;">{position}</td>
            <td style="text-align: center; font-size: 14px; font-weight: bold; color: black; padding: 2px; border-right: 1px solid grey;">{department_name}</td>
            <td style="text-align: center; font-size: 14px; font-weight: bold; color: black; padding: 2px;">{value_to_display}</td>
        </tr>
        """

    table_html += "</tbody></table>"

    # Add the top table to the map
    table_location = (50, -16)  # Adjust the location as needed
    folium.Marker(
        location=[table_location[0], table_location[1]],
        icon=folium.DivIcon(html=table_html)
    ).add_to(m)


# --- Add logo to the map ---
def add_logo(m, image_path, offset_x, offset_y):
    # Convert image to base64
    img_base64 = get_image_base64(image_path)
    
    logo_html = f"""
    <div style="position: absolute; top: {offset_y}px; left: {offset_x}px; width: 250px; height: 250px;">
        <img src="data:image/png;base64,{img_base64}" style="width: 100%; height: 100%; object-fit: contain;">
    </div>
    """
    # Use a folium.Marker to place the logo at a fixed position on the map
    folium.Marker(
        location=[46.5, 2],  # Location is irrelevant because we use absolute positioning in HTML
        icon=folium.DivIcon(html=logo_html)
    ).add_to(m)

# --- Streamlit UI for Column Selection ---
# List of columns to include in the dropdown
column_list = [
    'Taux d\'épargne brute', 
    'Délai de désendettement', 
    'Epargne brute par habitant (INSEE)', 
    'Epargne nette par habitant (INSEE)', 
    'Produits de fonctionnement par habitant (INSEE)', 
    'Dépenses réelles de fonctionnement par habitant (INSEE)', 
    'Prestation de service DGF 2023', 
    'Moyenne dépenses d\'investissement par habitant 2021/2023 (INSEE)', 
    'Moyenne dépenses d\'équipement par habitant 2021/2023 (INSEE)', 
    'Moyenne subventions versées par habitant 2021/2023 (INSEE)', 
    'Moyenne dépenses d\'investissement par habitant 2018/2023 (INSEE)', 
    'Moyenne dépenses d\'équipement par habitant 2018/2023 (INSEE)', 
    'Moyenne subventions versées par habitant 2018/2023 (INSEE)',
    'Population INSEE',
    'Population DGF',
    'Produits de fonctionnement',
    'Dépenses de fonctionnement',
    'Epargne brute',
    'Epargne nette',
    'Dette encours',
    'Dette par habitant (INSEE)',
    'Dépenses directes équipement',
    'Dépenses directes équipement par habitant (INSEE)',
    'Subventions d\'équipement',
    'Subventions d\'équipement par habitant (INSEE)',
]

# List of columns to exclude from the dropdown (add any column names you want to exclude)
columns_to_exclude = [
    'Population INSEE 2022_y', 
    'Population INSEE 2023_y',
    'Population DGF 2022_y',
    'Population DGF 2023_y',
    'Population INSEE 2022_x', 
    'Population INSEE 2023_x',
    'Population DGF 2022_x',
    'Population DGF 2023_x',
    'Encours de dette par habitant 2022',
    'Encours de dette par habitant 2023'
]

# Add columns dynamically based on the filtered_results DataFrame, excluding unwanted columns
column_list += [
    col for col in filtered_results.columns 
    if col not in column_list + columns_to_exclude and 
    col not in [
        'Numéro Département', 'Département', 'dep', 'geometry',
        'Taux d\'épargne brute 2022', 'Taux d\'épargne brute 2023',
        'Délai de désendettement 2022', 'Délai de désendettement 2023',
        'Epargne brute par habitant 2022', 'Epargne brute par habitant 2023',
        'Epargne nette par habitant 2022', 'Epargne nette par habitant 2023',
        'Produits de fonctionnement par habitant 2022', 'Produits de fonctionnement par habitant 2023',
        'Dépenses réelles de fonctionnement par habitant 2022', 'Dépenses réelles de fonctionnement par habitant 2023',
        'Population INSEE 2022', 'Population INSEE 2023',
        'Population DGF 2022', 'Population DGF 2023',
        'Produits de fonctionnement 2022', 'Produits de fonctionnement 2023',
        'Dépenses de fonctionnement 2022', 'Dépenses de fonctionnement 2023',
        'Epargne brute 2022', 'Epargne brute 2023',
        'Epargne nette 2022', 'Epargne nette 2023',
        'Dette encours 2022', 'Dette encours 2023',
        'Dette par habitant 2022', 'Dette par habitant 2023',
        'Dépenses directes équipement 2022', 'Dépenses directes équipement 2023',
        'Dépenses directes équipement par habitant 2022', 'Dépenses directes équipement par habitant 2023',
        'Subventions d\'équipement 2022', 'Subventions d\'équipement 2023',
        'Subventions d\'équipement par habitant 2022', 'Subventions d\'équipement par habitant 2023',
        'reg', 'libgeo'
    ]
]

# Sort the columns in alphabetical order
sorted_column_list = sorted(column_list)

# Create the dropdown menu with sorted columns
selected_column = st.selectbox('Select Column:', sorted_column_list)

# Display the main map with the selected column data
create_map(selected_column)


import streamlit as st
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from PIL import Image
import zipfile
import os
import time
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options


chrome_options = Options()
chrome_options.add_argument('--headless')  # Nécessaire pour l'exécution sur un serveur
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

# URL de votre application Streamlit locale
streamlit_url = 'https://analysedepartements-cd05-pinpon.streamlit.app/'  # Remplacez par le port de votre application Streamlit

# Dossier de stockage des captures
capture_folder = 'captures'
if not os.path.exists(capture_folder):
    os.makedirs(capture_folder)

# Fonction pour prendre les captures d'écran
def take_screenshots():
    driver.get(streamlit_url)
    wait = WebDriverWait(driver, 20)

    # Trouver le menu déroulant et les options
    select_element = wait.until(EC.presence_of_element_located((By.TAG_NAME, 'select')))
    options = select_element.find_elements(By.TAG_NAME, 'option')

    # Limiter aux trois premiers éléments du menu pour le test
    for i in range(min(3, len(options))):  # Limite aux 3 premiers éléments
        option_value = options[i].get_attribute('value')
        
        # Sélectionner l'option
        select = Select(select_element)
        select.select_by_value(option_value)

        # Attendre que la carte soit mise à jour (ajuster le délai si nécessaire)
        time.sleep(5)

        # Prendre une capture d'écran complète
        screenshot_path = os.path.join(capture_folder, f'{option_value}.png')
        driver.save_screenshot('full_screenshot.png')

        # Charger l'image et la rogner pour n'afficher que la carte (ajustez les coordonnées)
        image = Image.open('full_screenshot.png')
        cropped_image = image.crop((100, 200, 1820, 1080))  # Ajustez les coordonnées selon l'emplacement de la carte
        cropped_image.save(screenshot_path)

        st.write(f'Capture d\'écran sauvegardée pour {option_value}.')

# Fonction pour créer un fichier ZIP des captures
def create_zip():
    zip_path = os.path.join(capture_folder, 'captures.zip')
    with zipfile.ZipFile(zip_path, 'w') as zipf:
        for root, _, files in os.walk(capture_folder):
            for file in files:
                if file.endswith('.png'):
                    zipf.write(os.path.join(root, file), file)
    return zip_path

# --- Interface Streamlit ---
st.title("Capture d'écran de la carte")

# Bouton pour lancer les captures
if st.button('Lancer les captures d\'écran'):
    take_screenshots()
    st.success('Captures d\'écran terminées.')

# Bouton pour télécharger le ZIP
if st.button('Télécharger les captures (ZIP)'):
    zip_file = create_zip()
    with open(zip_file, 'rb') as f:
        st.download_button('Télécharger le fichier ZIP', f, file_name='captures.zip')

# Fermer le navigateur à la fin
driver.quit()

