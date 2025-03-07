from math import radians
from sqlite3 import adapt
from sre_parse import MAXWIDTH
from tracemalloc import start
import flet as ft
#from networkx import radius

from add_product_page import AddProductPage



class Stock:
    def __init__(self, page: ft.Page):
        self.page = page
        self.page.scroll = "adaptive"
        self.page.title = "Stock App"
        self.page.vertical_alignment = ft.MainAxisAlignment.START
        self.page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        #self.page.window.width = 1024
        #self.page.window.height = 768
        self.page.window.min_width = 620
        self.page.window.min_height = 620
        #self.page.window.center()

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
                "PS4": 2000,
                "PS5": 5000,   
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

        self.page.padding = ft.Padding(left=0, right=0, top=0, bottom=0)  # Padding em todas as direções
        self.search_text = ""  # Variável para armazenar o texto digitado na busca
        self.table_container = None  # Referência ao container da tabela para atualização dinâmica
        self.sort_column = None  # Coluna atualmente ordenada
        self.sort_ascending = True  # Ordem crescente ou decrescente

        # Chama main_page após a inicialização
        self.main_page()

    # ---------------------------------------------------------------------

    # Barra superior
    def topBar(self):
        # Ícone de home à esquerda
        home_icon = ft.Container(
            content=ft.Icon(
                name=ft.Icons.HOME,
                size=30,
                color=ft.Colors.WHITE
            ),
            padding=ft.Padding(left=50, right=0, top=0, bottom=0)  # Padding de 50px à esquerda
        )
        
        # Ícone de usuário à direita
        user_icon = ft.Container(
            content=ft.Icon(
                name=ft.Icons.PERSON,
                size=30,
                color=ft.Colors.WHITE
            ),
            padding=ft.Padding(left=0, right=50, top=0, bottom=0)  # Padding de 50px à direita
        )
        
        # Barra superior com os ícones dentro de um Container para aplicar bgcolor
        top_bar_content = ft.Row(
            controls=[home_icon, user_icon],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            expand=True,
        )
        
        top_bar = ft.Container(
            content=top_bar_content,
            bgcolor=ft.Colors.BLUE_300,
            height=40,
        )
        
        return top_bar

    # ---------------------------------------------------------------------

    # Botões do topo: Adicionar e Usados
    def topButtons(self):
        addButton = ft.ElevatedButton(
            text="Adicionar",
            bgcolor="Green",
            color="Black",
            width=100,
            height=40,
            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10)),
            on_click=self.open_add_product_dialog  # Evento para abrir a nova página
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
    
    def open_add_product_dialog(self, e):
        # Cria o diálogo de adicionar produto
        dialog = AddProductPage(self.page, self.products, self.update_table)
        self.page.dialog = dialog.dialog  # Define o diálogo na página
        dialog.dialog.open = True
        self.page.update()

    def update_table(self):
        if self.table_container:
            self.table_container.content = self.products_list()
            self.table_container.update()

    # ---------------------------------------------------------------------

    # def products_list(self):
    #     # Filtra os produtos com base no texto de busca
    #     filtered_products = {}
    #     if self.search_text:
    #         for cat, items in self.products.items():
    #             filtered_items = {p: q for p, q in items.items() if self.search_text.lower() in p.lower()}
    #             if filtered_items:
    #                 filtered_products[cat] = filtered_items
    #     else:
    #         filtered_products = self.products

    #     #Configurando as colunas da tabela
    #     columns = [
    #         ft.DataColumn(ft.ElevatedButton("Categoria")),
    #         ft.DataColumn(ft.ElevatedButton("Produto")),
    #         ft.DataColumn(ft.ElevatedButton("Quantidade")),
    #         ft.DataColumn(ft.ElevatedButton("Ações")),
    #     ]
        
    #     # Criando as linhas da tabela
    #     rows = []
    #     for cat, items in filtered_products.items():
    #         for product, quantity in items.items():
    #             rows.append(
    #                 ft.DataRow(
    #                     cells=[
    #                         ft.DataCell(ft.Text(cat)),
    #                         ft.DataCell(ft.Text(product)),
    #                         ft.DataCell(ft.Text(str(quantity))),
    #                         ft.DataCell(
    #                             ft.Row(
    #                                 controls=[
    #                                     ft.IconButton(icon=ft.Icons.EDIT, icon_color="Blue"),
    #                                     ft.IconButton(icon=ft.Icons.DELETE, icon_color="Red")
    #                                 ],
    #                                 spacing=10
    #                             )
    #                         ),
    #                     ]
    #                 )
    #             )

    #     # Retornando a tabela
    #     return ft.DataTable(
    #         columns=columns,
    #         rows=rows,
    #         border=ft.border.all(1, ft.Colors.GREY_400),  # Adicionando bordas à tabela
    #         border_radius=10,
    #         column_spacing=adapt
    #     )
        
    # --------------------------------------------------------------------
    
    # Função de ordenação e filtro da tabela
    def products_list(self):
        # Filtra os produtos com base no texto de busca
        filtered_products = {}
        if self.search_text:
            for cat, items in self.products.items():
                filtered_items = {p: q for p, q in items.items() if self.search_text.lower() in p.lower()}
                if filtered_items:
                    filtered_products[cat] = filtered_items
        else:
            filtered_products = self.products

        # Converte os produtos em uma lista plana para ordenação
        flat_list = []
        for cat, items in filtered_products.items():
            for product, quantity in items.items():
                flat_list.append({"categoria": cat, "produto": product, "quantidade": quantity})

        # Ordena a lista com base na coluna selecionada
        if self.sort_column == "Categoria":
            flat_list.sort(key=lambda x: x["categoria"], reverse=not self.sort_ascending)
        elif self.sort_column == "Produto":
            flat_list.sort(key=lambda x: x["produto"], reverse=not self.sort_ascending)
        elif self.sort_column == "Quantidade":
            flat_list.sort(key=lambda x: x["quantidade"], reverse=not self.sort_ascending)

        # Função de ordenação ao clicar no botão do cabeçalho
        def sort_table(e):
            column_name = e.control.data  # Usa o atributo data para identificar a coluna
            if self.sort_column == column_name:
                # Se já está ordenado pela mesma coluna, inverte a ordem
                self.sort_ascending = not self.sort_ascending
            else:
                # Nova coluna, começa com ordem crescente
                self.sort_column = column_name
                self.sort_ascending = True
            self.table_container.content = self.products_list()
            self.table_container.update()

        # Configurando as colunas da tabela com ElevatedButton
        columns = [
            ft.DataColumn(
                ft.ElevatedButton(
                    text="Categoria",
                    data="Categoria",
                    on_click=sort_table,
                    style=ft.ButtonStyle(
                        shape=ft.RoundedRectangleBorder(radius=5),
                    )
                )
            ),
            ft.DataColumn(
                ft.ElevatedButton(
                    text="Produto",
                    data="Produto",
                    on_click=sort_table,
                    style=ft.ButtonStyle(
                        shape=ft.RoundedRectangleBorder(radius=5),
                    )
                )
            ),
            ft.DataColumn(
                ft.ElevatedButton(
                    text="Quantidade",
                    data="Quantidade",
                    on_click=sort_table,
                    style=ft.ButtonStyle(
                        shape=ft.RoundedRectangleBorder(radius=5),
                    )
                )
            ),
            ft.DataColumn(ft.Text("Ações", weight=ft.FontWeight.BOLD)),
        ]
        
        # Criando as linhas da tabela
        rows = []
        for item in flat_list:
            rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(item["categoria"])),
                        ft.DataCell(ft.Text(item["produto"])),
                        ft.DataCell(ft.Text(str(item["quantidade"]))),
                        ft.DataCell(
                            ft.Row(
                                controls=[
                                    ft.IconButton(icon=ft.Icons.EDIT, icon_color="Blue"),
                                    ft.IconButton(icon=ft.Icons.DELETE, icon_color="Red")
                                ],
                                spacing=10
                            )
                        ),
                    ]
                )
            )

        return ft.DataTable(
            columns=columns,
            rows=rows,
            border=ft.border.all(1, ft.Colors.GREY_400),
            border_radius=10,
            column_spacing=25
        )

    # ---------------------------------------------------------------------

    # MAIN PAGE
    def main_page(self):
        self.page.add(self.topBar())
        self.table_container = ft.Container(content=self.products_list(), expand=True)
        # Container para a tabela, que será atualizado dinamicamente
        self.table_container = ft.Container(
            content=self.products_list(),
            expand=True,
        )
        # Container para o conteúdo principal com padding
        main_content = ft.Container(
            content=ft.Column(
                controls=[
                    self.topButtons(),
                    ft.Row(
                        controls=[
                            ft.TextField(
                                hint_text="Procure um produto",
                                expand=False,
                                align_label_with_hint=True,
                                text_size=15,
                                border_radius=10,
                                bgcolor="#FFFFFF",
                                color="#000000",
                                on_change=self.update_search  # Evento de mudança de texto
                            )
                        ],
                        #expand=True
                        alignment=ft.MainAxisAlignment.CENTER,
                    ),
                    self.table_container  # Referência ao container da tabela
                ],
                alignment=ft.MainAxisAlignment.START,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=20
            ),
            padding=ft.Padding(left=20, right=20, top=10, bottom=0)  # Padding no conteúdo principal
        )

        # Adicionando o Container com padding à página
        self.page.add(main_content)
        self.page.update()

    def update_search(self, e):
        # Atualiza o texto de busca e re-renderiza a tabela
        self.search_text = e.control.value
        if self.table_container:
            self.table_container.content = self.products_list()  # Atualiza o conteúdo da tabela
            self.table_container.update()  # Atualiza apenas o container da tabela

ft.app(target=Stock)