from TablesMaker import TablesMaker
import fitz  # PyMuPDF
import re


class Analyzer:
    def __init__(self, pdf1_path):
        self.pdf1_path = pdf1_path
        self.list_orders = self.extract_text_from_pdf(self.pdf1_path)
        self.single_products, self.multi_products, self.orders_multi_product = (
            self.categorize_orders(self.list_orders)
        )
        self.single_products, self.multi_products, self.orders_multi_product = (
            self.group_same_products(
                self.single_products, self.multi_products, self.orders_multi_product
            )
        )
        self.insertion_sort(self.single_products)
        self.insertion_sort(self.multi_products)
        self.insertion_sort(self.orders_multi_product, "true")
        self.tablesMaker = None

    def initialize_tablesMaker(self, output_path):
        self.tablesMaker = TablesMaker(
            self.single_products,
            self.multi_products,
            self.orders_multi_product,
            output_path,
        )

    def generate_pdf(self, output_path):
        self.initialize_tablesMaker(output_path)
        self.tablesMaker.create_pdf_with_tables()

    def elaborate_pdfs(self, pdf2_path, output_path):
        self.add_product_name_to_pdf(pdf2_path, self.list_orders)
        self.initialize_tablesMaker(output_path)
        self.tablesMaker.create_pdf_with_tables()

    def extract_text_from_pdf(self, pdf1_path):
        all_elements = []
        with fitz.open(pdf1_path) as pdf_file:
            for page_num in range(len(pdf_file)):
                page = pdf_file.load_page(page_num)
                page_text = page.get_text()

                product_details = self.extract_product_details(page_text)
                all_elements.append(product_details)

        all_elements = self.group_buyer_multi_orders(all_elements)
        return all_elements

    def extract_product_details(self, text):
        product = []

        buyer_name = self.extract_buyer_name(text)
        shipping_address, shipping_address2 = self.extract_shipping_address(text)
        nome_prod1 = self.extract_product_name(text, "first")
        quantity_prod1 = self.extract_product_quantity(text, "first")
        quantity_prod2 = self.extract_product_quantity(text, "second")

        if not quantity_prod2:
            product.append(
                (
                    buyer_name,
                    nome_prod1,
                    quantity_prod1,
                    shipping_address,
                    shipping_address2,
                )
            )
            return product

        nome_prod2 = self.extract_product_name(text, "second")
        product.append(
            (
                buyer_name,
                nome_prod1,
                quantity_prod1,
                shipping_address,
                shipping_address2,
            )
        )
        product.append(
            (
                buyer_name,
                nome_prod2,
                quantity_prod2,
                shipping_address,
                shipping_address2,
            )
        )
        return product

    def extract_buyer_name(self, text):
        pattern = r"Spedire a:\n(.*?)(?=\n)"
        match_buyer_name = re.search(pattern, text)
        if match_buyer_name:
            return match_buyer_name.group(1).strip()[:22].upper()
        else:
            return None

    def extract_shipping_address(self, text):
        pattern = r"Spedire a:(?:.*\n){2}(.*?)(?=\n)"
        pattern2 = r"Spedire a:(?:.*\n){3}(.*?)(?=\n)"
        match_shipping_address = re.search(pattern, text)
        match_shipping_address2 = re.search(pattern2, text)
        if match_shipping_address:
            return (
                match_shipping_address.group(1).strip()[:20].upper(),
                match_shipping_address2.group(1).strip()[:20].upper(),
            )
        else:
            return None, None

    def extract_product_name(self, text, position):
        if position == "first":
            pattern = r"Totale ordine\n\d+\n(.*?)(?=\nSKU:)"
        else:
            pattern = r"Tot\. articolo\n(?:.*\n)*[0-9]+\n(.*?)(?=SKU:)"

        match_nome_prod = (
            re.search(pattern, text, re.DOTALL)
            if re.search(pattern, text, re.DOTALL) is not None
            else re.search(r"Gift Options\n\d+\n(.*?)(?=\nSKU:)", text, re.DOTALL)
        )
        if match_nome_prod:
            return self.order_distinction(
                re.sub(r"[\s-]+", " ", match_nome_prod.group(1))
            )
        else:
            return None

    def extract_product_quantity(self, text, position):
        if position == "first":
            pattern = r"Totale ordine\n(\d+)\n"
        else:
            pattern = r"Tot\. articolo.*\n(?P<quantity>\d+)\n.*\nSKU"

        match_prod_quantity = re.search(pattern, text, re.DOTALL)
        if match_prod_quantity is not None:
            return match_prod_quantity.group(1).strip()
        else:
            match_prod_quantity = re.search(r"Gift Options\n(\d+)\n", text, re.DOTALL)
            if match_prod_quantity is not None and position == "first":
                return match_prod_quantity.group(1).strip()
            else:
                return None

    def categorize_orders(self, list_orders):
        single_products = []
        multi_products = []
        orders_multi_product = []

        for order in list_orders:
            if len(order) > 1:
                orders_multi_product.append(order)
            elif order[0][2] != "1":
                multi_products.append(order)
            else:
                single_products.append(order)

        return single_products, multi_products, orders_multi_product

    def order_distinction(self, product_name):
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

    def add_product_name_to_pdf(self, pdf2_path, list_orders):
        with fitz.open(pdf2_path) as pdf_document:
            # Pre-calculate all page texts
            page_texts = [re.sub(r"\s+", " ", page.get_text()) for page in pdf_document]

            for order in list_orders:
                buyer_name_find = any(
                    order[0][0] in page_text for page_text in page_texts
                )
                if not buyer_name_find:
                    continue

                # Get the first page containing the shipping address
                page_index = next(
                    (
                        i
                        for i, page_text in enumerate(page_texts)
                        if (order[0][0] in page_text and order[0][3] in page_text)
                        or (order[0][0] in page_text and order[0][4] in page_text)
                    ),
                    None,
                )

                if page_index is None:
                    print("Errore omonimia pdf2 (Nome+indirizzo): " + order[0][0])

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
                        page.insert_text(
                            (x_offset, y_offset),
                            text=item[1],
                            fontsize=10,
                            rotate=180,
                            render_mode=0,
                        )
                        if item[2] != "1":
                            page.insert_text(
                                (x_offset - 192, y_offset),
                                text=" --> x" + str(item[2]),
                                fontsize=15,
                                rotate=180,
                                render_mode=0,
                            )
                        y_offset += 10
                elif order[0][2] != "1":
                    page.insert_text(
                        (x_offset, y_offset),
                        text=order[0][1],
                        fontsize=10,
                        rotate=180,
                        render_mode=0,
                    )
                    page.insert_text(
                        (x_offset - 192, y_offset),
                        text=" --> x" + str(order[0][2]),
                        fontsize=15,
                        rotate=180,
                        render_mode=0,
                    )
                else:
                    page.insert_text(
                        (x_offset, y_offset),
                        text=order[0][1],
                        fontsize=10,
                        rotate=180,
                        render_mode=0,
                    )

            # Save the modified PDF
            pdf_document.saveIncr()

    def group_same_products(
        self, single_products, multi_products, orders_multi_product
    ):
        single_prod_dict = {}
        multiple_prod_dict = {}

        # Raggruppa i prodotti per nome e somma le quantità
        for item in single_products:
            product_name = item[0][1]
            quantity = int(item[0][2])
            if product_name in single_prod_dict:
                single_prod_dict[product_name] += quantity
            else:
                single_prod_dict[product_name] = quantity

        # Raggruppa i prodotti multipli per nome e quantità
        for item in multi_products:
            product_name = item[0][1]
            quantity = int(item[0][2])
            key = (product_name, quantity)
            if key in multiple_prod_dict:
                multiple_prod_dict[key] += 1
            else:
                multiple_prod_dict[key] = 1

        # Costruisci la lista di prodotti sommati
        single_products = [
            (product_name, str(quantity))
            for product_name, quantity in single_prod_dict.items()
        ]

        # Costruisci la lista di prodotti multipli raggruppati
        multi_products = [
            (product_name, f"{count}", f"x{quantity}")
            for (product_name, quantity), count in multiple_prod_dict.items()
        ]

        i = 0
        while i < len(orders_multi_product):
            for k, single_item in enumerate(orders_multi_product[i]):
                for next_single_item in orders_multi_product[i][k + 1 :]:
                    # Controllo se il nome del prodotto è lo stesso
                    if single_item[1] == next_single_item[1]:
                        # Inserisco nella prima tupla la somma delle quantità eliminando la tupla relativa alla corrispondenza
                        orders_multi_product[i][k] = (
                            single_item[0],
                            single_item[1],
                            str(int(single_item[2]) + int(next_single_item[2])),
                            single_item[3],
                        )
                        orders_multi_product[i].remove(next_single_item)
            i += 1
        return single_products, multi_products, orders_multi_product

    """
    Raggruppa gli ordini multipli effettuati da buyer con stesso name e stesso shipping addess.

    Itera attraverso list_orders e confronta ciascun elemento con gli elementi successivi.
    Se trova una corrispondenza tra il buyer_name e lo shipping_address, combina gli ordini.
    Nella combinazione degli ordini viene effettuato un check relativamente ai prodotti combinati nel seguente
    itera attraverso list_orders[i] e confronta ciascun elemento con gli elementi successivi.
    Se trova una corrispondenza tra il product_name allora unisco il product e sommo la quantita'.
    
    Args:
        list_orders (list): Lista degli ordini
        
    Returns:
        list: Lista degli ordini con raggruppamento buyer multi order
    """

    def group_buyer_multi_orders(self, list_orders):

        i = 0
        while i < len(list_orders):
            order = list_orders[i]

            j = i + 1
            while j < len(list_orders):
                item = list_orders[j]

                if order[0][0] == item[0][0] and order[0][3] == item[0][3]:
                    print("Trovato buyer multi order -> " + order[0][0] + "\n")

                    """ Aggiungo ciascun elemento presente in item come tupla a list_orders[i] """
                    for single_item in item:
                        list_orders[i].append(tuple(single_item))

                    del list_orders[j]
                else:
                    j += 1

            i += 1

        return list_orders

    def insertion_sort(self, arr, order_multi_prod="false"):
        if len(arr) <= 1:
            return arr

        if order_multi_prod == "false":
            for i in range(1, len(arr)):
                key = arr[i]
                j = i - 1
                while j >= 0 and int(key[1]) > int(arr[j][1]):
                    arr[j + 1] = arr[j]
                    j -= 1
                arr[j + 1] = key
        else:
            for single_item in arr:
                for i in range(1, len(single_item)):
                    j = i - 1
                    while j >= 0 and int(single_item[i][2]) > int(single_item[j][2]):
                        single_item[j + 1] = single_item[j]
                        j -= 1
                    single_item[j + 1] = single_item[i]
