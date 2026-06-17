import sys
import os
import time

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.calculate_graph import calculate_graph
from utils.importer import load_simulation_data
from utils.cost_function import calculate_fuel_cost
from algorithm.heuristic_greedy import greedy_route
from algorithm.exact_bnb import exact_route_bnb


class GraphAdapter:
    def __init__(self, graph_dict):
        self.graph_dict = graph_dict

    def get_distance(self, from_node, to_node):
        return self.graph_dict.get(from_node, {}).get(to_node, float('inf'))


def main():
    # CLI routing
    if len(sys.argv) > 1 and sys.argv[1] == "--calculate-graph":
        calculate_graph()
        return

    # Load data
    graph_dict, hub_node, customers_list, raw_customer_data = load_simulation_data()

    print("Data valid.")
    print(f"Hub: {hub_node}")
    print(f"Total Customer: {len(customers_list)}\n")

    graph_adapter = GraphAdapter(graph_dict)

    # --- HEURISTIK GREEDY ---
    print("Mengeksekusi algoritma Heuristic Greedy...")
    t_start = time.perf_counter()
    route_greedy, dist_greedy = greedy_route(graph_adapter, hub_node, customers_list)
    elapsed_greedy = time.perf_counter() - t_start

    print("\n=== HASIL RUTE GREEDY ===")
    for i, location in enumerate(route_greedy):
        print(f"  {i}. {location}")
    print(f"\n  Total Jarak Tempuh : {dist_greedy:.2f} km")
    print(f"  Waktu Eksekusi     : {elapsed_greedy:.6f} detik")
    print("-" * 50)

    # --- EXACT BRANCH AND BOUND ---
    print("\nMengeksekusi algoritma Exact (Branch and Bound)...")
    t_start = time.perf_counter()
    route_exact, dist_exact = exact_route_bnb(graph_adapter, hub_node, customers_list)
    elapsed_exact = time.perf_counter() - t_start

    print("\n=== HASIL RUTE EXACT (B&B) ===")
    for i, location in enumerate(route_exact):
        print(f"  {i}. {location}")
    print(f"\n  Total Jarak Tempuh : {dist_exact:.2f} km")
    print(f"  Waktu Eksekusi     : {elapsed_exact:.6f} detik")
    print("-" * 50)

    # --- DEMO COST FUNCTION (placeholder harga BBM, diganti Tahap 2) ---
    fuel_price_demo = 10000  # Rp/liter — akan diganti oleh --scenario
    fuel_greedy = calculate_fuel_cost(route_greedy, graph_adapter, raw_customer_data, fuel_price_demo)
    fuel_exact  = calculate_fuel_cost(route_exact,  graph_adapter, raw_customer_data, fuel_price_demo)

    print(f"\n[Demo Biaya BBM @ Rp {fuel_price_demo:,}/L]")
    print(f"  Greedy : Rp {fuel_greedy:,.0f}")
    print(f"  Exact  : Rp {fuel_exact:,.0f}")


if __name__ == "__main__":
    main()