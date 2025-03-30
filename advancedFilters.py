import flet as ft
import datetime
import pytz
import sqlite3

def main(page: ft.Page):
    page.scroll = "adaptive"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.theme_mode = ft.ThemeMode.LIGHT
    
    # Função para determinar o spacing da DataTable
    def get_spacing():
        if page.window.width <= 425:  # Celulares menores
            return 11
        return 60  # Padrão para telas maiores
    
    # Colunas para as tabelas
    data_table = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("Data")),
            ft.DataColumn(ft.Text("Categoria")),
            ft.DataColumn(ft.Text("Produto")),
            ft.DataColumn(ft.Text("Antes")),
            ft.DataColumn(ft.Text("Depois")),
        ],
        rows=[],
        border=ft.border.all(1, ft.colors.GREY_500),
        heading_row_color=ft.Colors.BLUE_300,
        #vertical_lines=ft.border.BorderSide(1, ft.colors.GREY_500),
        #border_radius=10,
        column_spacing=get_spacing(),
    )
    
    # Container principal que será atualizado dinamicamente
    content_container = ft.Container(expand=True)
    
    # Função para converter data dd/mm/yyyy para YYYY-MM-DD
    def parse_date(date_str):
        if date_str:
            day, month, year = map(int, date_str.split('/'))
            return f"{year}-{month:02d}-{day:02d}"
        return None

    def join_tables(filter="all", start_date=None, end_date=None, month=None, year=None):
        con = sqlite3.connect("tb_products.db")
        cursor = con.cursor()

        # Construindo a query base
        query = """
            SELECT p.category, p.product, h.quantity_before, h.quantity_after,
            strftime('%d/%m/%Y %H:%M:%S', h.data_modify) as data_formatada
            FROM products AS p
            INNER JOIN quantity_history AS h
            ON p.id_prod = h.prod_hist
        """

        # Adicionando filtros dinâmicos de data
        if filter == "hoje":
            query += " WHERE DATE(h.data_modify) = DATE('now')"
        elif filter == "semana":
            query += " WHERE DATE(h.data_modify) >= DATE('now', '-7 days')"
        elif filter == "mes":
            query += " WHERE strftime('%Y-%m', h.data_modify) = strftime('%Y-%m', 'now')"
        elif filter == "mes_anterior":
            query += " WHERE strftime('%Y-%m', h.data_modify) = strftime('%Y-%m', 'now', '-1 month')"
        elif filter == "personalizado" and start_date and end_date:
            # Filtro entre duas datas
            query += f" WHERE DATE(h.data_modify) BETWEEN '{parse_date(start_date)}' AND '{parse_date(end_date)}'"

        query += " ORDER BY h.data_modify DESC;"  # Ordenação por data mais recente primeiro

        # Executar a query
        cursor.execute(query)
        results = cursor.fetchall()
        con.close()

        # Limpar as linhas atuais da tabela
        data_table.rows.clear()
        
        if not results:
            content_container.content = ft.Text(
                "Nenhum dado encontrado para o filtro de data selecionado.\nTente selecionar outro filtro.",
                color="RED",
                text_align=ft.TextAlign.CENTER
            )
        else:
            for product in results:
                data_table.rows.append(
                    ft.DataRow(
                        cells=[
                            ft.DataCell(ft.Text(product[4])),
                            ft.DataCell(ft.Text(product[0])),
                            ft.DataCell(ft.Text(product[1])),
                            ft.DataCell(ft.Text(product[2])),
                            ft.DataCell(ft.Text(product[3])),
                        ]
                    )
                )
            content_container.content = data_table
        page.update()
    
    def pop_up_menu():

        pb = ft.PopupMenuButton(
            icon=ft.Icons.FILTER_ALT_OUTLINED,
            style=ft.ButtonStyle(icon_size=30,  shape=ft.RoundedRectangleBorder(radius=10)),
            items=[
                ft.PopupMenuItem(text="Filtrar por:", disabled=True),
                ft.PopupMenuItem(icon=ft.Icons.CALENDAR_TODAY_OUTLINED, text="hoje", on_click=lambda _: join_tables("hoje")),
                ft.PopupMenuItem(icon=ft.Icons.CALENDAR_VIEW_WEEK_OUTLINED, text="semana", on_click=lambda _: join_tables("semana")),
                ft.PopupMenuItem(icon=ft.Icons.CALENDAR_MONTH_OUTLINED, text="mes atual", on_click=lambda _: join_tables("mes")),
                ft.PopupMenuItem(icon=ft.Icons.CALENDAR_MONTH_ROUNDED, text="mes anterior", on_click=lambda _: join_tables("mes_anterior")),
            ]
        )
        return pb
    
    # DATE PICKER
    # Definir o timezone de São Paulo
    sao_paulo_tz = pytz.timezone("America/Sao_Paulo")

    # Função para formatar a data no padrão brasileiro
    def format_date(date):
        if date:
            return date.strftime("%d/%m/%Y")
        return ""

    # Função para obter a data atual em São Paulo
    def get_current_date():
        return datetime.datetime.now(sao_paulo_tz)

    # Função de callback para atualizar o TextField com a data selecionada
    def handle_change(e):
        selected_date = e.control.value
        if selected_date:
            initial_date_field.value = format_date(selected_date)
        page.update()
        
    def handle_change_final(e):
        selected_date = e.control.value
        if selected_date:
            final_date_field.value = format_date(selected_date)
        page.update()

    def handle_dismissal(e):
        page.update()

    # DatePicker
    initial_date_picker_dialog = ft.DatePicker(
        first_date=datetime.datetime(2025, 1, 1, tzinfo=sao_paulo_tz),
        last_date=datetime.datetime(2030, 1, 1, tzinfo=sao_paulo_tz),
        cancel_text="Cancelar",
        confirm_text="Confirmar",
        value=get_current_date(),  # Data inicial padrão é a atual
        on_change=handle_change,
        on_dismiss=handle_dismissal,
    )
    
    final_date_picker_dialog = ft.DatePicker(
        first_date=datetime.datetime(2025, 1, 1, tzinfo=sao_paulo_tz),
        last_date=datetime.datetime(2030, 1, 1, tzinfo=sao_paulo_tz),
        cancel_text="Cancelar",
        confirm_text="Confirmar",
        value=get_current_date(),  # Data inicial padrão é a atual
        on_change=handle_change_final,
        on_dismiss=handle_dismissal,
    )

    # Adicionar o DatePicker ao overlay
    page.overlay.append(initial_date_picker_dialog)
    page.overlay.append(final_date_picker_dialog)

    # IconButton que abre o DatePicker
    initial_date_picker = ft.IconButton(
        icon=ft.Icons.CALENDAR_MONTH_OUTLINED,
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=10)
        ),
        on_click=lambda e: page.open(initial_date_picker_dialog),  # Abre o DatePicker
    )
    
    final_date_picker = ft.IconButton(
        icon=ft.Icons.CALENDAR_MONTH_OUTLINED,
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=10)
        ),
        on_click=lambda e: page.open(final_date_picker_dialog),  # Abre o DatePicker
    )

    # Criar o TextField que exibirá a data selecionada
    initial_date_field = ft.TextField(
        value=format_date(get_current_date()),  # Valor inicial é a data atual
        width=120,
        height=40,
        text_align=ft.TextAlign.CENTER,
        read_only=True,  # Impede edição manual
    )
    
    # TextField que exibirá a data selecionada
    final_date_field = ft.TextField(
        value=format_date(get_current_date()),  # Valor inicial é a data atual
        width=120,
        height=40,
        text_align=ft.TextAlign.CENTER,
        read_only=True,  # Impede edição manual
    )
    
    confirm_personalized_filter_btn = ft.ElevatedButton(
                text="Filtrar",
                width=80,
                height=40,
                style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=10),
                ),
                on_click=lambda _: join_tables("personalizado", initial_date_field.value, final_date_field.value)
            )
    
    download_pdf_btn = ft.IconButton(
        icon=ft.Icons.FILE_OPEN_OUTLINED,
        icon_color=ft.Colors.RED_300,
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=10)
        ),
        on_click=lambda x: print("Abrir documento em pdf")
    )

    # Organizar o IconButton e o TextField em uma Row
    date_row = ft.Row(
        controls=[
            initial_date_picker,
            initial_date_field,
            final_date_picker,
            final_date_field,
            ft.Container(padding=ft.padding.only(left=5)),
            confirm_personalized_filter_btn,
            ft.Container(padding=ft.padding.only(left=10)),
            download_pdf_btn
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        spacing=3,  # Espaço entre o botão e o campo
    )

    main_content = ft.Container(
        content=ft.Column(
            controls=[
                ft.Row(
                    controls=[
                        pop_up_menu(),
                        ft.Container(padding=ft.padding.only(right=50, left=50)),
                        date_row,
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                content_container
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        padding=ft.Padding(left=0, right=0, top=10, bottom=0)
    )
    
    page.add(main_content)

    # Chamar a função para preencher a tabela com dados da semana
    join_tables("semana")
    
#ft.app(target=main)