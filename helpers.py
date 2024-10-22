import os
from pydub import AudioSegment

def get_api(path="api.txt"):
    api = []
    if isinstance(path, str):
        with open(path, "r+") as f:
            file = f.read()
            api = str(file)
            
        return api

    else:
        print("Błędna ściezka")
        

class Audio:
    def __init__(self, input_audio_path="./Audio/input/", output_audio_path="./Audio/output/"):       
        self.input_audio_path = input_audio_path
        self.output_audio_path = output_audio_path
        try:
            self.isInExist = os.path.exists(input_audio_path)
            self.isOutExist = os.path.exists(output_audio_path)
            if self.isInExist != True and self.isOutExist != True:
                os.makedirs(input_audio_path), os.makedirs(output_audio_path)
            else:
                pass
        except Exception as e:
            print(e)
            
    class converter():
        def __init__(self):
            self.audio = Audio()
        
        def m4a_to_mp3(self, input_file, output_file=None):                    
            input_file_path = str(self.audio.input_audio_path)+input_file
            output_file_path = str(self.audio.output_audio_path)+output_file
            if not output_file_path:
                output_file = os.path.splitext(input_file_path)[0] + ".mp3"
            else:
                print("err")
            
            #print(f"Konwertowanie {input_file} na {output_file}...")
            
            audio = AudioSegment.from_file(input_file_path)
            
            audio.export(output_file_path, format="mp3")
            
            #print(f"Konwersja zakończona. Plik został zapisany jako {output_file}")
            