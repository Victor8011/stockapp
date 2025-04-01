import flet as ft
import sqlite3

class AddQuantity:
    def __init__(self, page: ft.Page, data_table: ft.DataTable, category: str, product: str):
        page.vertical_alignment = ft.MainAxisAlignment.START
        page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        self.page = page
        self.data_table = data_table    # Referência à DataTable para atualização
        self.category = category        # Categoria do produto selecionado
        self.product = product          # Nome do produto selecionado
        self.quantity_field = ft.TextField(
            hint_text="Acrescentar quantidade",
            expand=False,
            width=180,
            text_size=15,
            border_radius=10,
            bgcolor=ft.Colors.GREY_200,
            color="#000000",
            keyboard_type=ft.KeyboardType.NUMBER, # Apenas números
        )
        self.snack_bar = ft.SnackBar(
            content=ft.Text("", weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
            open=False,
            bgcolor=ft.Colors.GREY_800,
            padding=10,
            elevation=8,
            duration=1800,
        )
        # Obter a quantidade atual do banco de dados
        self.quantity_only = ft.Text(
            value=f"{self.get_current_quantity()}",
            size=15,
            weight=ft.FontWeight.BOLD,
            color=ft.Colors.YELLOW_900,
            disabled=True
        )
        
    # resgata a quantidade atual de produtos no banco de dados
    def get_current_quantity(self):
        """Obtém a quantidade atual do produto no banco de dados."""
        conexao = sqlite3.connect("tb_products.db")
        cursor = conexao.cursor()
        cursor.execute(
            "SELECT quantity FROM products WHERE category = ? AND product = ?",
            (self.category, self.product)
        )
        result = cursor.fetchone()
        conexao.close()
        return result[0] if result else 0

    def confirm_product(self, e):
        quantity = self.quantity_field.value.strip()

        # Validação: deve ser um número inteiro
        if not quantity.isdigit():
            self.snack_bar.content.value = "Digite um número inteiro"
            self.snack_bar.bgcolor = ft.Colors.ORANGE_600
            self.snack_bar.open = True
            self.page.update()
            return

        # Validação: deve ser maior que zero
        quantity_int = int(quantity)
        if quantity_int <= 0:
            self.snack_bar.content.value = "A quantidade deve ser maior que zero!"
            self.snack_bar.bgcolor = ft.Colors.ORANGE_600
            self.snack_bar.open = True
            self.page.update()
            return
        
        # Atualizar a quantidade no banco de dados
        conexao = sqlite3.connect("tb_products.db")
        cursor = conexao.cursor()
        cursor.execute(
            "UPDATE products SET quantity = quantity + ? WHERE category = ? AND product = ?",
            (quantity_int, self.category, self.product)
        )
        conexao.commit()
        conexao.close()

        # Limpa o campo
        self.quantity_field.value = ""

        # Atualiza o valor de quantity_only na tela
        new_quantity = self.get_current_quantity()
        self.quantity_only.value = f"{new_quantity}"
        self.quantity_only.update()

        # Atualiza a DataTable na página principal (se necessário)
        self.update_data_table()
        
        self.snack_bar.content.value = f"{quantity_int} unidade(s) adicionada(s) a '{self.product}' em '{self.category}'!"
        self.snack_bar.bgcolor = ft.Colors.GREEN_400
        self.snack_bar.open = True
        self.page.update()
        
    def update_data_table(self):
        """Atualiza a DataTable com os dados mais recentes do banco de dados."""
        self.data_table.rows.clear()
        conexao = sqlite3.connect("tb_products.db")
        cursor = conexao.cursor()
        cursor.execute("SELECT category, product, quantity FROM products")
        data_db = cursor.fetchall()
        conexao.close()
        
        for category, product, quantity in data_db:
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
                                        # on_click deve ser definido no contexto da página principal
                                    ),
                                    ft.IconButton(
                                        icon=ft.icons.DELETE,
                                        icon_color="RED",
                                        icon_size=20,
                                        data={"category": category, "product": product},
                                        # on_click deve ser definido no contexto da página principal
                                    ),
                                ],
                                spacing=10,
                            )
                        ),
                    ]
                )
            )

    def addMainPage(self):
        # TextButtons para exibir categoria, produto e quantidade atual (não editáveis)
        category_display = ft.Text(value=f"{self.category}:", size=16)
        product_display = ft.Text(value=f"{self.product}", size=16)  
        quantity_display = ft.Text(value="Quantidade atual:", size=16,)

        cat_product_row = ft.Row(
            controls=[category_display, product_display],
            alignment=ft.MainAxisAlignment.CENTER,
        )

        quantity_row = ft.Row(
            controls=[quantity_display, self.quantity_only],
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
                        color=ft.Colors.BLUE_500,
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
