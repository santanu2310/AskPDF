# Lexi.sg RAG Backend Test

> A FastAPI-based Retrieval-Augmented Generation (RAG) backend for legal query answering

&#x20;

---

## 📦 Prerequisites

- Python 3.10 or higher
- [UV](https://github.com/astral-sh/uv) installed globally

  ```bash
  pip install uv
  ```

---

## 🔧 Installation & Setup

### 1. Clone the Repository

```bash
git clone https://github.com/santanu2310/lexi.sg-rag-backend-test.git
cd lexi.sg-rag-backend-test
```

### 2. Create Virtual Environment & Install Dependencies

```bash
uv venv .venv
uv pip sync requirements.txt
uv pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
```

### 3. Activate the Virtual Environment

#### 🐧 Linux/macOS

```bash
source .venv/bin/activate
```

#### 🪟 Windows

```bash
.\.venv\Scripts\activate
```

---

## 📚 Embed Documents

This step will:

- ▼ Optionally delete the existing embeddings
- ▼ Load and embed documents from the `data/` folder
- ▼ Store them in the vector store

```bash
python3 -m app.embed_docs --delete_old_embedding
```

---
## Setup .env file
    create a .env file inside app dir and add the template form example.venv with your credentials

---

## 🏃 Run the Application

Start the FastAPI server in development mode:

```bash
uvicorn app.main:app --reload
```

Navigate to the interactive API docs at:

➡️ [http://localhost:8000/docs](http://localhost:8000/docs)

---

## Input Output Example
### Input
    {
        "query": "Is an insurance company liable to pay compensation if a transport vehicle involved in an accident was being used without a valid permit?"
    }
### Output
    {
    "answer": "No, according to the context provided, the insurance company is not liable to pay compensation if a transport vehicle involved in an accident was being used without a valid permit. The use of a vehicle in a public place without a permit is considered a fundamental statutory infraction and cannot be equated with the absence of a license.\n",
    "citations": [
        {
        "text": "relevant period, the insurer would not be allowed to avoid its liability towards the insured unless the said breach or breaches on the condition of driving licence is/are so fundamental as are found to have contributed to the cause of the accident. The Tribunals in interpreting the policy condition",
        "source": "Amrit Paul Singh v. TATA AIG (SC NO ROUTE Permit insurance Co. Recover from Owner).docx"
        },
        {
        "text": "Vehicles Act, 1988 Sections 166, 66 and 149 Accident - No permit - Liability to pay compensation - Vehicle at time of accident did not have permit - Use of vehicle in public place without permit is fundamental statutory infraction - Said situations cannot be equated with absence of licence or fake",
        "source": "Amrit Paul Singh v. TATA AIG (SC NO ROUTE Permit insurance Co. Recover from Owner).docx"
        }
    ]
    }

_Happy coding!_