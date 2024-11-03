# def create_embeddings()

#  # Load all PDFs from the "/workspaces/Rag_ht/data/pdfs" folder
#             .loader = PyPDFDirectoryLoader(Config.PDF_DIR)
#             .docs = .loader.load()

#             # Split the loaded documents into chunks
#             .text_splitter = RecursiveCharacterTextSplitter(
#                 chunk_size=Config.CHUNK_SIZE, chunk_overlap=Config.CHUNK_OVERLAB
#             )
#             .final_documents = (
#                 .text_splitter.split_documents(.docs)
#             )

#             # Create vector embeddings for the split documents
#             .vectors = FAISS.from_documents(
#                 .final_documents, .embeddings
#             )

#             # Save FAISS index to disk
#             .vectors.save_local(vector_store_path)
#             write("Vector store saved to disk.")

#         # Display the total processing time
#         end = time.time()
#         total_time = end - start
#         write(f"Total time to process documents: {round(total_time/60, 2)} minutes.")
