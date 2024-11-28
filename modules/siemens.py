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
    if not wait_for_element(driver, By.ID, "ContentPlaceHolder1_TextSiemensLogin", 10):
        print("La página de inicio de sesión no cargó correctamente.")
        return

    # Leer datos del Excel
    excel_path = r"D:\OneDrive - Tunning Ingenieria SPA\Escritorio\proyecto de automatiacion\Excel datos\Datos P&T Version Actualizada.xlsx"
    output_path = r"./data/results/platforms.xlsx"
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

            # Extraer los cursos en progreso y completados
            user_courses = extract_courses(driver)
            results.append({
                "Correo": correo,
                "Estado": "Proceso completado",
                "Cursos en Progreso": user_courses.get("In Progress", []),
                "Cursos Completados": user_courses.get("Completed", [])
            })

            print(f"Usuario {correo} procesado exitosamente.")
        except Exception as e:
            print(f"Error inesperado con {correo}: {e}")
            results.append({"Correo": correo, "Estado": f"Error inesperado: {e}"})

        # Pausa opcional entre usuarios
        time.sleep(5)

    # Guardar los resultados en un archivo Excel
    save_to_excel(results, output_path)


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
        driver.find_element(By.ID, "ContentPlaceHolder1_TextSiemensLogin").send_keys(email)
        driver.find_element(By.ID, "ContentPlaceHolder1_TextPassword").send_keys(password)
        driver.find_element(By.ID, "ContentPlaceHolder1_LoginUserNamePasswordButton").click()

        # Verificar errores de login
        if wait_for_element(driver, By.ID, "ContentPlaceHolder1_MessageRepeaterLogin_MessageItemLogin_0", 5):
            print(f"Error de login para {email}")
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
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "hamburger-trigger"))
        ).click()
        print("Menú hamburguesa abierto.")

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "framework-tilenav-me-link"))
        ).click()
        print("Navegación exitosa a la sección 'Me'.")
        return True
    except TimeoutException:
        print("Error: No se pudo navegar a la sección 'Me'.")
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
        # Extraer cursos "In Progress" (cargados por defecto)
        print("Extrayendo cursos en progreso...")
        courses["In Progress"] = extract_course_details(driver)

        # Cambiar a la sección "Completed"
        print("Cambiando a la sección de cursos completados...")
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//span[text()='Completed']"))
        ).click()

        # Extraer cursos "Completed"
        print("Extrayendo cursos completados...")
        courses["Completed"] = extract_course_details(driver)
    except Exception as e:
        print(f"Error al extraer cursos: {e}")

    return courses


def extract_course_details(driver):
    """
    Extrae detalles de los cursos de la sección actual.

    Args:
        driver (WebDriver): Instancia del navegador.

    Returns:
        list: Lista de diccionarios con los detalles de cada curso.
    """
    courses = []
    try:
        print("Esperando que carguen los elementos de los cursos...")
        # Esperar a que los elementos estén presentes
        course_elements = WebDriverWait(driver, 15).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "goalTitleListGoals"))
        )

        print(f"Se encontraron {len(course_elements)} cursos en esta sección.")

        # Iterar sobre cada curso y extraer detalles
        for index, course in enumerate(course_elements, start=1):
            try:
                # Nombre del curso
                name = course.text.strip()
                # Enlace al detalle del curso
                link = course.get_attribute("href")

                # Debug: Imprimir los detalles del curso
                print(f"Curso {index}: Nombre: {name}, Enlace: {link}")

                # Agregar a la lista de cursos
                courses.append({"Nombre": name, "Enlace": link})
            except Exception as e:
                print(f"Error al procesar el curso {index}: {e}")
                continue

    except TimeoutException:
        print("No se encontraron cursos en esta sección o el tiempo de espera expiró.")
    except Exception as e:
        print(f"Error inesperado durante la extracción de cursos: {e}")

    # Devolver la lista de cursos
    return courses



def wait_for_element(driver, by, identifier, timeout):
    """
    Espera a que un elemento esté presente.

    Args:
        driver (WebDriver): Instancia del navegador.
        by (By): Tipo de localizador (e.g., By.ID, By.XPATH).
        identifier (str): Identificador del elemento.
        timeout (int): Tiempo máximo de espera.

    Returns:
        WebElement: El elemento encontrado, o None si no se encuentra.
    """
    try:
        return WebDriverWait(driver, timeout).until(EC.presence_of_element_located((by, identifier)))
    except TimeoutException:
        return None


def save_to_excel(data, file_path):
    """
    Guarda los resultados en un archivo Excel.

    Args:
        data (list): Lista de diccionarios con los datos.
        file_path (str): Ruta del archivo Excel.
    """
    try:
        results_df = pd.DataFrame(data)
        results_df.to_excel(file_path, index=False)
        print(f"Resultados guardados en {file_path}")
    except Exception as e:
        print(f"Error al guardar los resultados: {e}")
