import json
import pandas as pd
import sys
import os

def load_simulation_data():
    # Setup path
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    graph_path = os.path.join(base_dir, 'data', 'generated', 'graph.csv')
    customer_path = os.path.join(base_dir, 'data', 'customer.json')

    # Load graph
    try:
        df_graph = pd.read_csv(graph_path, index_col=0)
        graph = df_graph.to_dict(orient='index')
    except FileNotFoundError:
        print(f"File tidak ditemukan: {graph_path}. Run --calculate-graph dulu.")
        sys.exit(1)

    # Load customer
    try:
        with open(customer_path, 'r') as f:
            customer_data = json.load(f)
    except FileNotFoundError:
        print(f"File tidak ditemukan: {customer_path}")
        sys.exit(1)

    # Validasi node
    customers_list = [cust["name"] for cust in customer_data]
    available_nodes = list(graph.keys())

    for cust in customers_list:
        if cust not in available_nodes:
            print(f"Customer {cust} tidak ada di graph.csv.")
            sys.exit(1)


    hub_node = available_nodes[0]

    return graph, hub_node, customers_list, customer_data