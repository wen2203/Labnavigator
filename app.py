import streamlit as st  # Import Streamlit om een webapp te maken
import os  # Import os voor bestands- en mapbewerkingen
from labmate import connect_db, calculate_tm  # Eigen functies: verbinden met DB, smelttemp berekenen
from genemate import convert_fastq_to_fasta, download_gene  # Eigen functies voor bestand en gen ophalen
from Bio import SeqIO
import io
import re
import io
# Verbind met de database en krijg cursor om queries uit te voeren
conn, c = connect_db()

st.image("Untitled_Artwork.png", width=500)

# Titel bovenaan de webapp
st.title("✧˖✧ Lab Navigator ✧˖✧")
st.write("Welkom bij Lab Navigator! " \
"Dit is een hulpmiddel om eenvoudig het lab te navigeren. " \
"Maak een keuze welke tool je wilt gebruiken, zoals een planner om experimenten in te plannen," \
" Gene Fetcher om gensequenties te downloaden, een FASTQ naar FASTA converter en de smelttemperatuur-rekenmachine.")

# Maak een dropdownmenu (selectbox) waarin de gebruiker een optie kiest
menu = st.selectbox("Maak een keuze uit de toolbox:", [
    "Nieuw experiment",
    "Bekijk experimenten",
    "Rond experiment af",
    "Verwijder experiment",
    "Exporteer CSV",
    "Smelttemperatuur berekenen",
    "Convert FASTQ → FASTA",
    "Gen downloaden (NCBI database)",
    "Afsluiten"
])

# Voor elke optie wordt iets anders getoond en uitgevoerd:

if menu == "Nieuw experiment":
    st.header("Nieuw experiment toevoegen")
    # Hier vraagt de app om gegevens van het experiment
    name = st.text_input("Experimentnaam")
    date = st.date_input("Datum:")
    time = st.time_input("Tijd:")
    
    duration = st.number_input("Duur in minuten", min_value=1)  # Getal voor duur
    user = st.text_input("Gebruiker")  # Naam van de persoon

    # Als gebruiker op knop 'Toevoegen' klikt:
    if st.button("Toevoegen"):
        # Zet date en time om naar string formats
        date_str = date.strftime("%Y-%m-%d")
        time_str = time.strftime("%H:%M")

        # Voeg de ingevoerde data toe in de database
        c.execute('''
            INSERT INTO experiments (name, date, start_time, duration, user)
            VALUES (?, ?, ?, ?, ?)
        ''', (name, date_str, time_str, duration, user))
        # Sla de wijziging op in DB
        conn.commit()
        # Laat een succesbericht zien
        st.success("Experiment toegevoegd!")

elif menu == "Bekijk experimenten":
    st.header("Experimentenlijst")
    c.execute("SELECT * FROM experiments")
    rows = c.fetchall()
    if rows:
        for row in rows:
            st.write(f"ID: {row[0]} | Naam: {row[1]} | Datum: {row[2]} | Start: {row[3]} | "
                     f"Duur: {row[4]} min | Gebruiker: {row[5]} | Status: {row[6]}")
    else:
        st.info("Geen experimenten gevonden.")

elif menu == "Rond experiment af":
    st.header("Markeer experiment als afgerond")
    c.execute("SELECT id, name, date, start_time, duration, user, status FROM experiments WHERE status != 'done'")
    rows = c.fetchall()

    if rows:
        opties = [f"{row[0]} - {row[1]} ({row[2]}) Status: {row[6]}" for row in rows]
        keuze = st.selectbox("Selecteer experiment om af te ronden", opties)
        exp_id = int(keuze.split(" - ")[0])

        if st.button("Afronden"):
            c.execute("UPDATE experiments SET status='done' WHERE id=?", (exp_id,))
            conn.commit()
            st.success(f"Experiment {exp_id} gemarkeerd als afgerond.")
    else:
        st.info("Geen openstaande experimenten gevonden.")

elif menu == "Verwijder experiment":
    st.header("Verwijder experiment")
    c.execute("SELECT id, name, date, start_time, duration, user, status FROM experiments")
    rows = c.fetchall()
    if rows:
        opties = [f"{row[0]} - {row[1]} ({row[2]}) Status: {row[6]}" for row in rows]
        keuze = st.selectbox("Selecteer experiment om te verwijderen", opties)
        exp_id = int(keuze.split(" - ")[0])
    
        if st.button("Verwijderen"):
            c.execute("DELETE FROM experiments WHERE id=?", (exp_id,))
            conn.commit()
            st.success(f"Experiment {exp_id} verwijderd.")
    else:
        st.info("Geen openstaande experimenten gevonden.")

elif menu == "Exporteer CSV":
    st.header("Exporteer experimenten naar CSV")
    if st.button("Exporteer CSV"):
        c.execute("SELECT * FROM experiments")
        rows = c.fetchall()
        import csv
        output_dir = "output"
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, "experiments_export.csv")
        with open(output_path, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['ID','Naam','Datum','Starttijd','Duur','Gebruiker','Materialen','Locatie','Status'])
            writer.writerows(rows)
        st.success(f"✅ CSV-bestand opgeslagen in: {output_path}")

elif menu == "Smelttemperatuur berekenen":
    st.header("Smelttemperatuur berekenen")
    seq = st.text_input("Voer DNA-sequentie in (A,T,G,C):")
    if st.button("Bereken"):
        resultaat = calculate_tm(seq)
        st.write(resultaat)


elif menu == "Convert FASTQ → FASTA":
    from Bio import SeqIO
    import io

    st.title("FASTQ naar FASTA Converter")

    uploaded_file = st.file_uploader("Upload FASTQ-bestand", type=["fastq"])

    if uploaded_file is not None:
        out_name = st.text_input("Naam outputbestand (zonder .fasta):", value="output")

        if st.button("Converteren"):
            if not out_name.endswith(".fasta"):
                out_name += ".fasta"

            # Open bestand als tekst
            fastq_text = uploaded_file.getvalue().decode("utf-8")
            fastq_io = io.StringIO(fastq_text)
            fasta_io = io.StringIO()

            SeqIO.convert(fastq_io, "fastq", fasta_io, "fasta")
            fasta_str = fasta_io.getvalue()

            st.success("✅ Conversie gelukt!")
            st.download_button(
                label="⬇️ Download FASTA bestand",
                data=fasta_str,
                file_name=out_name,
                mime="text/plain"
            )


elif menu == "Gen downloaden (NCBI database)":
    from Bio import Entrez
    Entrez.email = "your.email@example.com"  # ← vervang met jouw echte e-mail

    st.header("Gen downloaden van NCBI")
    gene = st.text_input("Gennaam:")
    organism = st.selectbox("Organisme:", [
        "Homo sapiens",
        "Mus musculus",
        "Rattus norvegicus",
        "Danio rerio",
        "Gallus gallus domesticus",
        "Oryctolagus cuniculus",
        "Sus scrofa domesticus",
        "Macaca mulatta",
        "Cavia porcellus",
        "Drosophila melanogaster",
        "Gorilla gorilla"
    ])

    def fetch_gene_data(gene_name, organism):
        try:
            handle = Entrez.esearch(db="nucleotide", term=f"{gene_name}[Gene] AND {organism}[Organism]", retmax=1)
            record = Entrez.read(handle)
            ids = record.get("IdList", [])
            if not ids:
                return None
            fetch_handle = Entrez.efetch(db="nucleotide", id=ids[0], rettype="fasta", retmode="text")
            fasta_data = fetch_handle.read()
            return fasta_data if fasta_data.strip() else None
        except Exception as e:
            return None

    if st.button("Downloaden"):
        data = fetch_gene_data(gene, organism)
        if data:
            st.success(f"✅ Gen {gene} voor {organism} gevonden!")
            st.download_button(
                label="⬇️ Download FASTA bestand",
                data=data,
                file_name=f"{gene}.fasta",
                mime="text/plain"
            )
        else:
            st.error(f"❌ Gen '{gene}' niet gevonden of download mislukt.")


elif menu == "Afsluiten":
    st.write("Sluit de app of stop het script.")
