import os
import time
import pyaudio
import speech_recognition as sr
import playsound 
from gtts import gTTS
import openai
import pyautogui
import pytesseract
from PIL import Image 
import re
import subprocess
import sys

api_key = "Change THIS"
lang = 'en'
openai.api_key = api_key

guy = ""

microphone = sr.Microphone(device_index=1)

def delete_lines_and_restart(program_path, start_line, end_line):
    with open(program_path, 'r') as file:
        lines = file.readlines()
    
    with open(program_path, 'w') as file:
        for i, line in enumerate(lines, start=1):
            if not start_line <= i <= end_line:
                file.write(line)
    subprocess.Popen(['/home/parallels/Desktop/new_ai/restart_script.sh'])
    sys.exit()


def update_program(new_code_snippet):
    program_path = '/home/parallels/Desktop/new_ai/main.py'
    try:
        with open(program_path, 'r+') as f:
            lines = f.readlines()
            lines.insert(129, new_code_snippet + '\n')  
            f.seek(0)
            f.truncate()
            f.writelines(lines)

        subprocess.Popen(['/home/parallels/Desktop/new_ai/restart_script.sh'])
    except Exception as e:
        print(f"Failed to update program: {e}")
    sys.exit()

def play_audio(text):
    speech = gTTS(text=text, lang=lang, slow=False, tld="com.au")
    speech.save("output.mp3")
    playsound.playsound("output.mp3")

def create_note_file(note, file_path):
    with open(file_path, "a") as f:
        f.write(note + "\n")

def add_note_again(note, file_path):
    with open(file_path, "a") as f:
        f.write(note + "\n")

def get_audio():
    r = sr.Recognizer()
    with microphone as source:
        audio = r.listen(source)
        said = ""

        try:
            said = r.recognize_google(audio)
            print(said)
            global guy
            guy = said

            if "note" in said:
                print("Opening note")
                play_audio("What would you like to make a note about")
                note_audio = r.listen(source)
                note = r.recognize_google(note_audio)
                print("Note saved")
                play_audio("Note saved successfully.")
                file_path = os.path.expanduser("~/Desktop/note.txt")
                create_note_file(note, file_path)

                while True:
                    play_audio("Would you like to save another note?")
                    another_note_audio = r.listen(source)
                    response = r.recognize_google(another_note_audio)
                    if "yes" in response:
                        play_audio("What would you like to add to the notes")
                        note_audio = r.listen(source)
                        note = r.recognize_google(note_audio)
                        add_note_again(note, file_path)
                        play_audio("The note was saved again")
                    else:
                        break

            elif "stuck" in said:
                play_audio("I am sorry you are frustrated")

            elif "scroll down" in said:
                pyautogui.press('pagedown')
                play_audio("Scrolled down")

            elif "scroll up" in said:
                pyautogui.press('pageup')
                play_audio("Scrolled up")

            elif "booger" in said:
                new_string = said.replace("Friday", "")
                new_string = new_string + " response should be no longer than 2 sentances"
                print(new_string)
                completion = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=[{"role": "user", "content": new_string}])
                text = completion.choices[0].message.content
                play_audio(text)




 








            elif "delete" in said:
                match = re.match(r"delete (\d+) from (\d+)", said)
                print(match)
                if match:
                    start_line = int(match.group(1))
                    end_line = int(match.group(2))
                    program_path = '/home/parallels/Desktop/new_ai/main.py'
                    delete_lines_and_restart(program_path, start_line, end_line)
                    play_audio("Code deleted and program restarted")
                else:
                    play_audio("Sorry, I didn't understand the line numbers.")

            elif "add code" in said:
                new_string = said.replace("add code", "").strip()
                prompt_for_openai = f"Generate a Python 'elif' statement block for a voice command program that handles the following intent: '{new_string}'. and if an elif statment is created it will be in this format: elif 'trigger_word_for_elif_statement' in said: then add fucntion below"
                print(prompt_for_openai) 
                
                completion = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": prompt_for_openai}]
                )
                generated_code = completion.choices[0].message.content
                print(generated_code) 
                code_lines = generated_code.split('\n')
                indented_code_lines = ["    " * 3 + line if line.strip() != "" else line for line in code_lines]
                filtered_code = '\n'.join(indented_code_lines)
                update_program(filtered_code)
                play_audio("New functionality is being added to the program.")


            elif "screenshot" in said:
                print("Getting the screenshot")
                screenshot_dir = os.path.expanduser("~/Desktop")
                file_name = "screenshot"
                extension = ".png"
                file_path = os.path.join(screenshot_dir, file_name + extension)

                if os.path.exists(file_path):
                    counter = 1
                    while os.path.exists(file_path):
                        new_filename = file_name + str(counter) + extension
                        file_path = os.path.join(screenshot_dir, new_filename)
                        counter += 1
                
                capture_screenshot(file_path)
                play_audio("Screenshot was saved")


        except Exception as e:
            print("Exception:", str(e))

def capture_screenshot(file_path):
    screenshot = pyautogui.screenshot()
    screenshot.save(file_path)

while True:
    if "stop" in guy:
        break
    get_audio()
