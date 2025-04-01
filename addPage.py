import flet as ft
import sqlite3

class AddPage:
    def __init__(self, page: ft.Page, data_table: ft.DataTable):
        self.page = page
        self.data_table = data_table  # Referência à DataTable para atualização
        self.dropdown = self.categories_dropdown()
        self.new_category_field = None  # Referência ao TextField para categoria
        self.new_product_field = None   # Referência ao TextField para produto
        self.quantity_field = None      # Referência ao TextField para quantidade
        self.snack_bar = ft.SnackBar(
            content=ft.Text("", weight=ft.FontWeight.BOLD),
            open=False,
            bgcolor=ft.Colors.GREY_800,
            padding=10,
            elevation=8,
            duration=1800,
        )

    def get_categories(self):
        """Obtém as categorias existentes do banco de dados."""
        conexao = sqlite3.connect("tb_products.db")
        cursor = conexao.cursor()
        cursor.execute("SELECT DISTINCT category FROM products")
        categories = [row[0] for row in cursor.fetchall()]
        conexao.close()
        return categories

    def add_new_category(self):
        # Campo de texto para a nova categoria
        self.new_category_field = ft.TextField(
            hint_text="Adicionar categoria",
            expand=False,
            width=200,
            text_size=15,
            border_radius=10,
            bgcolor=ft.Colors.GREY_100,
            color="#000000",
        )

        # Botão de confirmar categoria
        confirm_button = ft.ElevatedButton(
            text="OK",
            bgcolor="Green",
            color="White",
            width=50,
            height=40,
            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10)),
            on_click=self.confirm_category
        )

        # Retorna um Row contendo o TextField e o botão
        return ft.Row(
            controls=[
                self.new_category_field,
                confirm_button
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=10
        )

    def confirm_category(self, e):
        # Pega o valor digitado no campo de texto
        new_category = self.new_category_field.value.strip()

        if not new_category:
            self.snack_bar.content.value = "Por favor, digite uma categoria!"
            self.snack_bar.bgcolor = ft.Colors.ORANGE_300
            self.snack_bar.open = True
            self.page.update()
            return

        # Verifica se a categoria já existe no banco (case-insensitive)
        categories = self.get_categories()
        if new_category.lower() in (cat.lower() for cat in categories):
            self.snack_bar.content.value = f"A categoria '{new_category}' já existe!"
            self.snack_bar.bgcolor = ft.Colors.ORANGE_200
            self.snack_bar.open = True
            self.page.update()
            return

        # Como estamos apenas criando a categoria, podemos adicionar um produto vazio ou apenas atualizar o dropdown
        self.dropdown.options = [ft.dropdown.Option(cat) for cat in self.get_categories() + [new_category]]
        self.new_category_field.value = ""
        self.snack_bar.content.value = f"Categoria '{new_category}' adicionada com sucesso!"
        self.snack_bar.bgcolor = ft.Colors.GREEN_400
        self.snack_bar.open = True
        self.page.update()

    def categories_dropdown(self):
        # Cria o dropdown com base nas categorias do banco de dados
        return ft.Dropdown(
            label="Selecione uma Categoria",
            width=260,
            border_color=ft.Colors.GREY_100,
            hint_text="Selecione uma categoria",
            options=[ft.dropdown.Option(cat) for cat in self.get_categories()],
        )

    def add_new_product(self):
        # Campo de texto para o nome do produto
        self.new_product_field = ft.TextField(
            hint_text="Nome do produto",
            expand=False,
            width=260,
            text_size=15,
            border_radius=10,
            bgcolor=ft.Colors.GREY_100,
            color="#000000",
        )

        # Campo de texto para a quantidade (somente inteiros)
        self.quantity_field = ft.TextField(
            hint_text="Quantidade (somente números)",
            expand=False,
            width=260,
            text_size=15,
            border_radius=10,
            bgcolor=ft.Colors.GREY_100,
            color="#000000",
            keyboard_type=ft.KeyboardType.NUMBER, # Apenas números
        )

        # Botão de confirmar produto
        confirm_product_button = ft.ElevatedButton(
            text="Confirmar",
            bgcolor="Green",
            color="White",
            width=100,
            height=40,
            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10)),
            on_click=self.confirm_product
        )

        # Retorna uma Column com os campos e o botão
        return ft.Column(
            controls=[
                self.new_product_field,
                self.quantity_field,
                confirm_product_button
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=22
        )

    def confirm_product(self, e):
        # Pega os valores dos campos
        selected_category = self.dropdown.value
        new_product = self.new_product_field.value.strip()
        quantity = self.quantity_field.value.strip()

        # Validações
        if not selected_category:
            self.snack_bar.content.value = "Por favor, selecione uma categoria!"
            self.snack_bar.bgcolor = ft.Colors.ORANGE_300
            self.snack_bar.open = True
            self.page.update()
            return

        if not new_product:
            self.snack_bar.content.value = "Por favor, digite o nome do produto!"
            self.snack_bar.bgcolor = ft.Colors.ORANGE_300
            self.snack_bar.open = True
            self.page.update()
            return

        if not quantity:
            self.snack_bar.content.value = "Por favor, digite a quantidade!"
            self.snack_bar.bgcolor = ft.Colors.ORANGE_300
            self.snack_bar.open = True
            self.page.update()
            return

        # Validação manual da quantidade
        if not quantity.isdigit():
            self.snack_bar.content.value = "A quantidade deve ser um número inteiro!"
            self.snack_bar.bgcolor = ft.Colors.RED_400
            self.snack_bar.open = True
            self.page.update()
            return

        quantity_int = int(quantity)
        if quantity_int < 0:
            self.snack_bar.content.value = "A quantidade deve ser um número positivo!"
            self.snack_bar.bgcolor = ft.Colors.ORANGE_600
            self.snack_bar.open = True
            self.page.update()
            return

        # Verifica se o produto já existe na categoria selecionada no banco
        conexao = sqlite3.connect("tb_products.db")
        cursor = conexao.cursor()
        cursor.execute(
            "SELECT product FROM products WHERE category = ? AND product = ?",
            (selected_category, new_product)
        )
        if cursor.fetchone():
            self.snack_bar.content.value = f"O produto '{new_product}' já existe em '{selected_category}'!"
            self.snack_bar.bgcolor = ft.Colors.ORANGE_200
            self.snack_bar.open = True
            self.page.update()
            conexao.close()
            return

        # Adiciona o novo produto ao banco de dados
        cursor.execute(
            "INSERT INTO products (category, product, quantity) VALUES (?, ?, ?)",
            (selected_category, new_product, quantity_int)
        )
        conexao.commit()
        conexao.close()

        # Limpa os campos
        self.new_product_field.value = ""
        self.quantity_field.value = ""

        # Atualiza a DataTable
        self.update_data_table()

        # Exibe mensagem de sucesso
        self.snack_bar.content.value = f"Produto '{new_product}' adicionado a '{selected_category}' com sucesso!"
        self.snack_bar.bgcolor = ft.Colors.GREEN_400
        self.snack_bar.open = True
        self.page.update()

    def update_data_table(self):
        """Atualiza a DataTable com os dados mais recentes do banco de dados."""
        self.data_table.rows.clear()
        conexao = sqlite3.connect("tb_products.db")
        cursor = conexao.cursor()
        cursor.execute("SELECT category, product, quantity FROM products")
        dados = cursor.fetchall()
        conexao.close()

        for category, product, quantity in dados:
            self.data_table.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(category)),
                        ft.DataCell(ft.Text(product)),
                        ft.DataCell(ft.Text(str(quantity))),
                        ft.DataCell(
                            ft.Row(
                                controls=[
                                    ft.IconButton(
                                        icon=ft.icons.ADD_CIRCLE_OUTLINE,
                                        icon_color="BLUE",
                                        icon_size=20,
                                        data={"category": category, "product": product},
                                        # on_click definido na página principal
                                    ),
                                    ft.IconButton(
                                        icon=ft.icons.DELETE,
                                        icon_color="RED",
                                        icon_size=20,
                                        data={"category": category, "product": product},
                                        # on_click definido na página principal
                                    ),
                                ],
                                spacing=10,
                            )
                        ),
                    ]
                )
            )

    def addMainPage(self):
        main_content = ft.Container(
            expand=True,
            padding=20,
            alignment=ft.alignment.center,
            content=ft.Column(
                controls=[
                    ft.Text(
                        "Crie categorias e produtos",
                        weight=ft.FontWeight.BOLD,
                        text_align=ft.TextAlign.CENTER,
                        size=30,
                        font_family="Consolas"
                    ),
                    self.add_new_category(),
                    self.dropdown,
                    self.add_new_product()
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=22
            ),
        )
        # Adiciona o SnackBar à página
        self.page.overlay.append(self.snack_bar)
        self.page.add(main_content)
        self.page.update()