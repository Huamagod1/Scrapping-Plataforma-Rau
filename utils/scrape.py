from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import time




def scrape(driver, config):
    """
    Funcion para navegar y extraer datos de la pagina despues del inicio de sesion.

    """
    revisados = []
    errores = []
    try:
        print("Realizar el flujo para recorrer cada itinerario")
        
        mostrar_expediente(driver)

        while True:
             
            filtro_tipo_formacion(driver)
            itinerarios_activos = extraccion_itinerarios_totales_estados(driver)

            for itinerario in itinerarios_activos:
                    if itinerario["Nombre del curso"] not in revisados:
                        print(f"Procesando {itinerario['Nombre del curso']}...")
                        # Se realizan acciones necesarias

                        #Abrir itinerario
                        abrir_itinerario(driver, itinerario)

                        #Recoletar Datos
                        print("Se recoletan los datos")
                        revisados.append(itinerario["Nombre del curso"])


                        #Volver al expediente principal
                        print("Se devuelve a la pagina anterior")
                        volver_a_expediente(driver)

                        

                        #Aplicar filtros 
                        filtro_tipo_formacion(driver)

            if len(revisados) == len(itinerarios_activos):
                    print("Todos los itinerarios fueron procesados")
                    break
            
      

    except Exception as e:
        # Manejar errores generales
        print(f"No se pudo abrir el itinerario '{itinerario['Nombre del curso']}': {e}")
        errores.append({"itinerario": itinerario, "error": str(e)})




    #Funcion que detecta si tiene el filtro de itinerario formativo  
def filtro_tipo_formacion(driver):
    

    # Verifica que el botón esté clickeable después de la desaparición del modal
        filtro_formacion = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "a[data-tag='dropdownlist-tr-SelectedLoType']"))
        )
        filtro_formacion.click()
        print("Se presiona en el filtro 'TIPO DE FORMACION' y muestra las opciones")
        
        #Selecciona el filtro todos, estado de formacion y selecciona itinerario formativo
        filtro_itinerario = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "_bj_p_dd_item_3"))
        )
        filtro_itinerario.click()
        print("Se seleccionanLA opcion itinerarios formativos")

        WebDriverWait(driver, 10).until(
            EC.invisibility_of_element((By.CLASS_NAME, "modal_wait"))
        )
        print("La pagina termino de cargar despues de seleccionar el filtro") 

        time.sleep(5)

def filtro_estado_formacion(driver):
     #Colocar filtro por estado de formacion
        filtro_estado_formacion = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "a[data-tag='dropdownlist-tr-SelectedCategory']"))
        )
        filtro_estado_formacion.click()
        print("Se presiona en el filtro por 'ESTADO DE FORMACION', muestra las opciones")
        #Selecciona la opcion todos
        filtro_estado_formacion_todos = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "_bj_j_dd_item_1"))
        )
        filtro_estado_formacion_todos.click()
        print("Se seleciona la opcion todos en el filtro formacion")

        time.sleep(5)

def mostrar_expediente(driver):
        
        print("Esta funcion muestra el expediente academico.")
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

def recoletar_datos_itinerario(driver):
     print("Esta funcion recolecta los datos dentro del itinerario")




def abrir_itinerario(driver, itinerario):


    #PATRON BOTONES _bjbi0k_u__o, _bjbi1k_u__o
    # Patron the rial: _bjbi0k_u__a

    try:
         #Identificar el contendedor del itinerario basado en el nombre del curso
        contenedor = WebDriverWait(driver,10).until(
              EC.presence_of_element_located
              ((By.XPATH,f"//div[contains(@id, 'k_e') and contains(., '{itinerario['Nombre del curso']}')]"))
        )
         #Derivar el patron del boton desde el contenedor
        contenedor_id = contenedor.get_attribute("id")
        boton_id = contenedor_id.replace("k_e", "k_u__a") #Derivar el ID al boton
        print("id del boton: " + boton_id)
         

        boton = WebDriverWait(driver, 10).until(
              EC.element_to_be_clickable((By.ID, boton_id))
        )
        
        
        boton.click()
        print(f"Se abrio el itinerario '{itinerario['Nombre del curso']}'.")

        # Esperar a que la página del itinerario termine de cargar
        WebDriverWait(driver, 15).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )
        time.sleep(4)
        print("La página del itinerario cargó completamente.")

    except Exception as e:
        print(f"No se pudo abrir el itinerario'{itinerario['Nombre del curso']}':{e}")





def volver_a_expediente(driver):
     '''
        Funcion para regresar al expendiente y validar que la pagina cargo correctamente.
     '''

     try: 
            driver.back()
            time.sleep(5)
            print("Se devuelve a la pagina anterior.")
          # Esperar que la página cargue completamente
            WebDriverWait(driver, 15).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
            )
            time.sleep(4)
            print("La pagina anterior cargo correctamente.")
     except Exception as e:
        if "Read timed out" in str(e):
            print("Tiempo de espera agotado al regresar a la página. Intentando recargar...")
            driver.refresh()  # Intenta recargar la página
        else:
            print(f"No se pudo regresar a la pagina anterior: {e}")
            raise
          

def extraccion_itinerarios_totales_estados(driver):
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
        #Devuelve la lista de itinerarios

        return itinerarios


        # Guardar los datos en un archivo Excel
        
        #df = pd.DataFrame(itinerarios)
        #df.to_excel("itinerarios_formativos.xlsx", index=False)
        #print("Datos guardados en 'itinerarios_formativos.xlsx'.")

