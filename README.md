# 🤖 Generative AI Knowledge Assistant & RAG Pipeline

A **Generative AI-powered Knowledge Assistant** that allows users to upload PDF documents and ask questions about their content. The system uses **Retrieval-Augmented Generation (RAG)** to retrieve relevant information from uploaded documents and generate accurate, context-aware responses using an LLM.

---

## 📌 Project Overview

Traditional AI chatbots may generate responses without having access to a user's private documents. This project solves that problem by combining:

* **Document Processing**
* **Text Chunking**
* **Vector Embeddings**
* **Semantic Search**
* **Vector Database**
* **Retrieval-Augmented Generation (RAG)**
* **Large Language Models (LLMs)**

Users can upload a PDF document, and the system processes and stores its content as vector embeddings. When a user asks a question, the application retrieves the most relevant document chunks and provides them as context to the LLM to generate a meaningful answer.

---

## 🚀 Key Features

* 📄 Upload PDF documents
* 🔍 Extract and process document content
* ✂️ Split documents into smaller chunks
* 🧠 Generate semantic embeddings
* 🗄️ Store embeddings in ChromaDB
* 🔎 Perform similarity-based document retrieval
* 🤖 Generate answers using Google Gemini
* ⚡ FastAPI backend
* 🔌 REST API endpoints
* 📚 Context-aware question answering
* 🛡️ Reduces hallucinations by grounding responses in retrieved documents

---

## 🏗️ System Architecture

```text
                ┌──────────────────────┐
                │       User           │
                └──────────┬───────────┘
                           │
                           ▼
                ┌──────────────────────┐
                │   Upload PDF / Ask   │
                │      Question        │
                └──────────┬───────────┘
                           │
                           ▼
                ┌──────────────────────┐
                │      FastAPI         │
                │      Backend         │
                └──────────┬───────────┘
                           │
             ┌─────────────┴─────────────┐
             │                           │
             ▼                           ▼
    ┌─────────────────┐         ┌─────────────────┐
    │ Document Loader │         │ User Question   │
    │   PyPDFLoader   │         └────────┬────────┘
    └────────┬────────┘                  │
             ▼                           ▼
    ┌─────────────────┐         ┌─────────────────┐
    │ Text Splitter   │         │ Query Embedding │
    │ Recursive       │         └────────┬────────┘
    │ Character       │                  │
    │ Text Splitter   │                  │
    └────────┬────────┘                  │
             ▼                           │
    ┌─────────────────┐                  │
    │ Hugging Face    │                  │
    │ Embeddings      │                  │
    └────────┬────────┘                  │
             │                           │
             ▼                           ▼
    ┌─────────────────────────────────────────────┐
    │                 ChromaDB                    │
    │              Vector Database                │
    └──────────────────────┬──────────────────────┘
                           │
                           ▼
                  ┌─────────────────┐
                  │    Retriever    │
                  └────────┬────────┘
                           │
                           ▼
                  ┌─────────────────┐
                  │ Retrieved       │
                  │ Context         │
                  └────────┬────────┘
                           │
                           ▼
                  ┌─────────────────┐
                  │  Google Gemini  │
                  │      LLM        │
                  └────────┬────────┘
                           │
                           ▼
                  ┌─────────────────┐
                  │ Generated Answer│
                  └─────────────────┘
```

---

## 🔄 RAG Workflow

The application follows these major steps:

### 1. Document Upload

The user uploads a PDF document through the FastAPI API.

### 2. Document Loading

The PDF content is extracted using `PyPDFLoader`.

### 3. Text Splitting

Large documents are divided into smaller chunks using `RecursiveCharacterTextSplitter`.

Example configuration:

```text
Chunk Size: 500
Chunk Overlap: 100
```

Chunking makes it easier to retrieve only the relevant parts of a document.

### 4. Embedding Generation

Each text chunk is converted into a numerical vector using:

```text
sentence-transformers/all-MiniLM-L6-v2
```

These vectors represent the semantic meaning of the text.

### 5. Vector Storage

The generated embeddings are stored in **ChromaDB**, which acts as the vector database.

### 6. Question Processing

When the user asks a question, the question is converted into an embedding.

### 7. Semantic Retrieval

The retriever searches ChromaDB for document chunks that are semantically similar to the user's question.

### 8. Context + Question

The retrieved document chunks are combined with the user's question and sent to the LLM.

### 9. Response Generation

Google Gemini generates the final answer using the retrieved document context.

---

## 🛠️ Technology Stack

### Programming Language

* Python

### Backend

* FastAPI
* Uvicorn

### Generative AI

* Google Gemini
* LangChain
* Retrieval-Augmented Generation (RAG)

### Embeddings

* Hugging Face
* Sentence Transformers
* `all-MiniLM-L6-v2`

### Vector Database

* ChromaDB

### Document Processing

* PyPDFLoader
* RecursiveCharacterTextSplitter

### API

* REST API
* FastAPI Swagger/OpenAPI

### Development Tools

* Git
* GitHub
* Python Virtual Environment
* `.env` environment variables

---

## 📁 Project Structure

```text
generative-ai-knowledge-assistant/
│
├── backend/
│   │
│   ├── app/
│   │   ├── main.py
│   │   │
│   │   ├── api/
│   │   │   └── upload.py
│   │   │
│   │   ├── rag/
│   │   │   ├── loader.py
│   │   │   ├── splitter.py
│   │   │   ├── embeddings.py
│   │   │   ├── vectorstore.py
│   │   │   └── retriever.py
│   │   │
│   │   └── llm/
│   │       ├── llm.py
│   │       └── chat.py
│   │
│   ├── chroma_db/
│   │
│   ├── .env
│   ├── requirements.txt
│   └── Dockerfile
│
├── frontend/
│
├── .gitignore
└── README.md
```

---

## 🔌 API Endpoints

### Health Check

```http
GET /
```

Returns a basic response confirming that the API is running.

### Health Endpoint

```http
GET /health
```

Checks the health/status of the backend.

### Upload Document

```http
POST /upload
```

Uploads a PDF and processes it through the RAG pipeline.

### Ask Question

```http
POST /ask
```

Accepts a user question and returns an AI-generated answer based on the indexed documents.

---

## ⚙️ Installation

### 1. Clone the Repository

```bash
git clone <your-github-repository-url>
```

Navigate to the project:

```bash
cd generative-ai-knowledge-assistant
```

---

### 2. Create a Virtual Environment

```bash
python -m venv venv
```

Activate the environment on Windows:

```bash
venv\Scripts\activate
```

---

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

### 4. Configure Environment Variables

Create a `.env` file inside the backend directory.

```env
GOOGLE_API_KEY=your_google_api_key
MODEL_NAME=gemini-2.5-flash
LLM_PROVIDER=gemini
CHROMA_DB_DIR=chroma_db
```

**Never upload your API key to GitHub.**

---

## ▶️ Running the Application

Navigate to the backend:

```bash
cd backend
```

Start the FastAPI server:

```bash
uvicorn app.main:app --reload
```

The API will run at:

```text
http://127.0.0.1:8000
```

Swagger API documentation:

```text
http://127.0.0.1:8000/docs
```

---

## 🧪 Example Workflow

### Step 1 — Upload a PDF

Upload a document such as:

```text
Machine_Learning_Notes.pdf
```

The application:

```text
PDF
 ↓
Text Extraction
 ↓
Text Chunking
 ↓
Embedding Generation
 ↓
ChromaDB
```

### Step 2 — Ask a Question

Example:

```text
What is supervised learning?
```

### Step 3 — Retrieval

The system searches the vector database for relevant content.

```text
Question
   ↓
Query Embedding
   ↓
Similarity Search
   ↓
Relevant Document Chunks
```

### Step 4 — Generate Answer

The retrieved context is passed to Gemini.

```text
Retrieved Context + User Question
                 ↓
             Gemini LLM
                 ↓
          Final Answer
```

---

## 🧠 Why RAG?

Large Language Models can sometimes generate incorrect or unsupported information.

RAG improves reliability by providing the LLM with relevant information retrieved from the user's documents.

### Without RAG

```text
User Question
      ↓
     LLM
      ↓
Generated Answer
```

### With RAG

```text
User Question
      ↓
Vector Search
      ↓
Relevant Documents
      ↓
Context
      ↓
     LLM
      ↓
Grounded Answer
```

This makes the system particularly useful for **private documents, technical documentation, research papers, manuals, reports, and knowledge bases**.

---

## 📊 Example Use Cases

* 📚 Personal study assistant
* 📄 PDF question-answering system
* 🏢 Enterprise knowledge assistant
* 🔬 Research paper assistant
* 📖 Educational document assistant
* 💻 Technical documentation assistant
* 📝 Company knowledge-base chatbot
* 📑 Business report analysis

---

## 🔐 Security

The project uses environment variables to store sensitive configuration such as API keys.

Example:

```env
GOOGLE_API_KEY=your_api_key
```

The `.env` file should be excluded from Git:

```gitignore
.env
venv/
.venv/
__pycache__/
*.pyc
chroma_db/
```

---

## 🚀 Future Improvements

* [ ] Add a modern frontend interface
* [ ] Support multiple document formats
* [ ] Add document deletion functionality
* [ ] Add conversation history
* [ ] Add streaming LLM responses
* [ ] Add source citations for retrieved chunks
* [ ] Add authentication and user accounts
* [ ] Support multiple users and separate knowledge bases
* [ ] Add hybrid search
* [ ] Improve chunking strategies
* [ ] Add reranking
* [ ] Deploy using Docker
* [ ] Deploy backend to a cloud platform
* [ ] Add monitoring and logging

---

## 📈 Skills Demonstrated

This project demonstrates practical experience with:

* Python
* FastAPI
* REST APIs
* Generative AI
* Large Language Models
* Retrieval-Augmented Generation
* LangChain
* Prompt Engineering
* Vector Databases
* ChromaDB
* Semantic Search
* Text Embeddings
* Hugging Face
* Sentence Transformers
* PDF Processing
* Environment Configuration
* Git & GitHub
* Docker

---

## 💼 Resume Description

You can describe the project on your resume as:

**Generative AI Knowledge Assistant & RAG Pipeline**

> Developed a Generative AI-powered document question-answering system using Python, FastAPI, LangChain, ChromaDB, Hugging Face embeddings, and Google Gemini. Implemented a complete RAG pipeline for PDF ingestion, text chunking, semantic embedding generation, vector storage, similarity-based retrieval, and context-aware response generation through REST APIs.

---

## 👨‍💻 Author

**Thumula Manvith Reddy**

Computer Science Engineering — Artificial Intelligence & Machine Learning

### Technologies

```text
Python | FastAPI | LangChain | RAG | Gemini
ChromaDB | Hugging Face | Machine Learning
REST APIs | Git | GitHub | Docker
```

---

## ⭐ If You Find This Project Useful

Give the repository a ⭐ on GitHub and feel free to explore the project.
