# appVersionUpdate.py
import flet as ft
import requests
import CURRENT_VERSION as cv

APP_VERSION = cv.current_version

def open_dlg_modal(page: ft.Page):
    
        
    snack_bar = ft.SnackBar(content=ft.Text(""), open=False)
    page.overlay.append(snack_bar)  # Adiciona o snack_bar à página

    try:
        response = requests.get("https://raw.githubusercontent.com/truelanz/stockapp/main/version.txt", timeout=5)
        response.raise_for_status()
        latest_version = response.text.strip()
        
        # Abre o link no navegador
        def open_link(e):
            page.launch_url("https://github.com/truelanz") 
            page.dialog.open = False
            page.update()
        
        # Fecha o Alert
        def close_dlg_false(e):
            page.dialog.open = False
            page.update()

        if latest_version > APP_VERSION:
            dlg_modal = ft.AlertDialog(
                modal=True,
                content=ft.Text(f"Há uma versão mais recente do App:\nversão {latest_version}.\nDeseja atualizar?"),
                actions=[
                    ft.Row(
                        controls=[
                            ft.TextButton("Atualizar", 
                                        style=ft.ButtonStyle(color={"": ft.colors.GREEN}),
                                        on_click=open_link
                            ),
                            
                            ft.TextButton("Não atualizar", 
                                        style=ft.ButtonStyle(color={"": ft.colors.RED_400}), 
                                        on_click=close_dlg_false),
                        ],
                        spacing=20,
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    )
                ],
                actions_alignment=ft.MainAxisAlignment.CENTER,
            )
            page.dialog = dlg_modal
            page.add(dlg_modal)
            dlg_modal.open = True
            page.update()
        else:
            dlg_modal_recent_already = ft.AlertDialog(
                modal=True,
                content=ft.Text(f"Você já está na versão mais recente do App!\nVersão atual: {APP_VERSION}"),
                actions=[
                    ft.TextButton("Confirmar", style=ft.ButtonStyle(color={"": ft.colors.GREEN}), on_click=close_dlg_false),
                ],
                actions_alignment=ft.MainAxisAlignment.CENTER
            )
            page.dialog = dlg_modal_recent_already
            page.add(dlg_modal_recent_already)
            dlg_modal_recent_already.open = True
            page.update()
            
    except requests.exceptions.HTTPError as http_err:
        snack_bar.content.value = f"Erro HTTP: {http_err}"
        snack_bar.open = True
    except requests.exceptions.ConnectionError:
        snack_bar.content.value = "Erro de conexão: Sem internet ou servidor inacessível"
        snack_bar.open = True
    except requests.exceptions.Timeout:
        snack_bar.content.value = "Erro: Tempo de requisição excedido"
        snack_bar.open = True
    except Exception as ex:
        snack_bar.content.value = f"Erro inesperado: {ex}"
        snack_bar.open = True
    page.update()
