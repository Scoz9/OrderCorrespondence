# OrderCorrespondence
The script accepts two PDFs as input:
- PFD1 -> list of orders to be shipped (downloaded from Amazon)
- PDF2 -> vehicle order list

In output you can decide what to return:
- PDF button -> insert PDF1 (required) as input, the script creates a PDF containing the order tables (single-product, multi-product, multi-product orders)
- Elaborate PDF button -> inserts into PDF2, for each order, the products relating to the shipment, above the "company name". It also creates a PDF containing the order tables (single products, multi-products, multi-product orders)

Features implemented:
Single Products -> grouping by name by adding the quantities.
Multi-Products -> grouping by name and quantity by entering in the quantity field the number of items present in the package and the quantity of each of these items in units

Non-work cases:
1- Multi-product orders with more than three products (waiting for case studies)
2- Multi-product orders with gift options (waiting for a case study)

The output path is the directory of PDF1