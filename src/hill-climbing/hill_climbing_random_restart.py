import copy
import time
import random
import matplotlib.pyplot as plt
from generate_all_neighbors import generate_all_neighbors


def print_schedule_table(jadwal, ruangan, hari):
    """Print schedule in weekly table format per room"""
    for ruang in ruangan:
        print(f"\n{'='*80}")
        print(f"JADWAL RUANGAN: {ruang['kode']}")
        print(f"{'='*80}")
        
        # Create table header
        print(f"{'Jam':<6}", end='')
        for h in hari:
            print(f"{h:<15}", end='')
        print()
        print('-' * 80)
        
        # For each hour from 7 to 18
        for jam in range(7, 19):
            print(f"{jam:<6}", end='')
            for h in hari:
                # Find classes in this room, day, and time
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
    """Print schedule in simple format"""
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
    """Plot objective function values over iterations"""
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
    """Generate a random initial schedule"""
    jadwal = []
    
    for kelas in kelas_mata_kuliah:
        sesi = {
            'kode': kelas['kode'],
            'ruangan': random.choice(ruangan)['kode'],
            'hari': random.choice(hari),
            'waktu_mulai': random.randint(7, 18 - kelas['sks']),
            'waktu_selesai': 0  # Will be set below
        }
        sesi['waktu_selesai'] = sesi['waktu_mulai'] + kelas['sks']
        jadwal.append(sesi)
    
    return jadwal


def hill_climbing_steepest_once(jadwal_awal, kelas_mata_kuliah, ruangan, mahasiswa, hari, 
                                objective_function, max_neighbors=500):
    """
    Run one iteration of steepest ascent hill climbing
    Returns: (best_schedule, best_penalty, iterations, history)
    """
    jadwal_sekarang = copy.deepcopy(jadwal_awal)
    penalti_awal = objective_function(jadwal_sekarang, kelas_mata_kuliah, ruangan, mahasiswa)
    penalti_sekarang = penalti_awal
    
    history = {'iterasi': [0], 'penalti': [penalti_awal]}
    iterasi = 0
    
    while True:
        # Generate neighbors
        semua_tetangga = generate_all_neighbors(jadwal_sekarang, ruangan, hari, max_neighbors=max_neighbors)
        
        if not semua_tetangga:
            break
        
        # Find best neighbor
        tetangga_terbaik = None
        penalti_terbaik_tetangga = float('inf')
        
        for tetangga in semua_tetangga:
            penalti_tetangga = objective_function(tetangga, kelas_mata_kuliah, ruangan, mahasiswa)
            
            if penalti_tetangga < penalti_terbaik_tetangga:
                penalti_terbaik_tetangga = penalti_tetangga
                tetangga_terbaik = tetangga
        
        # Move only if better
        if penalti_terbaik_tetangga < penalti_sekarang:
            jadwal_sekarang = tetangga_terbaik
            penalti_sekarang = penalti_terbaik_tetangga
            
            iterasi += 1
            history['iterasi'].append(iterasi)
            history['penalti'].append(penalti_sekarang)
        else:
            # Local optimum reached
            break
    
    return jadwal_sekarang, penalti_sekarang, iterasi, history


def hill_climbing_random_restart_procedure(kelas_mata_kuliah, ruangan, mahasiswa, hari, 
                                           objective_function, max_neighbors=500, max_restart=10):
    print("\n" + "="*80)
    print(f"{'HILL CLIMBING - RANDOM RESTART':^80}")
    print("="*80 + "\n")
    
    # Start timing
    start_time = time.time()
    
    # Track best overall
    jadwal_terbaik_global = None
    penalti_terbaik_global = float('inf')
    
    # Track all histories for combined plot
    combined_history = {'iterasi': [], 'penalti': []}
    iteration_offset = 0
    
    # Track per-restart statistics
    restart_stats = []
    
    # Initial state (first restart)
    jadwal_awal = generate_random_schedule(kelas_mata_kuliah, ruangan, hari)
    penalti_awal = objective_function(jadwal_awal, kelas_mata_kuliah, ruangan, mahasiswa)
    
    # Print initial state
    if penalti_awal == 0:
        print_schedule_table(jadwal_awal, ruangan, hari)
    else:
        print_schedule_simple(jadwal_awal, "STATE AWAL (Restart 1)")
    print(f"\nNilai Objective Function Awal: {penalti_awal}\n")
    
    # Perform restarts
    for restart in range(max_restart):
        print(f"\n{'='*80}")
        print(f"RESTART {restart + 1}/{max_restart}")
        print(f"{'='*80}")
        
        # Generate random initial schedule for this restart
        if restart == 0:
            jadwal_restart = jadwal_awal
        else:
            jadwal_restart = generate_random_schedule(kelas_mata_kuliah, ruangan, hari)
        
        penalti_restart = objective_function(jadwal_restart, kelas_mata_kuliah, ruangan, mahasiswa)
        print(f"Penalty awal restart {restart + 1}: {penalti_restart}")
        
        # Run steepest ascent from this starting point
        jadwal_hasil, penalti_hasil, iterasi, history = hill_climbing_steepest_once(
            jadwal_restart, kelas_mata_kuliah, ruangan, mahasiswa, hari, 
            objective_function, max_neighbors
        )
        
        print(f"Penalty akhir restart {restart + 1}: {penalti_hasil} (iterasi: {iterasi})")
        
        # Track statistics
        restart_stats.append({
            'restart': restart + 1,
            'initial_penalty': penalti_restart,
            'final_penalty': penalti_hasil,
            'iterations': iterasi
        })
        
        # Update combined history
        for i, p in zip(history['iterasi'], history['penalti']):
            combined_history['iterasi'].append(iteration_offset + i)
            combined_history['penalti'].append(p)
        iteration_offset += iterasi + 1
        
        # Update global best
        if penalti_hasil < penalti_terbaik_global:
            penalti_terbaik_global = penalti_hasil
            jadwal_terbaik_global = jadwal_hasil
            print(f"New global best found!")
        
        # Stop if perfect solution found
        if penalti_hasil == 0:
            print(f"\nSolusi sempurna ditemukan pada restart {restart + 1}!")
            break
    
    # End timing
    end_time = time.time()
    duration = end_time - start_time
    
    # Print final state
    print(f"\n{'='*80}")
    print(f"{'STATE AKHIR (BEST OVERALL)':^80}")
    print(f"{'='*80}")
    
    if penalti_terbaik_global == 0:
        print_schedule_table(jadwal_terbaik_global, ruangan, hari)
    else:
        print_schedule_simple(jadwal_terbaik_global, "STATE AKHIR (BEST OVERALL)")
    print(f"\nNilai Objective Function Akhir: {penalti_terbaik_global}")
    
    # Print statistics
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
    
    # Plot objective function
    if combined_history['iterasi']:
        plot_objective_function(combined_history, "Hill Climbing with Random Restart - Objective Function")
    else:
        print("Tidak ada data iterasi untuk diplot")