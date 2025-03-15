import flet as ft
import KEY

def main(page: ft.Page):
    page.vertical_alignment = ft.MainAxisAlignment.START
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.window.min_width = 620
    page.window.min_height = 620
    page.window.max_width = 620
    page.window.max_height = 1080
    
    wellcome = ft.Text(
        "Seu Usuário Stock APP",
        font_family="Arial",
        size=20, 
        weight="bold"
    )
    
    # Substitui o ícone por uma imagem circular
    profile_image = ft.Image(
        src='/user.png',  # Inicialmente sem imagem
        width=100,
        height=100,
        fit=ft.ImageFit.COVER,  # Ajusta a imagem ao tamanho do círculo
        border_radius=50,  # Raio = metade do tamanho (100/2) para formar um círculo
    )
    

    your_email = ft.Text(
        f"Seu email: {KEY.user_email}"
    )
    
    row_user = ft.Row(
        controls=[
            #defaut_image,
            profile_image,  # Imagem no lugar do ícone
            your_email
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        spacing=10  # Espaço entre a imagem e o texto
    )
    
    # FilePicker para selecionar a imagem
    file_picker = ft.FilePicker(
        on_result=lambda e: update_image(e)
    )
    
    # Botão para abrir o seletor de arquivos
    select_image_btn = ft.Button(
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
            # Atualiza a fonte da imagem com o caminho local
            profile_image.src = file_path
            page.update()
    
    layout = ft.Container(
        padding=ft.padding.only(top=80),
        content=ft.Column(
            controls=[
                wellcome,
                ft.Container(height=30),
                row_user,
                select_image_btn,  # Botão para selecionar a imagem
            ],
            #spacing=30,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        alignment=ft.alignment.top_center,
    )
    
    # Adiciona o FilePicker como overlay para funcionar
    page.overlay.append(file_picker)
    page.add(layout)

#ft.app(target=main, assets_dir='assets')