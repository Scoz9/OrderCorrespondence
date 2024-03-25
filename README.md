# OrderCorrespondence
The script accepts two PDFs as input:
- PFD1 -> list of orders to be shipped (made by Amazon)
- PDF2 -> vehicle order list

In output you can decide what to return:
- PDF button -> the script creates a PDF containing the order tables (single-product, multi-product, multi-product orders)
- Elaborate PDF button -> the script inserts into PDF2, for each order, the products relating to the shipment, above the "company name". It also creates a PDF containing the order tables (single products, multi-products, multi-product orders)

Features implemented:
Single Products -> grouping by name by adding the quantities.
Multi-Products -> grouping by name and quantity by entering in the quantity field the number of items present in the package and the quantity of each of these items in units
Buyer-multi-order -> grouping orders having same buyer_name and same shipping_address

Non-work cases:
1- Multi-product orders with more than three products (waiting for case studies)
2- Multi-product orders with gift options (waiting for a case study)

Fixed Cases:
1- Solved case when same buyer (same shipping_address) do multiple order by Buyer-multi-order feature
2- Solved case of homonimy (same buyer_name different shipping_address) by checking buyer_name and shipping_address before insert the product_name in the pdf2

:heavy_exclamation_mark:The output path is the directory of PDF1
