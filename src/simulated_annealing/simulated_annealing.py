import math
import random
import copy
from simulated_annealing.objective_function import objective_function
from simulated_annealing.generate_neighbor import generate_neighbor

def simulated_annealing(jadwal_awal,suhu_awal,laju_pendinginan,suhu_akhir,kelas_mata_kuliah,ruangan,mahasiswa,hari):
    suhu_sekarang = suhu_awal
    jadwal_sekarang = copy.deepcopy(jadwal_awal)
    penalti_sekarang = objective_function(jadwal_sekarang, kelas_mata_kuliah, ruangan, mahasiswa)
    
    jadwal_terbaik = copy.deepcopy(jadwal_awal)
    penalti_terbaik = penalti_sekarang
    
    history = {'suhu': [], 'penalti': [], 'penalti_terbaik': []}

    while suhu_sekarang > suhu_akhir:
        jadwal_tetangga = generate_neighbor(jadwal_sekarang, ruangan, hari)
        penalti_tetangga = objective_function(jadwal_tetangga, kelas_mata_kuliah, ruangan, mahasiswa)

        selisih_penalti = penalti_tetangga - penalti_sekarang
        if selisih_penalti < 0:
            jadwal_sekarang = jadwal_tetangga
            penalti_sekarang = penalti_tetangga
        else:
            probabilitas_penerimaan = math.exp(-selisih_penalti / suhu_sekarang)
            if random.random() < probabilitas_penerimaan:
                jadwal_sekarang = jadwal_tetangga
                penalti_sekarang = penalti_tetangga
        
        if penalti_sekarang < penalti_terbaik:
            jadwal_terbaik = jadwal_sekarang
            penalti_terbaik = penalti_sekarang
        
        history['suhu'].append(suhu_sekarang)
        history['penalti'].append(penalti_sekarang)
        history['penalti_terbaik'].append(penalti_terbaik)

        suhu_sekarang *= laju_pendinginan

    return jadwal_terbaik, penalti_terbaik, history