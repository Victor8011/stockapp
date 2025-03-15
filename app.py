import flet as ft
import addPage
import usedPage
import importlib
import userPage

def main(page: ft.Page):
    # Configurações iniciais da página
    page.scroll = "adaptive"
    page.title = "Stock App"
    page.vertical_alignment = ft.MainAxisAlignment.START
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.window.min_width = 620
    page.window.min_height = 620
    page.window.max_width = 620
    page.window.max_height = 1080

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
            content=ft.Icon(name=ft.Icons.HOME, size=30, color=ft.colors.WHITE),
            padding=ft.Padding(left=50, right=0, top=0, bottom=0),
            on_click=update_home
        )
        user_icon = ft.Container(
            content=ft.Icon(name=ft.Icons.PERSON, size=30, color=ft.colors.WHITE),
            padding=ft.Padding(left=0, right=50, top=0, bottom=0),
            on_click=update_user
        )
        top_bar_content = ft.Row(
            controls=[home_icon, user_icon],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            expand=True,
        )
        top_bar = ft.Container(
            content=top_bar_content,
            bgcolor=ft.colors.BLUE_300,
            height=40,
        )
        return top_bar

    # Botões do topo: Adicionar e Usados
    def topButtons():
        addButton = ft.ElevatedButton(
            text="Adicionar",
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
            ft.DataColumn(ft.Text("Ações", weight=ft.FontWeight.BOLD)),
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
                                    ft.IconButton(icon=ft.Icons.EDIT, icon_color="Blue"),
                                    ft.IconButton(icon=ft.Icons.DELETE, icon_color="Red", data={"categoria": item["categoria"], "produto": item["produto"]},  # data - Passando os dados do produto
                                        on_click=open_dlg_modal)
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
            border=ft.border.all(1, ft.colors.GREY_400),
            border_radius=10,
            column_spacing=50
        )

    # Alert Dialog
    def open_dlg_modal(e):
        item_data = e.control.data
        dlg_modal = ft.AlertDialog(
            modal=True,
            title=ft.Text("Confirme:"),
            content=ft.Text(f"Certeza que deseja excluir {item_data['produto']}?"),
            actions=[
                ft.TextButton("Sim", data=item_data, on_click=close_dlg_true),
                ft.TextButton(
                    "Não",
                    style=ft.ButtonStyle(color={"": ft.colors.RED}),
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
            if isinstance(control, ft.Container):
                for col in control.content.controls:
                    if isinstance(col, ft.Row):
                        for tf in col.controls:
                            if isinstance(tf, ft.TextField) and tf.hint_text == "Procure um produto":
                                tf.value = ""
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

ft.app(target=main, assets_dir='assets')
