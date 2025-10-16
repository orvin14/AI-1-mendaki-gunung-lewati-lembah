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
        print("No iteration data to plot")
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
        print(f"Plot saved to {filename}")
    else:
        plt.show()
    plt.close()


def hill_climbing_steepest_ascent(jadwal_awal, kelas_mata_kuliah, ruangan, mahasiswa, hari, 
                                   objective_function, max_neighbors=500):
    print("\n" + "="*80)
    print(f"{'HILL CLIMBING - STEEPEST ASCENT':^80}")
    print("="*80 + "\n")
    
    jadwal_sekarang = copy.deepcopy(jadwal_awal)
    penalti_sekarang = objective_function(jadwal_sekarang, kelas_mata_kuliah, ruangan, mahasiswa)
    
    print_schedule_simple(jadwal_sekarang, "STATE AWAL")
    print(f"\nNilai Objective Function Awal: {penalti_sekarang}\n")
    
    history = {'iterasi': [], 'penalti': []}
    iterasi = 0
    
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
            
            history['iterasi'].append(iterasi)
            history['penalti'].append(penalti_sekarang)
            iterasi += 1
        else:
            break
    
    end_time = time.time()
    duration = end_time - start_time
    
    print_schedule_simple(jadwal_sekarang, "STATE AKHIR")
    print(f"\nNilai Objective Function Akhir: {penalti_sekarang}")
    
    if penalti_sekarang == 0:
        print("\nSolusi sempurna ditemukan (tanpa konflik)!\n")
        print_schedule_table(jadwal_sekarang, ruangan, hari)
    
    print(f"\n{'='*80}")
    print(f"{'STATISTIK':^80}")
    print(f"{'='*80}")
    print(f"Banyak Iterasi: {iterasi}")
    print(f"Durasi Pencarian: {duration:.4f} detik")
    print(f"{'='*80}\n")
    
    if history['iterasi']:
        plot_objective_function(history, "Steepest Ascent Hill Climbing - Objective Function")
    else:
        print("Tidak ada iterasi (sudah optimal dari awal)")
