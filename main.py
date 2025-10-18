import sys
import os
import time
import copy
import matplotlib.pyplot as plt
import numpy as np 
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from genetic_algorithm.inputoutput import parse_input
from genetic_algorithm.preprocess import generate_population
from genetic_algorithm.genetic_algoritm import genetic_algorithm, fitness_function
from hill_climbing.hill_climbing_steepest_ascent import hill_climbing_steepest_ascent
from hill_climbing.hill_climbing_sideways import hill_climbing_sideways_procedure
from hill_climbing.hill_climbing_random_restart import hill_climbing_random_restart_procedure
from hill_climbing.stochastic import stochastic_hill_climbing
from simulated_annealing.simulated_annealing import simulated_annealing
from simulated_annealing.objective_function import objective_function

def print_schedule_table(jadwal, penalti, ruangan, hari, title="SCHEDULE"):
    print(f"\n{'='*80}")
    print(f"{title:^80}")
    print(f"{'='*80}\n")
        
    if penalti > 0:
        print("Schedule has conflicts - displaying in list:")
        print_schedule_simple(jadwal)
        return
    
    for ruang in ruangan:
        print(f"\nJADWAL RUANGAN: {ruang['kode']}")
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

def plot_objective_function_history(history, title="Objective Function vs Iterations", 
                                  xlabel="Iteration", ylabel="Objective Function (Penalty)",
                                  filename=None):
    if not history.get('iterasi') and not history.get('iterations'):
        print("No iteration data to plot")
        return
    
    plt.figure(figsize=(12, 6))
    
    iterations = history.get('iterasi') or history.get('iterations') or []
    penalties = history.get('penalti') or history.get('penalties') or []
    
    if iterations and penalties:
        plt.plot(iterations, penalties, marker='o', linestyle='-', linewidth=2, markersize=4, label='Penalty')
    
    plt.xlabel(xlabel, fontsize=12)
    plt.ylabel(ylabel, fontsize=12)
    plt.title(title, fontsize=14, fontweight='bold')
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    
    if filename:
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        print(f"Plot saved to {filename}")
    else:
        plt.show()
    plt.close()

def plot_sa_dashboard(history, title="Dashboard Hasil Simulated Annealing", filename=None):
    penalti_terbaik = history.get('penalti_terbaik_per_iterasi', [])
    penalti_sekarang = history.get('penalti_sekarang_per_iterasi', [])
    
    prob_data = history.get('probabilitas_penerimaan', [])
    prob_iterations = [i for i, p in enumerate(prob_data) if p is not None]
    probabilities = [p for p in prob_data if p is not None]

    if not penalti_terbaik:
        print("Tidak ada data untuk diplot.")
        return

    fig, axs = plt.subplots(2, 1, figsize=(14, 10), sharex=True)
    fig.suptitle(title, fontsize=18, fontweight='bold')

    axs[0].plot(penalti_sekarang, color='skyblue', linestyle='--', alpha=0.8, label='Penalti Saat Ini')
    axs[0].plot(penalti_terbaik, color='blue', linewidth=2.5, label='Penalti Terbaik')
    axs[0].set_ylabel('Nilai Penalti (Cost)', fontsize=12)
    axs[0].set_title('Perkembangan Nilai Objective Function', fontsize=14)
    axs[0].legend()
    axs[0].grid(True, linestyle='--', alpha=0.6)

    if probabilities:
        axs[1].scatter(prob_iterations, probabilities, color='red', alpha=0.3, s=15, label='Probabilitas (e^-ΔE/T)')
    axs[1].set_ylabel('Probabilitas', fontsize=12)
    axs[1].set_title('Probabilitas Penerimaan Solusi Buruk', fontsize=14)
    axs[1].set_xlabel('Iterasi', fontsize=12)
    axs[1].set_ylim(0, 1.05)
    axs[1].legend()
    axs[1].grid(True, linestyle='--', alpha=0.6)

    plt.tight_layout(rect=[0, 0.03, 1, 0.95])

    if filename:
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        print(f"Plot telah disimpan ke {filename}")
    else:
        plt.show()
    plt.close()

def plot_random_restart_history(restart_histories, title="Random Restart Hill Climbing - Objective Function", filename=None):
    if not restart_histories:
        print("No restart data to plot")
        return
    
    plt.figure(figsize=(14, 7))
    cumulative_iteration = 0
    colors = plt.cm.tab10(range(len(restart_histories)))
    
    for idx, restart_data in enumerate(restart_histories):
        iterations = restart_data['iterasi']
        penalties = restart_data['penalti']
        
        if iterations and penalties:
            adjusted_iterations = [cumulative_iteration + i for i in iterations]
            plt.plot(adjusted_iterations, penalties, 
                     marker='o', linestyle='-', linewidth=2, markersize=4,
                     color=colors[idx % 10], label=f'Restart {idx + 1}')
            cumulative_iteration = adjusted_iterations[-1] + 1
    
    plt.xlabel('Cumulative Iterations', fontsize=12)
    plt.ylabel('Objective Function (Penalty)', fontsize=12)
    plt.title(title, fontsize=14, fontweight='bold')
    plt.grid(True, alpha=0.3)
    if len(restart_histories) <= 20:
        plt.legend(loc='best', fontsize=10)
    plt.tight_layout()
    
    if filename:
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        print(f"Plot saved to {filename}")
    else:
        plt.show()
    plt.close()

def analyze_stagnation(history):
    stuck_periods = history.get('periode_stagnasi', [])
    print("Frekuensi ‘Stuck’ di Local Optima:")
    if not stuck_periods:
        print("    - Algoritma tidak pernah mengalami stagnasi.")
    else:
        print(f"    - Jumlah periode stagnasi: {len(stuck_periods)} kali")
        print(f"    - Durasi stagnasi terpanjang: {max(stuck_periods)} iterasi")
        avg_duration = np.mean(stuck_periods) if stuck_periods else 0
        print(f"    - Rata-rata durasi stagnasi: {avg_duration:.2f} iterasi")

def run_steepest_ascent_hill_climbing(jadwal_awal, kelas_mata_kuliah, ruangan, mahasiswa, hari):
    print("\n" + "="*80)
    print(f"{'STEEPEST ASCENT HILL CLIMBING':^80}")
    print("="*80 + "\n")
    
    max_neighbors = int(input("Enter maximum neighbors to sample (default 500): ") or "500")
    
    jadwal_sekarang = copy.deepcopy(jadwal_awal)
    penalti_awal = objective_function(jadwal_sekarang, kelas_mata_kuliah, ruangan, mahasiswa)
    
    print_schedule_simple(jadwal_sekarang, "INITIAL STATE")
    print(f"\nInitial Objective Function: {penalti_awal}")
    
    start_time = time.time()
    
    jadwal_akhir, penalti_akhir, history, iterasi = hill_climbing_steepest_ascent(
        jadwal_awal, kelas_mata_kuliah, ruangan, mahasiswa, hari, 
        objective_function, max_neighbors
    )
    
    duration = time.time() - start_time
    
    print_schedule_table(jadwal_akhir, penalti_akhir, ruangan, hari, "FINAL STATE")
    
    print(f"\n{'='*80}")
    print(f"{'RESULTS':^80}")
    print(f"{'='*80}")
    print(f"Final Objective Function: {penalti_akhir}")
    print(f"Number of Iterations: {iterasi}")
    print(f"Duration: {duration:.4f} seconds")
    print(f"{'='*80}\n")
    
    plot_objective_function_history(history, "Steepest Ascent Hill Climbing - Objective Function")
    
    return jadwal_akhir, penalti_akhir, iterasi, duration, history

def run_sideways_hill_climbing(jadwal_awal, kelas_mata_kuliah, ruangan, mahasiswa, hari):
    print("\n" + "="*80)
    print(f"{'HILL CLIMBING WITH SIDEWAYS MOVE':^80}")
    print("="*80 + "\n")
    
    max_neighbors = int(input("Enter maximum neighbors to sample (default 500): ") or "500")
    max_sideways = int(input("Enter maximum sideways moves (default 100): ") or "100")
    
    jadwal_sekarang = copy.deepcopy(jadwal_awal)
    penalti_awal = objective_function(jadwal_sekarang, kelas_mata_kuliah, ruangan, mahasiswa)
    
    print_schedule_simple(jadwal_sekarang, "INITIAL STATE")
    print(f"\nInitial Objective Function: {penalti_awal}")
    
    start_time = time.time()
    
    jadwal_akhir, penalti_akhir, history, iterasi = hill_climbing_sideways_procedure(
        jadwal_awal, kelas_mata_kuliah, ruangan, mahasiswa, hari, 
        objective_function, max_neighbors, max_sideways
    )
    
    duration = time.time() - start_time
    
    print_schedule_table(jadwal_akhir, penalti_akhir, ruangan, hari, "FINAL STATE")
    
    print(f"\n{'='*80}")
    print(f"{'RESULTS':^80}")
    print(f"{'='*80}")
    print(f"Final Objective Function: {penalti_akhir}")
    print(f"Number of Iterations: {iterasi}")
    print(f"Maximum Sideways Moves: {max_sideways}")
    print(f"Duration: {duration:.4f} seconds")
    print(f"{'='*80}\n")
    
    plot_objective_function_history(history, "Hill Climbing with Sideways Move - Objective Function")
    
    return jadwal_akhir, penalti_akhir, iterasi, duration, history

def run_random_restart_hill_climbing(kelas_mata_kuliah, ruangan, mahasiswa, hari):
    print("\n" + "="*80)
    print(f"{'RANDOM RESTART HILL CLIMBING':^80}")
    print("="*80 + "\n")
    
    max_neighbors = int(input("Enter maximum neighbors to sample (default 500): ") or "500")
    max_restart = int(input("Enter maximum restarts (default 10): ") or "10")
        
    start_time = time.time()

    jadwal_terbaik_global, penalti_terbaik_global, restart_stats, restart_histories = hill_climbing_random_restart_procedure(
        kelas_mata_kuliah, ruangan, mahasiswa, hari, 
        objective_function, max_neighbors, max_restart
    )

    duration = time.time() - start_time
    
    print_schedule_table(jadwal_terbaik_global, penalti_terbaik_global, ruangan, hari, "FINAL STATE")
    
    print(f"\n{'='*80}")
    print(f"{'RESULTS':^80}")
    print(f"{'='*80}")
    print(f"Final Objective Function: {penalti_terbaik_global}")
    print(f"Number of Restarts: {len(restart_stats)}")
    print(f"\nPer-Restart Statistics:")
    print(f"{'Restart':<10} {'Initial':<12} {'Final':<12} {'Iterations':<10}")
    print('-'*80)
    for stat in restart_stats:
        print(f"{stat['restart']:<10} {stat['initial_penalty']:<12} "
              f"{stat['final_penalty']:<12} {stat['iterations']:<10}")
    print(f"\nTotal Duration: {duration:.4f} seconds")
    print(f"{'='*80}\n")
    
    plot_random_restart_history(restart_histories, "Random Restart Hill Climbing - Objective Function")
    
    return jadwal_terbaik_global, penalti_terbaik_global, restart_stats, duration, restart_histories

def run_stochastic_hill_climbing(jadwal_awal, kelas_mata_kuliah, ruangan, mahasiswa, hari):
    print("\n" + "="*80)
    print(f"{'STOCHASTIC HILL CLIMBING':^80}")
    print("="*80 + "\n")
    
    max_iter = int(input("Enter maximum iterations (default 5000): ") or "5000")
    
    jadwal_sekarang = copy.deepcopy(jadwal_awal)
    penalti_awal = objective_function(jadwal_sekarang, kelas_mata_kuliah, ruangan, mahasiswa)

    print_schedule_simple(jadwal_sekarang, "INITIAL STATE")
    print(f"\nInitial Objective Function: {penalti_awal}")
    
    start_time = time.time()
    
    jadwal_akhir, penalti_akhir, history, total_iterasi = stochastic_hill_climbing(
        jadwal_awal, kelas_mata_kuliah, ruangan, mahasiswa, hari, max_iter
    )
    
    duration = time.time() - start_time
    
    print_schedule_table(jadwal_akhir, penalti_akhir, ruangan, hari, "FINAL STATE")
    
    print(f"\n{'='*80}")
    print(f"{'RESULTS':^80}")
    print(f"{'='*80}")
    print(f"Final Objective Function: {penalti_akhir}")
    print(f"Number of Iterations: {total_iterasi}")
    print(f"Duration: {duration:.4f} seconds")
    print(f"{'='*80}\n")
    
    plot_objective_function_history(history, "Stochastic Hill Climbing - Objective Function")
    
    return jadwal_akhir, penalti_akhir, history, duration

def run_simulated_annealing(jadwal_awal, kelas_mata_kuliah, ruangan, mahasiswa, hari):
    print("\n" + "="*80)
    print(f"{'SIMULATED ANNEALING':^80}")
    print("="*80 + "\n")
    
    suhu_awal = float(input("Enter initial temperature (default 1000): ") or "1000")
    laju_pendinginan = float(input("Enter cooling rate (default 0.999): ") or "0.999")
    suhu_akhir = float(input("Enter final temperature (default 0.01): ") or "0.01")
    
    jadwal_sekarang = copy.deepcopy(jadwal_awal)
    penalti_awal = objective_function(jadwal_sekarang, kelas_mata_kuliah, ruangan, mahasiswa)
    
    print_schedule_simple(jadwal_sekarang, "INITIAL STATE")
    print(f"\nInitial Objective Function: {penalti_awal}")
    
    start_time = time.time()
    jadwal_terbaik, penalti_terbaik, history = simulated_annealing(
        jadwal_awal, suhu_awal, laju_pendinginan, suhu_akhir,
        kelas_mata_kuliah, ruangan, mahasiswa, hari
    )
    duration = time.time() - start_time
    
    print_schedule_table(jadwal_terbaik, penalti_terbaik, ruangan, hari, "FINAL STATE")
    
    print(f"\n{'='*80}")
    print(f"{'RESULTS':^80}")
    print(f"{'='*80}")
    print(f"Final Objective Function: {penalti_terbaik}")
    print(f"Total Iterations: {len(history['penalti_terbaik_per_iterasi'])}")
    print(f"Duration: {duration:.4f} seconds")
    analyze_stagnation(history)
    print(f"{'='*80}\n")
    
    plot_sa_dashboard(history, "Simulated Annealing - Dashboard")
    
    return jadwal_terbaik, penalti_terbaik, duration, history

def run_genetic_algorithm_experiment(kelas_mata_kuliah, ruangan, mahasiswa, hari):
    print("\n" + "="*80)
    print(f"{'GENETIC ALGORITHM EXPERIMENTS':^80}")
    print("="*80 + "\n")
    
    print("Choose experiment type:")
    print("1. Fixed population size, vary iterations")
    print("2. Fixed iterations, vary population size")
    print("3. Single run with custom parameters")
    
    choice = input("\nEnter choice (1-3): ").strip()
    
    waktu_mulai = list(range(7, 18))
    hari_list = ['Senin', 'Selasa', 'Rabu', 'Kamis', 'Jumat']
    
    if choice == "1":
        population_size = int(input("\nEnter fixed population size (default 50): ") or "50")
        iterations_list = [
            int(input("Enter iteration count 1 (default 50): ") or "50"),
            int(input("Enter iteration count 2 (default 100): ") or "100"),
            int(input("Enter iteration count 3 (default 200): ") or "200")
        ]
        runs_per_config = int(input("Enter number of runs per configuration (default 3): ") or "3")
        
        print(f"\n{'='*80}")
        print(f"{'EXPERIMENT: FIXED POPULATION, VARYING ITERATIONS':^80}")
        print(f"{'='*80}\n")
        print(f"Fixed Population Size: {population_size}")
        print(f"Iteration Variations: {iterations_list}")
        print(f"Runs per Configuration: {runs_per_config}\n")
        
        all_results = []
        
        for iterations in iterations_list:
            print(f"\n{'='*80}")
            print(f"CONFIGURATION: Population={population_size}, Iterations={iterations}")
            print(f"{'='*80}\n")
            
            config_results = []
            
            for run in range(runs_per_config):
                print(f"\nRun {run + 1}/{runs_per_config}")
                print("-" * 80)
                
                population = [generate_population(kelas_mata_kuliah, ruangan, hari_list) for _ in range(population_size)]
                
                initial_schedule = population[0]
                initial_fitness = fitness_function(initial_schedule, kelas_mata_kuliah, ruangan, mahasiswa)
                initial_penalty = objective_function(initial_schedule, kelas_mata_kuliah, ruangan, mahasiswa)
                
                print(f"Initial fitness (from individual 0): {initial_fitness:.6f}")
                print(f"Initial penalty (from individual 0): {initial_penalty}")
                
                start_time = time.time()
                max_fitness, best_individual, final_gen, max_iter_hist, avg_iter_hist, total_ind = genetic_algorithm(
                    population, kelas_mata_kuliah, ruangan, mahasiswa, hari_list, waktu_mulai, iterations
                )
                duration = time.time() - start_time
                
                final_penalty = objective_function(best_individual, kelas_mata_kuliah, ruangan, mahasiswa)
                
                print(f"Final fitness: {max_fitness:.6f}")
                print(f"Final penalty: {final_penalty}")
                print(f"Generations completed: {final_gen}")
                print(f"Duration: {duration:.4f} seconds")
                
                config_results.append({
                    'run': run + 1,
                    'initial_fitness': initial_fitness, 'initial_penalty': initial_penalty, 'initial_schedule': initial_schedule,
                    'final_fitness': max_fitness, 'final_penalty': final_penalty, 'final_schedule': best_individual,
                    'generations': final_gen,
                    'max_fitness_history': max_iter_hist, 'avg_fitness_history': avg_iter_hist,
                    'total_individuals': total_ind, 'duration': duration
                })
            
            all_results.append({
                'population_size': population_size,
                'iterations': iterations,
                'runs': config_results
            })
            
            print(f"\n{'='*80}")
            print(f"SUMMARY FOR Configuration: Pop={population_size}, Iter={iterations}")
            print(f"{'='*80}")
            avg_final_fitness = np.mean([r['final_fitness'] for r in config_results])
            avg_final_penalty = np.mean([r['final_penalty'] for r in config_results])
            avg_duration = np.mean([r['duration'] for r in config_results])
            
            print(f"Average Final Fitness: {avg_final_fitness:.6f}")
            print(f"Average Final Penalty: {avg_final_penalty:.2f}")
            print(f"Average Duration: {avg_duration:.4f} seconds")
            print(f"{'='*80}\n")
            
            plt.figure(figsize=(12, 6))
            for i, result in enumerate(config_results):
                plt.plot(range(1, len(result['max_fitness_history'])+1), 
                         result['max_fitness_history'], 
                         marker='o', markersize=3, label=f'Run {i+1} - Max')
                plt.plot(range(1, len(result['avg_fitness_history'])+1), 
                         result['avg_fitness_history'], 
                         linestyle='--', alpha=0.6, label=f'Run {i+1} - Avg')
            
            plt.xlabel('Generation', fontsize=12)
            plt.ylabel('Fitness', fontsize=12)
            plt.title(f'Genetic Algorithm - Pop={population_size}, Iter={iterations}', 
                      fontsize=14, fontweight='bold')
            plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
            plt.grid(True, alpha=0.3)
            plt.tight_layout()
            plt.show()
            plt.close()
        
        print(f"\n{'='*80}")
        print(f"{'EXPERIMENT COMPLETE':^80}")
        print(f"{'='*80}\n")
        for result_set in all_results:
            best_run = max(result_set['runs'], key=lambda x: x['final_fitness'])
            print(f"\nBest result for Pop={result_set['population_size']}, Iter={result_set['iterations']}:")
            print(f"  Run {best_run['run']}: Fitness={best_run['final_fitness']:.6f}, Penalty={best_run['final_penalty']}")
            print(f"\nInitial State (Run {best_run['run']}):")
            print_schedule_simple(best_run['initial_schedule'], "INITIAL STATE")
            print(f"\nFinal State (Run {best_run['run']}):")
            print_schedule_table(best_run['final_schedule'], best_run['final_penalty'], ruangan, hari_list, "FINAL STATE")
    
    elif choice == "2":
        iterations = int(input("\nEnter fixed iteration count (default 100): ") or "100")
        population_sizes = [
            int(input("Enter population size 1 (default 30): ") or "30"),
            int(input("Enter population size 2 (default 50): ") or "50"),
            int(input("Enter population size 3 (default 70): ") or "70")
        ]
        runs_per_config = int(input("Enter number of runs per configuration (default 3): ") or "3")
        
        print("Experiment type 2 is complex and similar to type 1.")
        print("Please adapt the logic from experiment type 1 for this case.")

    
    else:
        population_size = int(input("\nEnter population size (default 50): ") or "50")
        iterations = int(input("Enter iteration count (default 100): ") or "100")
        
        print(f"\n{'='*80}")
        print(f"{'GENETIC ALGORITHM - SINGLE RUN':^80}")
        print(f"{'='*80}\n")
        print(f"Population Size: {population_size}")
        print(f"Iterations: {iterations}\n")
        
        population = [generate_population(kelas_mata_kuliah, ruangan, hari_list) for _ in range(population_size)]
        
        initial_schedule = population[0]
        initial_fitness = fitness_function(initial_schedule, kelas_mata_kuliah, ruangan, mahasiswa)
        initial_penalty = objective_function(initial_schedule, kelas_mata_kuliah, ruangan, mahasiswa)
        
        print(f"\nInitial State (from Individual 0):")
        print_schedule_simple(initial_schedule, "INITIAL STATE")
        print(f"\nInitial Fitness: {initial_fitness:.6f}")
        print(f"Initial Penalty: {initial_penalty}")
        
        start_time = time.time()
        max_fitness, best_individual, final_gen, max_iter_hist, avg_iter_hist, total_ind = genetic_algorithm(
            population, kelas_mata_kuliah, ruangan, mahasiswa, hari_list, waktu_mulai, iterations
        )
        duration = time.time() - start_time
        
        final_penalty = objective_function(best_individual, kelas_mata_kuliah, ruangan, mahasiswa)
        
        print(f"\nFinal State:")
        print_schedule_table(best_individual, final_penalty, ruangan, hari_list, "FINAL STATE")
        print(f"\nFinal Fitness: {max_fitness:.6f}")
        print(f"Final Objective Function: {final_penalty}")
        
        print(f"\n{'='*80}")
        print(f"{'RESULTS':^80}")
        print(f"{'='*80}")
        print(f"Final Fitness: {max_fitness:.6f}")
        print(f"Final Objective Function: {final_penalty}")
        print(f"Generations Completed: {final_gen}")
        print(f"Duration: {duration:.4f} seconds")
        print(f"{'='*80}\n")
        
        plt.figure(figsize=(12, 6))
        plt.plot(range(1, len(max_iter_hist)+1), max_iter_hist, 
                 marker='o', markersize=4, linewidth=2, label='Max Fitness')
        plt.plot(range(1, len(avg_iter_hist)+1), avg_iter_hist, 
                 marker='s', markersize=4, linewidth=2, label='Average Fitness', alpha=0.7)
        plt.xlabel('Generation', fontsize=12)
        plt.ylabel('Fitness', fontsize=12)
        plt.title('Genetic Algorithm - Fitness Over Generations', fontsize=14, fontweight='bold')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.show()
        plt.close()

def main():
    print("="*80)
    print(f"{'LOCAL SEARCH ALGORITHMS FOR COURSE SCHEDULING':^80}")
    print("="*80)
    
    base_dir = os.path.dirname(os.path.abspath(__file__))
    input_file = input(f"\nEnter input file path (default: {os.path.join(base_dir, 'test', 'input.json')}): ").strip()
    if not input_file:
        input_file = os.path.join(base_dir, 'test', 'input.json')
    
    if not os.path.exists(input_file):
        print(f"Error: File '{input_file}' not found!")
        return
    
    kelas_mata_kuliah, ruangan, mahasiswa = parse_input(input_file)
    hari = ['Senin', 'Selasa', 'Rabu', 'Kamis', 'Jumat']
    
    print(f"\nLoaded {len(kelas_mata_kuliah)} courses, {len(ruangan)} rooms, {len(mahasiswa)} students")
    
    jadwal_awal = generate_population(kelas_mata_kuliah, ruangan, hari)
    
    while True:
        print("\n" + "="*80)
        print("SELECT ALGORITHM")
        print("="*80)
        print("1. Steepest Ascent Hill Climbing")
        print("2. Hill Climbing with Sideways Move")
        print("3. Random Restart Hill Climbing")
        print("4. Stochastic Hill Climbing")
        print("5. Simulated Annealing")
        print("6. Genetic Algorithm")
        print("7. Run All Algorithms (except Genetic Algorithm)")
        print("0. Exit")
        
        choice = input("\nEnter your choice (0-7): ").strip()
        
        if choice == "1":
            run_steepest_ascent_hill_climbing(jadwal_awal, kelas_mata_kuliah, ruangan, mahasiswa, hari)
        
        elif choice == "2":
            run_sideways_hill_climbing(jadwal_awal, kelas_mata_kuliah, ruangan, mahasiswa, hari)
        
        elif choice == "3":
            run_random_restart_hill_climbing(kelas_mata_kuliah, ruangan, mahasiswa, hari)
        
        elif choice == "4":
            run_stochastic_hill_climbing(jadwal_awal, kelas_mata_kuliah, ruangan, mahasiswa, hari)
        
        elif choice == "5":
            run_simulated_annealing(jadwal_awal, kelas_mata_kuliah, ruangan, mahasiswa, hari)
        
        elif choice == "6":
            run_genetic_algorithm_experiment(kelas_mata_kuliah, ruangan, mahasiswa, hari)
        
        elif choice == "7":
            print("\n" + "="*80)
            print(f"{'RUNNING ALL ALGORITHMS (DEFAULT PARAMS)':^80}")
            print("="*80 + "\n")
            
            print("\n[1/5] Running Steepest Ascent Hill Climbing...")
            run_steepest_ascent_hill_climbing(jadwal_awal, kelas_mata_kuliah, ruangan, mahasiswa, hari)
            
            print("\n[2/5] Running Hill Climbing with Sideways Move...")
            run_sideways_hill_climbing(jadwal_awal, kelas_mata_kuliah, ruangan, mahasiswa, hari)
            
            print("\n[3/5] Running Random Restart Hill Climbing...")
            run_random_restart_hill_climbing(kelas_mata_kuliah, ruangan, mahasiswa, hari)
            
            print("\n[4/5] Running Stochastic Hill Climbing...")
            run_stochastic_hill_climbing(jadwal_awal, kelas_mata_kuliah, ruangan, mahasiswa, hari)
            
            print("\n[5/5] Running Simulated Annealing...")
            run_simulated_annealing(jadwal_awal, kelas_mata_kuliah, ruangan, mahasiswa, hari)
            
            print("\n" + "="*80)
            print(f"{'ALL ALGORITHMS COMPLETED':^80}")
            print("="*80 + "\n")
        
        elif choice == "0":
            print("\nGoodbye!")
            break
        
        else:
            print("\nInvalid choice! Please try again.")
        
        if choice != "0":
             input("\nPress Enter to return to the main menu...")

if __name__ == "__main__":
    main()