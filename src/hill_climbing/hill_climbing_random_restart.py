import copy
import time
import random
import matplotlib.pyplot as plt

from simulated_annealing.objective_function import objective_function
from hill_climbing.generate_all_neighbors import generate_all_neighbors 

def generate_random_schedule(kelas_mata_kuliah, ruangan, hari):
    jadwal = []
    for kelas in kelas_mata_kuliah:
        sks = kelas.get('sks', 1)
        sesi = {
            'kode': kelas['kode'],
            'ruangan': random.choice(ruangan)['kode'],
            'hari': random.choice(hari),
            'waktu_mulai': random.randint(7, 18 - sks),
        }
        sesi['waktu_selesai'] = sesi['waktu_mulai'] + sks
        jadwal.append(sesi)
    return jadwal

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

        jadwal_restart = generate_random_schedule(kelas_mata_kuliah, ruangan, hari)
        penalti_restart = objective_function(jadwal_restart, kelas_mata_kuliah, ruangan, mahasiswa)
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