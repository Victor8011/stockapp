from ctypes import alignment
from sre_parse import MAXWIDTH
from tkinter.tix import MAX
from tracemalloc import start
import flet as ft

class Stock:
    def __init__(self, page: ft.Page):
        self.page = page
        self.page.scroll = "adaptive"
        self.page.title = "Stock App"
        self.page.vertical_alignment = ft.MainAxisAlignment.START  # Alinha o conteúdo no topo
        self.page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        # Inicializando os produtos
        self.products = {
            "Eletrônicos": {
                "Smartphone": 50,
                "Notebook": 30,
                "Tablet": 20,
                "Smartwatch": 10,
                "Fone de Ouvido": 100,
                "Carregador": 50,
                "Cabo USB": 200,
                "Carregador Sem Fio": 30,
                "pS4": 2000,
                "ps5":5000,   
            },
            "Alimentos": {
                "Café": 10000,
                "Arroz": 100,
                "Feijão": 80,
                "Macarrão": 50,
                "Azeite de Oliva": 20,
                "Leite em Pó": 30,
                "Açúcar": 60,
                "Sal": 40,
                "Farinha de Trigo": 70,
                "Ovo": 10000,
                "Batata": 100,
                "Farinha": 80,
                "Repolho": 50,
                "Azeitona": 20,
                "Cereal": 30,
                "Páprica": 60,
                "Fermento": 40,
                "Hamburguer": 70,
            }
        }
        
        self.page.padding = ft.Padding(left=0, right=0, top=20, bottom=0)  # Padding em todas as direções

        # Chama main_page após a inicialização
        self.main_page()

    # Botões do topo: Adicionar e Usados
    def topButtons(self):
        addButton = ft.ElevatedButton(
            text="Adicionar",
            bgcolor="Green",
            color="Black",
            width=100,
            height=40,
            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10)),
        )
        productsUsedButton = ft.ElevatedButton(
            text="Usados",
            bgcolor="Yellow",
            color="Black",
            width=100,
            height=40,
            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10)),
        )
        row = ft.Row(
            controls=[addButton, productsUsedButton],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=20,
        )
        return row

    def products_list(self):
        itens = []
        for cat, items in self.products.items():
            for product, quantity in items.items():
                # Criando um Row para organizar os três elementos
                content_row = ft.Row(
                    controls=[
                        ft.Text(value=cat, color="#000000", text_align=ft.TextAlign.LEFT),  # Categoria à esquerda
                        ft.Text(value=product, color="#000000", text_align=ft.TextAlign.CENTER, expand=True),  # Produto no centro
                        ft.Text(value=str(quantity), color="#000000", text_align=ft.TextAlign.RIGHT),  # Quantidade à direita
                        ft.IconButton(icon=ft.Icons.EDIT, icon_color="Blue"),  # Ícone de exclusão à direita
                        ft.IconButton(icon=ft.Icons.DELETE, icon_color="Red")  # Ícone de exclusão à direita
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,  # Espaçamento uniforme entre os elementos
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                )
                
                # Criando o botão com o Row como conteúdo
                btn = ft.ElevatedButton(
                    content=content_row,
                    expand=True,  # Ocupa toda a largura disponível
                    height=50,
                    style=ft.ButtonStyle(
                        shape=ft.RoundedRectangleBorder(radius=10),
                        bgcolor="#E0E0E0",
                        padding=ft.Padding(20, 0, 20, 0)
                    ),
                )
                itens.append(btn)
        return ft.Column(controls=itens, spacing=5)

    def main_page(self):
        self.page.add(self.topButtons())

        input_task = ft.TextField(
            hint_text="Procure um produto",
            expand=True,
            align_label_with_hint=True,
            text_size=15,
            border_radius=10,
            bgcolor="#FFFFFF",
            color="#000000",
        )

        input_bar = ft.Row(
            controls=[input_task],
            expand=True  # Garante que a barra de pesquisa ocupe toda a largura
        )
        self.page.add(input_bar)

        # Envolvendo o products_list em um Container para ocupar toda a largura
        product_list_container = ft.Container(
            content=self.products_list(),
            expand=True,  # Faz o contêiner ocupar toda a largura da página
            padding=0
        )
        self.page.add(product_list_container)
        self.page.update()

ft.app(target=Stock)
