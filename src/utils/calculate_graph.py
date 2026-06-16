import json
import requests
import pandas as pd
import sys
import os

def calculate_graph():
    # Setup path
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    lokasi_path = os.path.join(base_dir, 'data', 'lokasi.json')
    generated_dir = os.path.join(base_dir, 'data', 'generated')
    graph_path = os.path.join(generated_dir, 'graph.csv')

    # Load lokasi
    try:
        with open(lokasi_path, 'r') as f:
            lokasi_data = json.load(f)
    except FileNotFoundError:
        print(f"File tidak ditemukan: {lokasi_path}")
        sys.exit(1)

    hub_node = next((loc for loc in lokasi_data if loc.get("type") == "hub"), None)
    if not hub_node:
        print("Hub tidak ditemukan di lokasi.json.")
        sys.exit(1)

    ordered_nodes = [hub_node] + [loc for loc in lokasi_data if loc.get("type") != "hub"]
    coord_string = ";".join([f"{node['lon']},{node['lat']}" for node in ordered_nodes])
    
    # Fetch jarak dengan OSRM
    url = f"http://router.project-osrm.org/table/v1/driving/{coord_string}?annotations=distance"

    try:
        response = requests.get(url, timeout=15)
        data = response.json()

        if data.get("code") == "Ok":
            distance_matrix = [[round(dist / 1000, 2) for dist in row] for row in data["distances"]]
            node_names = [node["name"] for node in ordered_nodes]

            # Export CSV
            os.makedirs(generated_dir, exist_ok=True)
            df = pd.DataFrame(distance_matrix, index=node_names, columns=node_names)
            df.to_csv(graph_path)

            print(f"Graph tersimpan di {graph_path}")
        else:
            print(f"OSRM Error: {data.get('code')}")
    except Exception as e:
        print(f"Error: {e}")