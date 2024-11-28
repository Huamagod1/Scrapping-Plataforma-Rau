from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
import pandas as pd


def run_cisco_analysis(driver):
    """
    Ejecuta el análisis para la plataforma Cisco, procesando un usuario a la vez.

    Args:
        driver (WebDriver): Instancia del navegador.
    """
    # URL de Cisco
    cisco_url = "https://salesconnect.cisco.com/blackbeltpartneracademy/s/"
    driver.get(cisco_url)

    # Leer datos del Excel
    excel_path = r"D:\OneDrive - Tunning Ingenieria SPA\Escritorio\proyecto de automatiacion\Excel datos\Datos P&T Version Actualizada.xlsx"
    output_path = r"D:\OneDrive - Tunning Ingenieria SPA\Escritorio\proyecto de automatiacion\data\results\platforms.xlsx"
    data = pd.read_excel(excel_path, sheet_name="Plan Capacitacion Cisco", header=3)

    results = []

    for _, row in data.iterrows():
        email = row['Correo']
        password = row['Clave Nueva De Acceso']

        try:
            # Login del usuario
            if not login_cisco(driver, email, password):
                results.append({"Correo": email, "Estado": "Falló el inicio de sesión"})
                continue

            # Verificar y manejar la pantalla "Finish Logging In"
            handle_finish_logging_in(driver)

            # Navegar al menú y seleccionar "My Learning"
            if not navigate_to_my_learning(driver):
                results.append({"Correo": email, "Estado": "Falló al acceder a 'My Learning'"})
                continue

            # Aquí puedes agregar pasos adicionales para extraer información
            print(f"Usuario {email} procesado exitosamente.")

            results.append({"Correo": email, "Estado": "Inicio de sesión exitoso y acceso a 'My Learning'"})

        except Exception as e:
            print(f"Error inesperado con {email}: {e}")
            results.append({"Correo": email, "Estado": f"Error inesperado: {e}"})

       

    # Guardar los resultados en un archivo Excel
    results_df = pd.DataFrame(results)
    results_df.to_excel(output_path, index=False)
    print(f"Resultados guardados en {output_path}")


def login_cisco(driver, email, password):
    """
    Realiza el inicio de sesión en la plataforma Cisco.

    Args:
        driver (WebDriver): Instancia del navegador.
        email (str): Correo del usuario.
        password (str): Contraseña del usuario.

    Returns:
        bool: True si el login fue exitoso, False de lo contrario.
    """
    try:
        # Ingresar correo electrónico
        email_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "input28"))
        )
        email_field.clear()
        email_field.send_keys(email)

        # Hacer clic en "Siguiente"
        next_button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//input[@value='Siguiente']"))
        )
        next_button.click()

        # Esperar a que aparezca el campo de contraseña
        password_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "credentials.passcode"))
        )
        time.sleep(2)

        # Ingresar contraseña
        password_field.clear()
        password_field.send_keys(password)

        # Hacer clic en "Verificar"
        verify_button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//input[@value='Verificar']"))
        )
        verify_button.click()

        # Esperar redirección o validación
        WebDriverWait(driver, 10).until(EC.url_changes(driver.current_url))

        print(f"Inicio de sesión exitoso para {email}")
        return True

    except TimeoutException:
        print(f"Error durante el inicio de sesión para {email}: Elemento no encontrado a tiempo.")
        return False
    except Exception as e:
        print(f"Error general durante el inicio de sesión para {email}: {e}")
        return False


def handle_finish_logging_in(driver):
    """
    Detecta y maneja la pantalla 'Finish Logging In' para completar el flujo de inicio de sesión.

    Args:
        driver (WebDriver): Instancia del navegador.
    """
    try:
        finish_link = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.XPATH, "//a[contains(@class, 'button') and contains(@class, 'primary') and contains(@class, 'wide') and contains(@class, 'mt16')]"))
        )
        finish_link.click()
        print("Se hizo clic en 'Finish Logging In'. Esperando la redirección...")

        WebDriverWait(driver, 10).until(
            EC.url_contains("salesconnect.cisco.com/blackbeltpartneracademy")
        )
        print("Inicio de sesión completado exitosamente.")
    except TimeoutException:
        print("No se encontró el botón 'Finish Logging In'.")


def navigate_to_my_learning(driver):
    """
    Navega al menú tipo hamburguesa y selecciona 'My Learning'.

    Args:
        driver (WebDriver): Instancia del navegador.

    Returns:
        bool: True si se pudo navegar exitosamente, False de lo contrario.
    """
    try:
        # Hacer clic en el botón del menú hamburguesa
        menu_button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'globalmenu_wrapper active-class-toggle active')]"))
        )
        menu_button.click()
        print("Menú hamburguesa abierto.")

        # Hacer clic en 'My Learning'
        my_learning_option = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//a[text()='My Learning']"))
        )
        my_learning_option.click()
        print("Se hizo clic en 'My Learning'.")
        return True

    except TimeoutException:
        print("Error: No se pudo navegar a 'My Learning'. Verifique los selectores.")
        return False
    except Exception as e:
        print(f"Error inesperado al navegar a 'My Learning': {e}")
        return False
