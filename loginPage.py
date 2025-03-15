import flet as ft
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
    page.window.min_height = 900
    page.window.max_width = 620
    page.window.max_height = 1080
    page.window.wait_until_ready_to_show
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
                
                #Snack bar de sucesso
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

    # criando elementos do front-end
    login_text = ft.Text("Login", size=26)
    textfield_email = ft.TextField(label="Email", width=300)
    textfield_password = ft.TextField(label="Password", password=True, width=300)
    confirm_button = ft.ElevatedButton(text="Login", width=100, height=40, on_click=btn_login)

    # inserindo elementos criados na pagina
    main_page = ft.Container(
        expand=False,
        content=ft.Column(
            controls=[
                login_text,
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

ft.app(target=main, assets_dir='assets')