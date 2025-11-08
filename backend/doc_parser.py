# import stateful_session as ss
import pdfplumber # to open PDF files
import docx2txt  # to open DOCX files
import os

def extract_text_from_pdf(file_bytes: bytes) -> str:
    text = ""
    with pdfplumber.open(file_bytes) as pdf:
        for page in pdf.pages:
            text += page.extract_text() or ""
    return text

def extract_text_from_docx(file: str) ->str:
    return docx2txt.process(file)

def parse_file(file: str) ->dict:
    ext = os.path.splitext(file)[1].lower() # get the file extension
    if ext == ".pdf":
        return {"status": "ok","response":extract_text_from_pdf(file)}
    elif ext == ".docx":
        return {"status": "ok","response":extract_text_from_docx(file)}
    else:
        return {"status":"error" ,"error-msg":f"Error: The given file type {ext} cannot be parsed."}

def send_text_agent(file: str) ->str:
    docdata = parse_file(file)
    if(docdata["status"] == "error"): return "error"
    else:
        text = docdata["response"]
        # result = ss.create_message(text)
        return result
        

if __name__ == "__main__":
    text = """
Acme Corporation held its quarterly meeting on June 20, 2025. Present were CEO Jane Doe and CFO John Smith. 
They announced a new partnership with ByteLabs. Action items include product rollout by Q3 and investor briefing by July.
"""
    file = "C:\\Users\\vskof\\OneDrive\\Desktop\\nature.pdf"

    #result = ss.create_message(text)
    result = send_text_agent(file)
    print(result)