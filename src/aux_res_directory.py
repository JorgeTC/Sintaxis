from pathlib import Path


def get_res_folder(*argv) -> Path:
    # Carpeta src
    path_file = Path(__file__).parent
    # Carpeta del proyecto
    path_file = path_file.parent
    # Carpeta res
    path_file = path_file / "res"
    # Subdirectorio indicado por el usuario
    for subdir in argv:
        path_file = path_file / subdir

    return path_file

def get_test_res_folder(*argv) -> Path:
    # Carpeta src
    path_file = Path(__file__).parent
    # Carpeta del proyecto
    path_file = path_file.parent
    # Carpeta test
    path_file = path_file / "test"
    # Carpeta res
    path_file = path_file / "res"
    # Subdirectorio indicado por el usuario
    for subdir in argv:
        path_file = path_file / subdir

    return path_file
