from gpt_connection import client
import sqlite3
from datetime import datetime

# Funkcja do transkrypcji i analizy rozmowy
def conv(audio_file_path):
    audio_file = open(audio_file_path, "rb")
    tytul = input("Podaj mi tytuł rozmowy: ")

    if tytul:
        print("Analizowanie...")
        transcript = client.audio.transcriptions.create(
            model="whisper-1", 
            file=audio_file
        )
        transcribed_text = transcript.text
        print("\033[0;35m"+str(transcribed_text)+"\033[0m")

        # Analiza
        print("\nAnalizuję twoje spotkanie...\n")
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": f"Wciel się w rolę CEO i podsumuj poniższą rozmowę i podaj swoje sugestie:\n\n{str(transcribed_text)}"}
            ],
            max_tokens=500,
            temperature=0.7
        )
        analysis = response.choices[0].message.content
        return tytul, transcribed_text, analysis

# Połączenie z bazą danych SQLite
def create_db_connection():
    conn = sqlite3.connect('conversations.db')
    return conn

# Tworzenie tabel
def create_tables(conn):
    c = conn.cursor()
    
    # Tworzenie tabeli na transkrypcje
    c.execute('''CREATE TABLE IF NOT EXISTS transcriptions
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  tag TEXT, 
                  transcription TEXT, 
                  timestamp DATETIME)''')

    # Tworzenie tabeli na analizy
    c.execute('''CREATE TABLE IF NOT EXISTS analyses
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  tag TEXT, 
                  summary TEXT, 
                  suggestions TEXT, 
                  timestamp DATETIME)''')
    
    conn.commit()

# Funkcja do dodawania transkrypcji
def add_transcription(conn, tag, transcription):
    timestamp = datetime.now()
    c = conn.cursor()
    c.execute("INSERT INTO transcriptions (tag, transcription, timestamp) VALUES (?, ?, ?)",
              (tag, transcription, timestamp))
    conn.commit()

# Funkcja do dodawania analiz
def add_analysis(conn, tag, summary, suggestions):
    timestamp = datetime.now()  # Ustal timestamp
    c = conn.cursor()
    
    # Teraz przekazujemy 4 wartości: tag, summary, suggestions, timestamp
    c.execute("INSERT INTO analyses (tag, summary, suggestions, timestamp) VALUES (?, ?, ?, ?)",
              (tag, summary, suggestions, timestamp))
    conn.commit()

# Funkcja do pobierania wcześniejszych analiz
def get_previous_analyses(conn, tag):
    c = conn.cursor()
    c.execute("SELECT summary, suggestions FROM analyses WHERE tag = ?", (tag,))
    return c.fetchall()

# Funkcja do porównania nowej rozmowy z wcześniejszymi analizami
def compare_with_previous_analyses(conn, tag, transcribed_text):
    previous_analyses = get_previous_analyses(conn, tag)

    # Tworzenie kontekstu dla GPT
    context = f"Poniżej znajdują się wcześniejsze analizy na temat: {tag}\n\n"
    for i, (summary, suggestions) in enumerate(previous_analyses):
        context += f"Analiza {i+1}:\nPodsumowanie: {summary}\nSugestie: {suggestions}\n\n"

    context += f"Nowa rozmowa:\n{transcribed_text}\n\nNa podstawie wcześniejszych analiz, jak oceniasz tę rozmowę? Co można poprawić?"

    response = client.chat.completions.create(
        model="gpt-3.5-turbo", 
        messages=[
            {"role": "system", "content": context}
        ],
        max_tokens=500,
        temperature=0.7
    )
    
    return response.choices[0].message.content

# Główna część programu
if __name__ == "__main__":
    conn = create_db_connection()
    create_tables(conn)

    # Przykład transkrypcji i analizy
    tytul, transcribed_text, analysis = conv("./Audio/output/test.mp3")

    # Zapis transkrypcji do bazy danych
    add_transcription(conn, tytul, transcribed_text)

    # Podział analizy na podsumowanie i sugestie (jeśli GPT je rozdziela)
    summary, suggestions = analysis.split("---") if "---" in analysis else (analysis, "")

    # Zapis analizy do bazy danych
    add_analysis(conn, tytul, summary.strip(), suggestions.strip())

    # Porównanie z wcześniejszymi analizami
    new_analysis_comparison = compare_with_previous_analyses(conn, tytul, transcribed_text)
    print(new_analysis_comparison)

    # Zamknięcie połączenia z bazą
    conn.close()
    


from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import sqlite3

# Funkcja do pobierania wszystkich transkrypcji z bazy danych
def get_all_transcriptions():
    conn = sqlite3.connect('conversations.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, transcription FROM transcriptions")
    transcriptions = cursor.fetchall()
    conn.close()
    return transcriptions

# Funkcja do obliczania podobieństwa między nową transkrypcją a wcześniejszymi
def find_similar_transcriptions(new_transcription):
    transcriptions = get_all_transcriptions()
    ids, texts = zip(*transcriptions)
    
    # Tworzymy wektory TF-IDF dla wszystkich transkrypcji
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(texts + (new_transcription,))
    
    # Obliczamy podobieństwo kosinusowe
    cosine_similarities = cosine_similarity(tfidf_matrix[-1], tfidf_matrix[:-1])
    
    # Sortowanie podobieństw i wybór najbardziej podobnych
    similar_indices = cosine_similarities.argsort()[0][-5:]  # np. 5 najbardziej podobnych
    similar_transcriptions = [(ids[i], texts[i], cosine_similarities[0][i]) for i in similar_indices]
    
    return similar_transcriptions

def analyze_meeting_with_context(new_transcription):
    similar_transcriptions = find_similar_transcriptions(new_transcription)
    
    context = "Poniżej znajdują się wcześniejsze rozmowy na podobny temat:\n\n"
    for id_, transcription, similarity in similar_transcriptions:
        context += f"Rozmowa {id_} (Podobieństwo: {similarity:.2f}):\n{transcription}\n\n"
    
    context += f"Nowa rozmowa:\n{new_transcription}\n\nNa podstawie wcześniejszych rozmów, podsumuj tę rozmowę i zasugeruj ewentualne poprawki."
    
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": context}
        ],
        max_tokens=500,
        temperature=0.7
    )
    
    return response.choices[0].message.content


def process_and_analyze_meeting(audio_file_path, tag):
    # Krok 1: Transkrypcja nagrania (Whisper)
    audio_file = open(audio_file_path, "rb")
    transcript = client.audio.transcriptions.create(
        model="whisper-1", 
        file=audio_file
    )['text']
    
    # Zapisz surową transkrypcję w bazie danych
    add_transcription(tag, transcript)
    
    # Krok 2: Analiza w oparciu o wcześniejsze rozmowy
    analysis = analyze_meeting_with_context(transcript)
    
    # Podział analizy na podsumowanie i sugestie (zakładamy, że GPT generuje takie dane)
    summary, suggestions = analysis.split("---")
    
    # Zapisz analizę w bazie danych
    add_analysis(tag, summary.strip(), suggestions.strip())

    print(f"Spotkanie o tagu '{tag}' zostało przetworzone i przeanalizowane.")