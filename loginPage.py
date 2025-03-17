import flet as ft
import time
import threading
import requests
import KEY

# console.firebase.google.com para pegar API KEY
# install request: pip install requests

# criando variável com chave API do Google Firebase
API_KEY = KEY.firebase_key  # Chave API da Web do Firebase

def main(page: ft.Page):
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.window.min_width = 620
    page.window.min_height = 620
    page.window.width = 620
    page.window.height = 620
    page.window.maximizable = True
    snack_bar = ft.SnackBar(content=ft.Text(""), open=False)

    def btn_login(e):
        try:
            # Usando a API REST do Firebase para autenticação
            url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={API_KEY}"
            payload = {
                "email": textfield_email.value,
                "password": textfield_password.value,
                "returnSecureToken": True
            }
            response = requests.post(url, json=payload)
            response.raise_for_status()  # Levanta exceção se houver erro HTTP

            data = response.json()
            if "idToken" in data:
                # Salva o email no módulo user_data
                KEY.user_email = textfield_email.value

                # Limpa a tela e mostra Pagina pós login
                page.clean()
                from app import main
                app_home_page = main(page)
                app_home_page

                # Snack bar de sucesso
                snack_bar.content=ft.Text("Logado com sucesso!", weight=ft.FontWeight.BOLD)
                snack_bar.bgcolor = ft.Colors.GREEN_400
                snack_bar.action="OK"
                snack_bar.action_color = ft.Colors.BLACK87
                snack_bar.duration=3000
                snack_bar.open = True
                page.update()

            else:
                raise Exception("Falha na autenticação")

        except Exception as e:
            error_message = "Erro ao fazer login. Verifique suas credenciais."
            if isinstance(e, requests.RequestException) and e.response is not None:
                error_message = e.response.json().get("error", {}).get("message", error_message)
            # Adiciona SnackBar de erro
            snack_bar.content=ft.Text("email ou senha incorreta", weight=ft.FontWeight.BOLD)
            snack_bar.bgcolor = ft.Colors.RED_400
            snack_bar.action="OK"
            snack_bar.action_color = ft.Colors.BLACK87
            snack_bar.duration=3000
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
    )

    # Container com gradiente animado
    gradient_container = ft.Container(
        content=login_text,
        padding=10,
        border_radius=10,
        gradient=ft.LinearGradient(
            begin=ft.Alignment(-1, 0),  # Início à esquerda
            end=ft.Alignment(1, 0),     # Fim à direita
            colors=[ft.colors.BLUE, ft.Colors.GREEN],
            stops=[0.0, 1.0],           # Posições iniciais das cores
            rotation=0,                 # Rotação inicial
        ),
        animate_rotation=True,  # Habilita animação na rotação
    )

    # Função para animar o gradiente
    def animate_gradient():
        rotation = 0
        while True:
            rotation += 0.2  # Incrementa a rotação
            if rotation >= 6.28:  # 2π (um ciclo completo)
                rotation = 0
            gradient_container.gradient.rotation = rotation
            page.update()
            time.sleep(0.05)  # Controla a velocidade da animação

    # Inicia a animação em uma thread separada para não bloquear a UI
    threading.Thread(target=animate_gradient, daemon=True).start()
    
    # ------------------------------

    textfield_email = ft.TextField(label="Email", width=300)
    textfield_password = ft.TextField(label="Senha", password=True, width=300)
    confirm_button = ft.ElevatedButton(text="Login", width=100, height=40, on_click=btn_login)

    # inserindo elementos criados na pagina
    main_page = ft.Container(
        expand=False,
        content=ft.Column(
            controls=[
                gradient_container,
                ft.Container(margin=ft.Margin(bottom=30, top=0, left=0, right=0)),
                textfield_email,
                textfield_password,
                ft.Container(margin=ft.Margin(bottom=0, top=5, left=0, right=0)),
                confirm_button,
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        padding=20,
    )
    page.overlay.append(snack_bar)
    page.add(main_page)

ft.app(target=main, assets_dir="assets", view=ft.WEB_BROWSER)
