from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd




def scrape(driver, config):
    """
    Funcion para navegar y extraer datos de la pagina despues del inicio de sesion.

    """
    try:
        menu_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "ctl00_header_headerResponsive_lnkNavBar"))
        )
        menu_button.click()

        opcion_learning = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "ctl00_header_headerResponsive_responsiveNav_rptMenu_ctl02_lnkMenu"))
        )
        opcion_learning.click()

        learning = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "ctl00_header_headerResponsive_responsiveNav_rptMenu_ctl02_rptSubMenu_ctl02_lnkSubMenu"))
        )
        learning.click()
        
        #Colocar filtro por estado de formacion

        filtro_estado_formacion = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "_bj_j"))
        )
        filtro_estado_formacion.click()
        print("Se presiona en el filtro por estado de formacion, muestra las opciones")

        filtro_estado_formacion_todos = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "_bj_j_dd_item_1"))
        )
        filtro_estado_formacion_todos.click()
        print("Se presiona en el filtro por estado de formacion, muestra las opciones")


        WebDriverWait(driver, 20).until(
            EC.invisibility_of_element_located((By.CLASS_NAME, "modal_wait"))
        )
        print("El modal de carga ha desaparecido")








        #Filtro tipo de formacion
        filtro_formacion = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "_bj_p"))
        )
        filtro_formacion.click()
        print("Se presiona en el filtro y muestra las opciones")
        
        #Selecciona el filtro todos, estado de formacion y selecciona itinerario formativo
        filtro_itinerario = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "_bj_p_dd_item_3"))
        )
        filtro_itinerario.click()
        print("Se seleccionan los itinerarios formativos")
            
        
        WebDriverWait(driver, 20).until(
            EC.invisibility_of_element_located((By.CLASS_NAME, "modal_wait"))
        )
        print("El modal de carga ha desaparecido")
        
        
        WebDriverWait(driver,20).until(
            EC.presence_of_all_elements_located((By.ID,"__u"))
        )

        print("La pagina ha terminado de cargar")




        
        #Extraer itinerraios formativos y sus estados
        itinerarios = []
        contenedores = driver.find_elements(By.CSS_SELECTOR, "div[id$='k_e']")
        if not contenedores:
            raise Exception("No se encontraron los contenendores de itinerarios.")

        print(f"Se encontraron {len(contenedores)} contenedores de itinerarios.")
        #´Patro rial itinerarios BLOQUES : _bjbi0k_e, _bjbi11k_e, _bjbi12k_e
        #Curso online: _bjbi1b_e, _bjbi14b_e,

        #patron para los nombres de los itinerarios: _bjbi0k_k_f, _bjbi1k_k_f, _bjbi2k_k_f
        #Patron nombres Curso online: _bjbi1b_k_f, _bjbi2b_k_f, 
        #Patron para los estados de los itinerarios: _bjbi0k_kbb, _bjbi1k_kbb, _bjbi2k_kbb

        for contenedor in contenedores:
            try:
                
                contenedor_id = contenedor.get_attribute("id")
                print("ID contenedor encontrado: "+  contenedor_id)

                # Se construyen los IDS A BUSCAR
                id_nombre = contenedor_id.replace("k_e", "k_k_f")
                id_estado = contenedor_id.replace("k_e", "k_kbb")

                #Se busca el nombre del itinerario
                nombre_elemento = driver.find_element(By.ID, id_nombre)
                nombre_curso = nombre_elemento.text.strip()
                print("Curso Encontrado: " + nombre_curso)
                #Busca el estado actual del itinerario

                estado_elemento = driver.find_element(By.ID, id_estado)
                estado_curso = estado_elemento.text.strip()
                print("Estado del Curso: "+ estado_curso)


                # Guardar los datos en la lista
                itinerarios.append({"Nombre del curso": nombre_curso, "Estado del curso": estado_curso})

            except Exception as e:
                # Manejar casos en los que no se pueda encontrar el estado
                print(f"No se pudo extraer el estado para el itinerario con ID {contenedor_id}: {e}")



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
 

      

        
    