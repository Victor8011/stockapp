import flet as ft

class AddPage:
    def __init__(self, page: ft.Page, products: dict):
        self.page = page
        self.products = products  # Recebe o dicionário products diretamente
        self.dropdown = self.categories_dropdown()
        self.new_category_field = None  # Referência ao TextField para categoria
        self.new_product_field = None   # Referência ao TextField para produto
        self.quantity_field = None      # Referência ao TextField para quantidade
        self.snack_bar = ft.SnackBar(content=ft.Text(""), open=False)  # SnackBar persistente

    def add_new_category(self):
        # Campo de texto para a nova categoria
        self.new_category_field = ft.TextField(
            hint_text="Adicionar categoria",
            expand=False,
            width=200,
            text_size=15,
            border_radius=10,
            bgcolor=ft.colors.GREY_100,
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
            self.snack_bar.content = ft.Text("Por favor, digite uma categoria!", weight=ft.FontWeight.BOLD)
            self.snack_bar.bgcolor = ft.colors.ORANGE_300
            self.snack_bar.open = True
            self.page.update()
            return

        # Verifica se a categoria já existe (case-insensitive)
        if new_category.lower() in (cat.lower() for cat in self.products.keys()):
            self.snack_bar.content = ft.Text(f"A categoria '{new_category}' já existe!", weight=ft.FontWeight.BOLD)
            self.snack_bar.bgcolor = ft.colors.ORANGE_200
            self.snack_bar.open = True
            self.page.update()
            return

        # Adiciona a nova categoria ao dicionário products
        self.products[new_category] = {}
        self.dropdown.options = [ft.dropdown.Option(cat) for cat in self.products.keys()]
        self.new_category_field.value = ""
        self.snack_bar.content = ft.Text(f"Categoria '{new_category}' adicionada com sucesso!", weight=ft.FontWeight.BOLD)
        self.snack_bar.bgcolor = ft.colors.GREEN_400
        self.snack_bar.open = True
        self.page.update()

    def categories_dropdown(self):
        # Cria o dropdown com base nas chaves do dicionário products
        return ft.DropdownM2(
            label="Selecione uma Categoria",
            width=260,
            border_color=ft.colors.GREY_100,
            hint_text="Selecione uma categoria",
            options=[ft.dropdown.Option(cat) for cat in self.products.keys()],
        )

    def add_new_product(self):
        # Campo de texto para o nome do produto
        self.new_product_field = ft.TextField(
            hint_text="Nome do produto",
            expand=False,
            width=260,
            text_size=15,
            border_radius=10,
            bgcolor=ft.colors.GREY_100,
            color="#000000",
        )

        # Campo de texto para a quantidade (somente inteiros)
        self.quantity_field = ft.TextField(
            hint_text="Quantidade (somente números)",
            expand=False,
            width=260,
            text_size=15,
            border_radius=10,
            bgcolor=ft.colors.GREY_100,
            color="#000000",
            #input_filter=ft.InputFilter(regex_string=r"[0-9]")  # Permite apenas números
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
            self.snack_bar.content = ft.Text("Por favor, selecione uma categoria!", weight=ft.FontWeight.BOLD)
            self.snack_bar.bgcolor = ft.colors.ORANGE_300
            self.snack_bar.open = True
            self.page.update()
            return

        if not new_product:
            self.snack_bar.content = ft.Text("Por favor, digite o nome do produto!", weight=ft.FontWeight.BOLD)
            self.snack_bar.bgcolor = ft.colors.ORANGE_300
            self.snack_bar.open = True
            self.page.update()
            return

        if not quantity:
            self.snack_bar.content = ft.Text("Por favor, digite a quantidade!", weight=ft.FontWeight.BOLD)
            self.snack_bar.bgcolor = ft.colors.ORANGE_300
            self.snack_bar.open = True
            self.page.update()
            return

        # Validação manual da quantidade
        if not quantity.isdigit():
            self.snack_bar.content = ft.Text("A quantidade deve ser um número inteiro!", weight=ft.FontWeight.BOLD)
            self.snack_bar.bgcolor = ft.colors.RED_400
            self.snack_bar.open = True
            self.page.update()
            return

        quantity_int = int(quantity)
        if quantity_int < 0:
            self.snack_bar.content.value = "A quantidade deve ser um número positivo!"
            self.snack_bar.bgcolor = ft.colors.ORANGE_600
            self.snack_bar.open = True
            self.page.update()
            return

        # Verifica se o produto já existe na categoria selecionada (case-insensitive)
        if new_product.lower() in (prod.lower() for prod in self.products[selected_category].keys()):
            self.snack_bar.content = ft.Text(f"O produto '{new_product}' já existe em '{selected_category}'!", weight=ft.FontWeight.BOLD)
            self.snack_bar.bgcolor = ft.colors.ORANGE_200
            self.snack_bar.open = True
            self.page.update()
            return

        # Adiciona o produto à categoria selecionada
        self.products[selected_category][new_product] = quantity_int

        # Limpa os campos
        self.new_product_field.value = ""
        self.quantity_field.value = ""

        # Exibe mensagem de sucesso
        self.snack_bar.content = ft.Text(f"Produto '{new_product}' adicionado a '{selected_category}' com sucesso!", weight=ft.FontWeight.BOLD)
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
                        "Crie categorias e produtos",
                        weight=ft.FontWeight.BOLD,
                        text_align=ft.TextAlign.CENTER,
                        size=30,
                        font_family="Consolas"
                    ),
                    self.add_new_category(),
                    self.dropdown,
                    self.add_new_product()  # Adiciona os campos de produto e quantidade
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=22  # Aumenta o espaçamento entre os elementos
            ),
        )
        # Adiciona o SnackBar à página
        self.page.overlay.append(self.snack_bar)
        self.page.add(main_content)
        self.page.update()
