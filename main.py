import fitz  # PyMuPDF
import tkinter as tk
from tkinter import filedialog, messagebox
import os
import time
import re

class Gui:
    def __init__(self):
        pass

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

        self.elaborate_button = tk.Button(
            self.root, text="Elaborate", command=self.elaborate_pdfs
        )
        self.elaborate_button.grid(row=3, column=1)

        self.time_label = tk.Label(self.root, text="Time: 0:00")
        self.time_label.grid(row=4, column=1)

        self.root.mainloop()

    def browse_pdf1(self):
        filename = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
        self.pdf1_entry.delete(0, tk.END)
        self.pdf1_entry.insert(0, filename)

    def browse_pdf2(self):
        filename = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
        self.pdf2_entry.delete(0, tk.END)
        self.pdf2_entry.insert(0, filename)

    """ def browse_output_path(self):
        path = filedialog.askdirectory()
        self.output_path_entry.delete(0, tk.END)
        self.output_path_entry.insert(0, path) """

    def elaborate_pdfs(self):
        pdf1_path = self.pdf1_entry.get()
        pdf2_path = self.pdf2_entry.get()
        """ output_path = self.output_path_entry.get() """

        """ and output_path """
        if not (pdf1_path and pdf2_path):
            messagebox.showerror("Error", "Please fill in all fields.")
            return

        start_time = time.time()
            
        # Estrai le informazioni da "Spedire a:" e "Dettagli prodotto" dal PDF1
        listOrders = extract_text_from_pdf(pdf1_path)

        # Aggiungi il nome del prodotto al PDF2 accanto allo shipping address
        add_product_name_to_pdf(pdf2_path, listOrders)

        elapsed_time = time.time() - start_time
        minutes = int(elapsed_time / 60)
        seconds = int(elapsed_time % 60)
        self.time_label.config(text="Time: {:02d}:{:02d}".format(minutes, seconds))
        
        messagebox.showinfo("Success", f"PDFs merged and saved to {pdf2_path}") 
        
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
    match = re.search(r"Spedire a:\n(.*?)(?=\n)", text)
    if match:
        return match.group(1).strip()[:22].upper()
    return None


def extract_product_details(text):
    match = re.search(r"Totale ordine\n\d+\n(.*?)(?=\nSKU:)", text, re.DOTALL)
    if match:
        return orderDistinction(re.sub(r"[\s-]+", " ", match.group(1))[5:])
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
        return product_name[:max_length_before_parentheses] + content_in_parentheses

    # Se non ci sono parentesi tonde nella stringa, restituisci la stringa stessa
    return product_name[:max_length]


def extract_product_quantity(text):
    match = re.search(r"Totale ordine\n(\d+)\n", text)
    if match:
        return match.group(1).strip()
    return None

def add_product_name_to_pdf(pdf_path, listOrders):
    with fitz.open(pdf_path) as pdf_document:
        # Pre-calculate all page texts
        page_texts = [re.sub(r'\s+', ' ', page.get_text()) for page in pdf_document]
        
        for order in listOrders:
            shipping_address_find = any(order[0] in page_text for page_text in page_texts)
            if not shipping_address_find:
                continue
            
            # Get the first page containing the shipping address
            page_index = next(i for i, page_text in enumerate(page_texts) if order[0] in page_text)
            page = pdf_document[page_index]
            page.wrap_contents()
            page.set_rotation(180)
            # Get the rectangle coordinates of the shipping address
            rect = page.search_for(order[0])[0]
           
            # Define offset for x and y coordinates in each quadrants
            x_offset = 267 if 0 < rect[0] < 300 else 565
            y_offset = 90 if 0 < rect[1] < 415 else 510

            if order[2] != "1": 
                page.insert_text((x_offset, y_offset), text=order[1], fontsize=10, rotate=180, render_mode=0)
                page.insert_text((x_offset - 185, y_offset), text=" --> x" + str(order[2]), fontsize=15, rotate=180, render_mode=0)
            else:
                page.insert_text((x_offset, y_offset), text=order[1], fontsize=10, rotate=180, render_mode=0)

        # Save the modified PDF
        pdf_document.saveIncr()


def main():
    guiObj = Gui()
    guiObj.avvia_interfaccia()


if __name__ == "__main__":
    main()
