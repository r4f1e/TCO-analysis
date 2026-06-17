import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.calculate_graph import calculate_graph
from utils.importer import load_simulation_data
from algorithm.heuristic_greedy import greedy_route
from algorithm.exact_bnb import exact_route_bnb

# Wrapper graph
class GraphAdapter:
    def __init__(self, graph_dict):
        self.graph_dict = graph_dict

    def get_distance(self, from_node, to_node):
        return self.graph_dict.get(from_node, {}).get(to_node, float('inf'))

def main():
    # CLI routing
    if len(sys.argv) > 1 and sys.argv[1] == "--calculate-graph":
        calculate_graph()
    else:
        # Load data
        graph_dict, hub_node, customers_list, raw_customer_data = load_simulation_data()
        
        print("Data valid.")
        print(f"Hub: {hub_node}")
        print(f"Total Customer: {len(customers_list)}\n")
        
        # Bungkus dictionary ke dalam adapter
        graph_adapter = GraphAdapter(graph_dict)

        # 1. HEURISTIK GREEDY
        print("Mengeksekusi algoritma Heuristic Greedy...")
        route_greedy = greedy_route(graph_adapter, hub_node, customers_list)

        dist_greedy = 0.0
        for i in range(len(route_greedy) - 1):
            dist_greedy += graph_adapter.get_distance(route_greedy[i], route_greedy[i+1])

        print("\n=== HASIL RUTE GREEDY ===")
        for i, location in enumerate(route_greedy):
            print(f"{i}. {location}")
        print(f"\nTotal Jarak Tempuh (Greedy): {dist_greedy:.2f} km\n")
        print("-" * 40)

        # 2. EXACT BRANCH AND BOUND
        print("\nMengeksekusi algoritma Exact (Branch and Bound)...")
        route_exact, dist_exact = exact_route_bnb(graph_adapter, hub_node, customers_list)

        print("\n=== HASIL RUTE EXACT (B&B) ===")
        for i, location in enumerate(route_exact):
            print(f"{i}. {location}")
        print(f"\nTotal Jarak Tempuh (Exact) : {dist_exact:.2f} km")

if __name__ == "__main__":
    main()