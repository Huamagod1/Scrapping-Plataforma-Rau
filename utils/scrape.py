from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd

def scrape(driver, config):
    """
    Funcion para navegar y extraer datos de la pagina despues del inicio de sesion.

    """
    try:
        menu_button = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.ID, "ctl00_header_headerResponsive_lnkNavBar"))
        )
        menu_button.click()

        opcion_learning = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.ID, "ctl00_header_headerResponsive_responsiveNav_rptMenu_ctl02_lnkMenu"))
        )
        opcion_learning.click()

        learning = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.ID, "ctl00_header_headerResponsive_responsiveNav_rptMenu_ctl02_rptSubMenu_ctl02_lnkSubMenu"))
        )
        learning.click()
        
        
        filtro_itinerarios_activos(driver, config)

        
        #Extraer itinerraios formativos y sus estados
        itinerarios = []
        elementos = driver.find_elements(By.CSS_SELECTOR, "a[id$='_k_a']")

        for elemento in elementos:
            # Verificar que sea un itinerario formativo
            tipo_formacion = elemento.find_element(By.XPATH, ".//following::span[contains(text(), 'Itinerario formativo')]")
            if tipo_formacion:
                # Extraer nombre del curso y estado
                nombre = elemento.text.strip()
                estado_id = elemento.get_attribute("id").replace("_k_a", "_k_kbb")
                estado = driver.find_element(By.ID, estado_id).text.strip()

                # Guardar en la lista
                itinerarios.append({"Curso": nombre, "Estado": estado})

        # Validar si se encontraron resultados
        if not itinerarios:
            print("No se encontraron itinerarios formativos.")
        else:
            print(f"Se encontraron {len(itinerarios)} itinerarios formativos.")
            for it in itinerarios:
                print(it)

             # Guardar en un archivo Excel
            df = pd.DataFrame(itinerarios)
            df.to_excel("itinerarios_formativos.xlsx", index=False)
            print("Itinerarios guardados en 'itinerarios_formativos.xlsx'.")

    except Exception as e:
        print(f"Se produjo un error: {e}")


def filtro_itinerarios_activos(driver,config):

        filtro_activo = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.ID, "_bj_j"))
        )
        filtro_activo.click()
        
        filtro_todos = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.ID, "_bj_j_dd_item_1"))
        )
        filtro_todos.click()
    