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

        # Generar y enviar el código TOTP
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

        # Esperar indicador de inicio de sesión exitoso
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
    Retorna True si no hay cursos; de lo contrario, False.
    """
    try:
        iframe = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.TAG_NAME, "iframe"))
        )
        driver.switch_to.frame(iframe)
        WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located(
                (By.XPATH, "//*[contains(text(), 'Plan does not have any items.')]")
            )
        )
        print("✅ Mensaje 'Plan does not have any items.' encontrado => Sin cursos.")
        return True
    except (TimeoutException, NoSuchElementException):
        print("✅ No se encontró el mensaje, sí hay cursos.")
        return False
    finally:
        driver.switch_to.default_content()


def apply_completed_filter(driver, timeout=10):
    """
    Aplica el filtro 'Completed' dentro del iframe.
    Retorna:
      - "NO_COURSES" si sale 'No data available for the selected filter'
      - "COURSES_FOUND" si se listan cursos
      - "ERROR" en caso de algún problema
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
        time.sleep(3)
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


def extract_course_details(driver, timeout=20):
    """
    Busca la tabla en el iframe y extrae la lista de cursos (nombre y estado).
    """
    courses = []
    print("⌛ Buscando la tabla de cursos...")
    try:
        iframes = driver.find_elements(By.TAG_NAME, "iframe")
        if iframes:
            print(f"🔍 Se encontraron {len(iframes)} iframes.")
            for index, iframe in enumerate(iframes):
                try:
                    driver.switch_to.frame(iframe)
                    print(f"✅ Cambiando al iframe {index+1} para buscar la tabla...")
                    tbody_candidates = driver.find_elements(By.TAG_NAME, "tbody")
                    if tbody_candidates:
                        print(f"🎯 ¡Encontrados {len(tbody_candidates)} tbodys en iframe {index+1}!")
                        break
                except NoSuchElementException:
                    print(f"❌ No se encontró tabla en iframe {index+1}, probando siguiente...")
                    driver.switch_to.default_content()
        time.sleep(2)
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
        driver.switch_to.default_content()
    return courses


def extract_course_progress(driver):
    """
    Extrae el porcentaje de progreso de cada curso en proceso.
    - Primero obtiene todos los enlaces de los cursos en progreso.
    - Usa una pestaña fija para cambiar de curso.
    - Interactúa con el botón "Load More" si es necesario.
    - Extrae los nombres y estados de las actividades.
    - Calcula el porcentaje de avance.
    - Al terminar todos los cursos, cierra la pestaña y regresa a "Me".
    """
    progress_data = {}

    print("📌 Detectando cursos en progreso...")

    # Intentar obtener los cursos dentro de un `iframe`
    try:
        iframe = driver.find_element(By.TAG_NAME, "iframe")
        driver.switch_to.frame(iframe)
        print("✅ Iframe encontrado, extrayendo cursos dentro del iframe.")
    except NoSuchElementException:
        print("ℹ️ No se encontró un iframe, usando documento principal.")

    # 🔹 Extraer TODOS los enlaces de los cursos en progreso antes de abrir una nueva pestaña
    courses = driver.find_elements(By.CSS_SELECTOR, "td.x-grid-cell-headerId-Title a.goalTitleListGoals.loc-le-title")

    if not courses:
        print("⚠ No se encontraron cursos en progreso.")
        return progress_data

    course_links = [(course.text.strip(), course.get_attribute("href")) for course in courses]
    print(f"📚 Se encontraron {len(course_links)} cursos en progreso.")

    # Volver al contenido principal si se usó un `iframe`
    try:
        driver.switch_to.default_content()
    except Exception:
        pass

    # ✅ Abrir una nueva pestaña para procesar los cursos
    driver.execute_script("window.open('', '_blank');")
    time.sleep(2)

    original_window = driver.current_window_handle  # Guardar la ventana principal
    new_window = [window for window in driver.window_handles if window != original_window][0]
    driver.switch_to.window(new_window)  # Cambiar a la pestaña procesadora

    for index, (course_name, course_url) in enumerate(course_links):
        print(f"➡ Ingresando al curso {index + 1}: {course_name} ({course_url})")

        try:
            # 🔹 Cambiar la URL de la pestaña en lugar de abrir una nueva
            driver.get(course_url)

            # Esperar a que la página del curso cargue completamente
            WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            print(f"✅ Página del curso {course_name} cargada.")

            time.sleep(3)  # Breve pausa para evitar errores de carga

            # 🔹 Manejo de doble vía: Intentar con iframe primero, luego documento principal
            try:
                iframe = driver.find_element(By.TAG_NAME, "iframe")
                driver.switch_to.frame(iframe)
                print("✅ Iframe encontrado en el curso.")
            except NoSuchElementException:
                print("ℹ️ No se encontró iframe, usando documento actual.")

            # Esperar a que las actividades estén visibles
            WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".activity--detail__bold-text"))
            )

            # 🔄 Si existe botón "Load More", hacer clic hasta que desaparezca
            while True:
                try:
                    botonLoadMore = WebDriverWait(driver, 5).until(
                        EC.presence_of_element_located((By.ID, "Learning-assignment-loading-button"))
                    )
                    if botonLoadMore and botonLoadMore.is_displayed():
                        print("🔄 Cargando más actividades...")
                        botonLoadMore.click()
                        time.sleep(3)
                    else:
                        break
                except TimeoutException:
                    break

            print("✅ Todas las actividades cargadas.")
            time.sleep(2)

            # Extraer nombres y estados de las actividades
            actividad_elements = driver.find_elements(By.CSS_SELECTOR, ".activity--detail__bold-text")
            estado_elements = driver.find_elements(By.CSS_SELECTOR, ".activity--detail__status span")

            nombres = [el.text.strip() for el in actividad_elements]
            estados = [el.text.strip() for el in estado_elements]

            completadas = sum(1 for s in estados if s == "Completed")
            total = len(nombres)
            progreso = (completadas / total) * 100 if total > 0 else 0

            progress_data[course_name] = round(progreso, 2)
            print(f"✅ {course_name}: {completadas} / {total} actividades completadas.")
            print(f"📊 Progreso: {progreso:.2f}%")

            # Volver al contenido principal si se usó un `iframe`
            try:
                driver.switch_to.default_content()
            except Exception:
                pass

        except Exception as e:
            print(f"❌ Error al procesar el curso {course_name}: {e}")
            progress_data[course_name] = "Error"

    # 🔹 Cerrar la pestaña procesadora al terminar todos los cursos en progreso
    driver.close()
    driver.switch_to.window(original_window)
    time.sleep(2)

    return progress_data



def extract_courses(driver):
    """
    Extrae la lista de cursos 'In Progress' y 'Completed' y calcula los porcentajes de avance
    para los cursos en progreso.
    """
    courses = {"In Progress": [], "Completed": [], "Progress Percentage": {}}

    print("🟩 Extrayendo cursos EN PROGRESO...")
    courses["In Progress"] = extract_course_details(driver)

    if courses["In Progress"]:
        print("📊 Calculando porcentajes de progreso para cursos en proceso...")
        courses["Progress Percentage"] = extract_course_progress(driver)

    driver.refresh()
    time.sleep(5)

    filter_result = apply_completed_filter(driver)

    if filter_result == "COURSES_FOUND":
        print("🟦 Extrayendo cursos COMPLETADOS...")
        courses["Completed"] = extract_course_details(driver)
    elif filter_result == "NO_COURSES":
        print("⚠ No hay cursos completados para este usuario.")
    else:
        print("⚠ Error al aplicar filtro 'Completed', no se extraerán cursos completados.")

    return courses
