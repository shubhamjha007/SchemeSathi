import os
from pypdf import PdfReader
from pdf2image import convert_from_path
import pytesseract
from langchain_text_splitters import (
    RecursiveCharacterTextSplitter)



PDF_FOLDER = "Schemes"
OUTPUT_FOLDER = "extracted_text"
CHUNK_FOLDER ="chunks"


os.makedirs(OUTPUT_FOLDER, exist_ok=True)
os.makedirs(CHUNK_FOLDER, exist_ok=True)



# TEXT CLEANING FUNCTION

def clean_text(text):

    text = text.replace("\n", " ")

    text = text.replace("\t", " ")

    text = " ".join(text.split())

    return text

splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50
)

# PDF PROCESSING LOOP

for file_name in os.listdir(PDF_FOLDER):

    # Process only PDFs
    if file_name.endswith(".pdf"):

        file_path = os.path.join(PDF_FOLDER, file_name)

        print(f"\nProcessing: {file_name}")

        final_text = ""

        try:

            # NORMAL PDF EXTRACTION
         

            reader = PdfReader(file_path)

            for page_number, page in enumerate(reader.pages):

                extracted_text = page.extract_text()

                # IF NORMAL TEXT EXISTS
               

                if extracted_text and extracted_text.strip():

                    print(f"Page {page_number+1}: Text extracted normally")

                    final_text += extracted_text + " "

            
                # OCR FALLBACK
              

                else:

                    print(f"Page {page_number+1}: Using OCR")

                    images = convert_from_path(
                        file_path,
                        first_page=page_number + 1,
                        last_page=page_number + 1
                    )

                    ocr_text = pytesseract.image_to_string(images[0])

                    final_text += ocr_text + " "

        
          
            final_text = clean_text(final_text)

           
          
            output_file_name = file_name.replace(".pdf", ".txt")

            output_path = os.path.join(
                OUTPUT_FOLDER,
                output_file_name
            )

            with open(output_path, "w", encoding="utf-8") as f:

                f.write(final_text)

            print(f"Saved cleaned text to: {output_file_name}")

            # Split text into chunks and save them
            chunks = splitter.split_text(final_text)

            print(f"Total Chunks Created: {len(chunks)}")

            for i, chunk in enumerate(chunks):
                chunk_file_name = (
                    file_name.replace(".pdf", "")
                    + f"_chunk_{i+1}.txt"
                )

                chunk_output_path = os.path.join(
                    CHUNK_FOLDER,
                    chunk_file_name
                )

                with open(
                    chunk_output_path,
                    "w",
                    encoding="utf-8"
                ) as chunk_file:
                    chunk_file.write(chunk)

            print(f"Chunks saved for {file_name}")
        except Exception as e:

            print(f"Error processing {file_name}")
            print(e)



print("\nAll PDFs processed successfully.")
