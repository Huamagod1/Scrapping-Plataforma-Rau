from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd

def scrape(driver, config):
    """
    Funcion para navegar y extraer datos de la pagina despues del inicio de sesion.

    """
    try:
        menu_button = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.ID, "ctl00_header_headerResponsive_lnkNavBar"))
        )
        menu_button.click()

        opcion_learning = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.ID, "ctl00_header_headerResponsive_responsiveNav_rptMenu_ctl02_lnkMenu"))
        )
        opcion_learning.click()

        learning = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.ID, "ctl00_header_headerResponsive_responsiveNav_rptMenu_ctl02_rptSubMenu_ctl02_lnkSubMenu"))
        )
        learning.click()
        
        
        filtro_activo = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.ID, "_bj_j"))
        )
        filtro_activo.click()
        print("Se presiona en el filtro y muestra las opciones")
        #Selecciona el filtro todos, estado de formacion
        filtro_todos = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.ID, "_bj_j_dd_item_1"))
        )
        filtro_todos.click()
        print("Se selecciona la opcion todos")
        



        #Filtra por tipo de formacion
        filtro_formacion = WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "[data-tag='dropdownlist-tr-SelectedLoType']"))
        )
        filtro_formacion.click()

        itinerario_formativo = WebDriverWait(driver,5).until(
            EC.element_to_be_clickable((By.ID,"_bj_p_dd_item_3"))
        )
        itinerario_formativo.click()



        
        #Extraer itinerraios formativos y sus estados
        itinerarios = []
        elementos = driver.find_elements(By.CSS_SELECTOR, "a[id$='_k_f']")
        print("Se encontraron los siguientes itinerarios: " + elementos)
        #patron para los nombres de los itinerarios: _bjbi0k_k_f, _bjbi1k_k_f, _bjbi2k_k_f
        #Patron para los estados de los itinerarios: _bjbi0k_kbb, _bjbi1k_kbb, _bjbi2k_kbb

        for elemento in elementos:
            try:
                
                # Extraer el nombre del curso
                nombre_curso = elemento.text.strip()
                print("Nombre Curso" + nombre_curso)
                # Construir el ID del estado a partir del ID del itinerario
                id_estado = elemento.get_attribute("id").replace("_k_f", "_k_kbb")

                # Buscar el elemento del estado usando el ID generado
                estado_elemento = driver.find_element(By.ID, id_estado)
                estado_curso = estado_elemento.text.strip()

                # Guardar los datos en la lista
                itinerarios.append({"Nombre del curso": nombre_curso, "Estado del curso": estado_curso})

            except Exception as e:
                # Manejar casos en los que no se pueda encontrar el estado
                print(f"No se pudo extraer el estado para el itinerario con ID {elemento.get_attribute('id')}: {e}")



        # Verificar si se encontraron itinerarios
        if not itinerarios:
            print("No se encontraron itinerarios formativos.")
        else:
            print(f"Se encontraron {len(itinerarios)} itinerarios formativos.")
            for it in itinerarios:
                    print(it)


        # Guardar los datos en un archivo Excel
        import pandas as pd
        df = pd.DataFrame(itinerarios)
        df.to_excel("itinerarios_formativos.xlsx", index=False)
        print("Datos guardados en 'itinerarios_formativos.xlsx'.")



    except Exception as e:
        # Manejar errores generales
        print(f"Ocurrió un error durante el scraping: {e}")
 

      





      


#def filtro_itinerarios_activos(driver,config):

        
    