# File: src/simulated_annealing/simulated_annealing.py

import math
import random
import copy
from .objective_function import objective_function
from .generate_neighbor import generate_neighbor

def simulated_annealing(
    jadwal_awal, suhu_awal, laju_pendinginan, suhu_akhir,
    kelas_mata_kuliah, ruangan, mahasiswa, hari
):
    suhu_sekarang = suhu_awal
    jadwal_sekarang = copy.deepcopy(jadwal_awal)
    penalti_sekarang = objective_function(jadwal_sekarang, kelas_mata_kuliah, ruangan, mahasiswa)

    jadwal_terbaik = copy.deepcopy(jadwal_awal)
    penalti_terbaik = penalti_sekarang

    history = {
        'penalti_sekarang_per_iterasi': [penalti_sekarang],
        'penalti_terbaik_per_iterasi': [penalti_terbaik],
        'probabilitas_penerimaan': [],
        'periode_stagnasi': []
    }
    iterasi_tanpa_peningkatan = 0

    while suhu_sekarang > suhu_akhir:
        jadwal_tetangga = generate_neighbor(jadwal_sekarang, ruangan, hari)
        penalti_tetangga = objective_function(jadwal_tetangga, kelas_mata_kuliah, ruangan, mahasiswa)
        selisih_penalti = penalti_tetangga - penalti_sekarang

        prob_val = None
        if selisih_penalti < 0 or (selisih_penalti >= 0 and random.random() < (prob_val := math.exp(-selisih_penalti / suhu_sekarang))):
            jadwal_sekarang = jadwal_tetangga
            penalti_sekarang = penalti_tetangga
        
        history['probabilitas_penerimaan'].append(prob_val)

        if penalti_sekarang < penalti_terbaik:
            penalti_terbaik = penalti_sekarang
            jadwal_terbaik = copy.deepcopy(jadwal_sekarang)
            if iterasi_tanpa_peningkatan > 0:
                history['periode_stagnasi'].append(iterasi_tanpa_peningkatan)
            iterasi_tanpa_peningkatan = 0 
        else:
            iterasi_tanpa_peningkatan += 1

        history['penalti_sekarang_per_iterasi'].append(penalti_sekarang)
        history['penalti_terbaik_per_iterasi'].append(penalti_terbaik)

        if penalti_terbaik == 0:
            print("\nInfo: Solusi optimal (penalti = 0) ditemukan.")
            break

        suhu_sekarang *= laju_pendinginan

    if iterasi_tanpa_peningkatan > 0:
        history['periode_stagnasi'].append(iterasi_tanpa_peningkatan)

    return jadwal_terbaik, penalti_terbaik, history