import json
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from utils.login import login


    # Ruta al ChromeDriver
chrome_driver_path = ".\chromedriver-win64\chromedriver.exe"

# Carga la configuración
with open("config.json", "r") as f:
        config = json.load(f)
    

# Configura el servicio de ChromeDriver
service = Service(chrome_driver_path)
driver = webdriver.Chrome(service=service)


try:
    # Realiza el inicio de sesión
    login(driver, config)
    print("Inicio de sesión exitoso.")
    
    
    # Pausa para observar el resultado
    input("Presiona Enter para cerrar el navegador...")

except Exception as e:
    print(f"Ocurrió un error: {e}")
finally:
    driver.quit()
