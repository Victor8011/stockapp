import flet as ft

class AddQuantity:
    def __init__(self, page: ft.Page, products: dict, category: str, product: str):
        page.vertical_alignment = ft.MainAxisAlignment.START
        page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        self.page = page
        self.products = products
        self.category = category  # Categoria do produto selecionado
        self.product = product    # Nome do produto selecionado
        self.quantity_field = ft.TextField(
            hint_text="Acrescentar quantidade",
            expand=False,
            width=180,
            text_size=15,
            border_radius=10,
            bgcolor=ft.colors.GREY_200,
            color="#000000",
            keyboard_type=ft.KeyboardType.NUMBER, # Apenas números
        )
        self.snack_bar = ft.SnackBar(
            content=ft.Text("", weight=ft.FontWeight.BOLD, color=ft.colors.WHITE),
            open=False,
            bgcolor=ft.colors.GREY_800,
            padding=10,
            elevation=8,
            duration=3000,
        )
        
    def confirm_product(self, e):
        quantity = self.quantity_field.value.strip()

        # Validação: deve ser um número inteiro
        if not quantity.isdigit():
            self.snack_bar.content.value = "Digite um número inteiro"
            self.snack_bar.bgcolor = ft.colors.ORANGE_600
            self.snack_bar.open = True
            self.page.update()
            return

        # Validação: deve ser maior que zero
        quantity_int = int(quantity)
        if quantity_int <= 0:
            self.snack_bar.content.value = "A quantidade deve ser maior que zero!"
            self.snack_bar.bgcolor = ft.colors.ORANGE_600
            self.snack_bar.open = True
            self.page.update()
            return

        # Soma a quantidade ao produto existente
        self.products[self.category][self.product] += quantity_int
        self.quantity_field.value = ""  # Limpa o campo

        self.snack_bar.content.value = f"{quantity_int} unidade(s) adicionada(s) a '{self.product}' em '{self.category}'!"
        self.snack_bar.bgcolor = ft.colors.GREEN_400
        self.snack_bar.open = True
        self.page.update()

    def addMainPage(self):
        # TextButtons para exibir categoria, produto e quantidade atual (não editáveis)
        category_display = ft.Text(value=f"{self.category}:", size=16, color=ft.colors.GREY_100)

        product_display = ft.Text(value=f"{self.product}", size=16, color=ft.colors.GREY_100)
        
        quantity_display = ft.Text(value="Quantidade atual:", size=16,)

        quantity_only = ft.Text(value=f"{self.products[self.category][self.product]}", size=16, color=ft.colors.YELLOW)

        cat_product_row = ft.Row(
            controls=[category_display, product_display],
            alignment=ft.MainAxisAlignment.CENTER,
        )
        
        quantity_row = ft.Row(
            controls=[quantity_display, quantity_only],
            alignment=ft.MainAxisAlignment.CENTER,
        )

        # Botão de confirmação
        confirm_product_button = ft.ElevatedButton(
            text="Confirmar",
            bgcolor="Green",
            color="White",
            width=100,
            height=40,
            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10)),
            on_click=self.confirm_product
        )

        # Layout principal
        main_content = ft.Container(
            padding=ft.padding.only(top=80),
            expand=True,
            alignment=ft.alignment.center,
            content=ft.Column(
                controls=[
                    ft.Text(
                        "Adicionar Quantidade",
                        color=ft.colors.BLUE_500,
                        weight=ft.FontWeight.BOLD,
                        text_align=ft.TextAlign.CENTER,
                        size=30,
                        font_family="Consolas",
                    ),
                    ft.Container(padding=ft.padding.only(top=20)),
                    cat_product_row,
                    quantity_row,
                    self.quantity_field,
                    confirm_product_button,
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=15,
            ),
        )
        self.page.overlay.append(self.snack_bar)
        self.page.add(main_content)
        self.page.update()
