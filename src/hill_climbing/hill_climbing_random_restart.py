import copy
import matplotlib.pyplot as plt

from simulated_annealing.objective_function import objective_function
from hill_climbing.generate_all_neighbors import generate_all_neighbors 
from genetic_algorithm.preprocess import generate_population

def print_schedule_simple(jadwal, title="SCHEDULE"):
    print(f"\n{'='*80}")
    print(f"{title:^80}")
    print(f"{'='*80}")
    print(f"{'Kode':<15} {'Ruangan':<15} {'Hari':<10} {'Jam':<15}")
    print('-'*80)
    for sesi in jadwal:
        print(f"{sesi['kode']:<15} {sesi['ruangan']:<15} {sesi['hari']:<10} "
              f"{sesi['waktu_mulai']}-{sesi['waktu_selesai']:<15}")
    print('='*80)

def hill_climbing_steepest_once(jadwal_awal, kelas_mata_kuliah, ruangan, mahasiswa, hari,
                                objective_function, max_neighbors=500):
    jadwal_sekarang = copy.deepcopy(jadwal_awal)
    penalti_sekarang = objective_function(jadwal_sekarang, kelas_mata_kuliah, ruangan, mahasiswa)
    history = {'iterasi': [0], 'penalti': [penalti_sekarang]}
    iterasi = 0
    while True:
        semua_tetangga = generate_all_neighbors(jadwal_sekarang, ruangan, hari, max_neighbors=max_neighbors)
        if not semua_tetangga: break
        tetangga_terbaik = None
        penalti_terbaik_tetangga = penalti_sekarang
        for tetangga in semua_tetangga:
            penalti_tetangga = objective_function(tetangga, kelas_mata_kuliah, ruangan, mahasiswa)
            if penalti_tetangga < penalti_terbaik_tetangga:
                penalti_terbaik_tetangga = penalti_tetangga
                tetangga_terbaik = tetangga
        
        if penalti_terbaik_tetangga < penalti_sekarang:
            jadwal_sekarang = tetangga_terbaik
            penalti_sekarang = penalti_terbaik_tetangga
            iterasi += 1
            history['iterasi'].append(iterasi)
            history['penalti'].append(penalti_sekarang)
            if penalti_sekarang == 0: break
        else:
            break
    return jadwal_sekarang, penalti_sekarang, iterasi, history

def hill_climbing_random_restart_procedure(
    kelas_mata_kuliah, ruangan, mahasiswa, hari,
    objective_function, max_neighbors, max_restart
):
    jadwal_terbaik_global = None
    penalti_terbaik_global = float('inf')
    restart_stats = []
    restart_histories = []

    for restart in range(max_restart):
        print(f"\n--- RESTART {restart + 1}/{max_restart} ---")

        jadwal_restart = generate_population(kelas_mata_kuliah, ruangan, hari)
        penalti_restart = objective_function(jadwal_restart, kelas_mata_kuliah, ruangan, mahasiswa)
        
        print(f"\nInitial State:")
        print_schedule_simple(jadwal_restart, "INITIAL STATE")
        print(f"\nInitial Objective Function: {penalti_restart}")
        
        print(f"Penalty awal: {penalti_restart}")

        jadwal_hasil, penalti_hasil, iterasi, history = hill_climbing_steepest_once(
            jadwal_restart, kelas_mata_kuliah, ruangan, mahasiswa, hari,
            objective_function, max_neighbors
        )
        print(f"Penalty akhir: {penalti_hasil} (iterasi: {iterasi})")

        restart_stats.append({
            'restart': restart + 1,
            'initial_penalty': penalti_restart,
            'final_penalty': penalti_hasil,
            'iterations': iterasi
        })
        restart_histories.append(history)

        if penalti_hasil < penalti_terbaik_global:
            penalti_terbaik_global = penalti_hasil
            jadwal_terbaik_global = jadwal_hasil

        if penalti_hasil == 0:
            break

    return jadwal_terbaik_global, penalti_terbaik_global, restart_stats, restart_histories