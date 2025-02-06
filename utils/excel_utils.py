import pandas as pd

def read_excel(file_path, sheet_name):
    """
    Lee una hoja específica de un archivo Excel.

    Args:
        file_path (str): Ruta al archivo Excel.
        sheet_name (str): Nombre de la hoja.

    Returns:
        pd.DataFrame: Datos leídos.
    """
    try:
        return pd.read_excel(file_path, sheet_name=sheet_name)
    except FileNotFoundError:
        raise FileNotFoundError(f"El archivo {file_path} no existe.")
    except ValueError:
        raise ValueError(f"La hoja '{sheet_name}' no existe en {file_path}.")

def write_excel(dataframe, file_path):
    """
    Escribe un DataFrame en un archivo Excel.

    Args:
        dataframe (pd.DataFrame): Datos a escribir.
        file_path (str): Ruta del archivo de salida.
    """
    dataframe.to_excel(file_path, index=False)


def save_to_excel(data, file_path):
    """
    Guarda los resultados de la extracción en un archivo Excel.
    """
    try:
        df = pd.DataFrame(data)
        df.to_excel(file_path, index=False)
        print(f"✅ Resultados guardados en {file_path}")
    except Exception as e:
        print(f"❌ Error al guardar en Excel: {e}")