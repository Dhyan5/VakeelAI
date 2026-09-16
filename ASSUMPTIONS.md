# Legal RAG Platform - Assumptions

## Architectural Decisions

### Embedding Model: paraphrase-multilingual-MiniLM-L12-v2
- **Reasoning**: This model covers 50+ languages including English, Hindi (Devanagari), and Kannada (Kannada script) in a shared embedding space. It enables cross-lingual retrieval without a separate translation step. The model is 470MB downloaded, ~1GB RAM at runtime. An alternative like mMiniLM-L12-v2 would also work but this is the most established multilingual option.

### NumPy-based Retrieval (not FAISS/Chroma)
- **Reasoning**: For a local-first, low-resource setup with a knowledge base of ~1000-5000 chunks, NumPy dot products are fast enough (<10ms on modern hardware). FAISS adds complexity and dependencies. This aligns with the $0 infrastructure and no-Docker-local constraints.

### Groq API (llama-3.3-70b-versatile)
- **Reasoning**: As of 2026, this is the fastest and most capable free-tier model on Groq. 8k context window is sufficient for legal RAG. If this model is deprecated, the code is parameterized to swap to another model.

### Turso (libSQL) for User Data
- **Reasoning**: Turso offers a free tier with no credit card required for the database. Supabase would also work but requires card for the free tier. SQLite works locally but Turso is better for deployed state.

### Vercel for Frontend
- **Reasoning**: Vercel offers free static hosting with GitHub integration. Cloudflare Pages would be an equally valid alternative with similar features.

### Hugging Face Spaces for Backend
- **Reasoning**: HF Spaces allows Docker-based deployment without local Docker. The build happens remotely after git push. This satisfies the "no local Docker" constraint while still enabling Tesseract OCR.

### Tesseract OCR (local install)
- **Reasoning**: Tesseract is the most reliable open-source OCR engine. The Windows/macOS/Linux installation instructions are well-documented. This is the only non-Pip dependency.

### Legal-Aware Chunking by Section Headers
- **Reasoning**: Legal texts have structured section headers (Section 302, S. 153, etc.). Chunking by these boundaries preserves the citation structure and improves retrieval relevance compared to naive fixed-size windows.

## Platform Decisions

### English as Internal Retrieval Language
- **Reasoning**: The knowledge base is primarily English. Converting all queries to English for retrieval (via LLM or simple translation rules) allows one unified index. Final output is translated back to user's language.

### Streamed Response Display
- **Reasoning**: Groq is fast. Streaming the response feels responsive. The frontend handles partial text rendering.

### JWT Authentication
- **Reasoning**: Simple token-based auth for local development and small-scale deployment. For production at scale, OAuth2 would be preferred.

### No Persistent File Storage on Free Tier
- **Reasoning**: HF Spaces free tier doesn't guarantee persistent disk. Files are processed in-memory and discarded after analysis. Only analysis results (not raw files) are stored in the database.

## Language Support Assumptions

### Kannada, Hindi, English Only
- **Reasoning**: Specified in requirements. The embedding model supports these scripts, and the legal corpus is primarily English with potential for code-mixed input.

### Input Language Auto-Detection
- **Reasoning**: langdetect or fasttext can identify the language from the query text. Users can override the auto-detected language.

## Security Assumptions

### HTTPS via HF Spaces/Vercel
- **Reasoning**: Both platforms provide HTTPS by default. TLS terminates at the CDN/proxy.

### Secrets via Environment Variables
- **Reasoning**: Environment variables are the standard way to handle secrets in containerized/cloud deployments. HF Spaces and Vercel both provide secret management.

### No LLM Training on User Data
- **Reasoning**: User cases are stored for history but not used to train models. This is a privacy best practice.

## Deployment Assumptions

### GitHub as Code Host
- **Reasoning**: Standard for open-source and private repos. Auto-deploy to both HF Spaces and Vercel via GitHub Actions or webhooks.

### Build-Time vs Runtime Environment Variables
- **Reasoning**: Vercel uses build-time env vars for static assets, runtime env vars for client-side fetch. HF Spaces uses runtime env vars for the Docker container.

## Legal Disclaimer Assumptions

### Generic Disclaimer Language
- **Reasoning**: Not legal advice. The disclaimer must be visible and clear but doesn't require jurisdiction-specific language for a research tool.

## Performance Assumptions

### Knowledge Base Size < 10000 chunks
- **Reasoning**: NumPy retrieval is sufficient for this scale. If the KB grows to 100k+ chunks, FAISS would become necessary.

### Single User Query Processing
- **Reasoning**: Each query triggers one embedding call, one retrieval, and one Groq call. Response time should be <5 seconds.

## Testing Assumptions

### Sample Case Testing
- **Reasoning**: Three test queries (English, Hindi, Kannada) verify cross-lingual retrieval works. The test suite uses pytest.
