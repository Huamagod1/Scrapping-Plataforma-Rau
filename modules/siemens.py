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
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "ContentPlaceHolder1_TextSiemensLogin"))
        )
    except TimeoutException:
        print("La página de inicio de sesión no cargó correctamente.")
        return

    # Leer datos del Excel
    excel_path = r"D:\OneDrive - Tunning Ingenieria SPA\Escritorio\proyecto de automatiacion\Excel datos\Datos P&T Version Actualizada.xlsx"
    output_path = r"D:\OneDrive - Tunning Ingenieria SPA\Escritorio\proyecto de automatiacion\data\results\platforms.xlsx"
    data = pd.read_excel(excel_path, sheet_name="Plan Capacitacion Siemens", header=1)

    results = []

    for _, row in data.iterrows():
        correo = row['Correo']
        contrasena = row["Clave Nueva De Acceso"]
        try:
            # Localizar los elementos
            email_field = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "ContentPlaceHolder1_TextSiemensLogin"))
            )
            password_field = driver.find_element(By.ID, "ContentPlaceHolder1_TextPassword")
            login_button = driver.find_element(By.ID, "ContentPlaceHolder1_LoginUserNamePasswordButton")

            # Ingresar credenciales y hacer clic en "Login"
            email_field.clear()
            password_field.clear()
            email_field.send_keys(correo)
            password_field.send_keys(contrasena)
            login_button.click()

            # Esperar redirección o validación
            try:
                WebDriverWait(driver, 15).until(
                    EC.url_changes(siemens_link)
                )
                # Si la redirección fue exitosa, proceder con la extracción de datos
                print(f"Ingreso exitoso para {correo}. Procediendo con la extracción de datos.")
                user_data = extract_user_data(driver)  # Implementar esta función según los datos necesarios
                results.append({"Correo": correo, "Estado": "Login exitoso", "Datos": user_data})

                # Esperar confirmación manual antes de continuar con el siguiente usuario
                input(f"Usuario {correo} procesado. Presiona ENTER para continuar con el siguiente usuario...")

            except TimeoutException:
                # Detectar error de contraseña incorrecta o formulario especial
                try:
                    error_message = WebDriverWait(driver, 5).until(
                        EC.presence_of_element_located((By.CLASS_NAME, "error-message"))  # Ajustar según el selector real
                    )
                    print(f"Contraseña incorrecta para {correo}: {error_message.text}")
                    results.append({"Correo": correo, "Estado": "Contraseña incorrecta. Actualizar."})
                except TimeoutException:
                    print(f"Timeout sin redirección para {correo}.")
                    results.append({"Correo": correo, "Estado": "Timeout sin redirección"})

        except NoSuchElementException as e:
            print(f"Error con {correo}: Elemento no encontrado - {e}")
            results.append({"Correo": correo, "Estado": f"Elemento no encontrado - {e}"})

        except WebDriverException as e:
            print(f"Error general del navegador con {correo}: {e}")
            results.append({"Correo": correo, "Estado": f"Error del navegador - {e}"})

        # Pausa opcional para asegurar que todo se haya completado
        time.sleep(5)

    # Guardar los resultados en un archivo Excel
    results_df = pd.DataFrame(results)
    results_df.to_excel(output_path, index=False)
    print(f"Resultados guardados en {output_path}")


def extract_user_data(driver):
    """
    Extrae los datos del usuario después de un login exitoso.

    Args:
        driver (WebDriver): Instancia del navegador.

    Returns:
        dict: Datos del usuario extraídos.
    """
    try:
        # Aquí debes implementar la lógica para extraer datos específicos del usuario.
        # Por ejemplo, cursos completados, progreso, etc.
        user_data = {
            "Cursos completados": 5,  # Reemplazar con lógica real
            "Progreso total": "80%",  # Reemplazar con lógica real
        }
        return user_data
    except Exception as e:
        print(f"Error al extraer datos del usuario: {e}")
        return {"Cursos completados": None, "Progreso total": None}
