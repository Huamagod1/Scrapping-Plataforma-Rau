from selenium import webdriver
from selenium.webdriver.edge.service import Service
from modules.rau import run_rau_analysis
from modules.siemens import run_siemens_analysis
"""from modules.cisco import run_cisco_analysis
from modules.honeywell import run_honeywell_analysis"""

def initialize_driver():
    """
    Inicializa y configura un navegador Edge.
    """
    driver_path = r"D:\OneDrive - Tunning Ingenieria SPA\Escritorio\proyecto de automatiacion\web\edgedriver_win64\msedgedriver.exe"
    service = Service(driver_path)
    options = webdriver.EdgeOptions()
    options.add_argument("--start-maximized")
    driver = webdriver.Edge(service=service, options=options)
    return driver

def execute_platform_analysis(platform):
    """
    Ejecuta el análisis de la plataforma seleccionada.

    Args:
        platform (str): Nombre de la plataforma ('RAU', 'Siemens', 'Cisco', 'Honeywell').
    """
    driver = initialize_driver()
    try:
        if platform == "RAU":
            run_rau_analysis(driver)
        elif platform == "Siemens":
            run_siemens_analysis(driver)
        elif platform == "Cisco":
            run_cisco_analysis(driver)
        elif platform == "Honeywell":
            run_honeywell_analysis(driver)
        else:
            print(f"Plataforma '{platform}' no reconocida.")
    finally:
        driver.quit()
