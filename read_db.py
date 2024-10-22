import sqlite3
from datetime import datetime

# Połączenie z bazą danych
conn = sqlite3.connect('conversations.db')
c = conn.cursor()

# Funkcja do odczytywania wszystkich transkrypcji
def get_all_transcriptions():
    c.execute("SELECT * FROM transcriptions")
    transcriptions = c.fetchall()
    return transcriptions

# Funkcja do odczytywania transkrypcji na podstawie tagu
def get_transcriptions_by_tag(tag):
    c.execute("SELECT * FROM transcriptions WHERE tag = ?", (tag,))
    transcriptions = c.fetchall()
    return transcriptions

# Funkcja do odczytywania transkrypcji na podstawie zakresu dat
def get_transcriptions_by_date(start_date, end_date):
    c.execute("SELECT * FROM transcriptions WHERE timestamp BETWEEN ? AND ?", (start_date, end_date))
    transcriptions = c.fetchall()
    return transcriptions

# Funkcja do odczytywania wszystkich analiz
def get_all_analyses():
    c.execute("SELECT * FROM analyses")
    analyses = c.fetchall()
    return analyses

# Funkcja do odczytywania analiz na podstawie tagu
def get_analyses_by_tag(tag):
    c.execute("SELECT * FROM analyses WHERE tag = ?", (tag,))
    analyses = c.fetchall()
    return analyses

# Funkcja do odczytywania analiz na podstawie zakresu dat
def get_analyses_by_date(start_date, end_date):
    c.execute("SELECT * FROM analyses WHERE timestamp BETWEEN ? AND ?", (start_date, end_date))
    analyses = c.fetchall()
    return analyses

# Formatowanie wyników do czytelnej formy
def format_transcription(transcription):
    return f"ID: {transcription[0]}, Tag: {transcription[1]}, Transcription: {transcription[2]}, Timestamp: {transcription[3]}"

def format_analysis(analysis):
    return f"ID: {analysis[0]}, Tag: {analysis[1]}, Summary: {analysis[2]}, Suggestions: {analysis[3]}, Timestamp: {analysis[4]}"

# Przykłady użycia:

# 1. Odczytanie wszystkich transkrypcji
all_transcriptions = get_all_transcriptions()
print("Wszystkie transkrypcje:")
for transcription in all_transcriptions:
    print(format_transcription(transcription))

# 2. Odczytanie transkrypcji według tagu
tag = "test"
tagged_transcriptions = get_transcriptions_by_tag(tag)
print(f"\nTranskrypcje z tagiem '{tag}':")
for transcription in tagged_transcriptions:
    print(format_transcription(transcription))

# 3. Odczytanie transkrypcji w zakresie dat
start_date = "2024-10-01"
end_date = "2024-10-20"
dated_transcriptions = get_transcriptions_by_date(start_date, end_date)
print(f"\nTranskrypcje od {start_date} do {end_date}:")
for transcription in dated_transcriptions:
    print(format_transcription(transcription))

# 4. Odczytanie wszystkich analiz
all_analyses = get_all_analyses()
print("\nWszystkie analizy:")
for analysis in all_analyses:
    print(format_analysis(analysis))

# 5. Odczytanie analiz według tagu
tagged_analyses = get_analyses_by_tag(tag)
print(f"\nAnalizy z tagiem '{tag}':")
for analysis in tagged_analyses:
    print(format_analysis(analysis))

# 6. Odczytanie analiz w zakresie dat
dated_analyses = get_analyses_by_date(start_date, end_date)
print(f"\nAnalizy od {start_date} do {end_date}:")
for analysis in dated_analyses:
    print(format_analysis(analysis))

# Zamknięcie połączenia z bazą danych
conn.close()