import io
from datetime import datetime
from io import StringIO

from barcode import Code128
from barcode.writer import ImageWriter
from reportlab.graphics.barcode import createBarcodeDrawing
from reportlab.graphics.shapes import Drawing
from reportlab.lib import colors
from reportlab.lib.colors import lightgrey
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, mm
from reportlab.graphics.barcode.qr import QrCodeWidget
from reportlab.lib.utils import ImageReader
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, HRFlowable, Image

styles = getSampleStyleSheet()


class PDFCreate:
    def __init__(self, row):
        self.row = row[1]
        self.ewb_date = self.row["EWB Date"].strip("")
        self.ewb_date = datetime.strptime(self.ewb_date, "%Y-%m-%d %H:%M:%S")
        self.doc_date = datetime.strptime(self.row["Doc.Date"], "%Y-%m-%d %H:%M:%S")
        self.valid_up_to = datetime.strptime(self.row["Valid Till Date"], "%Y-%m-%d %H:%M:%S")

    def get_qr_section(self):
        eway_bill_number = self.row["EWB No"].strip("").replace(" ", "")
        gstn = self.row["Other Party GSTIN"].strip("").replace(" ", "")
        date_n_time = self.ewb_date.strftime("%m/%d/%Y %I:%M:%S %p")

        qrw = QrCodeWidget(f"{eway_bill_number}/{gstn}/{date_n_time}")
        b = qrw.getBounds()
        w = b[2] - b[0]
        h = b[3] - b[1]

        d = Drawing(90, 90, transform=[90 / w, 0, 0, 90 / h, 0, 0])
        d.add(qrw)
        qr_data = [[self.get_e_way_header_element()], [self.get_flowable_line()], [d]]
        table = Table(qr_data)
        table.setStyle([('BOX', (0, 0), (-1, -1), .1, colors.black), ("ALIGN", (0, 0), (-1, -1), "CENTER"), ])
        return table

    def get_flowable_line(self):
        return HRFlowable(width="20%", thickness=1, lineCap='round', color=lightgrey, spaceBefore=0, spaceAfter=0,
                          hAlign='CENTER',
                          vAlign='BOTTOM', dash=None)

    def get_e_way_header_element(self):
        return Paragraph('e-Way Bill', styles['Title'])

    def part_b_sub_table(self):
        p1, p2, p3 = self.row["From GSTIN Info"].split(" ")[-3:]

        headers = ["Mode", "Vehicle / Trans\nDoc No & Dt.", "From", "Entered Date", "Entered By", "CEWB No.\n(If any)",
                   "Multi Veh.Info\n(If any)"]
        values = ["Road", "-", p1, self.ewb_date.strftime("%d/%m/%Y %I:%M %p"), "29AAACT1507C1ZT",
                  "-",
                  "-"]
        new_headers = list()
        new_values = list()
        for h in headers:
            new_headers.append(self._get_as_bold(h))

        for v in values:
            new_values.append(self._get_as_label(v))

        table_data = [new_headers, new_values]

        table = Table(table_data, colWidths="*")
        table.setStyle([("ALIGN", (0, 0), (-1, -1), "LEFT"),
                        ('GRID', (0, 0), (-1, -1), 0.01 * inch, (0, 0, 0,)),
                        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                        ])
        return table

    def bar_code(self):
        barcode_image = Code128(self.row["EWB No"], writer=ImageWriter())
        fp = io.BytesIO()
        barcode_image.write(fp, {"module_width": 0.09, "module_height": 3, "font_size": 3, "quiet_zone": 0, "text_distance": 2})
        # image = ImageReader(fp)
        image = Image(fp, width=50, height=50)
        return image


        # Save the barcode image to a file named "barcode" with the specified options
        barcode_image.save("barcode", options=options)
        barcode = createBarcodeDrawing('Code128', value=self.row["EWB No"], humanReadable=True, width=110, height=50, isoScale=10)
        return barcode

    @staticmethod
    def _get_as_label(inp):
        p = ParagraphStyle("label")
        p.fontSize = 8
        para = Paragraph(inp, p)
        return para

    @staticmethod
    def _get_as_mini_text(inp):
        p = ParagraphStyle("label")
        p.fontSize = 6
        para = Paragraph(inp, p)
        return para

    @staticmethod
    def _get_as_bold(inp):
        p = ParagraphStyle("bold")
        p.fontSize = 8
        para = Paragraph(f"<b>{inp}</b>", p)
        return para

    @staticmethod
    def _get_as_big_bold(inp):
        p = ParagraphStyle("big_bold")
        p.fontSize = 10
        para = Paragraph(f"<b>{inp}</b>", p)
        return para

    def get_e_way_table(self):
        p1, p2, p3 = self.row["From GSTIN Info"].split(" ")[-3:]
        place_of_dispatch = f"{p1},{p3}-{p2}"
        p1, p2, p3 = self.row["TO GSTIN Info"].split(" ")[-3:]
        place_of_delivery = f"{p1},{p3}-{p2}"
        hsn_code = f"{self.row['Main HSN Code']} - {self.row['Main HSN Desc']}"
        ewb_no = self.row["EWB No"]
        ewb_no = f"{ewb_no[0:4]} {ewb_no[4:8]} {ewb_no[8:]}"
        table_data = [
            [self._get_as_label("E-Way Bill No:"), self._get_as_big_bold(ewb_no)],
            [self._get_as_label("E-Way Bill Date:"), self._get_as_bold(self.ewb_date.strftime("%d/%m/%Y %I:%M %p"))],
            [self._get_as_label("Generated By:"), self._get_as_bold("29AAA CT150 7C1ZT - ACC LIMITED")],
            [self._get_as_label("Valid From:"), self._get_as_bold(self.ewb_date.strftime("%d/%m/%Y %I:%M %p"))],
            [self._get_as_label("Valid Until:"), self._get_as_bold(self.valid_up_to.strftime("%d/%m/%Y"))],
            [self._get_as_bold("Part - A"), ""],
            [self._get_as_label("GSTIN of Supplier"), self._get_as_bold("29AAACT1507C1ZT,ACC LIMITED")],
            [self._get_as_label("Place of Dispatch"), self._get_as_bold(place_of_dispatch)],
            [self._get_as_label("GSTIN of Recipient"), self._get_as_bold("29AAACT1507C1ZT,ACC LIMITED")],
            [self._get_as_label("Place of Delivery"), self._get_as_bold(place_of_delivery)],
            [self._get_as_label("Document No."), self._get_as_bold(self.row["Doc.No"])],
            [self._get_as_label("Document Date"), self._get_as_bold(self.doc_date.strftime("%d/%m/%Y"))],
            [self._get_as_label("Transaction Type:"), self._get_as_bold("- NA -")],
            [self._get_as_label("Value of Goods"), self._get_as_bold(self.row["Assessable Value"])],
            [self._get_as_label("HSN Code"), self._get_as_bold(hsn_code)],
            [self._get_as_label("Reason for Transportation"), self._get_as_bold(self.row["Supply Type"])],
            [self._get_as_label("Transporter"), ""],
            [self._get_as_bold("Part - B"), ""],
            [self.part_b_sub_table()],
            [self.bar_code()],
            [self._get_as_mini_text("Note*: If any discrepancy in information please try after sometime")]
        ]
        table = Table(table_data, colWidths=["33%", "67%"])
        table.setStyle([
            ("ALIGN", (0, 0), (-1, -1), "LEFT"),
            ('GRID', (0, 0), (-1, -1), 0.01, (0, 0, 0,)),
            ('SPAN', (0, 5), (1, 5)),
            ('SPAN', (0, 17), (1, 17)),
            ('SPAN', (0, 18), (1, 18)),
            ('SPAN', (0, 19), (1, 19)),
            ('SPAN', (0, 20), (1, 20)),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 7),
            ('TOPPADDING', (0, 0), (-1, -1), 7),
            ("ALIGN", (0, 19), (1, 19), "CENTER"),
        ])
        return table

    def build(self, index):
        file_name = f"output/{index}.{self.row['EWB No']}.pdf"
        doc = SimpleDocTemplate(file_name, leftMargin=0.25 * inch, rightMargin=0.25 * inch, topMargin=0.45 * inch,
                                bottomMargin=0)

        elems = []
        t1 = Table([[self.get_qr_section()], [self.get_e_way_table()]], )
        t1.setStyle([('BOX', (0, 0), (-1, -1), 0.1 * mm, (222, 226, 230, 0.1)), ])

        elems.append(t1)
        doc.build(elems)
