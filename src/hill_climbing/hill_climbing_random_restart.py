import copy
import time
import random
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


def generate_random_schedule(kelas_mata_kuliah, ruangan, hari):
    jadwal = []
    
    for kelas in kelas_mata_kuliah:
        sesi = {
            'kode': kelas['kode'],
            'ruangan': random.choice(ruangan)['kode'],
            'hari': random.choice(hari),
            'waktu_mulai': random.randint(7, 18 - kelas['sks']),
            'waktu_selesai': 0
        }
        sesi['waktu_selesai'] = sesi['waktu_mulai'] + kelas['sks']
        jadwal.append(sesi)
    
    return jadwal


def hill_climbing_steepest_once(jadwal_awal, kelas_mata_kuliah, ruangan, mahasiswa, hari, 
                                objective_function, max_neighbors=500):
    jadwal_sekarang = copy.deepcopy(jadwal_awal)
    penalti_awal = objective_function(jadwal_sekarang, kelas_mata_kuliah, ruangan, mahasiswa)
    penalti_sekarang = penalti_awal
    
    history = {'iterasi': [0], 'penalti': [penalti_awal]}
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
            
            iterasi += 1
            history['iterasi'].append(iterasi)
            history['penalti'].append(penalti_sekarang)
        else:
            break
    
    return jadwal_sekarang, penalti_sekarang, iterasi, history


def hill_climbing_random_restart_procedure(kelas_mata_kuliah, ruangan, mahasiswa, hari, 
                                           objective_function, max_neighbors=500, max_restart=10):
    print("\n" + "="*80)
    print(f"{'HILL CLIMBING - RANDOM RESTART':^80}")
    print("="*80 + "\n")
    
    start_time = time.time()
    
    jadwal_terbaik_global = None
    penalti_terbaik_global = float('inf')
    
    combined_history = {'iterasi': [], 'penalti': []}
    iteration_offset = 0
    
    restart_stats = []
    
    jadwal_awal = generate_random_schedule(kelas_mata_kuliah, ruangan, hari)
    penalti_awal = objective_function(jadwal_awal, kelas_mata_kuliah, ruangan, mahasiswa)
    
    if penalti_awal == 0:
        print_schedule_table(jadwal_awal, ruangan, hari)
    else:
        print_schedule_simple(jadwal_awal, "STATE AWAL (Restart 1)")
    print(f"\nNilai Objective Function Awal: {penalti_awal}\n")
    
    for restart in range(max_restart):
        print(f"\n{'='*80}")
        print(f"RESTART {restart + 1}/{max_restart}")
        print(f"{'='*80}")
        
        if restart == 0:
            jadwal_restart = jadwal_awal
        else:
            jadwal_restart = generate_random_schedule(kelas_mata_kuliah, ruangan, hari)
        
        penalti_restart = objective_function(jadwal_restart, kelas_mata_kuliah, ruangan, mahasiswa)
        print(f"Penalty awal restart {restart + 1}: {penalti_restart}")
        
        jadwal_hasil, penalti_hasil, iterasi, history = hill_climbing_steepest_once(
            jadwal_restart, kelas_mata_kuliah, ruangan, mahasiswa, hari, 
            objective_function, max_neighbors
        )
        
        print(f"Penalty akhir restart {restart + 1}: {penalti_hasil} (iterasi: {iterasi})")
        
        restart_stats.append({
            'restart': restart + 1,
            'initial_penalty': penalti_restart,
            'final_penalty': penalti_hasil,
            'iterations': iterasi
        })
        
        for i, p in zip(history['iterasi'], history['penalti']):
            combined_history['iterasi'].append(iteration_offset + i)
            combined_history['penalti'].append(p)
        iteration_offset += iterasi + 1
        
        if penalti_hasil < penalti_terbaik_global:
            penalti_terbaik_global = penalti_hasil
            jadwal_terbaik_global = jadwal_hasil
            print(f"New global best found!")
        
        if penalti_hasil == 0:
            print(f"\nSolusi sempurna ditemukan pada restart {restart + 1}!")
            break
    
    end_time = time.time()
    duration = end_time - start_time
    
    print(f"\n{'='*80}")
    print(f"{'STATE AKHIR (BEST OVERALL)':^80}")
    print(f"{'='*80}")
    
    if penalti_terbaik_global == 0:
        print_schedule_table(jadwal_terbaik_global, ruangan, hari)
    else:
        print_schedule_simple(jadwal_terbaik_global, "STATE AKHIR (BEST OVERALL)")
    print(f"\nNilai Objective Function Akhir: {penalti_terbaik_global}")
    
    print(f"\n{'='*80}")
    print(f"{'STATISTIK':^80}")
    print(f"{'='*80}")
    print(f"Maximum Restart: {max_restart}")
    print(f"Jumlah Restart Dilakukan: {len(restart_stats)}")
    print(f"\nDetail per Restart:")
    print(f"{'Restart':<10} {'Initial':<12} {'Final':<12} {'Iterasi':<10}")
    print('-'*80)
    for stat in restart_stats:
        print(f"{stat['restart']:<10} {stat['initial_penalty']:<12} "
              f"{stat['final_penalty']:<12} {stat['iterations']:<10}")
    print(f"\nDurasi Pencarian Total: {duration:.4f} detik")
    print(f"{'='*80}\n")
    
    if combined_history['iterasi']:
        plot_objective_function(combined_history, "Hill Climbing with Random Restart - Objective Function")
    else:
        print("Tidak ada data iterasi untuk diplot")