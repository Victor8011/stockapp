import flet as ft
import time
import threading
import requests
import KEY
import app

API_KEY = KEY.firebase_key  # Chave API da Web do Firebase

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

    def btn_login(e):
        try:
            url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={API_KEY}"
            payload = {
                "email": textfield_email.value,
                "password": textfield_password.value,
                "returnSecureToken": True
            }
            response = requests.post(url, json=payload)
            response.raise_for_status()

            data = response.json()
            if "idToken" in data:
                KEY.user_email = textfield_email.value
                snack_bar.content = ft.Text("Logado com sucesso!", weight=ft.FontWeight.BOLD)
                snack_bar.bgcolor = ft.Colors.GREEN_400
                snack_bar.action = "OK"
                snack_bar.action_color = ft.Colors.BLACK87
                snack_bar.duration = 1800
                snack_bar.open = True
                
                page.clean()
                app.main(page)
                page.update()
            else:
                raise Exception("Falha na autenticação")

        except Exception as e:
            error_message = "Erro ao fazer login. Verifique suas credenciais."
            if isinstance(e, requests.RequestException) and e.response is not None:
                error_message = e.response.json().get("error", {}).get("message", error_message)
            snack_bar.content = ft.Text("Email ou senha incorreta", weight=ft.FontWeight.BOLD)
            snack_bar.bgcolor = ft.Colors.RED_400
            snack_bar.action = "OK"
            snack_bar.action_color = ft.Colors.BLACK87
            snack_bar.duration = 1800
            snack_bar.open = True
            page.update()

            textfield_email.value = ""
            textfield_password.value = ""
            page.update()

    # TEXT TITLER STOCKAPP --------
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

    # Campos de login
    textfield_email = ft.TextField(label="Email", width=300)
    textfield_password = ft.TextField(label="Senha", password=True, width=300)
    confirm_button = ft.ElevatedButton(
        text="Login",
        width=100,
        height=40,
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=10),
            overlay_color=ft.Colors.GREEN_400
        ),
        on_click=btn_login
    )

    # Inserindo elementos na página
    main_page = ft.Container(
        expand=False,
        content=ft.Column(
            controls=[
                header_stack,  # Stack com imagem e gradient_container
                ft.Container(margin=ft.Margin(0, 30, 0, 0)),
                textfield_email,
                textfield_password,
                ft.Container(margin=ft.Margin(0, 30, 0, 0)),
                confirm_button,
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        padding=20,
    )
    page.overlay.append(snack_bar)
    page.add(main_page)

ft.app(target=main, assets_dir="assets")