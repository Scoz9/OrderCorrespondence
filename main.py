import fitz  # PyMuPDF

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
        line_start = text.find("\n", total_order_index) + 1
        line_end = text.find("\n", line_start)
        # Skipping one more line to get the next line after "Totale ordine"
        line_start = text.find("\n", line_end) + 1
        line_end = text.find("\n", line_start)
        info = text[line_start:line_end].strip()
        return info
    return None

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
                   page.insert_text((x, y), text=order[1] + " --> x" + str(order[2]), fontsize=10, rotate=180, render_mode=0)
                else:
                    page.insert_text((x, y), text=order[1], fontsize=10, rotate=180, render_mode=0)
                break
    # Save the modified PDF
    pdf_document.save("pdf2_modified.pdf")
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

# Path del file PDF da cui estrarre le informazioni
pdf_path_1 = 'pdf1.pdf'
pdf_path_2 = 'pdf2.pdf'

# Estrai le informazioni da "Spedire a:" e "Dettagli prodotto" dal PDF1
listOrders = extract_text_from_pdf(pdf_path_1)

# Aggiungi il nome del prodotto al PDF2 accanto allo shipping address
add_product_name_to_pdf(pdf_path_2, listOrders) 
