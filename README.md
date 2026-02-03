# Barca Analytics

Repo ini berisi script dan contoh output dashboard analitik untuk FC Barcelona.

Tujuan:
- Ambil data publik (FBref) untuk Barcelona (musim ini & musim sebelumnya)
- Lakukan ETL sederhana, agregasi per musim dan per bulan
- Hasilkan chart interaktif (Plotly) dan export Excel ringkasan
- Demo Streamlit untuk dashboard interaktif

Quickstart
1. Buat virtualenv dan install dependency:
   python -m venv .venv
   source .venv/bin/activate  # Linux / macOS
   .\.venv\Scripts\activate   # Windows PowerShell
   pip install -r requirements.txt

2. Jalankan fetch_data.py untuk mengunduh sample data dari FBref (team match logs):
   python fetch_data.py

   File CSV disimpan ke folder data/: data/matches.csv dan data/team_match_stats.csv

3. Jalankan dashboard.py untuk menghasilkan ringkasan dan chart HTML/Excel:
   python dashboard.py

   Output disimpan di folder output/

4. (Opsional) Jalankan demo Streamlit:
   streamlit run streamlit_app.py

Lisensi
Repo ini dilisensikan di bawah MIT License (file LICENSE).