import random


def fitness_function(population, kelas_mata_kuliah, ruangan, mahasiswa):
    conflict = 0
    for i in range(len(mahasiswa)):
        daftar_mk = mahasiswa[i]['daftar_mk']
        jadwal_mahasiswa = [sesi for sesi in population if sesi['kode'] in daftar_mk]
        for j in range(len(jadwal_mahasiswa)):
            for k in range(j + 1, len(jadwal_mahasiswa)):
                if jadwal_mahasiswa[j]['hari'] == jadwal_mahasiswa[k]['hari']:
                    if not (jadwal_mahasiswa[j]['waktu_selesai'] <= jadwal_mahasiswa[k]['waktu_mulai'] or
                            jadwal_mahasiswa[k]['waktu_selesai'] <= jadwal_mahasiswa[j]['waktu_mulai']):
                        conflict += 10
                        # print(f"Conflict for student {mahasiswa[i]['nim']} between {jadwal_mahasiswa[j]['kode']} and {jadwal_mahasiswa[k]['kode']}")
    for i in range(len(population)):
        sesi1 = population[i]
        for j in range(i + 1, len(population)):
            sesi2 = population[j]
            if sesi1['ruangan'] == sesi2['ruangan'] and sesi1['hari'] == sesi2['hari']:
                if not (sesi1['waktu_selesai'] <= sesi2['waktu_mulai'] or sesi2['waktu_selesai'] <= sesi1['waktu_mulai']):
                    conflict += 10
                    # print(f"Conflict in room {sesi1['ruangan']} between {sesi1['kode']} and {sesi2['kode']}")
    for i in range(len(population)):
        sesi = population[i]
        kelas_sesi = kelas_mata_kuliah[0]
        ruangan_sesi = ruangan[0]
        for kelas in kelas_mata_kuliah:
            if kelas['kode'] == sesi['kode']:
                kelas_sesi = kelas
        for ruang in ruangan:
            if ruang['kode'] == sesi['ruangan']:
                ruangan_sesi = ruang
        if kelas_sesi['jumlah_mahasiswa'] > ruangan_sesi['kuota']:
            conflict += (kelas_sesi['jumlah_mahasiswa'] - ruangan_sesi['kuota'])
            # print(f"Capacity conflict in room {sesi['ruangan']} for class {sesi['kode']}")
    return 1/(1+conflict)

def selection(population, kelas_mata_kuliah, ruangan, mahasiswa, num_parents):
    fitness_scores = [fitness_function(individual, kelas_mata_kuliah, ruangan, mahasiswa) for individual in population]
    total = sum(fitness_scores)
    probabilities = [score / total for score in fitness_scores]
    cumulative_probabilities = []
    cumulative_sum = 0
    for prob in probabilities:
        cumulative_sum += prob
        cumulative_probabilities.append(cumulative_sum)
    parents = []
    for _ in range(num_parents):
        r = random.random()
        for i, cumulative_prob in enumerate(cumulative_probabilities):
            if r <= cumulative_prob:
                parents.append(population[i])
                break
    return parents

def crossover(parent1, parent2):
    point = random.randint(1, len(parent1) - 1)
    child1 = parent1[:point] + parent2[point:]
    child2 = parent2[:point] + parent1[point:]
    return child1, child2

def mutate(individu, ruangan, hari, waktu_mulai, mutation_rate=0.1, fitness=None):
    if fitness is not None and fitness <0.2:
        mutation_rate *= 2
    elif fitness is not None and fitness <0.5:
        mutation_rate *= 1.5
    elif fitness is not None and fitness >0.8:
        mutation_rate /= 2
    individu_baru = []
    for gen in individu:
        gen_baru = gen.copy()
        if random.random() < mutation_rate:
            mutated = random.randint(0, 2)
            if mutated == 0:
                gen_baru["ruangan"] = random.choice(ruangan)
            elif mutated == 1:
                gen_baru["hari"] = random.choice(hari)
            else:
                durasi = gen_baru["waktu_selesai"] - gen_baru["waktu_mulai"]
                waktu_mulai_baru = random.choice(waktu_mulai)
                waktu_selesai_baru = waktu_mulai_baru + durasi

                if waktu_selesai_baru > 18:
                    waktu_mulai_baru = 18 - durasi
                    waktu_selesai_baru = 18

                gen_baru["waktu_mulai"] = waktu_mulai_baru
                gen_baru["waktu_selesai"] = waktu_selesai_baru

        individu_baru.append(gen_baru)
    return individu_baru

def genetic_algorithm(population, kelas_mata_kuliah, ruangan, mahasiswa, hari,waktu_mulai, num_parent, iterations):
    max_iter = []
    avg_iter = []
    for i in range(iterations):
        fitness_scores = [fitness_function(individual, kelas_mata_kuliah, ruangan, mahasiswa) for individual in population]
        max_fitness = max(fitness_scores)
        max_iter.append(max_fitness)
        avg_iter.append(sum(fitness_scores) / len(fitness_scores))
        best_individual = population[fitness_scores.index(max_fitness)]
        if max_fitness == 1:
            return max_fitness, best_individual, i+1, max_iter, avg_iter
        parents = selection(population, kelas_mata_kuliah, ruangan, mahasiswa, num_parent)
        new_population = []
        for j in range(0, num_parent, 2):
            parent1 = parents[j]
            parent2 = parents[j + 1] if j + 1 < num_parent else parents[0]
            child1, child2 = crossover(parent1, parent2)
            new_population.append(mutate(child1, ruangan, hari, waktu_mulai, fitness_function(child1, kelas_mata_kuliah, ruangan, mahasiswa)))
            new_population.append(mutate(child2, ruangan, hari, waktu_mulai, fitness_function(child2, kelas_mata_kuliah, ruangan, mahasiswa)))
        new_population[random.randint(0, num_parent - 1)] = best_individual
        population = new_population
    print("Max iterations reached")
    fitness_scores = [fitness_function(individual, kelas_mata_kuliah, ruangan, mahasiswa) for individual in population]
    max_fitness = max(fitness_scores)
    best_individual = population[fitness_scores.index(max_fitness)]
    return max_fitness, best_individual, iterations, max_iter, avg_iter