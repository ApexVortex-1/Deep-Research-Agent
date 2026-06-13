# 🔭 Deep Research Agent

🌐 Live Demo: https://deep-research-agent-ai.streamlit.app/

A multi-agent AI research system built with LangGraph, LangChain, Streamlit, and Groq LLMs.

The system simulates a complete research workflow using specialized AI agents that collaborate to generate structured research reports.

---

## ✨ Features

- 🗺️ Planner Agent
  - Breaks research topics into structured plans.
  - Generates sections, subsections, and research questions.

- 🔍 Research Agent
  - Collects relevant information from web search tools.
  - Summarizes findings.

- ✏️ Writer Agent
  - Produces detailed research reports.
  - Converts collected information into readable content.

- 🛡️ Critic Agent
  - Reviews generated reports.
  - Suggests improvements and refinements.

- 🔁 Iterative Research Workflow
  - Supports multiple refinement cycles.
  - Improves report quality through feedback loops.

- 📄 PDF Export
  - Download generated reports as PDF.

- 🎨 Modern Streamlit UI
  - Dark theme interface.
  - Agent status tracking.
  - Research history sidebar.
  - Progress visualization.

---

## 🏗️ Architecture

User Query  
→ Planner Agent  
→ Research Agent  
→ Writer Agent  
→ Critic Agent  
→ Final Research Report  

---

## 📂 Project Structure

deep-research-agent/  
├── agents/  
│   ├── planner.py  
│   ├── researcher.py  
│   ├── writer.py  
│   └── critic.py  
│  
├── graph/  
│   ├── state.py  
│   ├── workflow.py  
│   └── nodes/  
│  
├── tools/  
│   └── search_tool.py  
│  
├── app.py  
│  
├── test_planner.py  
├── test_pipeline.py  
├── requirements.txt  
├── .env  
└── README.md  

---

## ⚙️ Installation

### 1. Clone Repository

```bash
git clone https://github.com/ApexVortex-1/Deep-Research-Agent.git

cd Deep-Research-Agent
```

### 2. Create Conda Environment

```bash
conda create -n deep-research python=3.11

conda activate deep-research
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Create Environment Variables

Create a `.env` file:

```env
GROQ_API_KEY=your_groq_api_key
TAVILY_API_KEY=your_tavily_api_key
```

---

## 🚀 Running the Project

### Test Planner Agent

```bash
python test_planner.py
```

### Test Full Pipeline

```bash
python test_pipeline.py
```

### Launch Streamlit UI

```bash
streamlit run app.py
```

---

## 🔄 Workflow Example

Input:

```text
Agentic AI and Deep Research Systems
```

Output:

```text
1. Research Plan
2. Information Gathering
3. Report Generation
4. Critique & Refinement
5. Final Research Report
```

---

## 🧠 Tech Stack

- Python
- LangChain
- LangGraph
- Streamlit
- Groq LLMs
- ReportLab

---

## 🎯 Future Improvements

- Real-time agent streaming
- Live web search citations
- LangSmith tracing integration
- Multi-model support
- RAG-based research memory
- Agent performance analytics
- Export to DOCX and Markdown

---

## 👨‍💻 Author

Ahmed Taha

GitHub:

https://github.com/ApexVortex-1

---

## 📜 License

Apache License 2.0

Feel free to use, modify, and contribute.