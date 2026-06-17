COMPUTE_COST_PER_MS = 50  # Rp per milidetik eksekusi server


def calculate_tco(fuel_cost, elapsed_seconds):
    """
    Hitung Total Cost of Ownership (TCO) untuk satu eksekusi algoritma.

    TCO = Biaya BBM + Biaya Komputasi
    Biaya Komputasi = waktu_eksekusi_ms × Rp50
    """
    compute_cost = (elapsed_seconds * 1000) * COMPUTE_COST_PER_MS

    return {
        "fuel_cost":    fuel_cost,
        "compute_cost": compute_cost,
        "tco":          fuel_cost + compute_cost,
    }
