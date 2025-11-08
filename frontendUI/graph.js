import mermaid from 'mermaid';
import { writeFileSync } from 'fs';

const diagram = `
flowchart TD
  A[Start] --> B{Is it working?}
  B -->|Yes| C[Great!]
  B -->|No| D[Fix it]
  D --> B
`;

async function genGraph(code){
  const { svg } = await mermaid.render('flowchart1', code);
  writeFileSync('diagram.svg', svg);
  console.log('SVG flowchart saved to diagram.svg');
}

async function makeGraph(code){
    const diagram = await mermaid.mermaidAPI.getDiagramFromText(code);
    const graph = diagram.getParser().yy.getGraph();
    console.log(graph);
    return {diagram,graph};
}
