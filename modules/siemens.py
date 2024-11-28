from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
import pandas as pd
import time

def run_siemens_analysis(driver):
    """
    Ejecuta el análisis para la plataforma Siemens, procesando un usuario a la vez.

    Args:
        driver (WebDriver): Instancia del navegador.
    """
    # Link de Siemens
    siemens_link = "https://p-acad.siemens.cloud/"
    driver.get(siemens_link)

    # Esperar a que la página cargue
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "ContentPlaceHolder1_TextSiemensLogin"))
        )
    except TimeoutException:
        print("La página de inicio de sesión no cargó correctamente.")
        return

    # Leer datos del Excel
    excel_path = r"D:\OneDrive - Tunning Ingenieria SPA\Escritorio\proyecto de automatiacion\Excel datos\Datos P&T Version Actualizada.xlsx"
    output_path = r"D:\OneDrive - Tunning Ingenieria SPA\Escritorio\proyecto de automatiacion\data\results\platforms.xlsx"
    data = pd.read_excel(excel_path, sheet_name="Plan Capacitacion Siemens", header=1)

    results = []

    for _, row in data.iterrows():
        correo = row['Correo']
        contrasena = row["Clave Nueva De Acceso"]
        try:
            # Login del usuario
            if not login(driver, correo, contrasena):
                results.append({"Correo": correo, "Estado": "Login fallido"})
                continue

            # Navegar a la sección 'Me'
            if not navigate_to_me(driver):
                results.append({"Correo": correo, "Estado": "Falló la navegación a 'Me'"})
                continue

            # Aquí continuaríamos con la extracción de datos (In Progress y Completed)

            results.append({"Correo": correo, "Estado": "Proceso completado correctamente"})

        except Exception as e:
            print(f"Error inesperado con {correo}: {e}")
            results.append({"Correo": correo, "Estado": f"Error inesperado: {e}"})

        # Pausa opcional entre intentos
        time.sleep(5)

    # Guardar los resultados en un archivo Excel
    results_df = pd.DataFrame(results)
    results_df.to_excel(output_path, index=False)
    print(f"Resultados guardados en {output_path}")


def login(driver, email, password):
    """
    Realiza el inicio de sesión en la plataforma.

    Args:
        driver (WebDriver): Instancia del navegador.
        email (str): Correo del usuario.
        password (str): Contraseña del usuario.

    Returns:
        bool: True si el login fue exitoso, False de lo contrario.
    """
    try:
        # Localizar los elementos
        driver.find_element(By.ID, "ContentPlaceHolder1_TextSiemensLogin").send_keys(email)
        driver.find_element(By.ID, "ContentPlaceHolder1_TextPassword").send_keys(password)
        driver.find_element(By.ID, "ContentPlaceHolder1_LoginUserNamePasswordButton").click()

        # Esperar redirección o mensaje de error
        time.sleep(5)
        error_message = driver.find_elements(By.ID, "ContentPlaceHolder1_MessageRepeaterLogin_MessageItemLogin_0")
        if error_message:
            print(f"Error de login para {email}: {error_message[0].text}")
            return False

        print(f"Login exitoso para {email}")
        return True

    except Exception as e:
        print(f"Error durante el login para {email}: {e}")
        return False


def navigate_to_me(driver):
    """
    Navega al menú y selecciona la opción 'Me'.

    Args:
        driver (WebDriver): Instancia del navegador.

    Returns:
        bool: True si la navegación fue exitosa, False de lo contrario.
    """
    try:
        # Hacer clic en el menú (tres líneas)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "hamburger-trigger"))
        ).click()
        print("Menú abierto.")

        # Seleccionar la opción 'Me'
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "framework-tile"))
        ).click()
        print("Navegación exitosa a la sección 'Me'.")
        return True

    except TimeoutException:
        print("Error: No se pudo navegar a la sección 'Me'.")
        return False

