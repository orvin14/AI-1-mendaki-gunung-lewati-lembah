import copy
import time
from hill_climbing.generate_all_neighbors import generate_all_neighbors


def hill_climbing_sideways_procedure(jadwal_awal, kelas_mata_kuliah, ruangan, mahasiswa, hari, 
                                     objective_function, max_neighbors=500, max_sideways=100):
    
    jadwal_sekarang = copy.deepcopy(jadwal_awal)
    penalti_awal = objective_function(jadwal_sekarang, kelas_mata_kuliah, ruangan, mahasiswa)
    penalti_sekarang = penalti_awal
    
    history = {'iterasi': [0], 'penalti': [penalti_awal]}
    iterasi = 0
    sideways_count = 0
    
    while True:
        semua_tetangga = generate_all_neighbors(jadwal_sekarang, ruangan, hari, max_neighbors=max_neighbors)
        
        if not semua_tetangga:
            break
        
        tetangga_terbaik = None
        penalti_terbaik_tetangga = float('inf')
        
        for tetangga in semua_tetangga:
            penalti_tetangga = objective_function(tetangga, kelas_mata_kuliah, ruangan, mahasiswa)
            
            if penalti_tetangga < penalti_terbaik_tetangga:
                penalti_terbaik_tetangga = penalti_tetangga
                tetangga_terbaik = tetangga
        
        if penalti_terbaik_tetangga < penalti_sekarang:
            jadwal_sekarang = tetangga_terbaik
            penalti_sekarang = penalti_terbaik_tetangga
            sideways_count = 0
            
            iterasi += 1
            history['iterasi'].append(iterasi)
            history['penalti'].append(penalti_sekarang)
            
            if penalti_sekarang == 0:
                break
        elif penalti_terbaik_tetangga == penalti_sekarang and penalti_sekarang != 0 and sideways_count < max_sideways:
            jadwal_sekarang = tetangga_terbaik
            sideways_count += 1
            
            iterasi += 1
            history['iterasi'].append(iterasi)
            history['penalti'].append(penalti_sekarang)
        else:
            break
    
    penalti_akhir = penalti_sekarang

    return jadwal_sekarang, penalti_akhir, history, iterasi