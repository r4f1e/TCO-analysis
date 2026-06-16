def exact_route_held_karp(graph, hub, customers):
    """
    Held-Karp Dynamic Programming TSP : membangun solusi optimal secara bottom-up
    dengan menyimpan hasil subproblem ke dalam tabel dp[mask][i], di mana mask
    adalah bitmask subset pelanggan yang sudah dikunjungi dan i adalah posisi
    terakhir, sehingga setiap subproblem hanya dihitung sekali dan tidak diulang.
    """
    customers = list(customers)
    n = len(customers)

    FULL_MASK = (1 << n) - 1
    INF = float('inf')

    # tabel dp[mask][i] = jarak minimum mengunjungi subset 'mask', berakhir di customers[i]
    dp     = [[INF] * n for _ in range(1 << n)]
    # tabel parent untuk rekonstruksi rute: parent[mask][i] = node sebelum i pada mask ini
    parent = [[-1]  * n for _ in range(1 << n)]

    # base case: dari hub langsung ke masing-masing pelanggan sebagai kunjungan pertama
    for i in range(n):
        dp[1 << i][i] = graph.get_distance(hub, customers[i])

    # isi tabel bottom-up dari subset kecil ke subset besar
    for mask in range(1, 1 << n):
        for i in range(n):
            # skip jika customers[i] tidak ada di subset mask ini
            if not (mask >> i & 1):
                continue
            # skip jika state ini belum pernah dicapai
            if dp[mask][i] == INF:
                continue

            # coba extend ke node j yang belum ada di mask
            for j in range(n):
                if mask >> j & 1:
                    continue  # j sudah dikunjungi, skip

                new_mask = mask | (1 << j)
                new_dist = dp[mask][i] + graph.get_distance(customers[i], customers[j])

                # update jika rute ini lebih pendek
                if new_dist < dp[new_mask][j]:
                    dp[new_mask][j] = new_dist
                    parent[new_mask][j] = i  # catat dari mana datangnya

    # cari node terakhir terbaik pada FULL_MASK sebelum kembali ke hub
    best_dist = INF
    last_node = -1

    for i in range(n):
        if dp[FULL_MASK][i] == INF:
            continue
        total = dp[FULL_MASK][i] + graph.get_distance(customers[i], hub)
        if total < best_dist:
            best_dist = total
            last_node = i

    if last_node == -1:
        return None, INF

    # rekonstruksi rute dengan mundur dari last_node menggunakan tabel parent
    route_indices = []
    mask    = FULL_MASK
    current = last_node

    while current != -1:
        route_indices.append(current)
        prev    = parent[mask][current]
        mask    = mask ^ (1 << current)  # hapus current dari mask
        current = prev

    route_indices.reverse()  # balik karena dibangun dari belakang

    # konversi indeks ke node id asli, tambahkan hub di awal dan akhir
    route = [hub] + [customers[i] for i in route_indices] + [hub]

    return route, best_dist