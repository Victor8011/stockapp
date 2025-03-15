import flet as ft
import shutil
import os
import KEY  # Presumo que KEY.user_email esteja definido neste módulo

def main(page: ft.Page):
    page.vertical_alignment = ft.MainAxisAlignment.START
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.window.min_width = 620
    page.window.min_height = 620
    page.window.max_width = 620
    page.window.max_height = 1080

    # Caminho da pasta assets
    pasta_assets = "assets"

    # Função para limpar a pasta assets
    def limpar_pasta_assets():
        if os.path.exists(pasta_assets):
            for arquivo in os.listdir(pasta_assets):
                caminho_arquivo = os.path.join(pasta_assets, arquivo)
                if os.path.isfile(caminho_arquivo):
                    os.remove(caminho_arquivo)
        else:
            os.makedirs(pasta_assets)

    # Função para carregar a imagem padrão ao iniciar
    def carregar_imagem_padrao():
        if os.path.exists(pasta_assets):
            arquivos = os.listdir(pasta_assets)
            if arquivos:  # Verifica se há arquivos na pasta
                return os.path.join(pasta_assets, arquivos[0])  # Retorna o caminho da primeira imagem
        return '/user.png'  # Imagem padrão caso não haja nada em assets

    wellcome = ft.Text(
        "Seu Usuário Stock APP",
        font_family="Arial",
        size=20, 
        weight="bold"
    )

    # Imagem do perfil inicial (carrega a padrão ou a existente em assets)
    profile_image = ft.Image(
        src=carregar_imagem_padrao(),  # Carrega a imagem padrão ou a última selecionada
        width=100,
        height=100,
        fit=ft.ImageFit.COVER,
        border_radius=50,
    )

    your_email = ft.Text(
        f"Seu email: {KEY.user_email}"
    )

    row_user = ft.Row(
        controls=[
            profile_image,
            your_email
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        spacing=10
    )

    # FilePicker para selecionar a imagem
    file_picker = ft.FilePicker(
        on_result=lambda e: update_image(e)
    )

    # Botão para abrir o seletor de arquivos
    select_image_btn = ft.ElevatedButton(
        text="adicionar foto",
        on_click=lambda e: file_picker.pick_files(
            allow_multiple=False,
            allowed_extensions=["jpg", "png", "jpeg"]
        ),
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=10)
        )
    )

    # Função para atualizar a imagem
    def update_image(e):
        if e.files and len(e.files) > 0:
            # Pega o caminho do arquivo selecionado
            file_path = e.files[0].path
            file_name = e.files[0].name
            
            # Limpa a pasta assets antes de adicionar a nova imagem
            limpar_pasta_assets()
            
            # Caminho de destino na pasta assets
            caminho_destino = os.path.join(pasta_assets, file_name)
            
            # Copia a nova imagem para a pasta assets
            shutil.copy(file_path, caminho_destino)
            
            # Atualiza a fonte da imagem com o caminho em assets
            profile_image.src = caminho_destino
            page.update()

    layout = ft.Container(
        padding=ft.padding.only(top=80),
        content=ft.Column(
            controls=[
                wellcome,
                ft.Container(height=30),
                row_user,
                select_image_btn,
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        alignment=ft.alignment.top_center,
    )

    # Adiciona o FilePicker como overlay para funcionar
    page.overlay.append(file_picker)
    page.add(layout)