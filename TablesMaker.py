from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Spacer

class TablesMaker:
    def __init__(self, singleProducts, multiProducts, ordersMultiProduct, outputPath):
        self.singleProducts = singleProducts
        self.multiProducts = multiProducts
        self.ordersMultiProduct = ordersMultiProduct
        self.outputPath = outputPath
        
    def create_pdf_with_tables(self):
            doc = SimpleDocTemplate(self.outputPath + 'tabelle.pdf', pagesize=letter)
            elements = []

            # Creazione delle tabelle per i singoli prodotti, prodotti multipli e ordini multi-prodotto
            singleTableData = [['Single-Packaging', 'Quantità']]
            for order in self.singleProducts:
                singleTableData.append([order[0], order[1]])
            singleTable = self.create_table(singleTableData)
            elements.append(singleTable)
            elements.append(Spacer(1, 0.5 * inch))

            multiTableData = [['Multi-Packaging', 'Quantità', 'Unità']]
            for order in self.multiProducts:
                multiTableData.append([order[1], order[0], order[2]])
            multiTable = self.create_table(multiTableData)
            elements.append(multiTable)
            elements.append(Spacer(1, 0.5 * inch))

            ordersMultiTableData = [['Orders-Multi-Product', 'Quantità']]
            for order in self.ordersMultiProduct:
                for item in order:
                    ordersMultiTableData.append([item[1], item[2]])
                ordersMultiTableData.append(['Pacco'])
            ordersMultiTable = self.create_table(ordersMultiTableData)
            elements.append(ordersMultiTable)

            # Salvataggio del PDF
            doc.build(elements)

    # Funzione per creare una tabella da una lista di dati
    def create_table(self, data):
        table = Table(data)
        style = TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                            ('GRID', (0, 0), (-1, -1), 1, colors.black)])
        table.setStyle(style)
        return table