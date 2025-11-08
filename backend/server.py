# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')
print("starting server.....")
print("Please wait")
from fastapi import FastAPI, File, UploadFile, Request
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import uvicorn
import doc_parser
import os
import glob
import shutil
import endpoint as model
import traceback
import qntAnalysis



app = FastAPI()
session_files = []
session_file_names = []
current_response = ""
current_dir = os.path.dirname(os.path.abspath(__file__))
upload_dir = os.path.join(current_dir, "file_cache")
graph = ''
doc_content = ''
doc_list = []
# Allow frontend to access backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

def delCacheFiles():
    global doc_content
    session_file_names.clear()
    session_files.clear()
    doc_content = ''
    doc_list.clear()
    files = glob.glob(os.path.join(upload_dir, "*"))
    for file in files:
        try:
            os.remove(file)
            print(f"Deleted: {file}")
        except Exception as e:
            print(f"Error deleting {file}: {e}")

@app.post("/analyze/")
async def analyze(files: List[UploadFile] = File(...)):
    global doc_content
    print(len(files))
    try:
        for file in files:
            upload_file = os.path.join(upload_dir,file.filename)
            with open(upload_file,'wb') as buffer:
                shutil.copyfileobj(file.file,buffer)
            session_files.append({
                "filename": file.filename,
                "content_type": file.content_type,
                "file_path": upload_file
            })
            session_file_names.append(file.filename)
        i = 0
        for file in session_files:
            fp = os.path.join(upload_dir,file["filename"])
            temp = doc_parser.parse_file(fp)["response"]
            doc_list.append(temp)
            doc_content += temp
            i+=1
        response = model.gemini_llm.invoke(doc_content).content
        model.chat_history.append(model.HumanMessage(doc_content))
        model.chat_history.append(model.AIMessage(response))        
        print(response)
        return {'status':'1','response':response}
    except Exception as error:
        traceback.print_exc()
        return {'status':'0','error':str(error)}

@app.delete("/clearCache/")
async def clearCache():
    delCacheFiles()
    model.chat_history.clear()
    return {'message':'All files and cache cleared'}

@app.post("/query/")
async def query(text: Request):
    data = await text.json()  # Parse JSON body
    query = data.get("query", "")
    model.chat_history.append(model.SystemMessage("Give accurate short or medium sized response to this user query."))
    model.chat_history.append(model.HumanMessage(query))
    response = model.gemini_llm.invoke(model.chat_history).content
    model.chat_history.append(model.AIMessage(response))
    return {"status":'1',"response":response}

command = "Generate Mermaid code to show relationships and infomation flow between the entities in the given data.Only the code must be returned, no other explanations."
@app.get("/graph/")
async def graph(errmsg: str = command):
    model.chat_history.append(model.HumanMessage(errmsg+'\n,got this error from previous mermaid code, resolve it'))
    code = model.gemini_llm.invoke(model.chat_history).content
    model.chat_history.append(model.AIMessage(code))
    print(code)
    return{"code":code}

@app.get("/qntAnl/")
async def qntAnl():
    qnt = qntAnalysis.perform_quantitative_analysis(doc_list)
    model.chat_history.append(model.HumanMessage("Analyzes text to determine the dominant focus area based on keyword frequency, response should be under 7 words."))
    focus = model.gemini_llm.invoke(model.chat_history).content
    print(qnt)
    return {"focus":focus,"qntRes":qnt}

if __name__ == "__main__":
    delCacheFiles()
    print("loading server, please wait.....")
    uvicorn.run(app, host="0.0.0.0", port=8000)

