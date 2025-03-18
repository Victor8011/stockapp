import flet as ft
import addPage
import usedPage
import importlib
import userPage
import addQuantityPage
#import loginPage

def main(page: ft.Page):
    # Configurações iniciais da página
    page.scroll = "adaptive"
    page.title = "Stock App"
    page.vertical_alignment = ft.MainAxisAlignment.START
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.window.min_width = 620
    page.window.min_height = 620
    page.window.width = 620
    page.window.height = 620
    page.window.maximizable = True

    # Função para determinar o spacing da DataTable
    def get_spacing():
        if page.window.width <= 425:  # Celulares menores
            return 11
        return 60  # Padrão para telas maiores

    # Atualiza o spacing quando a janela é redimensionada
    def on_resize(e):
        nonlocal table_container
        if table_container and isinstance(table_container.content, ft.DataTable):
            table_container.content.column_spacing = get_spacing()
            table_container.update()
        page.update()

    page.on_resized = on_resize

    # Inicializando os produtos
    products = {"Eletrônicos": {
        "Smartphone": 2500.00,
        "Notebook": 4500.00,
        "Fone de Ouvido": 200.00
    }}

    page.padding = ft.Padding(left=0, right=0, top=0, bottom=0)
    search_text = ""  # Variável para armazenar o texto digitado na busca
    table_container = None  # Referência ao container da tabela
    sort_column = None  # Coluna atualmente ordenada
    sort_ascending = True  # Ordem crescente ou decrescente

    # Barra superior
    def topBar():
        home_icon = ft.Container(
            content=ft.TextButton(
                content=ft.Row(
                    controls=[
                        ft.Icon(ft.icons.HOME_OUTLINED, size=30, color="GREEN"),
                        ft.Text("HOME", size=12, color="WHITE"),  # Cor ajustada para visibilidade
                    ],
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,  # Centraliza verticalmente
                    spacing=5,  # Espaço entre ícone e texto
                ),
                on_click=update_home
            ),
            padding=ft.Padding(left=15, right=0, top=10, bottom=0),
        )

        user_icon = ft.Container(
            content=ft.TextButton(
                content=ft.Row(
                    controls=[
                        ft.Icon(ft.icons.PERSON_OUTLINE, size=30, color="GREEN"),
                        ft.Text("USER", size=12, color="WHITE"),
                    ],
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=5,
                ),
                on_click=update_user,  # Substitua por update_user
            ),
            padding=ft.Padding(left=5, right=0, top=10, bottom=0),
        )

        exit_icon = ft.Container(
            content=ft.TextButton(
                content=ft.Row(
                    controls=[
                        ft.Icon(ft.icons.EXIT_TO_APP, size=30, color="GREY_200"),
                        ft.Text("EXIT", size=12, color="WHITE"),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    spacing=5,
                ),
                on_click=lambda e: page.window.close()
            ),
            padding=ft.Padding(left=0, right=15, top=10, bottom=0),
        )

        top_bar_content = ft.Container(
            content=ft.Row(
                controls=[
                    ft.Row(
                        controls=[home_icon, user_icon],
                        spacing=20
                    ),
                    exit_icon
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,  # Empurra EXIT para a direita
                expand=True,
                spacing=20,
            )
        )

        top_bar = ft.Container(
            content=top_bar_content,
            height=40,
        )
        return top_bar

    # Botões do topo: Adicionar e Usados
    def topButtons():
        addButton = ft.ElevatedButton(
            text="Criar",
            color=ft.Colors.BLUE_100,
            width=100,
            height=40,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=10),
                overlay_color=ft.Colors.GREEN_400,
            ),
            on_click=update_add,
        )
        productsUsedButton = ft.ElevatedButton(
            text="Usados",
            color=ft.Colors.BLUE_100,
            width=100,
            height=40,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=10),
                overlay_color=ft.Colors.YELLOW_400),
            on_click=update_used
        )
        row = ft.Row(
            controls=[addButton, productsUsedButton],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=20,
        )
        return row

    # Função de ordenação e filtro da tabela
    def products_list():
        nonlocal search_text, sort_column, sort_ascending
        filtered_products = {}

        # Se search_text estiver vazio, exibe todos os produtos
        if not search_text:
            filtered_products = products
        else:
            # Filtra os produtos com base no texto digitado
            for cat, items in products.items():
                filtered_items = {p: q for p, q in items.items() if search_text.lower() in p.lower()}
                if filtered_items:
                    filtered_products[cat] = filtered_items

        flat_list = []
        for cat, items in filtered_products.items():
            for product, quantity in items.items():
                flat_list.append({"categoria": cat, "produto": product, "quantidade": quantity})

        if sort_column == "Categoria":
            flat_list.sort(key=lambda x: x["categoria"], reverse=not sort_ascending)
        elif sort_column == "Produto":
            flat_list.sort(key=lambda x: x["produto"], reverse=not sort_ascending)
        elif sort_column == "Quantidade":
            flat_list.sort(key=lambda x: x["quantidade"], reverse=not sort_ascending)

        def sort_table(e):
            nonlocal sort_column, sort_ascending
            column_name = e.control.data
            if sort_column == column_name:
                sort_ascending = not sort_ascending
            else:
                sort_column = column_name
                sort_ascending = True
            table_container.content = products_list()
            table_container.update()

        columns = [
            ft.DataColumn(ft.ElevatedButton(text="Categoria", data="Categoria", on_click=sort_table, style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=5)))),
            ft.DataColumn(ft.ElevatedButton(text="Produto", data="Produto", on_click=sort_table, style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=5)))),
            ft.DataColumn(ft.ElevatedButton(text="Quantidade", data="Quantidade", on_click=sort_table, style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=5)))),
            ft.DataColumn(ft.Text("Editar")),
        ]

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
                                    ft.IconButton(
                                        icon=ft.Icons.ADD_CIRCLE_OUTLINE,
                                        icon_color="BLUE",
                                        icon_size=20,
                                        data={
                                            "categoria": item["categoria"],
                                            "produto": item["produto"],
                                        },  # Passa os dadosdo produto,
                                        on_click=update_add_quantity,
                                    ),
                                    ft.IconButton(
                                        icon=ft.Icons.DELETE,
                                        icon_color="Red",
                                        icon_size=20,
                                        data={
                                            "categoria": item["categoria"],
                                            "produto": item["produto"],
                                        },  # data - Passando os dados do produto
                                        on_click=open_dlg_modal,
                                    ),
                                ],
                                spacing=10,
                            )
                        ),
                    ]
                )
            )

        return ft.DataTable(
            columns=columns,
            rows=rows,
            border=ft.border.all(1, ft.colors.GREY_400),
            border_radius=10,
            column_spacing=get_spacing()
        )

    # Alert Dialog to delete buttom
    def open_dlg_modal(e):
        item_data = e.control.data
        dlg_modal = ft.AlertDialog(
            modal=True,
            title=ft.Text("Confirme:"),
            content=ft.Text(f"Certeza que deseja excluir {item_data['produto']}?"),
            actions=[
                ft.TextButton("Sim",
                    style=ft.ButtonStyle(color={"": ft.colors.RED}),
                    data=item_data, on_click=close_dlg_true),
                ft.TextButton(
                    "Não",
                    on_click=close_dlg_false,
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        page.dialog = dlg_modal  # Define o diálogo como o diálogo ativo da página
        page.add(dlg_modal)
        dlg_modal.open = True
        page.update()

    def close_dlg_true(e):
        nonlocal products, table_container
        item_data = e.control.data
        category = item_data["categoria"]
        product = item_data["produto"]

        if category in products and product in products[category]:
            del products[category][product]
            if not products[category]:
                del products[category]

        table_container.content = products_list()
        table_container.update()

        page.dialog.open = False  # Fecha o diálogo ativo
        page.update()

        page.overlay.append(
            ft.SnackBar(
                content=ft.Text(f"{product} removido com sucesso!"),
                open=True,
                bgcolor=ft.Colors.GREEN_400,
                duration=3000,
            )
        )
        page.update()

    def close_dlg_false(e):
        page.dialog.open = False  # Fecha o diálogo ativo
        page.update()

    def update_add_quantity(e):
        nonlocal products, table_container
        item_data = e.control.data  # Pega os dados do botão clicado
        category = item_data["categoria"]
        product = item_data["produto"]

        page.clean()
        page.add(topBar())
        importlib.reload(addQuantityPage)  # Recarrega o módulo para evitar cache
        add_quantity = addQuantityPage.AddQuantity(page, products, category, product)
        add_quantity.addMainPage()

    # funções dos buttons
    def update_add(e):
        nonlocal products
        page.clean()
        page.add(topBar())
        importlib.reload(addPage)
        add_page = addPage.AddPage(page, products)
        add_page.addMainPage()

    def update_used(e):
        nonlocal products
        page.clean()
        page.add(topBar())
        importlib.reload(usedPage)
        used_page = usedPage.UsedPage(page, products)
        used_page.addMainPage()

    def update_home(e):
        nonlocal search_text, sort_column, sort_ascending, table_container
        # Zera os filtros
        search_text = ""  # Limpa o texto de busca
        sort_column = None  # Remove a ordenação por coluna
        sort_ascending = True  # Reseta para ordem crescente
        # Recarrega a página principal
        page.clean()
        main_page()
        # Limpa o conteúdo do TextField visualmente
        for control in page.controls:
            if isinstance(control, ft.Container) and isinstance(control.content, ft.Column):
                for col_control in control.content.controls:
                    if isinstance(col_control, ft.Row):
                        for tf in col_control.controls:
                            if isinstance(tf, ft.TextField) and tf.hint_text == "Procure um produto":
                                tf.value = ""
                                break 
        page.update()

    def update_user(e):
        page.clean()
        page.add(topBar())
        importlib.reload(userPage)
        user_page = userPage.main(page)
        user_page

    # MAIN PAGE
    def main_page():
        nonlocal table_container
        page.add(topBar())
        table_container = ft.Container(content=products_list(), expand=True)
        main_content = ft.Container(
            content=ft.Column(
                controls=[
                    topButtons(),
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
                                on_change=update_search
                            )
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                    ),
                    table_container
                ],
                alignment=ft.MainAxisAlignment.START,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=20
            ),
            padding=ft.Padding(left=20, right=20, top=10, bottom=0)
        )
        page.add(main_content)
        page.update()

    def update_search(e):
        nonlocal search_text, table_container
        search_text = e.control.value.strip()  # Usa strip() para garantir que espaços não interfiram
        if table_container:
            table_container.content = products_list()
            table_container.update()

    # Iniciar a página principal
    main_page()
