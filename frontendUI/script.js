
import mermaid from "./node_modules/mermaid/dist/mermaid.esm.min.mjs";
mermaid.initialize({
  startOnLoad: false,
  theme: "forest",
  themeVariables: {
    fontSize: '20px',
    lineColor: '#333',
  },
  flowchart: {
    useMaxWidth: true,
    htmlLabels: true,
    curve: 'basis',
  },
});
const msgBox = document.getElementById("messageBox");
const chat_menu = document.getElementById("chatMenu");
const chat_menu_btn = document.getElementById("chatMenuBtn");
const file_menu = document.getElementById("fileMenu");
const file_menu_btn = document.getElementById('fileMenuBtn');
const spinLoad = document.createElement("div");spinLoad.className = 'loader';
const file = document.getElementById('file-input');
const ifb = document.getElementById("infoBar");ifb.style.marginLeft = "22px";
const iline = document.createElement("p");
const info = document.getElementById("info");info.appendChild(iline);
const qntAnalysis = document.getElementById("qntAnl");
let states = {"fileMenu":false,"chatMenu":false,"search":false,"graph":false,"qnt":false};
let ufiles = [];
let uploaded = false;

function listFiles(){
    const fnames = document.getElementById("fileNames");
    if(ufiles.length != 0){
        fnames.innerText = "";
        for(let i=0;i<ufiles.length;i++){
            const p = document.createElement("p");
            p.innerText = `${i+1}) ${ufiles[i]}`;
            fnames.appendChild(p);
        }
    }
    else{
        fnames.innerText = '';
    }
}

async function removeAllFiles(){
    document.getElementById('workspace').innerHTML = '<p id="head1"> Upload Files for Summary, flowchart and Quantitative Analysis';
    ufiles = [];
    listFiles();
    uploaded = false;
    document.getElementById("qntAnl").innerHTML = '<div id="qntAnlGen">Perform Quantitative Analysis</div>';
    document.getElementById("graphArea").innerHTML = '';
    const res = await fetch("http://localhost:8000/clearCache/", {
        method: "DELETE"
    });
    console.log(res);
}
window.removeAllFiles = removeAllFiles;

function addFile(){ifb.appendChild(spinLoad);file.click();}
window.addFile = addFile;

const createGraph = async(errmsg = '')=>{
        try{
            if(errmsg == ''){
                const res = await fetch(`http://localhost:8000/graph/`,{
                    method: 'GET'
                });
                let code = await res.json();
                console.log(code);
                code = String(code.code);
                console.log(code);
                code = code.replace(/```.*\n/, '').replace(/```/g, '').trim();
                console.log(code);
                const { svg } = await mermaid.render('graphSVG',code)
                console.log(svg);
                document.getElementById('graphArea').innerHTML = svg;
            }
            else{
                const res = await fetch(`http://localhost:8000/graph/?errmsg=${encodeURIComponent(errmsg)}`,{
                    method: 'GET'
                });
                let code = await res.json();
                console.log(code);
                code = String(code.code);
                console.log(code);
                code = code.replace(/```.*\n/, '').replace(/```/g, '').trim();
                console.log(code);
                const { svg } = await mermaid.render('graphSVG',code)
                console.log(svg);
                document.getElementById('graphArea').innerHTML = svg;
            }
        }catch(err){
            console.log(err);
            await createGraph(err);
        }
}

document.getElementById('reportBtn').addEventListener('click', async () => {
  window.print();  
});

document.getElementById('graphBtn').addEventListener("click",async function(){
    if(states["graph"]){
        states["graph"] = false;
        document.getElementById('graphArea').style.width = "0px";
    }
    else{
        if(uploaded){
            states["graph"] = true;
            document.getElementById('graphArea').style.width = "90%";
        }
        else{
            alert("No files found!!");
        }
    }
});

document.getElementById("graphGen").addEventListener("click",async function(){
    document.getElementById('graphArea').appendChild(spinLoad);
    try{
        await createGraph();
    }catch(err){
        console.log(err);
    }
});

document.getElementById('uploadFile').addEventListener("click",async function (){
    try{
        iline.innerText = "Uploading Files...";
        ifb.appendChild(spinLoad);
        let formData = new FormData();
        console.log(file.files.length);
        for (let i = 0; i < file.files.length; i++) {
            formData.append("files", file.files[i]);
            console.log(file.files[i]); // "files" will be the key on backend
        }

        const response = await fetch("http://localhost:8000/analyze/", {
            method: "POST",
            body: formData
        });
        ifb.removeChild(spinLoad);
        iline.innerText = "Files uploaded";
        const result = await response.json();
        console.log(result);
        const resView = document.getElementById("workspace");
        resView.innerHTML = '';
        const text1 = document.createElement('p');
        text1.id = 'head1';
        text1.innerText = 'Summary';
        const text2 = document.createElement('p');
        text2.id = 'head2';
        let temp = result.response.split(/\r?\n/);
        let heading = temp[0].trim();
        heading = heading.replace(/\*/g, "");
        heading = heading.trim();
        text2.innerText = heading;
        const text3 = document.createElement('p');
        text3.id= 'head3';
        text3.innerText = result.response;
        resView.appendChild(text1);
        resView.appendChild(text2);
        resView.appendChild(text3);
        uploaded = true;
    }
    catch(err){
        console.log(err);
        iline.innerText = "Error, Try again";

    }
});

window.addEventListener("beforeunload",function () {
  console.log("Browser tried to reload!");
});

file_menu_btn.addEventListener("click",function(){
    if(states["fileMenu"] == false){
        file_menu.style.height = "430px";
        states["fileMenu"] = true;
        listFiles();
    }else{
        states["fileMenu"] = false;
        file_menu.style.height = "0px";
    }
});

chat_menu_btn.addEventListener("click",function(){
    if(states["chatMenu"] == false){
        chat_menu.style.display = "block";
        // document.getElementById("messageBox").addEventListener("keydown",enterKeyCheck);
        document.getElementById("messageBox").focus();
        states["chatMenu"] = true;
    }else{
        // document.getElementById("messageBox").removeEventListener("keydown",enterKeyCheck);
        states["chatMenu"] = false;
        chat_menu.style.display = "none";
    }
})

document.getElementById("sendBtn").addEventListener("click",async function(){
    const query = document.getElementById("messageBox").value;
    document.getElementById("messageBox").value = '';
    document.getElementById('tools').appendChild(spinLoad);
    let msgCont = document.getElementById('chatContent');
    try{
        const uq = document.createElement('div');
        uq.id = 'userMsg';
        uq.innerText = query;
        msgCont.appendChild(uq);
        const res = await fetch("http://localhost:8000/query/",{
            method: 'POST',
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ query: query }) 
        })
        let text = await res.json();
        text = text.response;
        const am = document.createElement('div');
        am.id = 'agentMsg';
        am.innerText = text;
        msgCont.appendChild(am);
        document.getElementById("tools").removeChild(spinLoad);
    }catch(err){
        document.getElementById("tools").removeChild(spinLoad);
        console.log(err);
    }
    
});

document.getElementById("analyticsBtn").addEventListener("click",function(){
    if(uploaded){
        if(!states["qnt"]){
            qntAnalysis.style.width = "90%";
            states["qnt"] = true;
        }
        else{
            states["qnt"] = false;
            qntAnalysis.style.width = "0px";
        }
    }
    else{
        alert("No files found!!");
    }
});

document.getElementById("qntAnlGen").addEventListener("click",async function(){
    try{
        qntAnalysis.appendChild(spinLoad);
        const res = await fetch("http://localhost:8000/qntAnl/",{
            method: 'GET'
        });
        qntAnalysis.innerHTML = '<div id="focusArea" class="focus-box"></div><div id="resultsTable"></div>';
        const data = await res.json();
        const focusText = data.focus || "No focus determined.";
        const results = data.qntRes || [];

        // Display focus summary
        document.getElementById('focusArea').innerText = `Focus: ${focusText}`;

        // Build results table
        const table = document.createElement('table');
        const headerRow = `
        <tr>
            <th>ID</th>
            <th>Word Count</th>
            <th>Sentence Count</th>
            <th>Flesch-Kincaid Grade</th>
            <th>Gunning Fog Index</th>
            <th>Sentiment (Compound)</th>
            <th>Sentiment Breakdown</th>
            <th>Keywords</th>
        </tr>
        `;
        table.innerHTML = headerRow;

        // Populate rows
        results.forEach(doc => {
        const kw = Object.entries(doc.keyword_frequencies)
            .map(([k, v]) => `${k}: ${v}`)
            .join('<br>');

        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${doc.document_id}</td>
            <td>${doc.word_count}</td>
            <td>${doc.sentence_count}</td>
            <td>${doc.flesch_kincaid_grade.toFixed(2)}</td>
            <td>${doc.gunning_fog_index.toFixed(2)}</td>
            <td>${doc.sentiment_compound_score.toFixed(3)}</td>
            <td>
            <div class="keyword-details">
                Neg: ${doc.sentiment_neg.toFixed(3)}<br>
                Neu: ${doc.sentiment_neu.toFixed(3)}<br>
                Pos: ${doc.sentiment_pos.toFixed(3)}
            </div>
            </td>
            <td>
            <details>
                <summary>Show Keywords</summary>
                <div class="keyword-details">${kw}</div>
            </details>
            </td>
        `;
        table.appendChild(row);
        });

        // Inject table into page
        const tableContainer = document.getElementById('resultsTable');
        tableContainer.innerHTML = '';
        tableContainer.appendChild(table);

    } catch (err) {
        console.error('Error fetching results:', err);
        document.getElementById('resultsTable').innerHTML =
        `<div style="color:red;">Error fetching data: ${err.message}</div>`;
    }
});

file.addEventListener("change",function(){
    for(let i = 0;i < file.files.length;i++){
        let content = file.files[i];
        ufiles.push(content.name);
    }
    ifb.removeChild(spinLoad);
    iline.innerText = "Files ready for upload";
    listFiles();
});
