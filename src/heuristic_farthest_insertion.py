def farthest_insertion_route(graph, hub, customers):
    """
    Farthest Insertion Heuristic: Membangun rute dengan menyisipkan 
    pelanggan terjauh ke dalam sub-rute secara bertahap.
    """
    unvisited = list(customers)
    route = [hub, hub]  # Memulai sub-rute awal: Hub -> Hub
    
    # Langkah 1: Cari pelanggan pertama yang paling jauh dari Hub untuk memulai lingkaran
    farthest_node = None
    max_dist = -1
    for node in unvisited:
        d = graph.get_distance(hub, node)
        if d > max_dist:
            max_dist = d
            farthest_node = node
            
    route.insert(1, farthest_node)
    unvisited.remove(farthest_node)
    
    # Langkah 2: Masukkan sisa pelanggan satu per satu
    while unvisited:
        # Cari pelanggan 'k' yang memiliki jarak TERJAUH ke rute saat ini
        next_node = None
        max_to_route = -1
        
        for node in unvisited:
            # Jarak terdekat dari 'node' ke salah satu kota di dalam rute saat ini
            min_to_route = min(graph.get_distance(node, r_node) for r_node in route[:-1])
            if min_to_route > max_to_route:
                max_to_route = min_to_route
                next_node = node
                
        # Cari posisi penyisipan terbaik untuk 'next_node' di dalam rute
        best_idx = 1
        min_insertion_cost = float('inf')
        
        for i in range(len(route) - 1):
            # Hitung pembengkakan jarak jika disisipkan di antara indeks i dan i+1
            cost = (graph.get_distance(route[i], next_node) + 
                    graph.get_distance(next_node, route[i+1]) - 
                    graph.get_distance(route[i], route[i+1]))
            if cost < min_insertion_cost:
                min_insertion_cost = cost
                best_idx = i + 1
                
        # Sisipkan pelanggan terpilih ke posisi terbaiknya
        route.insert(best_idx, next_node)
        unvisited.remove(next_node)
        
    return route