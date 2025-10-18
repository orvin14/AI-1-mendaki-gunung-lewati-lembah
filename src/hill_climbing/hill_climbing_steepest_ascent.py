import copy
from hill_climbing.generate_all_neighbors import generate_all_neighbors


def hill_climbing_steepest_ascent(jadwal_awal, kelas_mata_kuliah, ruangan, mahasiswa, hari, 
                                   objective_function, max_neighbors=500):
    jadwal_sekarang = copy.deepcopy(jadwal_awal)
    penalti_sekarang = objective_function(jadwal_sekarang, kelas_mata_kuliah, ruangan, mahasiswa)
    
    history = {'iterasi': [], 'penalti': []}
    iterasi = 0
    
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
            
            history['iterasi'].append(iterasi)
            history['penalti'].append(penalti_sekarang)
            iterasi += 1
        else:
            break
    
    return jadwal_sekarang, penalti_sekarang, history, iterasi