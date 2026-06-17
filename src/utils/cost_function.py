RATIO_FULL  = 0.05  # liter per km saat beban maksimal
RATIO_EMPTY = 0.02  # liter per km saat beban kosong


def calculate_fuel_cost(route, graph, customer_data, fuel_price):
    """
    Hitung biaya BBM sepanjang rute dengan beban yang berkurang setiap kali
    kurir selesai mengantarkan paket ke satu lokasi customer.

    Rasio konsumsi bersifat linear terhadap beban:
        ratio = RATIO_EMPTY + (beban_sekarang / total_beban) * (RATIO_FULL - RATIO_EMPTY)
    """
    demand_map = {c["name"]: c["demand_kg"] for c in customer_data}
    total_load = sum(demand_map.values())

    current_load = total_load
    total_cost = 0.0

    for i in range(len(route) - 1):
        origin = route[i]
        dest   = route[i + 1]

        distance = graph.get_distance(origin, dest)

        # rasio konsumsi berdasarkan beban sebelum tiba di tujuan
        if total_load > 0:
            ratio = RATIO_EMPTY + (current_load / total_load) * (RATIO_FULL - RATIO_EMPTY)
        else:
            ratio = RATIO_EMPTY

        total_cost += distance * ratio * fuel_price

        # setelah tiba di customer, turunkan beban paket-nya
        if dest in demand_map:
            current_load -= demand_map[dest]

    return total_cost
