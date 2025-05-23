import flet as ft
import sqlite3

class UsedPage:
    def __init__(self, page: ft.Page, data_table: ft.DataTable, database_name: str):
        self.user_db = database_name
        self.page = page
        self.data_table = data_table  # Referência à DataTable para atualização
        self.dropdown_category = self.categories_dropdown()
        self.dropdown_product = self.products_dropdown()
        self.quantity_field = None
        self.snack_bar = ft.SnackBar(
            content=ft.Text("", weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
            open=False,
            bgcolor=ft.Colors.GREY_800,
            padding=10,
            elevation=8,
            duration=1800,
        )

    def get_categories(self):
        """Obtém as categorias existentes do banco de dados."""
        conexao = sqlite3.connect(self.user_db)
        cursor = conexao.cursor()
        cursor.execute("SELECT DISTINCT category FROM products")
        categories = [row[0] for row in cursor.fetchall()]
        conexao.close()
        return categories

    def get_products_by_category(self, category):
        """Obtém os produtos de uma categoria específica do banco de dados."""
        conexao = sqlite3.connect(self.user_db)
        cursor = conexao.cursor()
        cursor.execute("SELECT product FROM products WHERE category = ?", (category,))
        products = [row[0] for row in cursor.fetchall()]
        conexao.close()
        return products

    def get_quantity(self, category, product):
        """Obtém a quantidade atual de um produto no banco de dados."""
        conexao = sqlite3.connect(self.user_db)
        cursor = conexao.cursor()
        cursor.execute(
            "SELECT quantity FROM products WHERE category = ? AND product = ?",
            (category, product)
        )
        result = cursor.fetchone()
        conexao.close()
        return result[0] if result else 0

    def categories_dropdown(self):
        dropdown = ft.Dropdown(
            label="Selecione uma Categoria",
            width=260,
            border_color=ft.Colors.GREY_100,
            hint_text="Selecione uma categoria",
            options=[ft.dropdown.Option(cat) for cat in self.get_categories()],
            on_change=self.update_products_dropdown
        )
        return dropdown

    def products_dropdown(self):
        dropdown = ft.Dropdown(
            label="Selecione ou digite um Produto",
            width=260,
            border_color=ft.Colors.GREY_100,
            hint_text="Selecionar",
            options=[],
            text_size=15,
            autofocus=True,
            on_change=self.filter_products
        )
        return dropdown

    def update_products_dropdown(self, e):
        selected_category = self.dropdown_category.value
        if selected_category:
            self.dropdown_product.options = [
                ft.dropdown.Option(product) for product in self.get_products_by_category(selected_category)
            ]
        else:
            self.dropdown_product.options = []
        self.dropdown_product.value = None  # Limpa o produto ao mudar categoria
        self.dropdown_product.label = "Selecione um Produto"
        self.page.update()

    def filter_products(self, e):
        search_text = self.dropdown_product.value.lower() if self.dropdown_product.value else ""
        selected_category = self.dropdown_category.value
        if selected_category:
            self.dropdown_product.options = [
                ft.dropdown.Option(product)
                for product in self.get_products_by_category(selected_category)
                if search_text in product.lower()
            ]
        else:
            self.dropdown_product.options = []
        self.page.update()

    def add_new_product(self):
        self.quantity_field = ft.TextField(
            hint_text="Quantidade usada (somente números)",
            expand=False,
            width=260,
            text_size=15,
            border_radius=10,
            bgcolor=ft.Colors.GREY_100,
            color="#000000",
            keyboard_type=ft.KeyboardType.NUMBER,  # Apenas números
        )

        confirm_product_button = ft.ElevatedButton(
            text="Confirmar",
            bgcolor="Green",
            color="White",
            width=100,
            height=40,
            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10)),
            on_click=self.confirm_product
        )

        return ft.Column(
            controls=[
                self.dropdown_product,
                self.quantity_field,
                confirm_product_button
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=22
        )

    def confirm_product(self, e):
        selected_category = self.dropdown_category.value
        selected_product = self.dropdown_product.value
        quantity = self.quantity_field.value.strip()

        if not selected_category:
            self.snack_bar.content.value = "Por favor, selecione uma categoria!"
            self.snack_bar.bgcolor = ft.Colors.ORANGE_300
            self.snack_bar.open = True
            self.page.update()
            return

        if not selected_product:
            self.snack_bar.content.value = "Por favor, selecione um produto!"
            self.snack_bar.bgcolor = ft.Colors.ORANGE_300
            self.snack_bar.open = True
            self.page.update()
            return

        if not quantity:
            self.snack_bar.content.value = "Por favor, digite a quantidade usada!"
            self.snack_bar.bgcolor = ft.Colors.ORANGE_300
            self.snack_bar.open = True
            self.page.update()
            return

        if not quantity.isdigit():
            self.snack_bar.content.value = "A quantidade deve ser um número inteiro!"
            self.snack_bar.bgcolor = ft.Colors.RED_400
            self.snack_bar.open = True
            self.page.update()
            return

        quantity_int = int(quantity)
        if quantity_int <= 0:
            self.snack_bar.content.value = "A quantidade deve ser maior que zero!"
            self.snack_bar.bgcolor = ft.Colors.ORANGE_600
            self.snack_bar.open = True
            self.page.update()
            return

        current_quantity = self.get_quantity(selected_category, selected_product)
        if quantity_int > current_quantity:
            self.snack_bar.content.value = f"A quantidade inserida ({quantity_int}) é maior que o estoque disponível ({current_quantity})!"
            self.snack_bar.bgcolor = ft.Colors.RED_400
            self.snack_bar.open = True
            self.page.update()
            return

        # Atualiza a quantidade no banco de dados
        conexao = sqlite3.connect(self.user_db)
        cursor = conexao.cursor()
        cursor.execute(
            "UPDATE products SET quantity = quantity - ? WHERE category = ? AND product = ?",
            (quantity_int, selected_category, selected_product)
        )
        conexao.commit()
        conexao.close()

        # Limpa os campos
        self.quantity_field.value = ""
        self.dropdown_product.value = None
        self.update_products_dropdown(None)

        # Atualiza a DataTable
        self.update_data_table()

        self.snack_bar.content.value = f"{quantity_int} unidade(s) de '{selected_product}' usada(s) em '{selected_category}'!"
        self.snack_bar.bgcolor = ft.Colors.GREEN_400
        self.snack_bar.open = True
        self.page.update()

    def update_data_table(self):
        """Atualiza a DataTable com os dados mais recentes do banco de dados."""
        self.data_table.rows.clear()
        conexao = sqlite3.connect(self.user_db)
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
                        "Produtos utilizados",
                        weight=ft.FontWeight.BOLD,
                        text_align=ft.TextAlign.CENTER,
                        size=30,
                        font_family="Consolas"
                    ),
                    self.dropdown_category,
                    self.add_new_product()
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=22
            ),
        )
        self.page.overlay.append(self.snack_bar)
        self.page.add(main_content)
        self.page.update()
