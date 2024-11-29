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
    data = pd.read_excel(excel_path, sheet_name="Plan Capacitacion Cisco", header=3)

    # Ruta del archivo de resultados
    output_path = r"D:\OneDrive - Tunning Ingenieria SPA\Escritorio\proyecto de automatiacion\data\results\platforms.xlsx"
    # Limpiar contenido del archivo de resultados antes de empezar
    clean_results_excel(output_path)
    
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
                results.append({"Correo": email, "Estado": "Falló al acceder a 'My Learning'."})
                continue

            # **Agregar extracción de cursos**
            user_courses = extract_courses(driver)
            results.append({
                "Correo": email,
                "Estado": "Proceso completado",
                "Cursos en Progreso": user_courses.get("In Progress", []),
                "Cursos Completados": user_courses.get("Completed", ["No tiene cursos completados"])
            })
            print(f"Usuario {email} procesado exitosamente.")

        except TimeoutException as te:
            print(f"TimeoutException con {email}: {te}")
            results.append({"Correo": email, "Estado": f"Timeout: {te}"})

        except Exception as e:
            print(f"Error inesperado con {email}: {e}")
            results.append({"Correo": email, "Estado": f"Error inesperado: {e}"})

        finally:
            # Cerrar el navegador antes de pasar al siguiente usuario
            print(f"Cerrando navegador para el usuario {email}...")
            driver.quit()
            time.sleep(2)
            
    # Guardar los resultados en un archivo Excel
    try:
        results_df = pd.DataFrame(results)
        results_df.to_excel(output_path, index=False)
        print(f"Resultados guardados en {output_path}")
    except Exception as e:
        print(f"Error al guardar el archivo de resultados: {e}")

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
        email_field = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.ID, "input28" or "input29"))
        )
        email_field.clear()
        email_field.send_keys(email)

        # Hacer clic en "Siguiente"
        next_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//input[@value='Siguiente']"))
        )
        next_button.click()

        # Esperar a que aparezca el campo de contraseña
        password_field = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.NAME, "credentials.passcode"))
        )
        time.sleep(2)  # Tiempo de espera opcional

        # Ingresar contraseña
        password_field.clear()
        password_field.send_keys(password)

        # Hacer clic en "Verificar"
        verify_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//input[@value='Verificar']"))
        )
        verify_button.click()

        # Esperar redirección o validación
        WebDriverWait(driver, 15).until(EC.url_changes(driver.current_url))

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
            EC.presence_of_element_located((By.XPATH, "//a[contains(text(), 'Finish Logging In')]"))
        )
        finish_link.click()
        print("Se hizo clic en 'Finish Logging In'. Esperando la redirección...")

        WebDriverWait(driver, 10).until(
            EC.url_contains("salesconnect.cisco.com/blackbeltpartneracademy")
        )
        print("Inicio de sesión completado exitosamente.")
    except TimeoutException:
        print("No se encontró el botón 'Finish Logging In'.")
    except Exception as e:
        print(f"Error inesperado al manejar 'Finish Logging In': {e}")

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
        menu_button = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'globalmenu_wrapper')]"))
        )
        menu_button.click()
        print("Menú hamburguesa abierto.")

        # Hacer clic en 'My Learning'
        my_learning_option = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.XPATH, "//a[contains(text(), 'My Learning')]"))
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
    
def extract_courses(driver):
    """
    Extrae los cursos en progreso y completados.

    Args:
        driver (WebDriver): Instancia del navegador.

    Returns:
        dict: Diccionario con los cursos en progreso y completados.
    """
    courses = {"In Progress": [], "Completed": []}

    try:
        # Extraer cursos en progreso
        print("Extrayendo cursos en progreso...")
        courses["In Progress"] = extract_course_names(driver, "//h3[contains(@class, 'visually-hidden')]")

        # Cambiar a la pestaña "Completed Learning"
        print("Cambiando a la pestaña de cursos completados...")
        completed_tab = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'Completed Learning')]"))
        )
        completed_tab.click()

        # Esperar que cargue la sección de cursos completados
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.XPATH, "//h1[contains(@class, 'ltui-learningitemlwc_carouselviewtemplate')]"))
        )
        print("Sección de cursos completados cargada.")

        # Extraer cursos completados
        print("Extrayendo cursos completados...")
        courses["Completed"] = extract_course_names(driver, "//h1[contains(@class, 'ltui-learningitemlwc_carouselviewtemplate')]")

    except TimeoutException:
        print("Timeout al intentar extraer cursos o cambiar a la pestaña 'Completed Learning'.")
        if not courses["In Progress"]:
            courses["In Progress"] = ["No tiene cursos en progreso."]
        if not courses["Completed"]:
            courses["Completed"] = ["No tiene cursos completados."]
    except Exception as e:
        print(f"Error inesperado al extraer cursos: {e}")

    return courses


def extract_course_names(driver, xpath_selector):
    """
    Extrae los nombres de los cursos de la sección actual.

    Args:
        driver (WebDriver): Instancia del navegador.
        xpath_selector (str): Selector XPath para localizar los nombres de los cursos.

    Returns:
        list: Lista de nombres de cursos.
    """
    course_names = []
    try:
        courses = WebDriverWait(driver, 15).until(
            EC.presence_of_all_elements_located((By.XPATH, xpath_selector))
        )
        for course in courses:
            course_name = course.text.strip()
            if course_name:  # Filtrar entradas vacías
                course_names.append(course_name)
        print(f"{len(course_names)} cursos extraídos exitosamente.")
    except TimeoutException:
        print(f"No se encontraron cursos con el selector {xpath_selector}.")
    except Exception as e:
        print(f"Error inesperado al extraer nombres de cursos: {e}")
    return course_names

def clean_results_excel(file_path):
    """
    Limpia el contenido de la fila 2 hacia abajo en todas las columnas del archivo de resultados `platforms.xlsx`.

    Args:
        file_path (str): Ruta del archivo de resultados.
    """
    try:
        # Leer el archivo de resultados existente
        df = pd.read_excel(file_path)

        # Limpiar el contenido desde la fila 2 hacia abajo
        df.iloc[1:] = ""

        # Sobrescribir el archivo con los datos limpiados
        with pd.ExcelWriter(file_path, engine="openpyxl", mode="w") as writer:
            df.to_excel(writer, index=False)

        print(f"Archivo de resultados limpiado exitosamente: {file_path}")
    except FileNotFoundError:
        # Si el archivo no existe, no hacemos nada
        print(f"El archivo {file_path} no existe. Se generará uno nuevo al guardar los resultados.")
    except Exception as e:
        print(f"Error al limpiar el archivo de resultados: {e}")
