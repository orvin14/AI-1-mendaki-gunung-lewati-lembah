import random

def bobot_penalti(prioritas):
    match prioritas:
        case 1: return 1.75
        case 2: return 1.5
        case 3: return 1.25
        case _: return 1.0

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
                    for siswa in mahasiswa:
                        if sesi1['kode'] in siswa['daftar_mk']:
                            conflict += (sesi1['waktu_selesai'] - sesi1['waktu_mulai'])*bobot_penalti(siswa['prioritas'][siswa['daftar_mk'].index(sesi1['kode'])])
                    for siswa in mahasiswa:
                        if sesi2['kode'] in siswa['daftar_mk']:
                            conflict += (sesi2['waktu_selesai'] - sesi2['waktu_mulai'])*bobot_penalti(siswa['prioritas'][siswa['daftar_mk'].index(sesi2['kode'])])
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
    parents = []
    index = list(range(len(population)))
    tournament_size = min(3, max(2, len(population) // 10))
    tournament_p = 0.75
    for _ in range(num_parents):
        contenders = random.sample(index, k=min(tournament_size, len(index)))
        contenders.sort(key=lambda i: fitness_scores[i], reverse=True)
        if random.random() < tournament_p:
            winner_idx = contenders[0]
        else:
            winner_idx = random.choice(contenders)
        parents.append(population[winner_idx])
    return parents

def crossover(parent1, parent2):
    point = random.randint(1, len(parent1) - 1)
    child1 = parent1[:point] + parent2[point:]
    child2 = parent2[:point] + parent1[point:]
    return child1, child2

def mutate(individu, ruangan, hari, waktu_mulai, mutation_rate=0.1, fitness=None):
    # if fitness is not None and fitness <0.2:
    #     mutation_rate *= 2
    # elif fitness is not None and fitness <0.5:
    #     mutation_rate *= 1.5
    # elif fitness is not None and fitness >0.8:
    #     mutation_rate /= 2
    individu_baru = []
    for gen in individu:
        gen_baru = gen.copy()
        if random.random() < mutation_rate:
            mutated = random.randint(0, 2)
            if mutated == 0:
                choice = random.choice(ruangan)
                if isinstance(choice, dict):
                    gen_baru["ruangan"] = choice.get('kode', choice)
                else:
                    gen_baru["ruangan"] = choice
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

def genetic_algorithm(population, kelas_mata_kuliah, ruangan, mahasiswa, hari,waktu_mulai, iterations):
    population_size = len(population)
    max_iter = []
    avg_iter = []
    total_ind = 0
    elite_count = max(1, population_size // 10)
    mutation_rate = 0.1
    stagnan = 0
    current_best = None

    for gen in range(1, iterations + 1):
        fitness_scores = [fitness_function(individual, kelas_mata_kuliah, ruangan, mahasiswa) for individual in population]
        max_fitness = max(fitness_scores)
        avg_fitness = sum(fitness_scores) / len(fitness_scores)
        max_iter.append(max_fitness)
        avg_iter.append(avg_fitness)
        best_idx = fitness_scores.index(max_fitness)
        best_individual = population[best_idx]

        if max_fitness == 1:
            return max_fitness, best_individual, gen, max_iter, avg_iter, total_ind

        # deteksi stagnasi
        if current_best is None or max_fitness > current_best + 1e-12:
            current_best = max_fitness
            stagnan = 0
        else:
            stagnan += 1

        # adaptive mutation
        mutation_multiplier = 1.0
        if stagnan >= 10:
            mutation_multiplier = 1.5
        if stagnan >= 30:
            mutation_multiplier = 2.5

        # elitism
        sorted_population = sorted(zip(population, fitness_scores), key=lambda p: p[1], reverse=True)
        new_population = [p[0] for p in sorted_population[:elite_count]]

        while len(new_population) < population_size:
            parents = selection(population, kelas_mata_kuliah, ruangan, mahasiswa, 2)
            parent1, parent2 = parents[0], parents[1]
            child1, child2 = crossover(parent1, parent2)
            # kemungkinan kecil ada individu baru
            immigrant_rate = 0.03
            def randomize_child(child):
                child_copy = [g.copy() for g in child]
                for _ in range(max(1, len(child_copy) // 5)):
                    g = random.choice(child_copy)
                    rc = random.choice(ruangan)
                    if isinstance(rc, dict):
                        g['ruangan'] = rc.get('kode', g.get('ruangan'))
                    else:
                        g['ruangan'] = rc
                    g['hari'] = random.choice(hari)
                    dur = g.get('waktu_selesai', 1) - g.get('waktu_mulai', 0)
                    start = random.choice(waktu_mulai)
                    g['waktu_mulai'] = start
                    g['waktu_selesai'] = min(18, start + max(1, dur))
                return child_copy

            if random.random() < immigrant_rate:
                child1 = randomize_child(child1)
            if random.random() < immigrant_rate:
                child2 = randomize_child(child2)

            f1 = fitness_function(child1, kelas_mata_kuliah, ruangan, mahasiswa)
            f2 = fitness_function(child2, kelas_mata_kuliah, ruangan, mahasiswa)
            child1 = mutate(child1, ruangan, hari, waktu_mulai, mutation_rate * mutation_multiplier, fitness=f1)
            child2 = mutate(child2, ruangan, hari, waktu_mulai, mutation_rate * mutation_multiplier, fitness=f2)
            new_population.append(child1)
            if len(new_population) < population_size:
                new_population.append(child2)
            total_ind += 2

        population = new_population[:population_size]

    fitness_scores = [fitness_function(individual, kelas_mata_kuliah, ruangan, mahasiswa) for individual in population]
    max_fitness = max(fitness_scores)
    best_individual = population[fitness_scores.index(max_fitness)]
    return max_fitness, best_individual, iterations, max_iter, avg_iter, total_ind