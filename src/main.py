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


def load_scenarios():
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    scenario_path = os.path.join(base_dir, 'data', 'scenarios.json')

    try:
        with open(scenario_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"File tidak ditemukan: {scenario_path}")
        sys.exit(1)


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
    return "simulate", scenario_key  # None = jalankan semua skenario


def run_scenario(scenario_key, scenario, graph_adapter, hub_node, customers_list, raw_customer_data):
    fuel_price = scenario["fuel_price_rp_per_liter"]

    t_start = time.perf_counter()
    route_greedy, dist_greedy = greedy_route(graph_adapter, hub_node, customers_list)
    elapsed_greedy = time.perf_counter() - t_start

    fuel_greedy = calculate_fuel_cost(route_greedy, graph_adapter, raw_customer_data, fuel_price)
    tco_greedy  = calculate_tco(fuel_greedy, elapsed_greedy)

    t_start = time.perf_counter()
    route_exact, dist_exact = exact_route_bnb(graph_adapter, hub_node, customers_list)
    elapsed_exact = time.perf_counter() - t_start

    fuel_exact = calculate_fuel_cost(route_exact, graph_adapter, raw_customer_data, fuel_price)
    tco_exact  = calculate_tco(fuel_exact, elapsed_exact)

    return {
        "key":      scenario_key,
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


def print_scenario_detail(result):
    scenario = result["scenario"]
    g = result["greedy"]
    e = result["exact"]
    W = 70

    print("\n" + "=" * W)
    print(f"  SKENARIO: {scenario['label'].upper()}")
    print(f"  Harga BBM: Rp {scenario['fuel_price_rp_per_liter']:,}/liter")
    print("=" * W)

    for label, data in [("HEURISTIC GREEDY", g), ("EXACT (Branch & Bound)", e)]:
        tco = data["tco"]
        route_str = " -> ".join(data["route"])
        print(f"\n  [{label}]")
        print(f"  Rute    : {route_str}")
        print(f"  Jarak   : {data['dist']:.2f} km")
        print(f"  Waktu   : {data['elapsed']:.6f} detik")
        print(f"  BBM     : Rp {tco['fuel_cost']:>12,.0f}")
        print(f"  Komput. : Rp {tco['compute_cost']:>12,.2f}")
        print(f"  TCO     : Rp {tco['tco']:>12,.2f}")


def print_comparison_table(results):
    W = 70
    print("\n\n" + "=" * W)
    print("  TABEL KOMPARASI TCO - SEMUA SKENARIO")
    print("=" * W)

    labels = {r["key"]: r["scenario"]["label"] for r in results}
    col_w = 22

    # Header
    header = f"  {'Metrik':<20}"
    for r in results:
        header += f"  {r['scenario']['label'][:col_w]:<{col_w}}"
    print(header)
    print("  " + "-" * (W - 2))

    # Rows
    rows = [
        ("Algoritma",     lambda r, k: k),
        ("Jarak (km)",    lambda r, k: f"{r[k]['dist']:.2f}"),
        ("Waktu (detik)", lambda r, k: f"{r[k]['elapsed']:.6f}"),
        ("Biaya BBM",     lambda r, k: f"Rp {r[k]['tco']['fuel_cost']:,.0f}"),
        ("Biaya Komput.", lambda r, k: f"Rp {r[k]['tco']['compute_cost']:,.2f}"),
        ("TCO",           lambda r, k: f"Rp {r[k]['tco']['tco']:,.2f}"),
    ]

    for algo_key, algo_label in [("greedy", "Heuristic Greedy"), ("exact", "Exact B&B")]:
        print(f"\n  >> {algo_label}")
        for row_label, extractor in rows[1:]:
            line = f"  {row_label:<20}"
            for r in results:
                val = extractor(r, algo_key)
                line += f"  {val:<{col_w}}"
            print(line)

    # Rekomendasi per skenario
    print("\n" + "  " + "-" * (W - 2))
    print("  REKOMENDASI PER SKENARIO")
    print("  " + "-" * (W - 2))

    for r in results:
        g_tco = r["greedy"]["tco"]["tco"]
        e_tco = r["exact"]["tco"]["tco"]
        selisih = abs(g_tco - e_tco)
        winner = "Heuristic Greedy" if g_tco <= e_tco else "Exact B&B"
        print(f"  {r['scenario']['label']:<30}: {winner} (selisih TCO Rp {selisih:,.2f})")

    # Break-even analysis
    print("\n" + "  " + "-" * (W - 2))
    print("  ANALISIS BREAK-EVEN")
    print("  " + "-" * (W - 2))

    # Ambil liter dari salah satu skenario untuk hitung break-even
    # fuel_cost = price * liters  =>  liters = fuel_cost / price
    ref = results[0]
    ref_price = ref["scenario"]["fuel_price_rp_per_liter"]
    liters_greedy = ref["greedy"]["tco"]["fuel_cost"] / ref_price
    liters_exact  = ref["exact"]["tco"]["fuel_cost"]  / ref_price
    delta_liters  = liters_greedy - liters_exact  # greedy pakai lebih banyak

    avg_compute_exact  = sum(r["exact"]["tco"]["compute_cost"]  for r in results) / len(results)
    avg_compute_greedy = sum(r["greedy"]["tco"]["compute_cost"] for r in results) / len(results)
    delta_compute = avg_compute_exact - avg_compute_greedy  # exact lebih mahal

    if delta_liters > 0:
        breakeven_price = delta_compute / delta_liters
        print(f"  Selisih konsumsi BBM : {delta_liters:.4f} liter (Greedy boros)")
        print(f"  Selisih biaya komput.: Rp {delta_compute:,.2f} (Exact lebih mahal)")
        print(f"  Break-even harga BBM : Rp {breakeven_price:,.0f}/liter")
        print(f"  => Exact baru menguntungkan jika harga BBM > Rp {breakeven_price:,.0f}/liter")
    else:
        print("  Break-even tidak dapat dihitung (selisih liter = 0)")

    print("=" * W)


def main():
    mode, scenario_key = parse_args()

    if mode == "calculate-graph":
        calculate_graph()
        return

    scenarios = load_scenarios()

    if scenario_key is not None and scenario_key not in scenarios:
        print(f"Skenario '{scenario_key}' tidak dikenal. Pilihan: {', '.join(scenarios.keys())}")
        sys.exit(1)

    # Tentukan skenario yang akan dijalankan
    keys_to_run = [scenario_key] if scenario_key else list(scenarios.keys())

    graph_dict, hub_node, customers_list, raw_customer_data = load_simulation_data()
    graph_adapter = GraphAdapter(graph_dict)

    print(f"Hub      : {hub_node}")
    print(f"Customer : {len(customers_list)} lokasi")

    results = []
    for key in keys_to_run:
        print(f"\nMenjalankan skenario '{key}'...")
        r = run_scenario(key, scenarios[key], graph_adapter, hub_node, customers_list, raw_customer_data)
        results.append(r)
        print_scenario_detail(r)

    # Tampilkan tabel komparasi hanya jika ada lebih dari satu skenario
    if len(results) > 1:
        print_comparison_table(results)


if __name__ == "__main__":
    main()
