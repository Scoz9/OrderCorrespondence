import fitz  # PyMuPDF
import tkinter as tk
from tkinter import filedialog, messagebox
import os
import time
import re

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Spacer

class Gui:
    def __init__(self):
        self.pdf1_path = ""
        self.pdf2_path = ""
        self.output_path = ""

    def avvia_interfaccia(self):
        self.root = tk.Tk()
        self.root.title("PDF Analyzer")

        self.label1 = tk.Label(self.root, text="PDF 1:")
        self.label1.grid(row=0, column=0)

        self.pdf1_entry = tk.Entry(self.root, width=50)
        self.pdf1_entry.grid(row=0, column=1)

        self.browse_button1 = tk.Button(
            self.root, text="Browse", command=self.browse_pdf1
        )
        self.browse_button1.grid(row=0, column=2)

        self.label2 = tk.Label(self.root, text="PDF 2:")
        self.label2.grid(row=1, column=0)

        self.pdf2_entry = tk.Entry(self.root, width=50)
        self.pdf2_entry.grid(row=1, column=1)

        self.browse_button2 = tk.Button(
            self.root, text="Browse", command=self.browse_pdf2
        )
        self.browse_button2.grid(row=1, column=2)

        """ self.label3 = tk.Label(self.root, text="Output Path:")
        self.label3.grid(row=2, column=0)

        self.output_path_entry = tk.Entry(self.root, width=50)
        self.output_path_entry.grid(row=2, column=1)

        self.browse_button3 = tk.Button(
            self.root, text="Browse", command=self.browse_output_path
        )
        self.browse_button3.grid(row=2, column=2) """
        
        self.generatePdf = tk.Button(
            self.root, text="generate pdf"
        )
        self.generatePdf.grid(row=3, column=1)

        self.button_frame = tk.Frame(self.root)
        self.button_frame.grid(row=3, column=0, columnspan=3)
        
        self.generate_button = tk.Button(
        self.button_frame, text="PDF", command=self.generate_pdf)
        self.generate_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.elaborate_button = tk.Button(
        self.button_frame, text="Elaborate", command=self.elaborate_pdfs)
        self.elaborate_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.time_label = tk.Label(self.root, text="Time: 0:00")
        self.time_label.grid(row=4, column=1)

        self.root.mainloop()

    def browse_pdf1(self):
        filename = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
        self.pdf1_entry.delete(0, tk.END)
        self.pdf1_entry.insert(0, filename)
        self.pdf1_path = self.pdf1_entry.get()
        self.output_path = os.path.dirname(self.pdf1_path) + '/'

    def browse_pdf2(self):
        filename = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
        self.pdf2_entry.delete(0, tk.END)
        self.pdf2_entry.insert(0, filename)
        self.pdf2_path = self.pdf2_entry.get()

    """ def browse_output_path(self):
        path = filedialog.askdirectory()
        self.output_path_entry.delete(0, tk.END)
        self.output_path_entry.insert(0, path)
        self.output_path = self.output_path_entry.get() + '/' """

    def elaborate_pdfs(self):
        if not (self.pdf1_path and self.pdf2_path):
            messagebox.showerror("Error", "Please fill in all fields.")
            return

        start_time = time.time()
            
        # Estrai le informazioni da "Spedire a:", "Dettagli prodotto" e "Quantita'" dal PDF1
        listOrders = extract_text_from_pdf(self.pdf1_path)
        
        # Aggiungi il nome del prodotto al PDF2 accanto allo shipping address
        add_product_name_to_pdf(self.pdf2_path, listOrders)
        
        #Distizione ordini in singleProducts, multiProducts e ordersMultiProducts
        singleProducts, multiProducts, ordersMultiProduct = categorize_orders(listOrders)
        
        #Raggruppamento singleProducts con stesso nome sommandone le quantita' e raggruppamento multiProducts 
        #con stesso nome e stessa quantita' contando il numero di unita'
        singleProducts, multiProducts = group_same_products(singleProducts, multiProducts)
        create_pdf_with_tables(singleProducts, multiProducts, ordersMultiProduct, self.output_path)
        
        elapsed_time = time.time() - start_time
        minutes = int(elapsed_time / 60)
        seconds = int(elapsed_time % 60)
        self.time_label.config(text="Time: {:02d}:{:02d}".format(minutes, seconds))

        messagebox.showinfo("Success", f"PDFs saved to {self.output_path}") 
        
    def generate_pdf(self):
        if not (self.pdf1_path):
            messagebox.showerror("Error", "Please fill in PDF1 field.")
            return

        # Estrai le informazioni da "Spedire a:" e "Dettagli prodotto" dal PDF1
        listOrders = extract_text_from_pdf(self.pdf1_path)
        singleProducts, multiProducts, ordersMultiProduct = categorize_orders(listOrders)
        singleProducts, multiProducts = group_same_products(singleProducts, multiProducts)
        
        create_pdf_with_tables(singleProducts, multiProducts, ordersMultiProduct, self.output_path)
            
        messagebox.showinfo("Success", f"Tables created and saved to {self.output_path}")

def extract_text_from_pdf(pdf_path):
    all_elements = []
    with fitz.open(pdf_path) as pdf_file:
        for page_num in range(len(pdf_file)):
            page = pdf_file.load_page(page_num)
            page_text = page.get_text()
            
            product_details = extract_product_details(page_text)           
            all_elements.append(product_details)
    return all_elements

def extract_shipping_address(text):
    pattern = r"Spedire a:\n(.*?)(?=\n)"
    match_shipping_address = re.search(pattern, text)
    if match_shipping_address:
        return match_shipping_address.group(1).strip()[:22].upper()
    else:
        return None
    
def extract_product_name(text, position):
    if position == "first":
        pattern = r"Totale ordine\n\d+\n(.*?)(?=\nSKU:)"
    else:
        pattern = r'Tot\. articolo\n(?:.*\n)*[0-9]+\n(.*?)(?=SKU:)'
        
    match_nome_prod = re.search(pattern, text, re.DOTALL)
    if match_nome_prod:
        return orderDistinction(re.sub(r"[\s-]+", " ", match_nome_prod.group(1))[5:]) 
    else:
        return None

def extract_product_quantity(text, position):
    if position == "first": 
        pattern = r"Totale ordine\n(\d+)\n"
    else:
        pattern = r'Tot\. articolo.*\n(?P<quantity>\d+)\n.*\nSKU'
        
    match_prod_quantity = re.search(pattern, text, re.DOTALL)
    if match_prod_quantity:
        return match_prod_quantity.group(1).strip()
    else:
        return None
    
def extract_product_details(text):
    product = []

    shipping_address = extract_shipping_address(text)
    nome_prod1 = extract_product_name(text, "first")
    quantity_prod1 = extract_product_quantity(text, "first")
    quantity_prod2 = extract_product_quantity(text, "second")
    
    if quantity_prod2: 
        nome_prod2 = extract_product_name(text, "second")

    if not quantity_prod2:
        product.append((shipping_address, nome_prod1, quantity_prod1))
        return product

    product.append((shipping_address, nome_prod1, quantity_prod1))
    product.append((shipping_address, nome_prod2, quantity_prod2))

    return product

def categorize_orders(listOrders):
    singleProducts = []
    multiProducts = []
    ordersMultiProduct = []
    
    for order in listOrders:
        if len(order) > 1:
            ordersMultiProduct.append(order)
        elif order[0][2] != "1": 
            multiProducts.append(order)
        else:
            singleProducts.append(order)

    return singleProducts, multiProducts, ordersMultiProduct

def orderDistinction(product_name):
    max_length = 40
    # Trova la posizione della parentesi tonda aperta nella stringa
    open_parenthesis_index = product_name.find("(")

    if open_parenthesis_index != -1:
        # Estrai il contenuto tra le parentesi tonde
        content_in_parentheses = product_name[open_parenthesis_index:]

        # Lunghezza della parte di stringa prima delle parentesi tonde
        length_before_parentheses = open_parenthesis_index

        # Lunghezza massima consentita per la parte di stringa prima delle parentesi tonde
        max_length_before_parentheses = max_length - len(content_in_parentheses)

        # Taglia la parte di stringa prima delle parentesi tonde se necessario
        if length_before_parentheses > max_length_before_parentheses:
            product_name = product_name[:max_length_before_parentheses]

        return product_name[:max_length_before_parentheses] + content_in_parentheses

    # Se non ci sono parentesi tonde nella stringa, restituisci la stringa stessa
    return product_name[:max_length]


def add_product_name_to_pdf(pdf_path, listOrders):
    with fitz.open(pdf_path) as pdf_document:
        # Pre-calculate all page texts
        page_texts = [re.sub(r'\s+', ' ', page.get_text()) for page in pdf_document]
        
        for order in listOrders:
            shipping_address_find = any(order[0][0] in page_text for page_text in page_texts)
            if not shipping_address_find:
                continue
            
            # Get the first page containing the shipping address
            page_index = next(i for i, page_text in enumerate(page_texts) if order[0][0] in page_text)
            page = pdf_document[page_index]
            page.wrap_contents()
            page.set_rotation(180)

            # Get the rectangle coordinates of the shipping address
            rect = page.search_for(order[0][0])[0]

            # Define offset for x and y coordinates in each quadrants
            x_offset = 267 if 0 < rect[0] < 300 else 565
            y_offset = 90 if 0 < rect[1] < 415 else 510

            if len(order) > 1:
                for item in order:
                    page.insert_text((x_offset, y_offset), text=item[1], fontsize=10, rotate=180, render_mode=0)
                    if item[2] != "1":
                        page.insert_text((x_offset - 185, y_offset), text=" --> x" + str(item[2]), fontsize=15, rotate=180, render_mode=0) 
                    y_offset+= 10
            elif order[0][2] != "1": 
                page.insert_text((x_offset, y_offset), text=order[0][1], fontsize=10, rotate=180, render_mode=0)
                page.insert_text((x_offset - 185, y_offset), text=" --> x" + str(order[0][2]), fontsize=15, rotate=180, render_mode=0)
            else:
                page.insert_text((x_offset, y_offset), text=order[0][1], fontsize=10, rotate=180, render_mode=0)

        # Save the modified PDF
        pdf_document.saveIncr()

def group_same_products(singleProducts, multiProducts):
    singleProdDict = {}
    multipleProdDict = {}

    # Raggruppa i prodotti per nome e somma le quantità
    for item in singleProducts:
        productName = item[0][1]
        quantity = int(item[0][2])
        if productName in singleProdDict:
            singleProdDict[productName] += quantity
        else:
            singleProdDict[productName] = quantity

    # Raggruppa i prodotti multipli per nome e quantità
    for item in multiProducts:
        product_name = item[0][1]
        quantity = int(item[0][2])
        key = (product_name, quantity)
        if key in multipleProdDict:
            multipleProdDict[key] += 1
        else:
            multipleProdDict[key] = 1

    # Costruisci la lista di prodotti sommati
    singleProducts = [(productName, str(quantity)) for productName, quantity in singleProdDict.items()]

    # Costruisci la lista di prodotti multipli raggruppati
    multiProducts = [('', product_name, f"x{quantity}") if count == 1 else (f"x{count}", product_name, f"x{quantity}") for (product_name, quantity), count in multipleProdDict.items()]

    return singleProducts, multiProducts

def create_pdf_with_tables(single_products, multi_products, orders_multi_product, output_path):
    doc = SimpleDocTemplate(output_path + 'tabelle.pdf', pagesize=letter)
    elements = []

    # Creazione delle tabelle per i singoli prodotti, prodotti multipli e ordini multi-prodotto
    single_table_data = [['Single-Packaging', 'Quantità']]
    for order in single_products:
        single_table_data.append([order[0], order[1]])
    single_table = create_table(single_table_data)
    elements.append(single_table)
    elements.append(Spacer(1, 0.5 * inch))

    multi_table_data = [['Multi-Packaging', 'Quantità', 'Unità']]
    for order in multi_products:
        multi_table_data.append([order[1], order[2], order[0]])
    multi_table = create_table(multi_table_data)
    elements.append(multi_table)
    elements.append(Spacer(1, 0.5 * inch))

    orders_multi_table_data = [['Orders-Multi-Product', 'Quantità']]
    for order in orders_multi_product:
        for item in order:
            orders_multi_table_data.append([item[1], item[2]])
        orders_multi_table_data.append(['Pacco'])
    orders_multi_table = create_table(orders_multi_table_data)
    elements.append(orders_multi_table)

    # Salvataggio del PDF
    doc.build(elements)

# Funzione per creare una tabella da una lista di dati
def create_table(data):
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

def main():
    guiObj = Gui()
    guiObj.avvia_interfaccia()


if __name__ == "__main__":
    main()
