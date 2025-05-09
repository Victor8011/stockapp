import flet as ft
import threading
import time
import re
import requests
import KEY
import app
import sqlite3

API_KEY = KEY.firebase_key

def main(page: ft.Page):
    page.theme_mode = ft.ThemeMode.LIGHT
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.window.min_width = 660
    page.window.min_height = 660
    page.window.width = 700
    page.window.height = 720
    page.window.maximizable = True
    page.window.title_bar_hidden = False
    snack_bar = ft.SnackBar(content=ft.Text(""), open=False)

    def init_db():
        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()
        cursor.execute("""
                       CREATE TABLE IF NOT EXISTS users (
                       email TEXT PRIMARY KEY,
                       database_name TEXT
                       )
                   """)
        conn.commit()
        conn.close()

    init_db()
    # Snackbar. Alerta de cadastro bem sucedido
    def snack_sucess():
            snack_bar.content = ft.Text("Cadastro realizado com sucesso!", weight=ft.FontWeight.BOLD)
            snack_bar.bgcolor = ft.Colors.GREEN_400
            snack_bar.duration = 1800
            snack_bar.open = True

    # Snackbar. Alerta para credenciais incorretas
    def snack_error():
            snack_bar.content = ft.Text("Erro! Verifique suas credencias!", weight=ft.FontWeight.BOLD)
            snack_bar.bgcolor = ft.Colors.RED_400
            snack_bar.duration = 1800
            snack_bar.open = True

    # Botão de cadastro
    def btn_register(e):
        email_format = r'^[a-zA-Z0-9._]+@[a-zA-Z0-9]+\.[a-zA-Z]{2,}$'
        password_format = r'[a-zA-Z0-9]{6,}'
        valid_email = ""
        valid_password = ""
        
        # Verifica se todos os campos foram preenchidos
        for field in[
            textfield_email_sign,
            textfield_confirm_email,
            textfield_password_sign,
            textfield_confirm_password
        ]:
            if not field.value:
                field.error_text = "Campo obrigatorio"

        page.update()

        # Verifica se os emails são válidos
        if not re.match(email_format, textfield_email_sign.value):
            snack_error()
            return
        
        if not re.match(email_format, textfield_confirm_email.value):
            snack_error()
            return

        # Verifica se os emails coincidem
        if textfield_email_sign.value != textfield_confirm_email.value:
            snack_error()
            return
        valid_email = textfield_confirm_email.value
        
        # Verifica se as senhas são válidas
        if not re.match(password_format, textfield_password_sign.value):
            snack_error()
            return
        
        if not re.match(password_format, textfield_confirm_password.value):
            snack_error()
            return

        # Verifica se as senhas coincidem
        if textfield_password_sign.value != textfield_confirm_password.value:
            snack_error()
            return
        valid_password = textfield_confirm_password.value
        
        try:
            url = f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={API_KEY}"
            payload = {
                "email": valid_email,
                "password": valid_password,
                "returnSecureToken": True
            }
            response = requests.post(url, json=payload)
            response.raise_for_status()

            data = response.json()
            if "idToken" in data:
                snack_sucess()

                # Limpa os campos
                textfield_email_sign.value = ""
                textfield_confirm_email.value = ""
                textfield_password_sign.value = ""
                textfield_confirm_password.value = ""

                page.clean()
                page.add(log_in_layout)
                page.update()
            else:
                raise Exception()
            
        except Exception as ex:
            snack_error()

    def btn_log_in(e):
        email_format = r'^[a-zA-Z0-9._]+@[a-zA-Z0-9]+\.[a-zA-Z]{2,}$'
        password_format = r'[a-zA-Z0-9]{6,}'
        valid_email = ""
        valid_password = ""

        # Verifica se o email é válido
        if not re.match(email_format, textfield_email.value):
            snack_error()
            return
        valid_email = textfield_email.value
        
        # Verifica se a senha é válida
        if not re.match(password_format, textfield_password.value):
            snack_error()
            return
        valid_password = textfield_password.value

        try:
            url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={API_KEY}"
            payload = {
                "email": valid_email,
                "password": valid_password,
                "returnSecureToken": True
            }
            response = requests.post(url, json=payload)

            # Verificar resposta
            if response.status_code == 200:
                data = response.json()
                
                if "idToken" in data:
                    conn = sqlite3.connect("users.db")
                    cursor = conn.cursor()
                    cursor.execute("SELECT database_name FROM users WHERE email = ?", (valid_email,))
                    result = cursor.fetchone()

                    if result is None:
                        # Cria a database do usuário caso não exista
                        database_name = f"db_{valid_email.replace('@', '_').replace('.', '_')}.db"
                        cursor.execute("INSERT INTO users (email, database_name) VALUES (?, ?)", (valid_email, database_name))
                        conn.commit()
                        
                        user_conn = sqlite3.connect(database_name)
                        user_cursor = user_conn.cursor()
                        user_cursor.execute("""
                                        CREATE TABLE products (id_prod INTEGER PRIMARY KEY AUTOINCREMENT, category TEXT, product TEXT, quantity INTEGER)
                                        """)
                        user_cursor.execute("""
                                            CREATE TABLE quantity_history (
                                                id_hist INTEGER PRIMARY KEY AUTOINCREMENT,
                                                prod_hist INTEGER,
                                                quantity_before INTEGER,
                                                quantity_after INTEGER,
                                                data_modify TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                                                FOREIGN KEY (prod_hist) REFERENCES products(id_prod)
                                                )
                                        """)
                        user_cursor.execute("""
                                            CREATE TRIGGER trg_update_quantity
                                            AFTER UPDATE OF quantity ON products
                                            FOR EACH ROW
                                            WHEN OLD.quantity != NEW.quantity
                                            BEGIN
                                                INSERT INTO quantity_history (prod_hist, quantity_before, quantity_after, data_modify)
                                                VALUES (OLD.id_prod, OLD.quantity, NEW.quantity, CURRENT_TIMESTAMP);
                                            END
                                        """)
                        user_conn.commit()
                        user_conn.close()
                    else:
                        database_name = result[0]
                        conn.close()
                        print(result)

                    # Limpa os campos de texto
                    textfield_email.value = ""
                    textfield_password.value = ""

                    # Carrega a pagina do app
                    page.clean()
                    app.main(page, database_name)
                    page.update()
                else:
                    snack_error()
            else:
                error_message = response.json().get("error",{}).get("message", "Erro desconhecido")
                print(f"Erro ao autenticar: {error_message}")
                snack_error()

        except requests.RequestException as ex:
            snack_error()
           


    # Titulo com icone animado
    login_text = ft.Text(
        "StockApp",
        size=30,
        font_family="Consolas",
        color="BLACK",
        weight=ft.FontWeight.BOLD,
        text_align=ft.TextAlign.CENTER
    )

    # Container com gradiente animado
    gradient_container = ft.Container(
        content=login_text,
        padding=10,
        border_radius=10,
        gradient=ft.LinearGradient(
            begin=ft.Alignment(-1, 0),
            end=ft.Alignment(1, 0),
            colors=[ft.Colors.BLUE, ft.Colors.GREEN],
            stops=[0.0, 1.0],
            rotation=0,
        ),
        animate_rotation=True,
        width=200,  # Largura fixa para referência
        height=60,  # Altura fixa para referência
    )

    # Imagem que vai aumentar e diminuir acima do container
    animated_image = ft.Image(
        src="images/ready-stock.png",  # Caminho relativo ao assets_dir
        width=50,  # Tamanho inicial
        height=50,
        animate_size=True,  # Habilita animação de tamanho
    )

    # Stack para posicionar a imagem acima do gradient_container
    header_stack = ft.Stack(
        controls=[
            ft.Container(
                content=animated_image,
                alignment=ft.Alignment(0, 0),  # Centraliza a imagem no Stack
                width=200,
                height=50,  # Espaço para a imagem acima do container
            ),
            ft.Container(
                content=gradient_container,
                top=50,  # Posiciona o gradient_container abaixo da imagem
                alignment=ft.Alignment(0, 0),
            ),
        ],
        width=200,
        height=110,  # Altura total para acomodar imagem + container
    )

    # Animar o gradiente
    def animate_gradient():
        rotation = 0
        while True:
            rotation += 0.2
            if rotation >= 6.28:  # 2π (um ciclo completo)
                rotation = 0
            gradient_container.gradient.rotation = rotation
            page.update()
            time.sleep(0.05)

    # Animar o tamanho da imagem
    def animate_image_size():
        min_size = 40  # Tamanho mínimo
        max_size = 60  # Tamanho máximo
        growing = True  # Controla se está crescendo ou diminuindo
        current_size = min_size
        
        while True:
            if growing:
                current_size += 0.5  # Incremento suave
                if current_size >= max_size:
                    growing = False
            else:
                current_size -= 0.5  # Decremento suave
                if current_size <= min_size:
                    growing = True
            
            animated_image.width = current_size
            animated_image.height = current_size
            page.update()
            time.sleep(0.03)  # Velocidade da animação (suave, não acelerada)

    # Inicia as animações em threads separadas
    threading.Thread(target=animate_gradient, daemon=True).start()
    threading.Thread(target=animate_image_size, daemon=True).start()

    # Campos de texto

    # Valida o campo "textfield_email"
    def textfield_email_check(e):
        email_format = r'^[a-zA-Z0-9._]+@[a-zA-Z0-9]+\.[a-zA-Z]{2,}$'

        if textfield_email.value == "":
            textfield_email.error_text = "Campo obrigatorio"
            return
        
        if not re.match(email_format, textfield_email.value):
            textfield_email.error_text = "Email inválido"
            return
        textfield_email.error_text = ""

    # Valida o campo "textfield_password"
    def textfield_password_check(e):
        password_format = r'[a-zA-Z0-9]{6,}'

        if textfield_password.value == "":
            textfield_password.error_text = "Campo obrigatorio"
            return
        
        if not re.match(password_format, textfield_password.value):
            textfield_password.error_text = "Mínimo de 6 caracteres: a-z, A-Z, 9-0"
            return
        textfield_password.error_text = ""


    # Valida o campo "textfield_email_sign"
    def textfield_email_sign_check(e):
        email_format = r'^[a-zA-Z0-9._]+@[a-zA-Z0-9]+\.[a-zA-Z]{2,}$'

        if textfield_email_sign.value == "":
            textfield_email_sign.error_text = "Campo obrigatorio"
            return
        
        if not re.match(email_format, textfield_email_sign.value):
            textfield_email_sign.error_text = "Email inválido"
            return
        textfield_email_sign.error_text = ""

    # Valida o campo "textfield_confirm_email"
    def textfield_confirm_email_check(e):
        email_format = r'^[a-zA-Z0-9._]+@[a-zA-Z0-9]+\.[a-zA-Z]{2,}$'

        if textfield_confirm_email.value == "":
            textfield_confirm_email.error_text = "Campo obrigatorio"
            return
        
        if not re.match(email_format, textfield_confirm_email.value):
            textfield_confirm_email.error_text = "Email inválido"
            return
        
        if textfield_confirm_email.value != textfield_email_sign.value:
            textfield_confirm_email.error_text = "Emails não coincidem"
            return
        textfield_confirm_email.error_text = ""

    # Valida o campo "textfield_password_sign"
    def textfield_password_sign_check(e):
        password_format = r'[a-zA-Z0-9]{6,}'

        if textfield_password_sign.value == "":
            textfield_password_sign.error_text = "Campo obrigatorio"
            return
        
        if not re.match(password_format, textfield_password_sign.value):
            textfield_password_sign.error_text = "Mínimo de 6 caracteres: a-z, A-Z, 9-0"
            return
        textfield_password_sign.error_text = ""

    # Valida o campo "textfield_confirm_password"
    def textfield_confirm_password_check(e):
        password_format = r'[a-zA-Z0-9]{6,}'

        if textfield_confirm_password.value == "":
            textfield_confirm_password.error_text = "Campo obrigatorio"
            return
        
        if not re.match(password_format, textfield_confirm_password.value):
            textfield_confirm_password.error_text = "Mínimo de 6 caracteres: a-z, A-Z, 9-0"
            return
        
        if textfield_confirm_password.value != textfield_password_sign.value:
            textfield_confirm_password.error_text = "Senhas não coincidem"
            return
        textfield_confirm_password.error_text = ""

    # Pagina de Log in
    textfield_email = ft.TextField(
        label = "Email",
        on_blur = textfield_email_check,
        error_text = "",
        width = 300
    )

    textfield_password = ft.TextField(
        label = "Senha",
        password = True,
        can_reveal_password = True,
        on_blur = textfield_password_check,
        error_text = "",
        width = 300)

    # Pagina de Cadastro
    textfield_email_sign = ft.TextField(
        label = "Email",
        on_blur = textfield_email_sign_check,
        error_text = "",
        width = 300
    )

    textfield_confirm_email = ft.TextField(
        label = "Confirmar Email",
        on_blur = textfield_confirm_email_check,
        error_text = "",
        width = 300
    )

    textfield_password_sign = ft.TextField(
        label = "Senha",
        password = True,
        can_reveal_password = True,
        on_blur = textfield_password_sign_check,
        error_text = "",
        width = 300
    )

    textfield_confirm_password = ft.TextField(
        label = "Confirmar senha",
        password = True,
        can_reveal_password = True,
        on_blur = textfield_confirm_password_check,
        error_text = "",
        width = 300
    )

    # Botões
    log_in_button = ft.ElevatedButton(
        text = "Entrar",
        width = 100,
        height = 40,
        style = ft.ButtonStyle(
            shape = ft.RoundedRectangleBorder(radius = 10),
            overlay_color = ft.Colors.GREEN_400
        ),
        on_click = btn_log_in
    )

    sign_up_button = ft.ElevatedButton(
        text = "Cadastrar-se",
        width = 120,
        height = 40,
        style = ft.ButtonStyle(
            shape = ft.RoundedRectangleBorder(radius = 10),
            overlay_color = ft.Colors.GREEN_400
        ),
        on_click = btn_register
    )

    def return_to_log_in(e):
        # Limpa os campos de texto e mensagens de erro
        textfield_email_sign.value = ""
        textfield_confirm_email.value = ""
        textfield_password_sign.value = ""
        textfield_confirm_password.value = ""
        textfield_email_sign.error_text = ""
        textfield_confirm_email.error_text = ""
        textfield_password_sign.error_text = ""
        textfield_confirm_password.error_text = ""
        # Carrega a pagina de log in
        page.clean()
        page.add(log_in_layout)
    
    def return_to_sign_up(e):
        # Limpa os campos de texto e mensagens de erro
        textfield_email.value = ""
        textfield_password.value = ""
        textfield_email.error_text = ""
        textfield_password.error_text = ""
        # Carrega a pagina de cadastro
        page.clean()
        page.add(sign_up_layout)

    # Hyperlinks
    log_in_hyperlink = ft.TextButton(
        text = "Entrar",
        on_click = return_to_log_in
    )

    sign_up_hyperlink = ft.TextButton(
        text = "Cadastrar-se",
        on_click = return_to_sign_up
    )

    # Coloca os botões em uma linha
    log_in_button_row = ft.Row(
        controls = [
            log_in_button,
            sign_up_hyperlink
        ],
        alignment = ft.MainAxisAlignment.CENTER,
        spacing = 10
    )

    sign_up_button_row = ft.Row(
        controls = [
            sign_up_button,
            log_in_hyperlink
        ],
        alignment = ft.MainAxisAlignment.CENTER,
        spacing = 10
    )

    # Carrega os elementos da pagina
    # Pagina de log in
    log_in_layout = ft.Container(
        expand = False,
        content = ft.Column(
            alignment = ft.MainAxisAlignment.CENTER,
            horizontal_alignment = ft.CrossAxisAlignment.CENTER,
            controls=[
                header_stack,
                ft.Container(margin=ft.Margin(0, 30, 0, 0)),
                textfield_email,            
                textfield_password,
                ft.Container(margin=ft.Margin(0, 30, 0, 0)),
                log_in_button_row
            ]
        )
    )

    # Pagina de cadastro
    sign_up_layout = ft.Container(
        expand = False,
        content = ft.Column(
            alignment = ft.MainAxisAlignment.CENTER,
            horizontal_alignment = ft.CrossAxisAlignment.CENTER,
            controls=[
                header_stack,
                ft.Container(margin=ft.Margin(0, 30, 0, 0)),
                textfield_email_sign,
                textfield_confirm_email,            
                textfield_password_sign,
                textfield_confirm_password,
                ft.Container(margin=ft.Margin(0, 30, 0, 0)),
                sign_up_button_row
            ]
        )
    )

    # Carrega a pagina de login
    page.add(log_in_layout)
    page.overlay.append(snack_bar)

ft.app(main)
