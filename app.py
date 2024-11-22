import os
from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory
from fpdf import FPDF

app = Flask(__name__)
app.secret_key = "secret-key"

# Directory paths
PDF_FOLDER = "saved_pdfs"
if not os.path.exists(PDF_FOLDER):
    os.makedirs(PDF_FOLDER)

UPLOAD_FOLDER = "uploads"
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

ALLOWED_EXTENSIONS = {
    ".txt", ".py", ".java", ".cpp", ".html", ".css",
    ".js", ".rb", ".php", ".swift", ".go", ".pl", ".ts"
}

# Helper function: allowed file types
def allowed_file(filename):
    return "." in filename and os.path.splitext(filename)[1].lower() in ALLOWED_EXTENSIONS

# PDF generation class
class PDF(FPDF):
    def header(self):
        self.set_font("Arial", "B", 12)
        self.cell(0, 10, "Code to PDF Converter", 0, 1, "C")

@app.route("/")
def index():
    pdf_files = os.listdir(PDF_FOLDER)
    return render_template("index.html", pdf_files=pdf_files)

@app.route("/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        flash("No file part", "error")
        return redirect(url_for("index"))
    
    file = request.files["file"]
    if file.filename == "":
        flash("No selected file", "error")
        return redirect(url_for("index"))
    
    if file and allowed_file(file.filename):
        file_path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(file_path)
        return redirect(url_for("convert_to_pdf", filename=file.filename))
    else:
        flash("Invalid file type", "error")
        return redirect(url_for("index"))

@app.route("/convert/<filename>")
def convert_to_pdf(filename):
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    pdf_filename = os.path.splitext(filename)[0] + ".pdf"
    pdf_path = os.path.join(PDF_FOLDER, pdf_filename)
    
    try:
        pdf = PDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)

        with open(file_path, "r", encoding="utf-8") as file:
            for line in file:
                pdf.multi_cell(0, 10, line)
        
        pdf.output(pdf_path)
        flash(f"PDF created: {pdf_filename}", "success")
    except Exception as e:
        flash(f"Error converting to PDF: {str(e)}", "error")
    
    return redirect(url_for("index"))

@app.route("/download/<filename>")
def download_pdf(filename):
    return send_from_directory(PDF_FOLDER, filename)

@app.route("/delete/<filename>")
def delete_pdf(filename):
    pdf_path = os.path.join(PDF_FOLDER, filename)
    try:
        os.remove(pdf_path)
        flash(f"Deleted {filename}", "success")
    except Exception as e:
        flash(f"Error deleting file: {str(e)}", "error")
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)
