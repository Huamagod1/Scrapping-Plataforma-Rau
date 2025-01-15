from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import pandas as pd
import time
import pyotp

def login_to_siemens(driver, siemens_link, correo, contrasena, clave_totp):
    """
    Realiza el login en la plataforma Siemens.
    
    Args:
        driver (WebDriver): Instancia del navegador.
        siemens_link (str): URL de la plataforma Siemens.
        correo (str): Correo del usuario.
        contrasena (str): Contraseña del usuario.
        clave_totp (str): Clave secreta para generar el TOTP.

    Returns:
        bool: True si el login fue exitoso, False en caso contrario.
    """
    try:
        # 1. Navegar al link de Siemens
        driver.get(siemens_link)

        # 2. Ingresar correo
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "username"))
        ).send_keys(correo)
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.NAME, "action"))
        ).click()
        print(f"[{correo}] Correo ingresado.")

        # 3. Ingresar contraseña
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "password"))
        ).send_keys(contrasena)
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.NAME, "action"))
        ).click()
        print(f"[{correo}] Contraseña ingresada.")

        # 4. Generar y usar el código TOTP
        totp = pyotp.TOTP(clave_totp)
        codigo_totp = totp.now()  # Generar el código TOTP actual
        print(f"[{correo}] Código TOTP generado: {codigo_totp}")

        # 5. Ingresar el código TOTP
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "code"))
        ).send_keys(codigo_totp)
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.NAME, "action"))
        ).click()
        print(f"[{correo}] Código TOTP ingresado.")

        # 6. Verificar si el login fue exitoso
        WebDriverWait(driver, 35).until(
            EC.presence_of_element_located((By.CLASS_NAME, "alert-text"))
        )
        print(f"[{correo}] Login exitoso.")
        return True

    except TimeoutException as te:
        print(f"[{correo}] Error de tiempo de espera al iniciar sesión: {te}")
        return False
    except Exception as e:
        print(f"[{correo}] Error inesperado durante el login: {e}")
        return False


def run_siemens_analysis(driver):
    """
    Ejecuta el análisis para la plataforma Siemens, procesando un usuario a la vez.

    Args:
        driver (WebDriver): Instancia del navegador.
    """
    # Configurar rutas
    siemens_link = "https://p-acad.siemens.cloud/"
    excel_path = r"D:\OneDrive - Tunning Ingenieria SPA\Escritorio\proyecto de automatiacion\Excel datos\Datos P&T Version Actualizada.xlsx"
    output_path = r"./data/results/platforms.xlsx"

    # Leer datos del Excel
    data = pd.read_excel(excel_path, sheet_name="Plan Capacitacion Siemens", header=1)

    results = []

    for _, row in data.iterrows():
        correo = row['Correo']
        contrasena = row['Clave Nueva De Acceso']
        clave_totp = row['Clave TOTP']

        # Verificar si falta alguna información
        if pd.isna(correo) or pd.isna(contrasena) or pd.isna(clave_totp):
            results.append({"Correo": correo, "Estado": "Faltan datos (correo, contraseña o clave TOTP)"})
            continue

        # Llamamos a la nueva función de login
        login_exitoso = login_to_siemens(driver, siemens_link, correo, contrasena, clave_totp)

        if not login_exitoso:
            # Si el login falla, guardamos el resultado y pasamos al siguiente usuario
            results.append({"Correo": correo, "Estado": "Login fallido"})
            continue

        # Si el login es exitoso, navegamos a "Me"
        if not navigate_to_me(driver):
            print(f"[{correo}] Falló la navegación a 'Me'.")
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
        time.sleep(5)  # Pausa opcional

    # Guardar los resultados en un archivo Excel
    save_to_excel(results, output_path)


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
    Extrae detalles de los cursos.

    Args:
        driver (WebDriver): Instancia del navegador.

    Returns:
        list: Lista de diccionarios con los detalles de cada curso.
    """
    courses = []
    try:
        course_elements = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "goalTitleListGoals.loc-le-title"))
        )

        for course in course_elements:
            try:
                name = course.text.strip()
                link = course.get_attribute("href")
                courses.append({"Nombre": name, "Enlace": link})
            except NoSuchElementException:
                continue
    except TimeoutException:
        print("No se encontraron cursos en esta sección.")

    return courses


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
