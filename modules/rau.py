from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
import pandas as pd
import time

def run_rau_analysis(driver):
    """
    Ejecuta el análisis para la plataforma RAU.

    Args:
        driver (WebDriver): Instancia del navegador.
    """
    # Link de RAU
    rau_link = "https://rockwell.csod.com/login/render.aspx?id=defaultclp"
    driver.get(rau_link)

    # Esperar a que la página cargue
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "userNameBox"))
        )
    except TimeoutException:
        print("La página de inicio de sesión no cargó correctamente.")
        return

    # Leer datos del Excel
    excel_path = r"D:\OneDrive - Tunning Ingenieria SPA\Escritorio\proyecto de automatiacion\Excel datos\Datos P&T Version Actualizada.xlsx"
    output_path = r"D:\OneDrive - Tunning Ingenieria SPA\Escritorio\proyecto de automatiacion\data\results\platforms.xlsx"
    data = pd.read_excel(excel_path, sheet_name="Plan Capacitacion RA", header=1)

    results = []

    for _, row in data.iterrows():
        correo = row['Correo']
        contrasena = row["Clave Nueva De Acceso"]
        try:
            # Localizar los elementos
            email_field = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "userNameBox"))
            )
            password_field = driver.find_element(By.ID, "passWordBox")
            login_button = driver.find_element(By.CSS_SELECTOR, '.CsImageButton1[aria-label="Click on Log In"]')

            # Ingresar credenciales y hacer clic en "Login"
            email_field.clear()
            password_field.clear()
            email_field.send_keys(correo)
            password_field.send_keys(contrasena)
            login_button.click()

            # Esperar redirección o validación (15 segundos máximo)
            try:
                WebDriverWait(driver, 15).until(
                    EC.url_changes(rau_link)
                )
            
                

            except TimeoutException:
                # Detectar si aparece el formulario de cambio de contraseña
                try:
                    change_password_form = WebDriverWait(driver, 5).until(
                        EC.presence_of_element_located((By.ID, "cancelImageButton"))
                    )
                    print(f"Solicitud de cambio de contraseña detectada para {correo}.")
                    # Hacer clic en "Cancelar"
                    cancel_button = driver.find_element(By.ID, "cancelImageButton")
                    cancel_button.click()
                    results.append({"Correo": correo, "Estado": "Cambio de contraseña solicitado"})
                    driver.get(rau_link)  # Regresar al inicio
                    continue
                except TimeoutException:
                    print(f"No se detectó formulario de cambio de contraseña para {correo}.")
                    results.append({"Correo": correo, "Estado": "Error al iniciar sesión"})
                    continue

            # Si el login es exitoso
            print(f"Ingreso exitoso para {correo}")
            results.append({"Correo": correo, "Estado": "Login exitoso"})

        except NoSuchElementException as e:
            print(f"Error con {correo}: Elemento no encontrado - {e}")
            results.append({"Correo": correo, "Estado": f"Elemento no encontrado - {e}"})

        except WebDriverException as e:
            print(f"Error general del navegador con {correo}: {e}")
            results.append({"Correo": correo, "Estado": f"Error del navegador - {e}"})

        # Pausa opcional entre intentos
        time.sleep(5)

    # Guardar los resultados en un archivo Excel
    results_df = pd.DataFrame(results)
    results_df.to_excel(output_path, index=False)
    print(f"Resultados guardados en {output_path}")
