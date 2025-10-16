import random
import copy

def generate_neighbor(state, ruangan, hari):
    langkah = random.choice(["swap","move"])
    if langkah == "swap":
        return generate_neighbor_swap(state)
    else:
        return generate_neighbor_move(state, ruangan, hari)
        
def generate_neighbor_swap(state):
    jadwal_baru = copy.deepcopy(state)
    
    if len(jadwal_baru) < 2:
        return jadwal_baru
    
    idx1 = random.randrange(len(jadwal_baru))
    sesi1 = jadwal_baru[idx1]
    durasi_sesi = sesi1['waktu_selesai'] - sesi1['waktu_mulai']
    
    kandidat_swap = []
    
    for i, sesi in enumerate(jadwal_baru):
        if i == idx1: continue
        durasi_sesi_lain = sesi['waktu_selesai'] - sesi['waktu_mulai']
        if durasi_sesi == durasi_sesi_lain:
            kandidat_swap.append(i)
        
    if kandidat_swap:
        idx2 = random.choice(kandidat_swap)
        sesi2 = jadwal_baru[idx2]

        sesi1['ruangan'], sesi2['ruangan'] = sesi2['ruangan'], sesi1['ruangan']
        sesi1['hari'], sesi2['hari'] = sesi2['hari'], sesi1['hari']
        sesi1['waktu_mulai'], sesi2['waktu_mulai'] = sesi2['waktu_mulai'], sesi1['waktu_mulai']
        
        sesi1['waktu_selesai'] = sesi1['waktu_mulai'] + durasi_sesi
        sesi2['waktu_selesai'] = sesi2['waktu_mulai'] + durasi_sesi
    
    return jadwal_baru

def generate_neighbor_move(state, ruangan, hari, maksimal=100):
    jadwal_baru = copy.deepcopy(state)
    
    terpakai = set()
    for i, sesi in enumerate(jadwal_baru):
        for jam in range(sesi['waktu_selesai'] - sesi['waktu_mulai']):
            terpakai.add((sesi['hari'], jam, sesi['ruangan']))
            
    idx = random.randrange(len(jadwal_baru))
    sesi = jadwal_baru[idx]
    durasi = sesi['waktu_selesai'] - sesi['waktu_mulai']
    
    percobaan = 0
    while percobaan < maksimal:
        percobaan += 1
        ruangan_baru = random.choice(ruangan)['kode']
        hari_baru = random.choice(hari)
        jam_mulai_baru = random.randint(7, 18 - durasi)
        
        kosong = True
        for jam in range(jam_mulai_baru, jam_mulai_baru + durasi):
            if (hari_baru, jam, ruangan_baru) in terpakai:
                kosong = False
                break
        
        if kosong:
            jadwal_baru[idx]['ruangan'] = ruangan_baru
            jadwal_baru[idx]['hari'] = hari_baru
            jadwal_baru[idx]['waktu_mulai'] = jam_mulai_baru
            jadwal_baru[idx]['waktu_selesai'] = jam_mulai_baru + durasi
            break
        
    return jadwal_baru