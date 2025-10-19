import copy
from simulated_annealing.objective_function import objective_function
from simulated_annealing.generate_neighbor import generate_neighbor

def stochastic_hill_climbing(initial_state, kelas_mata_kuliah, ruangan, mahasiswa, hari, max_iter=1000):
    current_state = copy.deepcopy(initial_state)
    current_penalty = objective_function(current_state, kelas_mata_kuliah, ruangan, mahasiswa)
    
    history = {'iterasi': [0], 'penalti': [current_penalty]}
    iterasi_total = 0
    for _ in range(max_iter):
        iterasi_total += 1
        neighbor = generate_neighbor(current_state, ruangan, hari)
        neighbor_penalty = objective_function(neighbor, kelas_mata_kuliah, ruangan, mahasiswa)
        
        if  neighbor_penalty == 0:
            history['iterasi'].append(iterasi_total)
            history['penalti'].append(neighbor_penalty)
            print("\nInfo: Solusi optimal (penalti = 0) ditemukan. Menghentikan pencarian lebih awal.")
            return neighbor, neighbor_penalty, history, iterasi_total
        
        if neighbor_penalty < current_penalty:
            history['iterasi'].append(iterasi_total)
            history['penalti'].append(neighbor_penalty)
            current_state = neighbor
            current_penalty = neighbor_penalty
    
    print("\nInfo: Maksimum iterasi tercapai. Menghentikan pencarian.")
    return current_state, current_penalty, history, history['iterasi'][-1]