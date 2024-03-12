from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Spacer


class TablesMaker:
    def __init__(self, single_products, multi_products, orders_multi_product, output_path):
        self.single_products = single_products
        self.multi_products = multi_products
        self.orders_multi_product = orders_multi_product
        self.output_path = output_path

    def create_pdf_with_tables(self):
        doc = SimpleDocTemplate(self.output_path + "tabelle.pdf", pagesize=letter)
        elements = []

        # Creazione delle tabelle per i singoli prodotti, prodotti multipli e ordini multi-prodotto
        single_table_data = [["Single-Packaging", "Quantità"]]
        for order in self.single_products:
            single_table_data.append([order[0], order[1]])
        single_table = self.create_table(single_table_data)
        elements.append(single_table)
        elements.append(Spacer(1, 0.5 * inch))

        multi_table_data = [["Multi-Packaging", "Quantità", "Unità"]]
        for order in self.multi_products:
            multi_table_data.append([order[1], order[0], order[2]])
        multi_table = self.create_table(multi_table_data)
        elements.append(multi_table)
        elements.append(Spacer(1, 0.5 * inch))

        orders_multi_table_data = [["Orders-Multi-Product", "Quantità"]]
        for order in self.orders_multi_product:
            for item in order:
                orders_multi_table_data.append([item[1], item[2]])
            orders_multi_table_data.append(["Pacco"])
        orders_multi_table = self.create_table(orders_multi_table_data)
        elements.append(orders_multi_table)

        # Salvataggio del PDF
        doc.build(elements)

    # Funzione per creare una tabella da una lista di dati
    def create_table(self, data):
        table = Table(data)
        style = TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
                ("GRID", (0, 0), (-1, -1), 1, colors.black),
            ]
        )
        table.setStyle(style)
        return table
