# Deploy options for Barca Analytics (Streamlit)

Pilihan deploy cepat:

A) Streamlit Community Cloud
- Hubungkan repo GitHub (ganendrard/barca-analytics) ke Streamlit Cloud.
- Start command: `streamlit run streamlit_app.py`
- Build akan menginstall dependencies dari requirements.txt.

B) Render
- New Web Service -> Connect GitHub repo -> Branch main
- Build command: `pip install -r requirements.txt`
- Start command: `streamlit run streamlit_app.py --server.port $PORT`

C) Docker (GHCR + host)
- Buat secret `GHCR_TOKEN` (PAT with packages:write) di repo Settings > Secrets.
- Jalankan workflow `publish` secara manual dari Actions untuk build & push image.
- Tarik image: `docker pull ghcr.io/<owner>/barca-analytics:latest`
- Run: `docker run -p 8501:8501 ghcr.io/<owner>/barca-analytics:latest`

Notes:
- Untuk workflow yang men-commit hasil kembali ke repo, Anda perlu PAT (REPO_PAT) disimpan sebagai secret.
- Setelah Anda menambahkan file workflow, jalankan Actions -> pilih workflow "CI - fetch & dashboard" -> Run workflow (workflow_dispatch) untuk memicu proses pertama.
