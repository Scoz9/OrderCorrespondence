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
        self.single_products, self.multi_products = self.group_same_products(
            self.single_products, self.multi_products
        )
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
        return all_elements

    def extract_product_details(self, text):
        product = []

        shipping_address = self.extract_shipping_address(text)
        nome_prod1 = self.extract_product_name(text, "first")
        quantity_prod1 = self.extract_product_quantity(text, "first")
        quantity_prod2 = self.extract_product_quantity(text, "second")

        if not quantity_prod2:
            product.append((shipping_address, nome_prod1, quantity_prod1))
            return product

        nome_prod2 = self.extract_product_name(text, "second")
        product.append((shipping_address, nome_prod1, quantity_prod1))
        product.append((shipping_address, nome_prod2, quantity_prod2))
        return product

    def extract_shipping_address(self, text):
        pattern = r"Spedire a:\n(.*?)(?=\n)"
        match_shipping_address = re.search(pattern, text)
        if match_shipping_address:
            return match_shipping_address.group(1).strip()[:22].upper()
        else:
            return None

    def extract_product_name(self, text, position):
        if position == "first":
            pattern = r"Totale ordine\n\d+\n(.*?)(?=\nSKU:)"
        else:
            pattern = r"Tot\. articolo\n(?:.*\n)*[0-9]+\n(.*?)(?=SKU:)"
        
        match_nome_prod = re.search(pattern, text, re.DOTALL) if re.search(pattern, text, re.DOTALL) is not None else re.search(r"Gift Options\n\d+\n(.*?)(?=\nSKU:)", text, re.DOTALL)
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
                shipping_address_find = any(
                    order[0][0] in page_text for page_text in page_texts
                )
                if not shipping_address_find:
                    continue

                # Get the first page containing the shipping address
                page_index = next(
                    i
                    for i, page_text in enumerate(page_texts)
                    if order[0][0] in page_text
                )
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

    def group_same_products(self, single_products, multi_products):
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
            (f"{count}", product_name, f"x{quantity}")
            for (product_name, quantity), count in multiple_prod_dict.items()
        ]

        return single_products, multi_products
