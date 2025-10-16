import copy
import random

def generate_all_neighbors(state, ruangan, hari, max_neighbors=500):
    """
    Generate neighbors for steepest ascent hill climbing with a limit.
    Combines swap neighbors and move neighbors up to max_neighbors limit.
    
    Args:
        state: Current schedule state
        ruangan: List of available rooms
        hari: List of available days
        max_neighbors: Maximum number of neighbors to generate (default: 500)
                      If None, generates all possible neighbors
    
    Returns:
        List of neighbor states (up to max_neighbors)
    """
    neighbors = []
    
    # Generate all swap neighbors (usually not too many)
    swap_neighbors = generate_all_swap_neighbors(state)
    neighbors.extend(swap_neighbors)
    
    # Calculate remaining budget for move neighbors
    if max_neighbors is not None:
        remaining = max_neighbors - len(neighbors)
        if remaining <= 0:
            return neighbors[:max_neighbors]
    else:
        remaining = None
    
    # Generate move neighbors (limited)
    move_neighbors = generate_all_move_neighbors(state, ruangan, hari, max_moves=remaining)
    neighbors.extend(move_neighbors)
    
    # Shuffle and limit if necessary
    if max_neighbors is not None and len(neighbors) > max_neighbors:
        random.shuffle(neighbors)
        neighbors = neighbors[:max_neighbors]
    
    return neighbors

def generate_all_swap_neighbors(state):
    neighbors = []
    
    if len(state) < 2:
        return neighbors
    
    # Try swapping every pair of sessions with the same duration
    for i in range(len(state)):
        sesi1 = state[i]
        durasi_sesi1 = sesi1['waktu_selesai'] - sesi1['waktu_mulai']
        
        for j in range(i + 1, len(state)):
            sesi2 = state[j]
            durasi_sesi2 = sesi2['waktu_selesai'] - sesi2['waktu_mulai']
            
            # Only swap if durations are the same
            if durasi_sesi1 == durasi_sesi2:
                jadwal_baru = copy.deepcopy(state)
                
                # Swap room, day, and start time
                jadwal_baru[i]['ruangan'], jadwal_baru[j]['ruangan'] = jadwal_baru[j]['ruangan'], jadwal_baru[i]['ruangan']
                jadwal_baru[i]['hari'], jadwal_baru[j]['hari'] = jadwal_baru[j]['hari'], jadwal_baru[i]['hari']
                jadwal_baru[i]['waktu_mulai'], jadwal_baru[j]['waktu_mulai'] = jadwal_baru[j]['waktu_mulai'], jadwal_baru[i]['waktu_mulai']
                
                # Update end times
                jadwal_baru[i]['waktu_selesai'] = jadwal_baru[i]['waktu_mulai'] + durasi_sesi1
                jadwal_baru[j]['waktu_selesai'] = jadwal_baru[j]['waktu_mulai'] + durasi_sesi2
                
                neighbors.append(jadwal_baru)
    
    return neighbors

def generate_all_move_neighbors(state, ruangan, hari, max_moves=None):
    neighbors = []
    
    # Build set of occupied slots for conflict checking
    terpakai = set()
    for i, sesi in enumerate(state):
        for jam in range(sesi['waktu_mulai'], sesi['waktu_selesai']):
            terpakai.add((i, sesi['hari'], jam, sesi['ruangan']))
    
    # Create list of all possible moves
    all_possible_moves = []
    for idx in range(len(state)):
        for ruang in ruangan:
            for hari_baru in hari:
                sesi = state[idx]
                durasi = sesi['waktu_selesai'] - sesi['waktu_mulai']
                for jam_mulai_baru in range(7, 19 - durasi):
                    all_possible_moves.append((idx, ruang['kode'], hari_baru, jam_mulai_baru))
    
    # Shuffle to get random sample if limited
    if max_moves is not None and len(all_possible_moves) > max_moves:
        random.shuffle(all_possible_moves)
        all_possible_moves = all_possible_moves[:max_moves]
    
    # Try each selected move
    for idx, ruangan_baru, hari_baru, jam_mulai_baru in all_possible_moves:
        sesi = state[idx]
        durasi = sesi['waktu_selesai'] - sesi['waktu_mulai']
        jam_selesai_baru = jam_mulai_baru + durasi
        
        # Skip if this is the same as current position
        if (ruangan_baru == sesi['ruangan'] and 
            hari_baru == sesi['hari'] and 
            jam_mulai_baru == sesi['waktu_mulai']):
            continue
        
        # Check if the new position is free (excluding current session's slots)
        kosong = True
        for jam in range(jam_mulai_baru, jam_selesai_baru):
            for (i, d, j, r) in terpakai:
                if i != idx and d == hari_baru and j == jam and r == ruangan_baru:
                    kosong = False
                    break
            if not kosong:
                break
        
        if kosong:
            jadwal_baru = copy.deepcopy(state)
            jadwal_baru[idx]['ruangan'] = ruangan_baru
            jadwal_baru[idx]['hari'] = hari_baru
            jadwal_baru[idx]['waktu_mulai'] = jam_mulai_baru
            jadwal_baru[idx]['waktu_selesai'] = jam_selesai_baru
            neighbors.append(jadwal_baru)
    
    return neighbors
