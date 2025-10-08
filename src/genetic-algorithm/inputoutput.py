import json

def parse_input(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
    kelas_mata_kuliah = data.get('kelas_mata_kuliah', [])
    ruangan = data.get('ruangan', [])
    mahasiswa = data.get('mahasiswa', [])
    return kelas_mata_kuliah, ruangan, mahasiswa
