from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def login(driver, config):
    """
    Realiza el inicio de sesión en la plataforma RAU.
    """
    # Navega a la página de inicio de sesión
    driver.get(config["url"])

        # Esperar a que la página esté completamente cargada
    WebDriverWait(driver, 20).until(
        lambda d: d.execute_script("return document.readyState") == "complete"
    )
    print("Página completamente cargada.")

    # Buscar el campo de usuario
    username_field = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.ID, "userNameBox"))
    )
    print("Campo de usuario encontrado")
    username_field.send_keys(config["username"])  # Ingresa el usuario

   # Buscar el campo de contraseña
    password_field = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.ID, "passWordBox"))
    )
    print("Campo contraseña encontrado exitosamente")
    # Ingresa la contraseña
    password_field.send_keys(config["password"])

    # Presiona Enter para iniciar sesión
    password_field.send_keys(Keys.RETURN)

#ID DEL BOTON CANCELAR DE LA VENTANA CAMBIAR CONTRASEÑA "cancelImageButton"
    handle_password_change_page(driver)



def handle_password_change_page(driver):
    '''
    Manejar la ventana de cambio de contraseña
    '''
    try:
        print("Ventana cambio de contrasñeña")
        cancel_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.ID, "cancelImageButton"))
        )
        cancel_button.click()
        print("Se hizo un click en el boton Cancelar.")
    except:
        print("No se detecta ventana de cambio de contraseña. Continuando...")