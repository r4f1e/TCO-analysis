def greedy_route(graph, hub, customers):
    """
    Nearest Neighbor Heuristic: selalu pergi ke pelanggan terdekat yang belum dikunjungi.
    Garansi: cepat, O(n²). Tidak garansi optimal.
    """
    unvisited = list(customers)
    route = [hub]
    current = hub

    while unvisited:
        nearest = None
        min_dist = float('inf')
        for node in unvisited:
            d = graph.get_distance(current, node)
            if d < min_dist:
                min_dist = d
                nearest = node
        route.append(nearest)
        unvisited.remove(nearest)
        current = nearest

    route.append(hub)
    return route