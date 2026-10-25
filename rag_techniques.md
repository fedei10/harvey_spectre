Technique RAG recommandee
Hybrid RAG + Reranking

Combiner :
- Dense Vector Search : recherche semantique.
- BM25 : recherche par mots-cles, articles et references exactes.
- Metadata Filtering : filtrage par code juridique, langue, date et version.
- Reciprocal Rank Fusion (RRF) : fusion des resultats.
- Cross-Encoder Reranker : classement des passages les plus pertinents.
- Parent-Child Retrieval : recuperation des passages avec leur contexte juridique.


2. Stack technique
Frontend	Next.js + TypeScript
Backend	Python + FastAPI
RAG	LangChain 
Embeddings	BGE-M3
Base de donnees	PostgreSQL
Vector Search	pgvector
Recherche lexical	OpenSearch BM25
Reranking	Multilingual Cross-Encoder
LLM	Qwen / modele multilingue evalue
PDF Extraction	PyMuPDF
OCR	PaddleOCR
Stockage PDF	MinIO
Background Jobs	Celery + Redis
Deploiement	Docker
Monitoring	Prometheus + Grafana

Architecture finale recommandee :

Hybrid RAG + Legal-aware Chunking + BGE-M3 + PostgreSQL/pgvector + BM25/OpenSearch + Reranking + LLM multilingue.