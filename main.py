import fitz  # PyMuPDF
import tkinter as tk
from tkinter import filedialog, messagebox
import os

class Gui:
    def __init__(self, master):
        self.master = master
        master.title("PDF Analyzer")

        self.label1 = tk.Label(master, text="PDF 1:")
        self.label1.grid(row=0, column=0)

        self.pdf1_entry = tk.Entry(master, width=50)
        self.pdf1_entry.grid(row=0, column=1)

        self.browse_button1 = tk.Button(master, text="Browse", command=self.browse_pdf1)
        self.browse_button1.grid(row=0, column=2)

        self.label2 = tk.Label(master, text="PDF 2:")
        self.label2.grid(row=1, column=0)

        self.pdf2_entry = tk.Entry(master, width=50)
        self.pdf2_entry.grid(row=1, column=1)

        self.browse_button2 = tk.Button(master, text="Browse", command=self.browse_pdf2)
        self.browse_button2.grid(row=1, column=2)

        self.label3 = tk.Label(master, text="Output Path:")
        self.label3.grid(row=2, column=0)

        self.output_path_entry = tk.Entry(master, width=50)
        self.output_path_entry.grid(row=2, column=1)

        self.browse_button3 = tk.Button(master, text="Browse", command=self.browse_output_path)
        self.browse_button3.grid(row=2, column=2)

        self.elaborate_button = tk.Button(master, text="Elaborate", command=self.elaborate_pdfs)
        self.elaborate_button.grid(row=3, column=1)

    def browse_pdf1(self):
        filename = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
        self.pdf1_entry.delete(0, tk.END)
        self.pdf1_entry.insert(0, filename)

    def browse_pdf2(self):
        filename = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
        self.pdf2_entry.delete(0, tk.END)
        self.pdf2_entry.insert(0, filename)

    def browse_output_path(self):
        path = filedialog.askdirectory()
        self.output_path_entry.delete(0, tk.END)
        self.output_path_entry.insert(0, path)

    def elaborate_pdfs(self):
        pdf1_path = self.pdf1_entry.get()
        pdf2_path = self.pdf2_entry.get()
        output_path = self.output_path_entry.get()
        
        if not (pdf1_path and pdf2_path and output_path):
            messagebox.showerror("Error", "Please fill in all fields.")
            return

        # Estrai le informazioni da "Spedire a:" e "Dettagli prodotto" dal PDF1
        listOrders = extract_text_from_pdf(pdf1_path)

        # Aggiungi il nome del prodotto al PDF2 accanto allo shipping address
        add_product_name_to_pdf(pdf2_path, listOrders)

        messagebox.showinfo("Success", f"PDFs merged and saved to {output_path}" + "pdf_result.pdf") 

def extract_text_from_pdf(pdf_path):
    all_elements = []
    with fitz.open(pdf_path) as pdf_file:
        for page_num in range(len(pdf_file)):
            page = pdf_file.load_page(page_num)
            page_text = page.get_text()
            shipping_address = extract_shipping_address(page_text)
            product_details = extract_product_details(page_text)
            quantity = extract_product_quantity(page_text)
            if shipping_address and product_details:
                all_elements.append((shipping_address, product_details, quantity))
            
    return all_elements

def extract_shipping_address(text):
    shipping_address = extract_info_after_keyword(text, "Spedire a:")
    if shipping_address:
        shipping_address = shipping_address.upper()  # Convert to uppercase
    return shipping_address[:22]

def extract_info_after_keyword(text, keyword):
    keyword_index = text.find(keyword)
    if keyword_index != -1:
        line_start = text.find("\n", keyword_index) + 1
        line_end = text.find("\n", line_start)
        info = text[line_start:line_end].strip()
        return info
    return None

def extract_product_details(text):
    total_order_index = text.find("Totale ordine")
    if total_order_index != -1:
        
        # Trova la riga dopo "Totale ordine"
        line_start = text.find("\n", total_order_index) + 1
        line_end = text.find("\n", line_start)
        
        # Trova la riga una linee dopo "Totale ordine" e prendi tutte le linee fino a quando non trovi SKU 
        next_line_start = text.find("\n", line_end) + 1
        while True:
            next_line_end = text.find("\n", next_line_start)
            line = text[next_line_start:next_line_end].strip()
            if line.startswith("SKU"):
                break
            next_line_start = next_line_end + 1
        
        # Estrai e pulisci l'informazione
        info = text[line_start:next_line_start].strip()
        
        info = info[7:].strip()  # Rimuovi i primi 7 caratteri
        info = info.replace("\n", " ") # Rimuovi tutti i caratteri "\n" dalla stringa
        info = info.replace("-", "") 
        info = orderDistinction(info)
        return info
    return None

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
        return product_name + content_in_parentheses
    else:
        # Se non ci sono parentesi tonde nella stringa, restituisci la stringa stessa
        return product_name[:max_length]

def extract_product_quantity(text):
    total_order_index = text.find("Quantità")
    if total_order_index != -1:
        # Trova la riga dopo "Quantità"
        line_start = text.find("\n", total_order_index) + 1
        line_end = text.find("\n", line_start)
        
        # Trova la terza riga dopo "Quantità"
        for _ in range(3):
            line_start = text.find("\n", line_end) + 1
            line_end = text.find("\n", line_start)
        
        # Estrai e pulisci l'informazione
        info = text[line_start:line_end].strip()
        return info
    return None

def add_product_name_to_pdf(pdf_path, listOrders):
    # Open the PDF
    pdf_document = fitz.open(pdf_path)

    for order in listOrders:
        
        # Loop through pages
        for page in pdf_document:
            # Set rotation of the page
            page.set_rotation(180)
            page.wrap_contents()
            
            # Find shipping address coordinates
            x, y = find_shipping_address_coordinates(page, order[0])
            
            # If shipping address is found
            if x is not None and y is not None:
                if(0 < x < 300 and 0 < y < 415):
                    # Calculate the x-coordinate for the product name
                    x = 267  # Offset for the product name
                
                    # Calculate the y-coordinate for the product name
                    y = 90  # Offset for the product name
                elif(0 < x < 300 and 415 <= y < 830): 
                    # Calculate the x-coordinate for the product name
                    x = 267  # Offset for the product name
                
                    # Calculate the y-coordinate for the product name
                    y = 510  # Offset for the product name
                elif(300 <= x < 595 and 0 < y < 415):
                    # Calculate the x-coordinate for the product name
                    x = 565  # Offset for the product name
                
                    # Calculate the y-coordinate for the product name
                    y = 90  # Offset for the product name
                elif(300 <= x < 595 and 415 <= y < 830):
                    # Calculate the x-coordinate for the product name
                    x = 565  # Offset for the product name
                
                    # Calculate the y-coordinate for the product name
                    y = 510  # Offset for the product name
                
                if order[2] != "1": 
                   page.insert_text((x, y), text=order[1], fontsize=10, rotate=180, render_mode=0)
                   page.insert_text((x-185, y), text=" --> x" + str(order[2]), fontsize=15, rotate=180, render_mode=0)
                else:
                    page.insert_text((x, y), text=order[1], fontsize=10, rotate=180, render_mode=0)
                break
            
    # Save the modified PDF
    pdf_document.save("pdf_result.pdf")
    pdf_document.close()
    
def find_shipping_address_coordinates(page, shipping_address):
    # Get text of the page
    page_text = page.get_text()
    shipping_address_find = shipping_address in " ".join(page_text.split())
    if shipping_address_find is True:
        # Get the rectangle coordinates of the shipping address
        rect = page.search_for(shipping_address)[0]
        # Calculate x and y coordinates
        x = rect[0]
        y = rect[1]
        return x, y
    else:
        return None, None



def main():
    root = tk.Tk()
    gui = Gui(root)
    root.mainloop() 

    """ # Path del file PDF da cui estrarre le informazioni
    pdf_path_1 = 'pdf1.pdf'
    pdf_path_2 = 'pdf2.pdf' """

    """ # Estrai le informazioni da "Spedire a:" e "Dettagli prodotto" dal PDF1
    listOrders = extract_text_from_pdf(pdf_path_1)

    # Aggiungi il nome del prodotto al PDF2 accanto allo shipping address
    add_product_name_to_pdf(pdf_path_2, listOrders)  """

if __name__ == "__main__":
    main()