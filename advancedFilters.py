import platform
import flet as ft
import datetime
import pytz
import sqlite3
import os
from fpdf import FPDF

def main(page: ft.Page):
    page.scroll = "adaptive"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    
    # Definir largura das colunas
    col_width_cat = 40
    col_width_prod = 65
    col_before_after = 20
    col_width_date = 45
    
    # Função para determinar o spacing da DataTable
    def get_spacing():
        if page.window.width <= 425:  # Celulares menores
            return 10
        return 40  # Padrão para telas maiores
    
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
        border=ft.border.all(1, ft.Colors.GREY_500),
        heading_row_color=ft.Colors.BLUE_300,
        column_spacing=get_spacing(),
    )
    
    # Container principal com padding fixo
    content_container = ft.Container(
        content=data_table,  # Iniciar com a tabela vazia
        expand=True,
        padding=ft.padding.all(10),  # Padding consistente
    )
    
    # Função para converter data dd/mm/yyyy para YYYY-MM-DD
    def parse_date(date_str):
        if date_str:
            day, month, year = map(int, date_str.split('/'))
            return f"{year}-{month:02d}-{day:02d}"
        return None
    
    # Classe PDF personalizada
    class CustomPDF(FPDF):
        def header(self):
            self.set_y(0)
            try:
                self.image("images/ready-stock.png", x=87, y=1, w=8, h=8)
            except:  # noqa: E722
                self.cell(0, 10, "Imagem não encontrada", align="C", ln=1)
            self.cell(0, 10, "StockApp", align="C", border=0, ln=1)
            self.ln(5)

        def footer(self):
            self.set_y(-10)
            self.set_x(-10)
            page_number = self.page_no()
            self.cell(w=5, h=10, txt=str(page_number), border=0)
    
    # Função para gerar o PDF
    def generate_pdf(results):
        pdf = CustomPDF("P", "mm", "A4")
        pdf.set_font("Arial", "", 12)
        pdf.add_page()

        pdf.set_font("Arial", "B", 12)
        pdf.cell(w=0, h=10, txt="Produtos alterados", border=0, ln=1)
        pdf.set_fill_color(126, 195, 222)
        pdf.cell(col_width_date, 7, "Data", border=1, fill=True)
        pdf.cell(col_width_cat, 7, "Categoria", border=1, fill=True)
        pdf.cell(col_width_prod, 7, "Produtos", border=1, fill=True)
        pdf.cell(col_before_after, 7, "Antes", border=1, fill=True)
        pdf.cell(col_before_after, 7, "Depois", border=1, fill=True)
        pdf.ln()

        pdf.set_font("Arial", "", 12)
        
        if not results:
            pdf.set_text_color(255, 0, 0)
            pdf.cell(0, 7, "Nenhum dado encontrado para o filtro de data selecionada", border=1)
            pdf.set_text_color(0, 0, 0)
        else:
            for product in results:
                pdf.set_text_color(0, 0, 0)
                pdf.cell(col_width_date, 7, str(product[4]), border=1)
                pdf.cell(col_width_cat, 7, str(product[0]), border=1)
                pdf.cell(col_width_prod, 7, str(product[1]), border=1)
                pdf.cell(col_before_after, 7, str(product[2]), border=1)
                pdf.cell(col_before_after, 7, str(product[3]), border=1)
                pdf.ln()
        
        # Dentro de generate_pdf, substitua a parte do file_name e pdf.output
        current_hour = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        file_name = f"stock-relatorio_{current_hour}.pdf"
        pdf_folder = "pdf"
        os.makedirs(pdf_folder, exist_ok=True)  # Cria a pasta /pdf se não existir
        full_path = os.path.join(pdf_folder, file_name)
        pdf.output(full_path)
        
        try:
            if platform.system() == "Windows":
                os.startfile(full_path)
            elif platform.system() == "Darwin":
                os.system(f"open {full_path}")
            else:
                os.system(f"xdg-open {full_path}")
        except Exception as e:
            page.overlay.append(
                ft.SnackBar(
                    content=ft.Text(f"Erro ao abrir o PDF: {str(e)}"),
                    open=True,
                    bgcolor=ft.Colors.RED_400,
                    duration=3000,
                )
            )
            
        page.overlay.append(
            ft.SnackBar(
                content=ft.Text(f"PDF salvo como '{file_name}'"),
                open=True,
                bgcolor=ft.Colors.GREEN_400,
                duration=2000,
            )
        )
        page.update()

    def join_tables(filter="all", start_date=None, end_date=None):
        con = sqlite3.connect("tb_products.db")
        cursor = con.cursor()

        query = """
            SELECT p.category, p.product, h.quantity_before, h.quantity_after,
            strftime('%d/%m/%Y %H:%M:%S', h.data_modify) as data_formatada
            FROM products AS p
            INNER JOIN quantity_history AS h
            ON p.id_prod = h.prod_hist
        """

        if filter == "hoje":
            query += " WHERE DATE(h.data_modify) = DATE('now')"
        elif filter == "semana":
            query += " WHERE DATE(h.data_modify) >= DATE('now', '-7 days')"
        elif filter == "mes":
            query += " WHERE strftime('%Y-%m', h.data_modify) = strftime('%Y-%m', 'now')"
        elif filter == "mes_anterior":
            now = datetime.datetime.now(pytz.utc)
            first_day_current_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            last_day_previous_month = first_day_current_month - datetime.timedelta(days=1)
            first_day_previous_month = last_day_previous_month.replace(day=1)
            query += f" WHERE h.data_modify BETWEEN '{first_day_previous_month.strftime('%Y-%m-%d')}' AND '{last_day_previous_month.strftime('%Y-%m-%d')}'"
        elif filter == "personalizado" and start_date and end_date:
            query += f" WHERE DATE(h.data_modify) BETWEEN '{parse_date(start_date)}' AND '{parse_date(end_date)}'"

        query += " ORDER BY h.data_modify DESC;"

        cursor.execute(query)
        results = cursor.fetchall()
        con.close()

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
        return results
    
    # Variável para rastrear o filtro ativo
    current_filter = "hoje"  # Filtro padrão
    last_results = []

    # FILTER POPUP
    def pop_up_menu():
        nonlocal current_filter
        pb = ft.PopupMenuButton(
            icon=ft.Icons.FILTER_ALT_OUTLINED,
            style=ft.ButtonStyle(icon_size=30, shape=ft.RoundedRectangleBorder(radius=10)),
            items=[
                ft.PopupMenuItem(text="Filtrar por:", disabled=True),
                ft.PopupMenuItem(icon=ft.Icons.CALENDAR_TODAY_OUTLINED, text="hoje", on_click=lambda _: set_filter("hoje")),
                ft.PopupMenuItem(icon=ft.Icons.CALENDAR_VIEW_WEEK_OUTLINED, text="semana", on_click=lambda _: set_filter("semana")),
                ft.PopupMenuItem(icon=ft.Icons.CALENDAR_MONTH_OUTLINED, text="mes atual", on_click=lambda _: set_filter("mes")),
                ft.PopupMenuItem(icon=ft.Icons.CALENDAR_MONTH_ROUNDED, text="mes anterior", on_click=lambda _: set_filter("mes_anterior")),
            ]
        )
        return pb
    
    def set_filter(filter, start_date=None, end_date=None):
        nonlocal current_filter, last_results
        current_filter = filter
        if filter == "personalizado" and start_date and end_date:
            last_results = join_tables(filter, start_date, end_date)
        else:
            last_results = join_tables(filter)

    # DATE PICKER
    sao_paulo_tz = pytz.timezone("America/Sao_Paulo")

    def format_date(date):
        if date:
            return date.strftime("%d/%m/%Y")
        return ""

    def get_current_date():
        return datetime.datetime.now(sao_paulo_tz)

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

    initial_date_picker_dialog = ft.DatePicker(
        first_date=datetime.datetime(2020, 1, 1, tzinfo=sao_paulo_tz),
        last_date=datetime.datetime(2030, 1, 1, tzinfo=sao_paulo_tz),
        cancel_text="Cancelar",
        confirm_text="Confirmar",
        value=get_current_date(),
        on_change=handle_change,
        on_dismiss=handle_dismissal,
    )
    
    final_date_picker_dialog = ft.DatePicker(
        first_date=datetime.datetime(2020, 1, 1, tzinfo=sao_paulo_tz),
        last_date=datetime.datetime(2034, 1, 1, tzinfo=sao_paulo_tz),
        cancel_text="Cancelar",
        confirm_text="Confirmar",
        value=get_current_date(),
        on_change=handle_change_final,
        on_dismiss=handle_dismissal,
    )

    page.overlay.append(initial_date_picker_dialog)
    page.overlay.append(final_date_picker_dialog)

    initial_date_picker = ft.IconButton(
        icon=ft.Icons.CALENDAR_MONTH_OUTLINED,
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10)),
        on_click=lambda e: page.open(initial_date_picker_dialog),
    )
    
    final_date_picker = ft.IconButton(
        icon=ft.Icons.CALENDAR_MONTH_OUTLINED,
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10)),
        on_click=lambda e: page.open(final_date_picker_dialog),
    )

    initial_date_field = ft.TextField(
        value=format_date(get_current_date()),
        width=120,
        height=40,
        text_align=ft.TextAlign.CENTER,
        read_only=True,
    )
    
    final_date_field = ft.TextField(
        value=format_date(get_current_date()),
        width=120,
        height=40,
        text_align=ft.TextAlign.CENTER,
        read_only=True,
    )
    
    confirm_personalized_filter_btn = ft.ElevatedButton(
        text="Filtrar",
        width=80,
        height=40,
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10)),
        on_click=lambda _: set_filter("personalizado", initial_date_field.value, final_date_field.value)
    )
    
    def update_and_save_pdf(e):
        nonlocal last_results
        if current_filter == "personalizado":
            last_results = join_tables("personalizado", initial_date_field.value, final_date_field.value)
        else:
            last_results = join_tables(current_filter)
        generate_pdf(last_results)

    download_pdf_btn = ft.IconButton(
        icon=ft.Icons.FILE_DOWNLOAD_OUTLINED,
        icon_color=ft.Colors.RED_300,
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10)),
        on_click=update_and_save_pdf
    )

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
        spacing=3,
    )

    main_content = ft.Container(
        content=ft.Column(
            controls=[
                ft.Row(
                    controls=[
                        pop_up_menu(),
                        ft.Container(padding=ft.padding.only(right=10, left=50)),
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
        padding=ft.padding.only(left=0, right=0, top=15, bottom=0)
    )
    
    page.add(main_content)
    last_results = join_tables("semana")

#ft.app(target=main)