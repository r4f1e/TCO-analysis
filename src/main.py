import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.calculate_graph import calculate_graph
from utils.importer import load_simulation_data

def main():
    # CLI routing
    if len(sys.argv) > 1 and sys.argv[1] == "--calculate-graph":
        calculate_graph()
    else:
        # Load data
        graph, hub_node, customers_list, raw_customer_data = load_simulation_data()
        
        print("Data valid.")
        print(f"Hub: {hub_node}")
        print(f"Total Customer: {len(customers_list)}")

if __name__ == "__main__":
    main()