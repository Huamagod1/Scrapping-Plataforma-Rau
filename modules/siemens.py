from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver import ActionChains
import pandas as pd
import time
import pyotp


def login_to_siemens(driver, siemens_link, correo, contrasena, clave_totp):
    """
    Realiza el login en la plataforma Siemens.
    """
    try:
        driver.get(siemens_link)

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "username"))
        ).send_keys(correo)
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.NAME, "action"))
        ).click()
        print(f"[{correo}] Correo ingresado.")

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "password"))
        ).send_keys(contrasena)
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.NAME, "action"))
        ).click()
        print(f"[{correo}] Contraseña ingresada.")

        totp = pyotp.TOTP(clave_totp)
        codigo_totp = totp.now()
        print(f"[{correo}] Código TOTP generado: {codigo_totp}")

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "code"))
        ).send_keys(codigo_totp)
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.NAME, "action"))
        ).click()
        print(f"[{correo}] Código TOTP ingresado.")

        # Esperamos a que aparezca algún elemento que indique login OK (clase "alert-text")
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
    Ejecuta el análisis para la plataforma Siemens.
    """
    siemens_link = "https://p-acad.siemens.cloud/"
    excel_path = r"D:\OneDrive - Tunning Ingenieria SPA\Escritorio\proyecto de automatiacion\Excel datos\Datos P&T Version Actualizada.xlsx"
    output_path = r"./data/results/platforms.xlsx"

    data = pd.read_excel(excel_path, sheet_name="Plan Capacitacion Siemens", header=1)
    results = []

    for _, row in data.iterrows():
        correo = row['Correo']
        contrasena = row['Clave Nueva De Acceso']
        clave_totp = row['Clave TOTP']

        if pd.isna(correo) or pd.isna(contrasena) or pd.isna(clave_totp):
            results.append({"Correo": correo, "Estado": "Faltan datos"})
            continue

        # 1) Login
        login_exitoso = login_to_siemens(driver, siemens_link, correo, contrasena, clave_totp)
        if not login_exitoso:
            results.append({"Correo": correo, "Estado": "Login fallido"})
            continue

        # 2) Navegar a "Me"
        if not navigate_to_me(driver):
            print(f"[{correo}] Falló la navegación a 'Me'.")
            results.append({"Correo": correo, "Estado": "Falló la navegación a 'Me'"})
            continue

        # 3) Extraer cursos (In Progress + Completed)
        user_courses = extract_courses(driver)
        results.append({
            "Correo": correo,
            "Estado": "Proceso completado",
            "Cursos en Progreso": user_courses.get("In Progress", []),
            "Cursos Completados": user_courses.get("Completed", [])
        })

        print(f"Usuario {correo} procesado exitosamente.")
        time.sleep(5)

        # Si cierras el browser aquí, no podrás procesar más usuarios
        # a menos que reinicies el driver cada vez.
        driver.close()

        # Guarda resultados en Excel
        save_to_excel(results, output_path)


def navigate_to_me(driver):
    """
    Navega al menú y selecciona la opción 'Me'.
    """
    try:
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.ID, "hamburger-trigger"))
        ).click()
        print("Menú hamburguesa abierto.")

        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.ID, "framework-tilenav-me-link"))
        ).click()
        print("Navegación exitosa a la sección 'Me'.")
        return True
    except TimeoutException:
        print("Error: No se pudo navegar a la sección 'Me'.")
        return False


def apply_completed_filter(driver, timeout=20):
    """
    1. Localiza el <iframe class="ng-star-inserted">
    2. Cambia el contexto a ese iframe.
    3. Localiza el span con "Completed" dentro del iframe.
       (En tu caso, podría ser "Successful" si la plataforma lo maneja distinto)
    4. Hace clic en él.
    """
    try:
        # 1) Esperar el iframe donde aparece la leyenda de "Completed"
        iframe = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "iframe.ng-star-inserted"))
        )
        print("Iframe encontrado")

        # 2) Cambiar de contexto al iframe
        driver.switch_to.frame(iframe)
        print("Cambiado al contexto del iframe")

        # 3) Localizar el span "Completed" (o "Successful" si fuera el caso)
        completed_span = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located(
                (By.XPATH, "//span[@class='sjs-legend-text' and text()='Completed']")
            )
        )
        print("Span 'Completed' encontrado dentro del iframe")

        # 4) Hacer clic
        completed_span.click()
        print("¡Click en 'Completed' realizado dentro del iframe con Selenium!")

        # Regresar al contexto principal (OPCIONAL si la tabla está afuera)
        driver.switch_to.default_content()
        return True

    except Exception as e:
        print(f"No se pudo hacer clic en 'Completed': {e}")
        return False


def extract_courses(driver):
    """
    Extrae los cursos 'In Progress' y 'Completed' utilizando filtros:
    - Primero asume que la vista actual muestra los 'In Progress'.
    - Luego hace clic en 'Completed' (apply_completed_filter) y extrae la lista.
    """
    courses = {"In Progress": [], "Completed": []}

    try:
        print("Extrayendo cursos en progreso...")
        courses["In Progress"] = extract_course_details(driver)

        driver.refresh()
        time.sleep(5)  # Esperar unos segundos para asegurar que la página se cargue bien
        
        print("Aplicando filtro para cursos completados...")
        if apply_completed_filter(driver):
            print("Extrayendo cursos completados...")
            courses["Completed"] = extract_course_details(driver)
    except Exception as e:
        print(f"Error al extraer cursos: {e}")

    return courses


def extract_course_details(driver, timeout=50):
    """
    Extrae los cursos en progreso y completados desde la tabla en la página de 'My Plan'.
    """
    courses = []

    try:
        print("⌛ Buscando la tabla de cursos...")

        # 1️⃣ VERIFICAR SI ESTAMOS EN UN IFRAME
        iframes = driver.find_elements(By.TAG_NAME, "iframe")
        if iframes:
            print(f"🔍 Se encontraron {len(iframes)} iframes en la página. Probando si la tabla está dentro de alguno...")
            for index, iframe in enumerate(iframes):
                try:
                    driver.switch_to.frame(iframe)
                    print(f"✅ Probando iframe {index + 1}...")

                    # Intentar buscar la tabla dentro del iframe
                    tbody_elements = driver.find_elements(By.TAG_NAME, "tbody")
                    if tbody_elements:
                        print(f"🎯 ¡Se encontraron {len(tbody_elements)} elementos tbody dentro del iframe {index + 1}!")
                        break  # Si encontramos la tabla, dejamos de buscar

                except NoSuchElementException:
                    print(f"❌ La tabla no está en el iframe {index + 1}, probando otro...")
                    driver.switch_to.default_content()  # Volver al contexto principal

        # 2️⃣ ESPERAR QUE SE CARGUE EL DOM
        time.sleep(3)  # Esperar 3 segundos extra para asegurar la carga

        # 3️⃣ LISTAR TODOS LOS TBODY DISPONIBLES PARA DEPURAR
        tbody_elements = driver.find_elements(By.TAG_NAME, "tbody")
        print(f"🔎 Se encontraron {len(tbody_elements)} elementos 'tbody' en la página.")

        for index, tbody in enumerate(tbody_elements):
            print(f"📌 {index + 1}: ID='{tbody.get_attribute('id')}' Clases='{tbody.get_attribute('class')}'")

        # 4️⃣ INTENTAR LOCALIZAR LA TABLA USANDO EL ID O CLASES
        try:
            tbody = driver.find_element(By.CSS_SELECTOR, "tbody#sjsgridview-1041-body")
        except NoSuchElementException:
            print("⚠ No se encontró 'sjsgridview-1041-body', probando con otro posible ID.")
            tbody = driver.find_element(By.CSS_SELECTOR, "tbody[id^='gridview']")  # Busca un ID que empiece con 'gridview'

        print("✅ ¡Tabla de cursos encontrada!")

        # 5️⃣ ESPERAR QUE LAS FILAS SEAN VISIBLES
        rows = WebDriverWait(driver, timeout).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "tbody tr.x-grid-row"))
        )

        if not rows:
            print("⚠ No se encontraron cursos en la tabla.")
            driver.save_screenshot("error_no_cursos.png")  # Guardar captura en caso de fallo
            return []

        print(f"📌 Se encontraron {len(rows)} cursos en la tabla.")

        # 6️⃣ EXTRAER LOS DATOS
        for index, row in enumerate(rows):
            try:
                title_anchor = row.find_element(By.CSS_SELECTOR, "td.x-grid-cell-headerId-Title a.goalTitleListGoals.loc-le-title")
                name = title_anchor.text.strip() if title_anchor else "(Sin nombre)"

                progress_el = row.find_element(By.CSS_SELECTOR, "td.x-grid-cell-headerId-Progress span b")
                progress = progress_el.text.strip() if progress_el else "(Desconocido)"

                courses.append({"Nombre": name, "Estado": progress})
                print(f"✅ [{index+1}] Curso: {name} | Estado: {progress}")

            except NoSuchElementException as e:
                print(f"⚠ [{index+1}] Error al extraer datos de la fila: {e}")

    except TimeoutException:
        print("❌ Error: La tabla de cursos no cargó dentro del tiempo límite.")
        driver.save_screenshot("error_tiempo_limite.png")  # Guardar captura en caso de fallo
    except Exception as e:
        print(f"❌ Error inesperado: {e}")

    return courses


def save_to_excel(data, file_path):
    """
    Guarda los resultados en un archivo Excel.
    """
    try:
        results_df = pd.DataFrame(data)
        results_df.to_excel(file_path, index=False)
        print(f"Resultados guardados en {file_path}")
    except Exception as e:
        print(f"Error al guardar los resultados: {e}")
