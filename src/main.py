import sys
import os
import time
import json

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.calculate_graph import calculate_graph
from utils.importer import load_simulation_data
from utils.cost_function import calculate_fuel_cost
from utils.tco import calculate_tco
from algorithm.heuristic_greedy import greedy_route
from algorithm.exact_bnb import exact_route_bnb


class GraphAdapter:
    def __init__(self, graph_dict):
        self.graph_dict = graph_dict

    def get_distance(self, from_node, to_node):
        return self.graph_dict.get(from_node, {}).get(to_node, float('inf'))


def load_scenario(scenario_key):
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    scenario_path = os.path.join(base_dir, 'data', 'scenarios.json')

    try:
        with open(scenario_path, 'r') as f:
            scenarios = json.load(f)
    except FileNotFoundError:
        print(f"File tidak ditemukan: {scenario_path}")
        sys.exit(1)

    if scenario_key not in scenarios:
        print(f"Skenario '{scenario_key}' tidak dikenal. Pilihan: {', '.join(scenarios.keys())}")
        sys.exit(1)

    return scenarios[scenario_key]


def parse_args():
    scenario_key = None
    i = 1
    while i < len(sys.argv):
        if sys.argv[i] == "--calculate-graph":
            return "calculate-graph", None
        if sys.argv[i] == "--scenario" and i + 1 < len(sys.argv):
            scenario_key = sys.argv[i + 1]
            i += 2
            continue
        i += 1

    if scenario_key is None:
        print("Penggunaan: python src/main.py --scenario <subsidi|krisis>")
        print("            python src/main.py --calculate-graph")
        sys.exit(1)

    return "simulate", scenario_key


def run_simulation(scenario_key):
    scenario = load_scenario(scenario_key)
    fuel_price = scenario["fuel_price_rp_per_liter"]

    graph_dict, hub_node, customers_list, raw_customer_data = load_simulation_data()

    print(f"\nSkenario   : {scenario['label']}")
    print(f"Harga BBM  : Rp {fuel_price:,}/liter")
    print(f"Hub        : {hub_node}")
    print(f"Customer   : {len(customers_list)} lokasi\n")

    graph_adapter = GraphAdapter(graph_dict)

    # --- HEURISTIK GREEDY ---
    print("Mengeksekusi Heuristic Greedy...")
    t_start = time.perf_counter()
    route_greedy, dist_greedy = greedy_route(graph_adapter, hub_node, customers_list)
    elapsed_greedy = time.perf_counter() - t_start

    fuel_greedy = calculate_fuel_cost(route_greedy, graph_adapter, raw_customer_data, fuel_price)
    tco_greedy  = calculate_tco(fuel_greedy, elapsed_greedy)

    # --- EXACT BRANCH AND BOUND ---
    print("Mengeksekusi Exact Branch and Bound...")
    t_start = time.perf_counter()
    route_exact, dist_exact = exact_route_bnb(graph_adapter, hub_node, customers_list)
    elapsed_exact = time.perf_counter() - t_start

    fuel_exact = calculate_fuel_cost(route_exact, graph_adapter, raw_customer_data, fuel_price)
    tco_exact  = calculate_tco(fuel_exact, elapsed_exact)

    return {
        "scenario": scenario,
        "greedy": {
            "route":   route_greedy,
            "dist":    dist_greedy,
            "elapsed": elapsed_greedy,
            "tco":     tco_greedy,
        },
        "exact": {
            "route":   route_exact,
            "dist":    dist_exact,
            "elapsed": elapsed_exact,
            "tco":     tco_exact,
        },
    }


def print_results(result):
    scenario = result["scenario"]
    g = result["greedy"]
    e = result["exact"]

    W = 62
    print("\n" + "=" * W)
    print(f"  HASIL SIMULASI - {scenario['label'].upper()}")
    print(f"  Harga BBM: Rp {scenario['fuel_price_rp_per_liter']:,}/liter")
    print("=" * W)

    for label, data in [("HEURISTIC GREEDY", g), ("EXACT (Branch & Bound)", e)]:
        tco = data["tco"]
        print(f"\n  [{label}]")
        route_str = " -> ".join(data["route"])
        print(f"  Rute    : {route_str}")
        print(f"  Jarak   : {data['dist']:.2f} km")
        print(f"  Waktu   : {data['elapsed']:.6f} detik")
        print(f"  BBM     : Rp {tco['fuel_cost']:>10,.0f}")
        print(f"  Komput. : Rp {tco['compute_cost']:>10,.2f}")
        print(f"  TCO     : Rp {tco['tco']:>10,.2f}")

    print("\n" + "-" * W)
    winner = "Heuristic Greedy" if g["tco"]["tco"] <= e["tco"]["tco"] else "Exact (B&B)"
    selisih = abs(g["tco"]["tco"] - e["tco"]["tco"])
    print(f"  Rekomendasi: {winner} lebih hemat (selisih TCO Rp {selisih:,.2f})")
    print("=" * W)


def main():
    mode, scenario_key = parse_args()

    if mode == "calculate-graph":
        calculate_graph()
        return

    result = run_simulation(scenario_key)
    print_results(result)


if __name__ == "__main__":
    main()
