from selenium import webdriver
from selenium.webdriver.common.by import By
import time

# Puerto de depuración de Edge (verifica si es diferente)
EDGE_DEBUG_PORT = 9222  # Si es diferente, cámbialo

# Configurar Selenium para adjuntarse a Edge ya abierto
options = webdriver.EdgeOptions()
options.debugger_address = f"127.0.0.1:{EDGE_DEBUG_PORT}"

# Conectar Selenium a Edge abierto
driver = webdriver.Edge(options=options)

# Verificar si la página está en Siemens Learning Partner Academy
expected_host = "siemens-learning-partneracademy.sabacloud.com"
current_host = driver.current_url.split("//")[-1].split("/")[0]

if current_host != expected_host:
    print(f"⚠️ No estás en {expected_host}. Estás en: {current_host}")
    exit()

print("✅ Conectado a Siemens Learning Partner Academy.")

# Función para entrar al primer curso dentro del iframe
def entrar_a_primer_curso():
    try:
        print("🔍 Buscando iframe...")
        iframe = driver.find_element(By.TAG_NAME, "iframe")
        driver.switch_to.frame(iframe)

        print("🔍 Buscando cursos dentro del iframe...")
        primer_curso = driver.find_element(By.CSS_SELECTOR, 'a[title="Course"]')

        if primer_curso:
            print(f"📚 Entrando al curso: {primer_curso.text}")
            primer_curso.click()
        else:
            print("⚠️ No se encontró ningún curso disponible.")

        driver.switch_to.default_content()
    except Exception as e:
        print(f"❌ Error al entrar al curso: {e}")

# Función para calcular el porcentaje de avance
def calcular_porcentaje_avance():
    try:
        print("📊 Cargando actividades...")
        time.sleep(2)

        while True:
            try:
                boton_load_more = driver.find_element(By.XPATH, '//button[@title="Load More"]')
                boton_load_more.click()
                time.sleep(3)  # Espera a que cargue más actividades
            except:
                break  # Salir si no hay más botones

        actividades = driver.find_elements(By.CSS_SELECTOR, '.activity--detail__bold-text')
        estados = driver.find_elements(By.CSS_SELECTOR, '.activity--detail__status span')

        completadas = sum(1 for estado in estados if estado.text.strip() == "Completed")
        total_actividades = len(actividades)
        porcentaje_avance = (completadas / total_actividades) * 100 if total_actividades > 0 else 0

        print(f"✅ Progreso del curso: {porcentaje_avance:.2f}%")
    except Exception as e:
        print("❌ Error al calcular el progreso:", e)

# Función para regresar a la lista de cursos
def regresar_a_lista_de_cursos():
    try:
        boton_regresar = driver.find_element(By.CSS_SELECTOR, "button.navigate__back")
        boton_regresar.click()
        print("↩️ Regresando a la lista de cursos...")
    except:
        print("⚠️ No se encontró el botón para regresar.")

# Ejecutar las funciones en secuencia
entrar_a_primer_curso()
time.sleep(5)
calcular_porcentaje_avance()
time.sleep(3)
regresar_a_lista_de_cursos()
