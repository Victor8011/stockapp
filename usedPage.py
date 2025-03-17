import flet as ft

class UsedPage:
    def __init__(self, page: ft.Page, products: dict):
        self.page = page
        self.products = products
        self.dropdown_category = self.categories_dropdown()
        self.dropdown_product = self.products_dropdown()
        self.quantity_field = None
        self.snack_bar = ft.SnackBar(
            content=ft.Text("", weight=ft.FontWeight.BOLD, color=ft.colors.WHITE),
            open=False,
            bgcolor=ft.colors.GREY_800,
            padding=10,
            elevation=8,
            duration=3000,
        )

    def categories_dropdown(self):
        dropdown = ft.DropdownM2(
            label="Selecione uma Categoria",
            width=260,
            border_color=ft.colors.GREY_100,
            hint_text="Selecione uma categoria",
            options=[ft.dropdown.Option(cat) for cat in self.products.keys()],
            on_change=self.update_products_dropdown
        )
        return dropdown

    def products_dropdown(self):
        dropdown = ft.DropdownM2(
            label="Selecione ou digite um Produto",
            width=260,
            border_color=ft.colors.GREY_100,
            hint_text="Selecionar",
            options=[],
            text_size=15,
            autofocus=True,  # Foco inicial para facilitar a digitação
            on_change=self.filter_products
        )
        return dropdown

    def update_products_dropdown(self, e):
        selected_category = self.dropdown_category.value
        if selected_category and selected_category in self.products:
            self.dropdown_product.options = [
                ft.dropdown.Option(product) for product in self.products[selected_category].keys()
            ]
        else:
            self.dropdown_product.options = []
        self.dropdown_product.value = None  # Limpa o produto ao mudar categoria
        self.dropdown_product.label = "Selecione um Produto" # retorna a pedir para selecionar um produto
        self.page.update()

    def filter_products(self, e):
        search_text = self.dropdown_product.value.lower() if self.dropdown_product.value else ""
        selected_category = self.dropdown_category.value
        if selected_category and selected_category in self.products:
            self.dropdown_product.options = [
                ft.dropdown.Option(product)
                for product in self.products[selected_category].keys()
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
            bgcolor=ft.colors.GREY_100,
            color="#000000",
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
            self.snack_bar.bgcolor = ft.colors.ORANGE_300
            self.snack_bar.open = True
            self.page.update()
            return

        if not selected_product:
            self.snack_bar.content.value = "Por favor, selecione um produto!"
            self.snack_bar.bgcolor = ft.colors.ORANGE_300
            self.snack_bar.open = True
            self.page.update()
            return

        if not quantity:
            self.snack_bar.content.value = "Por favor, digite a quantidade usada!"
            self.snack_bar.bgcolor = ft.colors.ORANGE_300
            self.snack_bar.open = True
            self.page.update()
            return

        if not quantity.isdigit():
            self.snack_bar.content.value = "A quantidade deve ser um número inteiro!"
            self.snack_bar.bgcolor = ft.colors.RED_400
            self.snack_bar.open = True
            self.page.update()
            return

        quantity_int = int(quantity)
        if quantity_int <= 0:
            self.snack_bar.content.value = "A quantidade deve ser maior que zero!"
            self.snack_bar.bgcolor = ft.colors.ORANGE_600
            self.snack_bar.open = True
            self.page.update()
            return

        current_quantity = self.products[selected_category].get(selected_product, 0)
        if quantity_int > current_quantity:
            self.snack_bar.content.value = f"A quantidade inserida ({quantity_int}) é maior que o estoque disponível ({current_quantity})!"
            self.snack_bar.bgcolor = ft.colors.RED_400
            self.snack_bar.open = True
            self.page.update()
            return

        self.products[selected_category][selected_product] -= quantity_int
        self.quantity_field.value = ""
        self.dropdown_product.value = None
        self.update_products_dropdown(None)

        self.snack_bar.content.value = f"{quantity_int} unidade(s) de '{selected_product}' usada(s) em '{selected_category}'!"
        self.snack_bar.bgcolor = ft.colors.GREEN_400
        self.snack_bar.open = True
        self.page.update()

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