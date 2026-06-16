def exact_route_bnb(graph, hub, customers):
    """
    Branch and Bound TSP : eksplorasi semua permutasi rute secara rekursif,
    memangkas cabang menggunakan lower bound estimasi sisa perjalanan minimum.
    """
    customers = list(customers)
    n = len(customers)
    best = {'route': None, 'distance': float('inf')}

    def _lower_bound(current_node, visited_mask, dist_so_far):
        bound = dist_so_far

        # kumpulkan node yang belum dikunjungi via bitmask
        unvisited_nodes = [
            customers[idx]
            for idx in range(n)
            if not (visited_mask >> idx & 1)
        ]

        # semua sudah dikunjungi, tinggal balik ke hub
        if not unvisited_nodes:
            return bound + graph.get_distance(current_node, hub)

        # tambahkan edge terkecil dari posisi saat ini ke node belum dikunjungi
        min_from_current = float('inf')
        for node in unvisited_nodes:
            d = graph.get_distance(current_node, node)
            if d < min_from_current:
                min_from_current = d
        bound += min_from_current

        # untuk tiap node belum dikunjungi, tambahkan edge terkecil yang keluar
        all_targets = unvisited_nodes + [hub]
        for node in unvisited_nodes:
            min_edge = float('inf')
            for neighbor in all_targets:
                if neighbor == node:
                    continue
                d = graph.get_distance(node, neighbor)
                if d < min_edge:
                    min_edge = d
            bound += min_edge

        return bound

    def _backtrack(current_node, visited_mask, path, dist_so_far):
        # base case: semua pelanggan sudah masuk path
        if len(path) == n + 1:
            total = dist_so_far + graph.get_distance(current_node, hub)
            if total < best['distance']:
                best['distance'] = total
                best['route'] = path + [hub]
            return

        for idx in range(n):
            # skip node yang sudah dikunjungi
            if visited_mask >> idx & 1:
                continue

            next_node = customers[idx]
            new_dist  = dist_so_far + graph.get_distance(current_node, next_node)
            new_mask  = visited_mask | (1 << idx)

            # pruning: buang cabang jika lower bound >= solusi terbaik saat ini
            if _lower_bound(next_node, new_mask, new_dist) >= best['distance']:
                continue

            _backtrack(next_node, new_mask, path + [next_node], new_dist)

    _backtrack(hub, 0, [hub], 0.0)
    return best['route'], best['distance']