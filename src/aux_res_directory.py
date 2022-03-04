from pathlib import Path

def get_res_folder(*argv):
    # Carpeta src
    sz_csv_file = Path(__file__).parent
    # Carpeta del proyecto
    sz_csv_file = sz_csv_file.parent
    # Carpeta res
    sz_csv_file = sz_csv_file / "res"
    # Subdirectorio indicado por el usuario
    for subdir in argv:
        sz_csv_file = sz_csv_file / subdir

    return sz_csv_file
