import copy
import time
import matplotlib.pyplot as plt
from hill_climbing.generate_all_neighbors import generate_all_neighbors


def print_schedule_table(jadwal, ruangan, hari):
    for ruang in ruangan:
        print(f"\n{'='*80}")
        print(f"JADWAL RUANGAN: {ruang['kode']}")
        print(f"{'='*80}")
        
        print(f"{'Jam':<6}", end='')
        for h in hari:
            print(f"{h:<15}", end='')
        print()
        print('-' * 80)
        
        for jam in range(7, 19):
            print(f"{jam:<6}", end='')
            for h in hari:
                classes = []
                for sesi in jadwal:
                    if (sesi['ruangan'] == ruang['kode'] and 
                        sesi['hari'] == h and 
                        sesi['waktu_mulai'] <= jam < sesi['waktu_selesai']):
                        classes.append(sesi['kode'])
                
                if classes:
                    print(f"{', '.join(classes):<15}", end='')
                else:
                    print(f"{'':15}", end='')
            print()
        print('='*80)


def print_schedule_simple(jadwal, title="Schedule"):
    print(f"\n{'='*80}")
    print(f"{title:^80}")
    print(f"{'='*80}")
    print(f"{'Kode':<15} {'Ruangan':<15} {'Hari':<10} {'Jam':<15}")
    print('-'*80)
    for sesi in jadwal:
        print(f"{sesi['kode']:<15} {sesi['ruangan']:<15} {sesi['hari']:<10} "
              f"{sesi['waktu_mulai']}-{sesi['waktu_selesai']:<15}")
    print('='*80)


def plot_objective_function(history, title="Objective Function vs Iterations", filename=None):
    if not history['iterasi']:
        print("Tidak ada data iterasi untuk diplot (sudah optimal dari awal)")
        return
    
    plt.figure(figsize=(10, 6))
    plt.plot(history['iterasi'], history['penalti'], marker='o', linestyle='-', linewidth=2, markersize=6)
    plt.xlabel('Iterasi', fontsize=12)
    plt.ylabel('Nilai Objective Function (Penalty)', fontsize=12)
    plt.title(title, fontsize=14, fontweight='bold')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    
    if filename:
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        print(f"Plot disimpan ke {filename}")
    else:
        plt.show()
    plt.close()


def hill_climbing_sideways_procedure(jadwal_awal, kelas_mata_kuliah, ruangan, mahasiswa, hari, 
                                     objective_function, max_neighbors=500, max_sideways=100):
    print("\n" + "="*80)
    print(f"{'HILL CLIMBING - SIDEWAYS MOVE':^80}")
    print("="*80 + "\n")
    
    jadwal_sekarang = copy.deepcopy(jadwal_awal)
    penalti_awal = objective_function(jadwal_sekarang, kelas_mata_kuliah, ruangan, mahasiswa)
    penalti_sekarang = penalti_awal
    
    if penalti_awal == 0:
        print_schedule_table(jadwal_sekarang, ruangan, hari)
    else:
        print_schedule_simple(jadwal_sekarang, "STATE AWAL")
    print(f"\nNilai Objective Function Awal: {penalti_awal}\n")
    
    history = {'iterasi': [0], 'penalti': [penalti_awal]}
    iterasi = 0
    sideways_count = 0
    
    start_time = time.time()
    
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
            
        elif penalti_terbaik_tetangga == penalti_sekarang and sideways_count < max_sideways:
            jadwal_sekarang = tetangga_terbaik
            sideways_count += 1
            
            iterasi += 1
            history['iterasi'].append(iterasi)
            history['penalti'].append(penalti_sekarang)
        else:
            break
    
    end_time = time.time()
    duration = end_time - start_time
    
    penalti_akhir = penalti_sekarang
    if penalti_akhir == 0:
        print_schedule_table(jadwal_sekarang, ruangan, hari)
    else:
        print_schedule_simple(jadwal_sekarang, "STATE AKHIR")
    print(f"\nNilai Objective Function Akhir: {penalti_akhir}")
    
    print(f"\n{'='*80}")
    print(f"{'STATISTIK':^80}")
    print(f"{'='*80}")
    print(f"Banyak Iterasi: {iterasi}")
    print(f"Maximum Sideways Move: {max_sideways}")
    print(f"Durasi Pencarian: {duration:.4f} detik")
    print(f"{'='*80}\n")
    
    plot_objective_function(history, "Hill Climbing with Sideways Move - Objective Function")
