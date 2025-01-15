from utils.selenium_utils import execute_platform_analysis

def main():
    """
    Ejecuta el análisis para la plataforma seleccionada.
    Cambia 'RAU' por la plataforma que deseas analizar.
    """
    platform = "Siemens"  # Cambiar a 'Siemens', 'Cisco', 'Honeywell' según sea necesario
    execute_platform_analysis(platform)

if __name__ == "__main__":
    main()
