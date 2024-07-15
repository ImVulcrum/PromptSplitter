import tkinter as tk
import customtkinter
import multiprocessing
import display_text
from time import sleep
import keyboard
import pyperclip

prompt_queue = [] #global

# Colors
primary_color1 = "#1f6aa5" #standard color of the blue color theme
primary_color2 = "#144870" #hovering animation standard color
text_color = "#ffffff"
secondary_color1 = "#051923"
secondary_color2 = '#191919'
disabled_color = "#4a4a4a"

# Default Text
default_instructions= 'The total length of the content that I want to send you is too large to send in only one piece. For sending you that content, I will follow this rule: [START PART 1/$] <this is the content of the part 1 out of $ in total> [END PART 1/$] Then you just answer: "Received part 1/$" And when I tell you "ALL PARTS SENT", then you can continue processing the data and answering my requests. \n this was already the first part so just answer as given in the previous. ("<Received part 1/$>")'
default_front = 'Do not answer yet. This is just another part of the text I want to send you. Just receive and acknowledge as "Part %/$ received" and wait for the next part.[START PART %/$]'
default_back = '[END PART %/$] Remember not answering yet. Just acknowledge you received this part with the message "Part %/$ received" and wait for the next part.'
final_back = '[END PART %/$] ALL PARTS SENT. Now you can continue processing the request.'

def split_button_callback():
    prompt_string = prompt.get("0.0", "end")
    chunk_size = int(token_length_slider.get())
    split_button.configure(text="Splitted", state="disabled", fg_color=disabled_color)
    paste_button.configure(state="normal", fg_color=primary_color1)
    split_prompt(prompt_string, chunk_size)

def paste_button_callback():
    if paste_button.cget("text") == "Paste": #executed when pasting thread is started
        paste_button.configure(text="Cancel", fg_color=secondary_color1)
        paste_process = (multiprocessing.Process(target = paste, args=(prompt_queue,)))
        paste_process.start()
    else:   #executed when canceling
        paste_button.configure(text="Paste", fg_color=primary_color1)
        paste_process.terminate()

def token_slider_callback(current_token_length):
    current_prompt_length = len(prompt.get("0.0", "end"))

    # update the caption below to slider to the right value
    value_string = str(current_token_length)
    displayed_text = "token length: " + value_string[:2] + "." + value_string[2:5]
    slider_caption.configure(text=displayed_text)

    #activate the split button (when its disabled) after an update of the token length slider
    if split_button.cget("state") == "disabled" and current_prompt_length > current_token_length:
        split_button.configure(text="Split", state="normal", fg_color=primary_color1)

    #deactivate the split button when the token length is bigger than the prompt length
    if current_prompt_length <= current_token_length:
        split_button.configure(text="Split", state="disabled", fg_color=disabled_color)


def split_prompt(prompt_string, chunk_size):
    # splitting
    chunks = []
    current_chunk = ""
    words = prompt_string.split()
    for word in words:
        if len(current_chunk) + len(word) + 1 <= chunk_size:  # +1 for space after the word
            if current_chunk:
                current_chunk += " " + word
            else:
                current_chunk += word
        else:
            chunks.append(current_chunk)
            current_chunk = word
    
    if current_chunk:
        chunks.append(current_chunk)

    # calculate the number of parts
    number_of_parts= len(chunks) +1

    add_parts_to_queue(chunks, number_of_parts)

def add_parts_to_queue(chunks, number_of_parts):
    global prompt_queue
    prompt_queue = [] #clear the queue

    # add the instructions to the prompt queue
    instructions_string = instructions.get("0.0", "end").replace("$", str(number_of_parts))
    prompt_queue.append(instructions_string)

    # add the splitted prompts
    current_part = 2
    for part in chunks:
        if current_part == number_of_parts: #last part is processed
            prompt_queue.append((default_front.replace("$", str(number_of_parts))).replace("%", str(current_part)) + "\n\n" + str(part) + "\n\n" + (final_back.replace("$", str(number_of_parts)).replace("%", str(current_part))))
            break
        else:
            prompt_queue.append((default_front.replace("$", str(number_of_parts)).replace("%", str(current_part))) + "\n\n" + str(part) + "\n\n" + (default_back.replace("$", str(number_of_parts)).replace("%", str(current_part))))
        current_part = current_part +1

def paste(queue):
    counter = 1
    display_process = None

    for part in queue:
        if display_process is not None:
            # Terminate the previous display process
            display_process.terminate()
            display_process.join()

        # Start a new display process
        display_process = multiprocessing.Process(target=display_text.display, args=(str(counter),))
        display_process.start()

        # Copy the part to clipboard
        pyperclip.copy(part)
        
        # Wait for the user to press enter
        keyboard.wait("enter")

        counter += 1

    # Ensure the last display process is also terminated
    if display_process is not None:
        display_process.terminate()
        display_process.join()

    print("finish")
    print(paste_button.cget("text"))
    paste_button.configure(text="Paste", fg_color=primary_color1)
    
    print("hfg")
    
# General GUI design settings
customtkinter.set_appearance_mode("System")
customtkinter.set_default_color_theme("blue")
customtkinter.deactivate_automatic_dpi_awareness()

# App frame
app = customtkinter.CTk()
app.geometry("780x520")
app.title("Prompt Splitter")

# creating the tabview
tabview = customtkinter.CTkTabview(app, corner_radius=12)
tabview.pack()
tabview.add("prompt")
tabview.add("instructions")
tabview.set("prompt")

# prompt tab
enter_prompt_title = customtkinter.CTkLabel(master=tabview.tab("prompt"), text="paste the prompt to be splitted", font=("<arial>", 20), fg_color=secondary_color2, corner_radius=12, height=35)
enter_prompt_title.pack(pady=(0,3))

prompt = customtkinter.CTkTextbox(master=tabview.tab("prompt"), width=680, height=280, font=("<arial>", 10), fg_color=secondary_color2, corner_radius=12)
prompt.pack(pady=0)

# instructions tab
enter_instructions_title = customtkinter.CTkLabel(master=tabview.tab("instructions"), text="enter the prompt instructions", font=("<arial>", 20), fg_color=secondary_color2, corner_radius=12, height=35)
enter_instructions_title.pack(pady=(0,3))

instructions = customtkinter.CTkTextbox(master=tabview.tab("instructions"), width=680, height=280, font=("<arial>", 10), fg_color=secondary_color2, corner_radius=12)
instructions.insert("0.0", text= default_instructions)
instructions.pack(pady=0)

# other elements
token_length_slider = customtkinter.CTkSlider(app, from_=15000, to=64000, width=600, command=token_slider_callback)
token_length_slider.pack(pady=(20,0))
token_length_slider.set(32000)

slider_caption = customtkinter.CTkLabel(app, text="token length: 32.000", font=("<arial>", 15))
slider_caption.pack()

button_frame = customtkinter.CTkFrame(app, fg_color="transparent")
button_frame.pack(pady=(20,0))

split_button = customtkinter.CTkButton(button_frame, text="Split", state="disabled", fg_color=disabled_color, command=split_button_callback)
split_button.grid(row=0, column =0, padx=20)

paste_button = customtkinter.CTkButton(button_frame, text="Paste", state="disabled", fg_color=disabled_color, command=paste_button_callback)
paste_button.grid(row=0, column =1, padx=20)

if __name__ == '__main__': # Run app

    entry = prompt.get("0.0", "end")
    
    while True:
        current_entry = prompt.get("0.0", "end")
        current_token_length = token_length_slider.get()

        #activate the split button (when its disabled) after an update in the prompt textbox
        if current_entry != entry and split_button.cget("state") == "disabled" and len(current_entry) > int(current_token_length):
            split_button.configure(text="Split", state="normal", fg_color=primary_color1)
        
        entry = current_entry

        #update window
        app.update()
        app.update_idletasks()
        sleep(0.05)