import pandas as pd

from pdf_gen.main import PDFCreate

p = r"I:\Projects\Viveks\PDFGen\final_data.xlsx"


if __name__ == '__main__':
    df = pd.read_excel(p, sheet_name="ACC", dtype="str")
    df = df.fillna("")

    for index, row in enumerate(df.iterrows()):
        try:
            print(f"Processing row {index+1}")
            pdf = PDFCreate(row)
            pdf.build(index+1)

        except Exception as e:
            print("-------------------\nError")
            print(e)
            print(f"{index} - {str(row)}")
            print("--------------------------")
