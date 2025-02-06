from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

import time
import pyotp

def login_to_siemens(driver, siemens_link, correo, contrasena, clave_totp):
    """
    Inicia sesión en la plataforma Siemens utilizando las credenciales proporcionadas.
    """
    try:
        driver.get(siemens_link)

        # Ingresar el correo electrónico y proceder
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "username"))
        ).send_keys(correo)
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.NAME, "action"))
        ).click()
        print(f"[{correo}] Correo ingresado correctamente.")

        # Ingresar la contraseña y proceder
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "password"))
        ).send_keys(contrasena)
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.NAME, "action"))
        ).click()
        print(f"[{correo}] Contraseña ingresada correctamente.")

        # Generar y ingresar el código TOTP
        totp = pyotp.TOTP(clave_totp)
        codigo_totp = totp.now()
        print(f"[{correo}] Código TOTP generado: {codigo_totp}")

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "code"))
        ).send_keys(codigo_totp)
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.NAME, "action"))
        ).click()
        print(f"[{correo}] Código TOTP ingresado correctamente.")

        # Esperar un indicador de inicio de sesión exitoso
        WebDriverWait(driver, 35).until(
            EC.presence_of_element_located((By.CLASS_NAME, "alert-text"))
        )
        print(f"[{correo}] Inicio de sesión exitoso.")
        return True

    except TimeoutException as te:
        print(f"[{correo}] Error de tiempo de espera durante el inicio de sesión: {te}")
        return False
    except Exception as e:
        print(f"[{correo}] Error inesperado durante el inicio de sesión: {e}")
        return False

def navigate_to_me(driver):
    """
    Navega al menú hamburguesa -> 'Me'.
    """
    try:
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.ID, "hamburger-trigger"))
        ).click()
        print("Menú hamburguesa abierto correctamente.")

        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.ID, "framework-tilenav-me-link"))
        ).click()
        print("Navegación a la sección 'Me' realizada con éxito.")
        return True
    except TimeoutException:
        print("Error: No se pudo navegar a la sección 'Me'.")
        return False


def check_no_courses(driver, timeout=10):
    """
    Verifica si aparece el mensaje 'Plan does not have any items.' dentro de un iframe.
    Retorna True si no hay cursos. De lo contrario, False.
    """
    try:
        # Esperar que aparezca el iframe y cambiar el contexto
        iframe = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.TAG_NAME, "iframe"))
        )
        driver.switch_to.frame(iframe)

        # Buscar el texto 'Plan does not have any items.'
        WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located(
                (By.XPATH, "//*[contains(text(), 'Plan does not have any items.')]")
            )
        )
        print("✅ Mensaje 'Plan does not have any items.' encontrado => Sin cursos.")
        return True

    except (TimeoutException, NoSuchElementException):
        print("✅ No se encontró mensaje de 'Plan does not have any items.', sí hay cursos.")
        return False

    finally:
        # Volver siempre al contexto principal
        driver.switch_to.default_content()


def apply_completed_filter(driver, timeout=10):
    """
    Aplica el filtro 'Completed' dentro del iframe.
    Retorna:
        - "NO_COURSES" si sale 'No data available for the selected filter'
        - "COURSES_FOUND" si se listan cursos
        - "ERROR" para cualquier problema inesperado
    """
    try:
        iframe = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "iframe.ng-star-inserted"))
        )
        driver.switch_to.frame(iframe)
        print("🔄 Cambiado al contexto del iframe para aplicar 'Completed'.")

        completed_span = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located(
                (By.XPATH, "//span[@class='sjs-legend-text' and text()='Completed']")
            )
        )
        completed_span.click()
        print("🎯 Filtro 'Completed' activado.")

        # Esperar un momento a que la tabla se actualice
        time.sleep(3)

        # Verificar si aparece 'No data available for the selected filter'
        no_data = driver.find_elements(
            By.XPATH, "//*[contains(text(), 'No data available for the selected filter')]"
        )
        driver.switch_to.default_content()

        if no_data:
            print("⚠ No hay cursos completados.")
            return "NO_COURSES"
        else:
            print("✅ Hay cursos completados.")
            return "COURSES_FOUND"

    except Exception as e:
        print(f"❌ Error en apply_completed_filter: {e}")
        driver.switch_to.default_content()
        return "ERROR"


def extract_courses(driver):
    """
    Extrae la lista de cursos 'In Progress' y 'Completed'.
    También obtiene el porcentaje de avance de los cursos en progreso.
    """
    courses = {"In Progress": [], "Completed": [], "Progress Percentage": {}}

    print("🟩 Extrayendo cursos EN PROGRESO...")
    # 1) Cursos en progreso
    courses["In Progress"] = extract_course_details(driver)

    if courses["In Progress"]:
        print("📊 Calculando porcentajes de progreso...")
        courses["Progress Percentage"] = extract_course_progress(driver)  # Nueva función

    # 2) Refrescar y aplicar filtro 'Completed'
    driver.refresh()
    time.sleep(5)  # Espera un poco a que la página se recargue
    filter_result = apply_completed_filter(driver)

    if filter_result == "COURSES_FOUND":
        print("🟦 Extrayendo cursos COMPLETADOS...")
        courses["Completed"] = extract_course_details(driver)
    elif filter_result == "NO_COURSES":
        print("⚠ No hay cursos completados para este usuario.")
        # Deja la lista 'Completed' vacía
    else:
        print("⚠ Error al aplicar filtro 'Completed', no se extraerán cursos completados.")

    return courses


def extract_course_details(driver, timeout=20):
    """
    Busca la tabla en el iframe y extrae la lista de cursos (nombre, estado).
    """
    courses = []
    print("⌛ Buscando la tabla de cursos...")

    try:
        # 1) Ubicar el iframe principal donde está la tabla
        iframes = driver.find_elements(By.TAG_NAME, "iframe")
        if iframes:
            print(f"🔍 Se encontraron {len(iframes)} iframes.")
            for index, iframe in enumerate(iframes):
                try:
                    driver.switch_to.frame(iframe)
                    print(f"✅ Cambiando al iframe {index+1} para buscar la tabla...")

                    # Ver si existe un tbody con la tabla de cursos
                    tbody_candidate = driver.find_elements(By.TAG_NAME, "tbody")
                    if tbody_candidate:
                        print(f"🎯 ¡Encontrados {len(tbody_candidate)} tbodys en iframe {index+1}!")
                        break
                except NoSuchElementException:
                    print(f"❌ No se encontró tabla en iframe {index+1}, probando siguiente...")
                    driver.switch_to.default_content()

        time.sleep(2)  # Pequeña espera para asegurar que se renderice

        # 2) Localizar el tbody final
        try:
            tbody = driver.find_element(By.CSS_SELECTOR, "tbody#sjsgridview-1041-body")
        except NoSuchElementException:
            print("⚠ No se encontró 'sjsgridview-1041-body', buscando con un selector alternativo...")
            tbody = driver.find_element(By.CSS_SELECTOR, "tbody[id^='gridview']")

        print("✅ ¡Tabla de cursos encontrada!")
        rows = WebDriverWait(driver, timeout).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "tbody tr.x-grid-row"))
        )
        if not rows:
            print("⚠ No se encontraron filas de cursos.")
            driver.save_screenshot("error_no_cursos.png")
            return []

        print(f"📌 Se encontraron {len(rows)} filas de cursos.")

        # 3) Extraer campos (nombre y estado)
        for i, row in enumerate(rows, start=1):
            try:
                title_anchor = row.find_element(
                    By.CSS_SELECTOR, "td.x-grid-cell-headerId-Title a.goalTitleListGoals.loc-le-title"
                )
                name = title_anchor.text.strip() if title_anchor else "(Sin nombre)"

                progress_el = row.find_element(
                    By.CSS_SELECTOR, "td.x-grid-cell-headerId-Progress span b"
                )
                progress = progress_el.text.strip() if progress_el else "(Desconocido)"

                courses.append({"Nombre": name, "Estado": progress})
                print(f"✅ [{i}] Curso: {name} | Estado: {progress}")

            except NoSuchElementException as e:
                print(f"⚠ [{i}] Error extrayendo datos de la fila: {e}")

    except TimeoutException:
        print("❌ La tabla no cargó dentro del tiempo límite.")
        driver.save_screenshot("error_timeout_tabla.png")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
    finally:
        # Regresar al main content
        driver.switch_to.default_content()

    return courses


def extract_course_progress(driver):
    """
    Extrae el porcentaje de progreso de cada curso en proceso.
    - Ingresa a cada curso en progreso.
    - Obtiene el total de actividades del curso.
    - Cuenta cuántas actividades han sido completadas.
    - Calcula el porcentaje de avance.
    - Regresa a la lista de cursos.
    
    Parámetros:
    - driver: Instancia del navegador Selenium.

    Retorna:
    - Un diccionario con los nombres de los cursos y sus respectivos porcentajes de progreso.
    """
    progress_data = {}

    # Encontrar todos los cursos en progreso
    courses = driver.find_elements(By.CSS_SELECTOR, "td.x-grid-cell-headerId-Title a.goalTitleListGoals.loc-le-title")
    
    for course in courses:
        try:
            course_name = course.text.strip()
            print(f"➡ Ingresando al curso: {course_name}")

            # Abrimos el curso en una nueva pestaña
            driver.execute_script("window.open(arguments[0]);", course.get_attribute("href"))
            driver.switch_to.window(driver.window_handles[-1])  # Cambiamos a la nueva pestaña
            
            time.sleep(3)  # Esperar carga de la página

            # Extraer el total de actividades del curso
            total_activities = len(driver.find_elements(By.CSS_SELECTOR, ".activity-item"))  # Ajustar selector
            completed_activities = len(driver.find_elements(By.CSS_SELECTOR, ".activity-completed"))  # Ajustar selector
            
            if total_activities > 0:
                progress_percentage = (completed_activities / total_activities) * 100
            else:
                progress_percentage = 0  # Si no tiene actividades, el progreso es 0

            progress_data[course_name] = round(progress_percentage, 2)
            print(f"✅ {course_name}: {progress_percentage:.2f}% completado.")

        except Exception as e:
            print(f"❌ Error al procesar el curso {course_name}: {e}")
            progress_data[course_name] = "Error"

        finally:
            # Cerrar la pestaña actual y regresar a la lista de cursos
            driver.close()
            driver.switch_to.window(driver.window_handles[0])
            time.sleep(2)  # Breve pausa antes del siguiente curso

    return progress_data
