import pdfplumber

pdf_path = r"c:/Users/baoma/TRD/Renesas/REN_r01uh0684jj0130-rh850f1kh-rh850f1km_MAH_20210930.pdf"

def analyze_pages(start_page, end_page):
    with pdfplumber.open(pdf_path) as pdf:
        for i in range(start_page, end_page):
            page = pdf.pages[i]
            text = page.extract_text()
            tables = page.extract_tables()

            print(f"--- Page {i+1} ---")
            print(text[:500] + "..." if text else "No text found")
            if tables:
                print(f"Found {len(tables)} tables.")
                print("First table sample:", tables[0][:3])
            print("\n")

if __name__ == "__main__":
    # Analyze a few pages to understand the structure
    # Assuming registers might be later in the doc, let's check a range
    analyze_pages(50, 55)
