import math
import random
import copy
from simulated_annealing.objective_function import objective_function
from simulated_annealing.generate_neighbor import generate_neighbor

def stochastic_hill_climbing(initial_state, kelas_mata_kuliah, ruangan, mahasiswa, hari, max_iter=1000):
    current_state = copy.deepcopy(initial_state)
    current_penalty = objective_function(current_state, kelas_mata_kuliah, ruangan, mahasiswa)
    
    iterasi = 0
    for iteration in range(max_iter):
        iterasi += 1
        neighbor = generate_neighbor(current_state, ruangan, hari)
        neighbor_penalty = objective_function(neighbor, kelas_mata_kuliah, ruangan, mahasiswa)
        
        if neighbor_penalty < current_penalty:
            current_state = neighbor
            current_penalty = neighbor_penalty
        
        if current_penalty == 0:
            print("\nInfo: Solusi optimal (penalti = 0) ditemukan. Menghentikan pencarian lebih awal.")
            return current_state, current_penalty, iterasi
    
    print("\nInfo: Maksimum iterasi tercapai. Menghentikan pencarian.")
    return current_state, current_penalty, iterasi