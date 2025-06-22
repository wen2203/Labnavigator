from Bio import SeqIO
import os
import requests
from Bio import Entrez

def convert_fastq_to_fasta(fastq_path, fasta_path):
    with open(fasta_path, "w") as fasta_file:
        SeqIO.convert(fastq_path, "fastq", fasta_file, "fasta")
    print(f"✅ FASTQ successfully converted to FASTA: {fasta_path}")

from Bio import Entrez

Entrez.email = "your_email@example.com"  # Vervang met je echte e-mail
import os
from Bio import Entrez


def download_gene(gene_name, organism="Homo sapiens", max_results=1):
    Entrez.email = "your.email@example.com"  # Vul je email in voor NCBI
    
    handle = Entrez.esearch(db="nucleotide", term=f"{gene_name}[Gene] AND {organism}[Organism]", retmax=max_results)
    record = Entrez.read(handle)
    ids = record.get("IdList", [])

    if not ids:
        print("No results found.\n")
        return False  # Geen resultaten

    output_dir = "/Users/rainy/Documentslocal/Lab_Navigator2/genes"
    os.makedirs(output_dir, exist_ok=True)

    for gene_id in ids:
        fetch_handle = Entrez.efetch(db="nucleotide", id=gene_id, rettype="fasta", retmode="text")
        fasta_data = fetch_handle.read()

        if not fasta_data.strip():  # check lege data
            print(f"Geen FASTA data gevonden voor ID {gene_id}\n")
            return False

        filename = f"{gene_name}_{gene_id}.fasta"
        output_path = os.path.join(output_dir, filename)

        with open(output_path, "w") as f:
            f.write(fasta_data)

        print(f"✅ Gene downloaded to: {output_path}\n")

    return True  # Download succesvol
