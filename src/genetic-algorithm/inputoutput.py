import json
import matplotlib.pyplot as plt
def parse_input(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
    kelas_mata_kuliah = data.get('kelas_mata_kuliah', [])
    ruangan = data.get('ruangan', [])
    mahasiswa = data.get('mahasiswa', [])
    return kelas_mata_kuliah, ruangan, mahasiswa

def print_schedule(schedule):
    rooms = {}
    weekdays = ['Senin', 'Selasa', 'Rabu', 'Kamis', 'Jumat']

    min_hour = 7
    max_hour = 18
    for sesi in schedule:
        ruangan = sesi.get('ruangan')
        if isinstance(ruangan, dict):
            room_key = ruangan.get('kode')
        else:
            room_key = str(ruangan)

        rooms.setdefault(room_key, []).append(sesi)

        jm = sesi.get('waktu_mulai')
        je = sesi.get('waktu_selesai')
        if isinstance(jm, int) and jm < min_hour:
            min_hour = jm
        if isinstance(je, int) and je > max_hour:
            max_hour = je
    for room in sorted(rooms):
        grid = {h: {d: '' for d in weekdays} for h in range(min_hour, max_hour)}

        for sesi in rooms[room]:
            kode = sesi.get('kode', '')
            hari = sesi.get('hari')
            jm = sesi.get('waktu_mulai')
            if hari in weekdays and isinstance(jm, int):
                grid[jm][hari] = kode

        print(f"Kode ruang: {room}")
        header = ['Jam'] + weekdays
        col_widths = [6] + [12] * len(weekdays)
        def format_row(cells):
            parts = []
            for i, cell in enumerate(cells):
                parts.append(str(cell).ljust(col_widths[i]))
            return '|'.join(parts)

        print(format_row(header))
        for hour in range(min_hour, max_hour):
            row = [str(hour)] + [grid[hour][d] for d in weekdays]
            print(format_row(row))
        print()

def output(best_individual, max_fitness, return_iteration, max_iter, avg_iter, total_ind, exec_time):
    print("Best individual:")
    print_schedule(best_individual)
    print("Max fitness:", max_fitness)
    print("Jumlah populasi: ", total_ind)
    print("Banyak iterasi: ", return_iteration)
    print(f"Durasi proses pencarian: {exec_time:.4f} detik")
    if return_iteration == 1:
        plt.scatter([1], max_iter, label="Max Fitness", s=100)
        plt.scatter([1], avg_iter, label="Average Fitness", s=100)
        plt.text(1, max_iter[0], "Solved at Iteration 1", ha='left', va='bottom')
    else:
        plt.plot(range(1, len(max_iter)+1), max_iter, label="Max Fitness")
        plt.plot(range(1, len(max_iter)+1), avg_iter, label="Average Fitness")
    plt.xlabel('Iterations')
    plt.ylabel('Fitness')
    plt.title('Genetic Algorithm Fitness Over Time')
    plt.legend()
    plt.show()