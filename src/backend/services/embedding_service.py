# src/backend/services/embedding_service.py
import logging
import uuid
from typing import List
from sentence_transformers import SentenceTransformer
from pinecone import Pinecone, ServerlessSpec

logger = logging.getLogger(__name__)


class EmbeddingService:
    """Service for handling text embeddings using HuggingFace Sentence Transformers and Pinecone."""
    
    def __init__(self, gemini_api_key: str, pinecone_config: dict):
        """Initialize the embedding service with HuggingFace and Pinecone."""
        # Initialize HuggingFace Sentence Transformer (free, local)
        # Using all-MiniLM-L6-v2: 384 dimensions, good quality, 2-3x FASTER!
        # Perfect for t3.micro - much faster embedding generation
        self.embedding_model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
        logger.info("HuggingFace Sentence Transformer loaded successfully (all-MiniLM-L6-v2)")
        
        # Initialize Pinecone
        try:
            self.pc = Pinecone(api_key=pinecone_config['api_key'])
            
            # Create index if it doesn't exist
            if pinecone_config['index_name'] not in self.pc.list_indexes().names():
                self.pc.create_index(
                    name=pinecone_config['index_name'],
                    dimension=pinecone_config['dimension'],
                    metric='cosine',  # Better for semantic similarity
                    spec=ServerlessSpec(
                        cloud=pinecone_config['cloud'],
                        region=pinecone_config['region']
                    )
                )
                logger.info(f"Created new Pinecone index: {pinecone_config['index_name']}")
            
            self.pinecone_index = self.pc.Index(pinecone_config['index_name'])
            self.dimension = pinecone_config['dimension']  # Store dimension for later use
            logger.info("Pinecone initialized successfully")
            
            print(f"\n=== Embedding Service Initialization ===")
            print(f"Embedding Model: HuggingFace sentence-transformers/all-MiniLM-L6-v2 (FAST, FREE)")
            print(f"Pinecone Index: {pinecone_config['index_name']}")
            print(f"Dimension: {pinecone_config['dimension']} (384 for all-MiniLM-L6-v2)")
            print(f"Performance: 2-3x FASTER than all-mpnet-base-v2!")
            print("=======================================\n")
            
        except Exception as e:
            logger.error(f"Failed to initialize Pinecone: {str(e)}")
            print(f"Error: Failed to initialize Pinecone: {str(e)}")
            raise RuntimeError("Pinecone initialization failed")

    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings using HuggingFace Sentence Transformers (free, local)."""
        try:
            logger.info(f"Generating embeddings for {len(texts)} text chunks using HuggingFace")
            print(f"Generating embeddings for {len(texts)} text chunks (local, no API calls)")
            
            # Generate embeddings using HuggingFace Sentence Transformer
            # This runs locally on your machine - no API calls, no quotas!
            embeddings = self.embedding_model.encode(
                texts,
                batch_size=32,  # Process in batches for efficiency
                show_progress_bar=True,
                convert_to_numpy=True
            )
            
            # Convert numpy arrays to lists
            embeddings_list = [emb.tolist() for emb in embeddings]
            
            logger.info(f"Successfully generated {len(embeddings_list)} embeddings locally")
            print(f"✅ Successfully generated {len(embeddings_list)} embeddings (384-dim, fast!)")
            return embeddings_list
            
        except Exception as e:
            logger.error(f"Failed to generate embeddings: {str(e)}")
            print(f"Error: Failed to generate embeddings: {str(e)}")
            raise

    def store_text_embeddings(self, text_chunks: List[str], pdf_uuid: str, original_filename: str = None) -> int:
        """Store text embeddings in Pinecone using HuggingFace embeddings (free, local)."""
        try:
            if not text_chunks:
                logger.warning("No text chunks provided for embedding")
                return 0
                
            logger.info(f"Processing {len(text_chunks)} text chunks for storage")
            print(f"\n=== Pinecone Storage ===")
            print(f"Processing {len(text_chunks)} text chunks")
            
            # Generate embeddings using HuggingFace (local, free)
            embeddings = self.generate_embeddings(text_chunks)
            
            # Prepare vectors for Pinecone
            vectors = [
                (
                    f"{pdf_uuid}_{uuid.uuid4()}",  # Unique ID
                    embedding,  # Embedding vector
                    {"text": chunk, "pdf_uuid": pdf_uuid, "original_filename": original_filename or pdf_uuid}  # Metadata
                )
                for chunk, embedding in zip(text_chunks, embeddings)
            ]
            
            logger.info(f"Upserting {len(vectors)} vectors to Pinecone")
            print(f"Upserting {len(vectors)} vectors")
            print(f"Vector Dimension: {len(vectors[0][1]) if vectors else 'N/A'}")
            
            # Store in Pinecone
            self.pinecone_index.upsert(vectors=vectors)
            
            logger.info(f"Successfully stored {len(vectors)} text embeddings in Pinecone")
            print(f"Successfully stored {len(vectors)} text embeddings")
            print("=======================\n")
            
            return len(vectors)
            
        except Exception as e:
            logger.error(f"Failed to store embeddings: {str(e)}")
            print(f"Error: Failed to store embeddings in Pinecone: {str(e)}")
            return 0

    def search_similar_text(self, query: str, top_k: int = 5) -> List[dict]:
        """Search for similar text chunks using semantic similarity."""
        try:
            # Generate embedding for the query
            query_embedding = self.generate_embeddings([query])[0]
            
            # Search in Pinecone
            results = self.pinecone_index.query(
                vector=query_embedding,
                top_k=top_k,
                include_metadata=True
            )
            
            # Extract relevant information
            similar_texts = []
            for match in results['matches']:
                similar_texts.append({
                    'text': match['metadata']['text'],
                    'pdf_uuid': match['metadata'].get('pdf_uuid', match['metadata'].get('filename', 'unknown')),
                    'original_filename': match['metadata'].get('original_filename', 'unknown'),
                    'score': match['score']
                })
            
            logger.info(f"Found {len(similar_texts)} similar text chunks for query")
            return similar_texts
            
        except Exception as e:
            logger.error(f"Failed to search similar text: {str(e)}")
            return []
