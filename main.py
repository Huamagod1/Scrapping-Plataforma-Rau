from modules.siemens import login_to_siemens, navigate_to_me, check_no_courses, extract_courses
from utils.excel_utils import save_to_excel
from selenium import webdriver
import pandas as pd
import time

def run_siemens_analysis():

    siemens_link = "https://p-acad.siemens.cloud/"
    excel_path = r"D:\OneDrive - Tunning Ingenieria SPA\Escritorio\proyecto de automatiacion\Excel datos\Datos P&T Version Actualizada.xlsx"
    output_path = r"./data/results/platforms.xlsx"

    try:
        data = pd.read_excel(excel_path, sheet_name="Plan Capacitacion Siemens", header=1)
    except Exception as e:
        print(f"❌ Error al leer el archivo Excel: {e}")
        return

    results = []

    for _, row in data.iterrows():
        correo = row.get('Correo')
        contrasena = row.get('Clave Nueva De Acceso')
        clave_totp = row.get('Clave TOTP')

        if pd.isna(correo) or pd.isna(contrasena) or pd.isna(clave_totp):
            results.append({"Correo": correo, "Estado": "Faltan datos"})
            continue

        # Intentar inicializar el navegador
        try:
            driver = webdriver.Edge()
            driver.maximize_window()
        except Exception as e:
            print(f"❌ Error al iniciar el navegador: {e}")
            results.append({"Correo": correo, "Estado": "Error iniciando navegador"})
            continue

        try:
            # 1) Login
            login_exitoso = login_to_siemens(driver, siemens_link, correo, contrasena, clave_totp)
            if not login_exitoso:
                results.append({"Correo": correo, "Estado": "Login fallido"})
                continue

            # 2) Navegar a 'Me'
            if not navigate_to_me(driver):
                print(f"[{correo}] Falló la navegación a la sección 'Me'.")
                results.append({"Correo": correo, "Estado": "Falló la navegación a 'Me'"})
                continue

            # 3) Verificar si no tiene cursos asignados
            if check_no_courses(driver):
                print(f"[{correo}] No tiene cursos asignados.")
                results.append({"Correo": correo, "Estado": "Sin cursos asignados"})
                continue

            # 4) Extraer cursos (en progreso y completados)
            user_courses = extract_courses(driver)
            results.append({
                "Correo": correo,
                "Estado": "Proceso completado",
                "Cursos en Progreso": user_courses.get("In Progress", []),
                "Cursos Completados": user_courses.get("Completed", [])
            })

            print(f"✅ Usuario {correo} procesado exitosamente.")

        except Exception as e:
            print(f"❌ Error inesperado con el usuario {correo}: {e}")
            results.append({"Correo": correo, "Estado": "Error inesperado"})

        finally:
            driver.quit()
            print(f"🔄 Navegador cerrado para {correo}.")

        time.sleep(5)  # Pausa antes de procesar el siguiente usuario

    # Guardar resultados en Excel
    try:
        save_to_excel(results, output_path)
        print("📂 Resultados guardados correctamente.")
    except Exception as e:
        print(f"❌ Error al guardar resultados en Excel: {e}")

def main():
    run_siemens_analysis()

if __name__ == "__main__":
    main()
