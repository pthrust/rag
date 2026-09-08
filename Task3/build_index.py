import time
from pathlib import Path
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

def build_index():
    # Paths
    docs_dir = "../Task2/knowledge_base"
    index_path = "faiss_index"

    # 1. Load all .md files
    print("[+] Loading documents from knowledge_base/ ...")
    loader = DirectoryLoader(
        docs_dir,
        glob="*.md",
        loader_cls=TextLoader,
        loader_kwargs={"encoding": "utf-8"}
    )
    documents = loader.load()
    print(f"[+] Loaded {len(documents)} documents.")

    # 2. Split into chunks
    print("[+] Splitting into chunks...")
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
        separators=["\n\n", "\n", " ", ""]
    )
    chunks = splitter.split_documents(documents)
    print(f"[+] Obtained {len(chunks)} chunks.")

    # 3. Generate embeddings
    print("[+] Generating embeddings (model all-MiniLM-L6-v2)...")
    embeddings = HuggingFaceEmbeddings(
        model_name="all-MiniLM-L6-v2",
        model_kwargs={"device": "cpu"}
    )

    # 4. Create and save FAISS index
    print("[+] Creating and saving FAISS index...")
    start_time = time.time()
    vectorstore = FAISS.from_documents(chunks, embeddings)
    vectorstore.save_local(index_path)
    elapsed = time.time() - start_time

    print(f"[+] Index saved to {index_path}/")
    print(f"  Indexing time: {elapsed:.2f} sec.")
    print(f"  Total chunks: {len(chunks)}")
    print("  Done!")

    # Optional: test search
    test_query = "Who destroyed the Void Engine?"
    print("\n[+] Test search for query:", test_query)
    results = vectorstore.similarity_search_with_score(test_query, k=3)
    for i, (doc, score) in enumerate(results, 1):
        print(f"\n--- Result {i} (score: {score:.4f}) ---")
        print(f"Source: {doc.metadata.get('source', 'unknown')}")
        print(f"Text: {doc.page_content[:200]}...")

if __name__ == "__main__":
    build_index()