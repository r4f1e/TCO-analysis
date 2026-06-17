def nearest_insertion_route(graph, hub, customers):
    """
    Nearest Insertion Heuristic: Membangun rute dengan menyisipkan
    pelanggan terdekat ke dalam sub-rute secara bertahap.
    """
    unvisited = list(customers)
    route = [hub, hub]  # Memulai sub-rute awal: Hub -> Hub
    
    # Langkah 1: Cari pelanggan pertama yang paling dekat dengan Hub
    nearest_node = None
    min_dist = float('inf')
    for node in unvisited:
        d = graph.get_distance(hub, node)
        if d < min_dist:
            min_dist = d
            nearest_node = node
            
    route.insert(1, nearest_node)
    unvisited.remove(nearest_node)
    
    # Langkah 2: Masukkan sisa pelanggan
    while unvisited:
        # Cari pelanggan 'k' yang memiliki jarak TERDEKAT ke rute saat ini
        next_node = None
        min_to_route = float('inf')
        
        for node in unvisited:
            min_dist_curr = min(graph.get_distance(node, r_node) for r_node in route[:-1])
            if min_dist_curr < min_to_route:
                min_to_route = min_dist_curr
                next_node = node
                
        # Cari posisi penyisipan terbaik
        best_idx = 1
        min_insertion_cost = float('inf')
        
        for i in range(len(route) - 1):
            cost = (graph.get_distance(route[i], next_node) + 
                    graph.get_distance(next_node, route[i+1]) - 
                    graph.get_distance(route[i], route[i+1]))
            if cost < min_insertion_cost:
                min_insertion_cost = cost
                best_idx = i + 1
                
        route.insert(best_idx, next_node)
        unvisited.remove(next_node)
        
    # Hitung total jarak rute hasil akhir
    total_distance = sum(graph.get_distance(route[i], route[i+1]) for i in range(len(route) - 1))
        
    return route, total_distance