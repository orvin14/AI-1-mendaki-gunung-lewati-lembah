import random
def bagi_sesi(sks):
    pembagian = []
    sisa = sks
    while sisa > 0:
        durasi = random.randint(1, sisa)
        pembagian.append(durasi)
        sisa -= durasi
    random.shuffle(pembagian)
    return pembagian

def generate_sesi(kode, durasi, ruangan, hari):
    ruangan = random.choice(ruangan)
    hari= random.choice(hari)
    waktu_mulai = random.randint(7, 18 - durasi)
    waktu_selesai = waktu_mulai + durasi
    return {
        'kode': kode,
        'ruangan': ruangan['kode'],
        'hari': hari,
        'waktu_mulai': waktu_mulai,
        'waktu_selesai': waktu_selesai
    }

def generate_population(kelas_mata_kuliah, ruangan, hari):
    population = []
    for kelas in kelas_mata_kuliah:
        sks = kelas['sks']
        kode = kelas['kode']
        sesi_durasi = bagi_sesi(sks)
        for durasi in sesi_durasi:
            sesi = generate_sesi(kode, durasi, ruangan, hari)
            population.append(sesi)
    return population