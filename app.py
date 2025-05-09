import flet as ft
import addPage
import advancedFilters
import usedPage
import importlib
import userPage
import addQuantityPage
import appVersionUpdate
import sqlite3

def main(page: ft.Page, database_name):

    user_db = database_name
    # Configurações iniciais da página
    page.scroll = "adaptive"
    page.title = "Stock App"
    page.theme_mode = ft.ThemeMode.LIGHT

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
    
    search_text = ft.TextField(label="Pesquisar produto...", on_change=lambda e: update_table())
    sort_column = None
    sort_ascending = True

    page.padding = ft.Padding(left=0, right=0, top=0, bottom=0)
    table_container = None  # Referência ao container da tabela

    # Mudar o tema
    def change_theme(e):
        if page.theme_mode == ft.ThemeMode.LIGHT:
            page.theme_mode = ft.ThemeMode.DARK
            print('Escuro')
        else:
            page.theme_mode = ft.ThemeMode.LIGHT
            print('Claro')
        page.update()

    # Mudar a cor da fonte
    def color_font_change():
        if page.theme_mode == ft.ThemeMode.LIGHT:
            return ft.Colors.BLUE_900
        else: 
            return ft.Colors.GREY_100

    # Barra superior
    def topBar():
        home_icon = ft.Container(
            content=ft.TextButton(
                content=ft.Row(
                    controls=[
                        ft.Icon(ft.icons.HOME_OUTLINED, size=30, color="GREEN"),
                        ft.Text("HOME", size=12, color=color_font_change),
                    ],
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=5,
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
                        ft.Text("USER", size=12, color=color_font_change),
                    ],
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=5,
                ),
                on_click=update_user,
            ),
            padding=ft.Padding(left=5, right=0, top=10, bottom=0),
        )

        changeTheme_icon = ft.Container(
            content=ft.TextButton(
                content=ft.Row(
                    controls=[
                        ft.Icon(ft.icons.LIGHTBULB_OUTLINE, size=22),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    spacing=5,
                ),
                on_click=change_theme,
            ),
            padding=ft.Padding(left=0, right=15, top=10, bottom=0),
        )

        exit_icon = ft.Container(
            content=ft.TextButton(
                content=ft.Row(
                    controls=[
                        ft.Icon(ft.icons.EXIT_TO_APP, size=22, color="GREY_200"),
                        ft.Text("EXIT", size=12, color=color_font_change),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    spacing=5,
                ),
                on_click=lambda e: page.window.close()
            ),
            padding=ft.Padding(left=0, right=15, top=10, bottom=0),
        )
        
        update_icon = ft.Container(
            content=ft.TextButton(
                content=ft.Row(
                    controls=[
                        ft.Icon(ft.icons.UPDATE_OUTLINED, size=22, color="GREY_200"),
                        ft.Text("", size=12, color=color_font_change),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    spacing=5,
                ),
                on_click=update_version
            ),
            padding=ft.Padding(left=0, right=15, top=10, bottom=0),
        )

        top_bar_content = ft.Container(
            content=ft.Row(
                controls=[
                    ft.Row(
                        controls=[home_icon, user_icon, changeTheme_icon, update_icon],
                        spacing=20
                    ),
                    exit_icon
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
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
            color=color_font_change,
            width=110,
            height=30,
            icon=ft.Icons.ADD_BOX_OUTLINED,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=10),
                overlay_color=ft.Colors.GREEN_200,
            ),
            on_click=update_add,
        )
        
        analyticsButton = ft.ElevatedButton(
            text="Relatório",
            color=color_font_change,
            width=110,
            height=30,
            icon=ft.Icons.ANALYTICS_OUTLINED,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=10),
                overlay_color=ft.Colors.PURPLE_200),
            on_click=update_analytics
        )
        
        productsUsedButton = ft.ElevatedButton(
            text="Usados",
            color=color_font_change,
            width=110,
            height=30,
            icon=ft.Icons.CHECK,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=10),
                overlay_color=ft.Colors.YELLOW_200),
            on_click=update_used
        )
        row = ft.Row(
            controls=[addButton, productsUsedButton, analyticsButton],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=5,
        )
        return row

    # Função para buscar dados do banco de dados
    def get_data(search_text="", sort_column=None, sort_ascending=True):
        conexao = sqlite3.connect(user_db)
        cursor = conexao.cursor()
        
        query = "SELECT category, product, quantity FROM products"
        params = []
        
        if search_text:
            query += " WHERE (category LIKE ? OR product LIKE ?)"
            params.extend([f"%{search_text}%", f"%{search_text}%"])
        
        if sort_column:
            query += f" ORDER BY {sort_column} {'ASC' if sort_ascending else 'DESC'}"
        
        cursor.execute(query, params)
        tb_data = cursor.fetchall()
        
        conexao.close()
        return tb_data
    
    data_table = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("Categoria"), on_sort=lambda e: order_table("category")),
            ft.DataColumn(ft.Text("Produto"), on_sort=lambda e: order_table("product")),
            ft.DataColumn(ft.Text("Quantidade"), on_sort=lambda e: order_table("quantity")),
            ft.DataColumn(ft.Text("Ações", color=ft.Colors.GREEN_400)),
        ],
        rows=[],
        border=ft.border.all(1, ft.Colors.GREY_500),
        border_radius=10,
        column_spacing=get_spacing()
    )
    
    # Atualiza a tabela com base no filtro de pesquisa e ordenação
    def update_table():
        nonlocal data_table
        data_table.rows.clear()
        
        dados = get_data(search_text.value, sort_column, sort_ascending)
        
        for category, product, quantity in dados:
            data_table.rows.append(
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
                                        icon_color=ft.Colors.BLUE_400,
                                        icon_size=20,
                                        data={"category": category, "product": product},
                                        on_click=update_add_quantity,
                                    ),
                                    ft.IconButton(
                                        icon=ft.icons.DELETE_OUTLINED,
                                        icon_color=ft.Colors.RED_400,
                                        icon_size=20,
                                        data={"category": category, "product": product},
                                        on_click=open_dlg_modal,
                                    ),
                                ],
                                spacing=10,
                            )
                        ),
                    ]
                )
            )
        # Só atualiza o table_container se ele já estiver na página
        if table_container and table_container in page.controls:
            table_container.content = data_table
            table_container.update()
        page.update()

    # Ordenar a tabela quando um cabeçalho for clicado
    def order_table(db_column):
        nonlocal sort_column, sort_ascending
        if sort_column == db_column:
            sort_ascending = not sort_ascending
        else:
            sort_column = db_column
            sort_ascending = True
        update_table()

    # Alert Dialog para exclusão
    def open_dlg_modal(e):
        item_data = e.control.data
        dlg_modal = ft.AlertDialog(
            modal=True,
            title=ft.Text("Confirme:"),
            content=ft.Text(f"Certeza que deseja excluir {item_data['product']}?"),
            actions=[
                ft.TextButton("Sim",
                    style=ft.ButtonStyle(color={"": ft.Colors.RED}),
                    data=item_data, on_click=close_dlg_true),
                ft.TextButton("Não", on_click=close_dlg_false),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        page.dialog = dlg_modal
        page.add(dlg_modal)
        dlg_modal.open = True
        page.update()

    def close_dlg_true(e):
        nonlocal data_table
        item_data = e.control.data
        category = item_data["category"]
        product = item_data["product"]
        
        conexao = sqlite3.connect(user_db)
        cursor = conexao.cursor()
        cursor.execute("DELETE FROM products WHERE category = ? AND product = ?", (category, product))
        conexao.commit()
        conexao.close()
        
        update_table()
        page.dialog.open = False
        page.update()
        
        page.overlay.append(
            ft.SnackBar(
                content=ft.Text(f"{product} removido com sucesso!"),
                open=True,
                bgcolor=ft.Colors.GREEN_400,
                duration=1000,
            )
        )
        page.update()

    def close_dlg_false(e):
        page.dialog.open = False
        page.update()

    def update_add_quantity(e):
        nonlocal data_table
        item_data = e.control.data
        category = item_data["category"]
        product = item_data["product"]

        page.clean()
        page.add(topBar())
        add_quantity = addQuantityPage.AddQuantity(page, data_table, category, product, database_name)
        add_quantity.addMainPage()

    # Funções dos botões
    def update_add(e):
        nonlocal data_table
        page.clean()
        page.add(topBar())
        importlib.reload(addPage)
        add_page = addPage.AddPage(page, data_table, database_name)
        add_page.addMainPage()

    def update_used(e):
        nonlocal data_table
        page.clean()
        page.add(topBar())
        importlib.reload(usedPage)
        used_page = usedPage.UsedPage(page, data_table, database_name)
        used_page.addMainPage()
        
    def update_analytics(e):
        page.clean()
        page.add(topBar())
        analytics = advancedFilters.main(page, database_name)
        analytics

    def update_home(e):
        nonlocal search_text, sort_column, sort_ascending, table_container
        search_text.value = ""  # Limpa o texto de busca
        sort_column = None
        sort_ascending = True
        page.clean()
        main_page()
        page.update()

    def update_user(e):
        page.clean()
        page.add(topBar())
        importlib.reload(userPage)
        user_page = userPage.main(page)
        user_page
        
    def update_version(e):
        appVersionUpdate.open_dlg_modal(page)

    # MAIN PAGE
    def main_page():
        nonlocal table_container
        page.add(topBar())
        
        table_container = ft.Container(content=data_table, expand=True)
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
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                    ),
                    table_container
                ],
                alignment=ft.MainAxisAlignment.START,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=20
            ),
            padding=ft.Padding(left=20, right=20, top=10, bottom=15)
        )
        page.add(main_content)
        update_table()  # Chama depois de adicionar à página
        
    def update_search(e):
        nonlocal search_text
        search_text.value = e.control.value.strip()
        update_table()

    # Iniciar a página principal
    main_page()
    
#ft.app(target=main)
