def main():

    from src.dlg_config import manage_config

    manage_config()

    from src.usuario import Usuario
    from src.excel_mgr import ExcelMgr
    from src.writer import Writer

    usuario = Usuario()

    ex_doc = ExcelMgr(usuario.nombre)

    writer = Writer(usuario.id, ex_doc.get_worksheet())
    writer.read_watched()

    ex_doc.save_wb()

if __name__ == "__main__":
    main()
