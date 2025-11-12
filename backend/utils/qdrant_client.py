"""
Qdrant Vector Database Client

Handles all interactions with Qdrant for storing and retrieving patient cases.
Uses embeddings to enable semantic search across patient history.
"""

import os
import uuid
from typing import List, Dict, Any, Optional
from datetime import datetime
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    VectorParams,
    PointStruct,
    Filter,
    FieldCondition,
    MatchValue,
)
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv

load_dotenv()


class MedicalQdrantClient:
    """
    Client for storing and retrieving medical cases in Qdrant.

    Collections:
    - patient_cases: Stores complete patient encounters with embeddings
    - clinical_patterns: Stores symptom patterns for pattern matching
    """

    def __init__(
        self,
        url: str = None,
        api_key: str = None,
        embedding_model: str = "all-MiniLM-L6-v2"
    ):
        """
        Initialize Qdrant client and embedding model.

        Args:
            url: Qdrant server URL (default from env)
            api_key: Qdrant API key (default from env)
            embedding_model: SentenceTransformer model name
        """
        self.url = url or os.getenv("QDRANT_URL", "http://localhost:6333")
        self.api_key = api_key or os.getenv("QDRANT_API_KEY")

        # Initialize Qdrant client
        self.client = QdrantClient(
            url=self.url,
            api_key=self.api_key,
            timeout=10.0
        )

        # Initialize embedding model
        print(f"🔧 Loading embedding model: {embedding_model}...")
        self.embedding_model = SentenceTransformer(embedding_model)
        self.embedding_dim = self.embedding_model.get_sentence_embedding_dimension()
        print(f"✅ Embedding model loaded (dimension: {self.embedding_dim})")

        # Collection names
        self.PATIENT_CASES_COLLECTION = "patient_cases"

        # Initialize collections
        self._initialize_collections()

    def _initialize_collections(self):
        """Create collections if they don't exist."""
        try:
            # Check if patient_cases collection exists
            collections = self.client.get_collections().collections
            collection_names = [c.name for c in collections]

            if self.PATIENT_CASES_COLLECTION not in collection_names:
                print(f"📦 Creating collection: {self.PATIENT_CASES_COLLECTION}")
                self.client.create_collection(
                    collection_name=self.PATIENT_CASES_COLLECTION,
                    vectors_config=VectorParams(
                        size=self.embedding_dim,
                        distance=Distance.COSINE  # Cosine similarity for semantic search
                    ),
                )
                print(f"✅ Collection created: {self.PATIENT_CASES_COLLECTION}")
            else:
                print(f"✅ Collection exists: {self.PATIENT_CASES_COLLECTION}")

        except Exception as e:
            print(f"⚠️  Error initializing collections: {e}")
            print("   Make sure Qdrant is running: docker-compose up -d qdrant")

    def create_embedding(self, text: str) -> List[float]:
        """
        Create embedding vector from text.

        Args:
            text: Input text to embed

        Returns:
            Embedding vector as list of floats
        """
        return self.embedding_model.encode(text).tolist()

    def store_patient_case(
        self,
        patient_id: str,
        case_data: Dict[str, Any],
        session_id: Optional[str] = None
    ) -> str:
        """
        Store a patient case in Qdrant with embeddings.

        Args:
            patient_id: Unique patient identifier
            case_data: Dictionary containing structured_data, clinical_summary, soap_report
            session_id: Optional session identifier

        Returns:
            Point ID (UUID) of stored case
        """
        try:
            # Create searchable text from the case
            searchable_text = self._create_searchable_text(case_data)

            # Generate embedding
            embedding = self.create_embedding(searchable_text)

            # Create point ID (proper UUID format required by Qdrant)
            point_id = str(uuid.uuid4())

            # Prepare payload (metadata)
            payload = {
                "patient_id": patient_id,
                "session_id": session_id,
                "timestamp": datetime.utcnow().isoformat(),
                "chief_complaint": case_data.get("chief_complaint", ""),
                "symptoms": case_data.get("symptoms", []),
                "medical_history": case_data.get("medical_history", []),
                "assessment": case_data.get("assessment", ""),
                "searchable_text": searchable_text,  # Store for debugging
            }

            # Upload to Qdrant
            self.client.upsert(
                collection_name=self.PATIENT_CASES_COLLECTION,
                points=[
                    PointStruct(
                        id=point_id,
                        vector=embedding,
                        payload=payload
                    )
                ]
            )

            print(f"💾 Stored case for patient {patient_id} in Qdrant")
            return point_id

        except Exception as e:
            print(f"❌ Error storing case in Qdrant: {e}")
            raise

    def search_similar_cases(
        self,
        query_text: str,
        limit: int = 5,
        score_threshold: float = 0.7,
        patient_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for similar patient cases using semantic search.

        Args:
            query_text: Text to search for (symptoms, complaints, etc.)
            limit: Maximum number of results
            score_threshold: Minimum similarity score (0-1)
            patient_id: Optional filter to search only this patient's history

        Returns:
            List of similar cases with scores
        """
        try:
            # Generate query embedding
            query_embedding = self.create_embedding(query_text)

            # Build filter if patient_id provided
            search_filter = None
            if patient_id:
                search_filter = Filter(
                    must=[
                        FieldCondition(
                            key="patient_id",
                            match=MatchValue(value=patient_id)
                        )
                    ]
                )

            # Search Qdrant
            results = self.client.search(
                collection_name=self.PATIENT_CASES_COLLECTION,
                query_vector=query_embedding,
                limit=limit,
                score_threshold=score_threshold,
                query_filter=search_filter
            )

            # Format results
            similar_cases = []
            for result in results:
                similar_cases.append({
                    "score": result.score,
                    "patient_id": result.payload.get("patient_id"),
                    "timestamp": result.payload.get("timestamp"),
                    "chief_complaint": result.payload.get("chief_complaint"),
                    "symptoms": result.payload.get("symptoms"),
                    "assessment": result.payload.get("assessment"),
                })

            print(f"🔍 Found {len(similar_cases)} similar cases")
            return similar_cases

        except Exception as e:
            print(f"❌ Error searching Qdrant: {e}")
            return []

    def get_patient_history(
        self,
        patient_id: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get all cases for a specific patient (chronological history).

        Args:
            patient_id: Patient identifier
            limit: Maximum number of cases to retrieve

        Returns:
            List of patient's previous cases
        """
        try:
            # Scroll through all points with this patient_id
            results, _ = self.client.scroll(
                collection_name=self.PATIENT_CASES_COLLECTION,
                scroll_filter=Filter(
                    must=[
                        FieldCondition(
                            key="patient_id",
                            match=MatchValue(value=patient_id)
                        )
                    ]
                ),
                limit=limit,
                with_payload=True,
                with_vectors=False
            )

            # Format results
            history = []
            for point in results:
                history.append({
                    "timestamp": point.payload.get("timestamp"),
                    "chief_complaint": point.payload.get("chief_complaint"),
                    "symptoms": point.payload.get("symptoms"),
                    "assessment": point.payload.get("assessment"),
                })

            # Sort by timestamp (newest first)
            history.sort(key=lambda x: x["timestamp"], reverse=True)

            print(f"📚 Retrieved {len(history)} previous cases for patient {patient_id}")
            return history

        except Exception as e:
            print(f"❌ Error retrieving patient history: {e}")
            return []

    def _create_searchable_text(self, case_data: Dict[str, Any]) -> str:
        """
        Create a searchable text representation of a case for embedding.

        This combines the most relevant clinical information into a single text
        that captures the semantic meaning of the case.
        """
        parts = []

        # Chief complaint
        if "chief_complaint" in case_data:
            parts.append(f"Chief complaint: {case_data['chief_complaint']}")

        # Symptoms
        if "symptoms" in case_data and case_data["symptoms"]:
            symptoms_str = ", ".join(case_data["symptoms"])
            parts.append(f"Symptoms: {symptoms_str}")

        # Medical history
        if "medical_history" in case_data and case_data["medical_history"]:
            history_str = ", ".join(case_data["medical_history"])
            parts.append(f"Medical history: {history_str}")

        # Assessment
        if "assessment" in case_data:
            parts.append(f"Assessment: {case_data['assessment']}")

        return " | ".join(parts)

    def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics about the patient cases collection."""
        try:
            collection_info = self.client.get_collection(
                collection_name=self.PATIENT_CASES_COLLECTION
            )
            return {
                "total_cases": collection_info.points_count,
                "vector_dimension": self.embedding_dim,
                "status": collection_info.status
            }
        except Exception as e:
            return {"error": str(e)}


# Singleton instance
_qdrant_client = None


def get_qdrant_client() -> MedicalQdrantClient:
    """Get or create the Qdrant client singleton."""
    global _qdrant_client
    if _qdrant_client is None:
        _qdrant_client = MedicalQdrantClient()
    return _qdrant_client
