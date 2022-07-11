#
# Display QRCodeGenerator
# --------------------

from qrgen import *
from passgen import *
from PIL import ImageTk, Image

import sys
import argparse
import qrcode
import tkinter as tk

from file_handler import FileHandler, qr_files, payloads

# --------------------- CONFIG ---------------------

_qr_error = 'L'
_qr_scale = 7
update_time = 500

# --------------------- MAIN ---------------------
def main():   
    
    opt = cmd()
    
    app_index = opt.app
    list_index = opt.list

    if app_index is None: 
        print("[QRCodeGenerator] Please select an app with the argument -a")
        exit(1)
    app_fun = app_names[app_index]
    
    print(app_index)
    if list_index is not None:
        dicts = [word_files[list_index]]
        name = word_file_names[list_index]
    
    else:
        dicts = word_files
        name = "all"

    for dd in dicts:
        f = open(dd, encoding='utf-8')

        for i, s in enumerate(f.readlines()):
            if name != "all":
                qr_files.append(name + "-" + str(i))
            else:
                qr_files.append(dd.replace("words/","").replace(".txt", "") + "-" + str(i))
            payloads.append(s)
            i += 1

    # ------------------------------------

    # Set Json path     
    if opt.jsonpath:
        file = FileHandler(opt.jsonpath)
    else:
        file = FileHandler()

    # Set starting position
    if opt.start_from:
        file.iterator = opt.start_from

    def genqr(text="test"):
        try:
            qr = qrcode.QRCode(
                error_correction=qrcode.constants.ERROR_CORRECT_L,
            )
            qr.add_data(text)
            qr.make(fit=True)

            img = qr.make_image(fill_color="black", back_color="white")
            print("> Text:", text)
        except Exception as e:
            img = qrcode.make("Error")
            print("> Text:", "Error")
        
        return img

        
    # ----------- TK -----------
    window = tk.Tk()
    window.title("QR Code Visualizer")

    window_height = 800
    window_width = 800

    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    y_cordinate = int((screen_height/2) - (window_height/2))

    if opt.position == "left":
        x_cordinate = int(50)
    elif opt.position == "right":
        x_cordinate = int((screen_width/2) + 100)
    else:
        x_cordinate = int((screen_width/2) - (window_width/2))

    window.geometry("{}x{}+{}+{}".format(window_width, window_height, x_cordinate, y_cordinate))

    #window.geometry("800x800")
    window.configure(background='white')

    # ------ Canvas

    global img 
    img = genqr("test")

    ph = ImageTk.PhotoImage(img)
    label = tk.Label(window, image= ph)
    # canvas.create_bitmap(100, 100, bitmap=img, anchor=tk.NW)


    def update():
        # ---------- main loop -----------
        if file.checker():
            gp = app_fun(payloads[file.iterator])
            img = genqr(gp)
            
            new_width = label.winfo_width()
            new_height = label.winfo_height()
            image = img.resize((new_width, new_height))
            photo = ImageTk.PhotoImage(image)
            label.config(image = photo)
            label.image = photo 
            # panel.config(image= img2)
            # panel.image = img2 #IPER MEGA IMPORTANT
            file.next()
            window.after(update_time, update)
        else:
            if file.hasNotNext():
                print("End of QR codes, closing in 10 seconds...")
                window.after(10000, close)
            else:
                window.after(update_time, update)
            

    def close():
        print("Done")
        window.destroy()
    
    def resize_image(e):
        new_width = e.width
        new_height = e.height
        image = img.resize((new_width, new_height))
        photo = ImageTk.PhotoImage(image)
        label.config(image = photo)
        label.image = photo #avoid garbage collection
        

    label.bind('<Configure>', resize_image)
    label.pack(fill=tk.BOTH, expand = tk.YES)
    # add some widgets to the canvas
    window.after(update_time, update)
    window.mainloop()


# --------------------- CMD ---------------------

def cmd():
    parser = argparse.ArgumentParser(
        description="Generate and Display QR Code while scanning with Appium-controlled app",
        usage=f"main.py -l [number]\nusage: main.py -w [/path/to/custom/wordlist]\n\nPayload lists: \n {fuzz_type}"
    )
    sgroup = parser.add_argument_group("Options available")
    sgroup.add_argument(
        "--list",
        "-l",
        type=int,
        help="Set wordlist to use",
        choices=[i[0] for i in fuzz_type],
    ) 
    sgroup.add_argument(
        "--app",
        "-a",
        type=str,
        help="Set app to use",
        choices=app_names.keys(),
    )
    sgroup.add_argument(
        "--jsonpath",
        "-j",
        type=str,
        help="Set path to json file to use (the json file must be named 'fuzzer.json')"
    )
    sgroup.add_argument(
        "--position",
        "-p",
        type=str,
        help="Set position of the window in the screen",
        choices=("left", "right", "center")
    )
    sgroup.add_argument(
        "--start-from",
        "-sf",
        type=int,
        help="Start QR Code scan from the given position"
    )
    opt = parser.parse_args()
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)
    return opt


if __name__ == "__main__":
    main()