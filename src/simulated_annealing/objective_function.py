def bobot_penalti(prioritas):
    match prioritas:
        case 1: return 1.75
        case 2: return 1.5
        case 3: return 1.25
        case _: return 1.0

def objective_function(population, kelas_mata_kuliah, ruangan, mahasiswa):
    conflict = 0
    for i in range(len(mahasiswa)):
        daftar_mk = mahasiswa[i]['daftar_mk']
        jadwal_mahasiswa = [sesi for sesi in population if sesi['kode'] in daftar_mk]
        for j in range(len(jadwal_mahasiswa)):
            for k in range(j + 1, len(jadwal_mahasiswa)):
                if jadwal_mahasiswa[j]['hari'] == jadwal_mahasiswa[k]['hari']:
                    if not (jadwal_mahasiswa[j]['waktu_selesai'] <= jadwal_mahasiswa[k]['waktu_mulai'] or
                            jadwal_mahasiswa[k]['waktu_selesai'] <= jadwal_mahasiswa[j]['waktu_mulai']):
                        conflict += 2
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
            conflict += (kelas_sesi['jumlah_mahasiswa'] - ruangan_sesi['kuota'])*(sesi['waktu_selesai'] - sesi['waktu_mulai'])
            # print(f"Capacity conflict in room {sesi['ruangan']} for class {sesi['kode']}")
    return conflict