#http://my-python3-code.blogspot.com/2012/08/basic-tkinter-text-editor-online-example.html
import tkFileDialog
from Tkinter import *
import os.path
import sys
import subprocess
from tkColorChooser import askcolor

def we_are_frozen():
    # All of the modules are built-in to the interpreter, e.g., by py2exe
    return hasattr(sys, "frozen")

def module_path():
    encoding = sys.getfilesystemencoding()
    if we_are_frozen():
        return os.path.dirname(unicode(sys.executable, encoding))
    return os.path.dirname(unicode(__file__, encoding))

class App:
#File Menu Functions:
#----------------------------------------------------------------------
    def doNew(self):
            # Clear the text
            self.text.delete(0.0, END)

    def doSaveAs(self):
            # Returns the saved file
            file = tkFileDialog.asksaveasfile(mode='w', defaultextension=".asm")
            if file == None:
                return False
            textoutput = self.text.get(0.0, END) # Gets all the text in the field
            file.write(textoutput.rstrip()) # With blank perameters, this cuts off all whitespace after a line.
            file.write("\n") # Then we add a newline character.

    def doOpen(self):
            # Returns the opened file
            file = tkFileDialog.askopenfile(mode='r')
            if file == None:
                return False
            fileContents = file.read() # Get all the text from file.

            # Set current text to file contents
            self.text.delete(0.0, END)
            self.text.insert(0.0, fileContents)  

#Compile Menu Functions:
#----------------------------------------------------------------------            
    def verify_requirements(self):
        if not os.path.isfile(os.path.join(self.path,"as.exe")):
            return str(os.path.join(self.path,"as.exe"))
        if not os.path.isfile(os.path.join(self.path,"objcopy.exe")):
            return str(os.path.join(self.path,"objcopy.exe"))
        if not os.path.isfile(os.path.join(self.path,"Thumbs.db")):
            return str(os.path.join(self.path,"Thumbs.db"))
        return False
    
    def do_error(self, error_msg):
        error_pop_up = Toplevel()
        error_pop_up.title("Error")
        error_pop_up.grid_columnconfigure(0, minsize=200)
        
        msg = Message(error_pop_up, text=error_msg, width=200)
        msg.grid(row=0, column=0, pady=5)

        button = Button(error_pop_up, text="Dismiss", command=error_pop_up.destroy, width=12)
        button.grid(row=2, column=0, pady=5)
        
    def do_popup(self, title, msg):
        pop_up = Toplevel()
        pop_up.title(title)
        pop_up.grid_columnconfigure(0, minsize=200)
        
        msg = Message(pop_up, text=msg, width=200)
        msg.grid(row=0, column=0, pady=5)

        button = Button(pop_up, text="Dismiss", command=pop_up.destroy, width=12)
        button.grid(row=2, column=0, pady=5)


    def accept_prompt_input(self):
        offset = self.field.get()
        offset = int(offset, 16)
        try: offset = hex(offset)
        except:
            self.do_error("Please type a valid hexadecimal number.")
            return False
        #0x08YYYYYY
        if len(offset) >= 6:
            pure_offset = offset[-6:]
        else:
            pure_offset = offset[2:]
        pure_offset_dec = int(pure_offset, 16)
        if (pure_offset_dec % 4) != 0:
            self.do_error("Offset must end in a 0, 4, 8, or C")
            return False
        
        self.ROM.seek(pure_offset_dec)
        with open(self.binary, "rb") as binary:
            binary.seek(0,os.SEEK_END)
            length = binary.tell()

            for i in range(length):
                char = self.ROM.read(1)
                if char != '\xff':
                    self.yes_or_no = Toplevel()
                    self.yes_or_no.title("Free Space Warning")
                    self.yes_or_no.grid_columnconfigure(0, minsize=100)
                    self.yes_or_no.grid_columnconfigure(1, minsize=100)
                    self.yes_or_no.grid_columnconfigure(2, minsize=100)
                    
                    msg = Message(self.yes_or_no, text="There is not enough free space at the specified offset. Are you sure you want to compile?", width=300)
                    msg.grid(row=0, column=0, columnspan=3, pady=5)

                    button = Button(self.yes_or_no, text="No", command=self.cancelRomInsert, width=12)
                    button.grid(row=2, column=0, pady=5, columnspan=2)
                    
                    button = Button(self.yes_or_no, text="Yes", command=self.yes_or_no.destroy, width=12)
                    button.grid(row=2, column=1, pady=5, columnspan=2)
                    
                    self.root.wait_window(self.yes_or_no)
                    break
                    
            if self.ROM.closed:
                return
            else:
                self.ROM.seek(pure_offset_dec)
                binary.seek(0)
                self.ROM.write(binary.read())
                self.ROM.close()
                self.prompt.destroy()

        
    def cancelRomInsert(self):
        self.yes_or_no.destroy()
        self.prompt.destroy()
        self.ROM.close()
        
    def doRomInsert(self):
        self.binary = os.path.join(self.path, "temp.bin")
        error = self.createBinary("temp.asm", self.binary)
        if error:
            return False
            
        self.ROM = tkFileDialog.askopenfile(mode='r+b', title="Select Rom...", filetypes=[("Rom Files","*.gba"), ("Binary Files",'*.bin'),('All Files','*')])
        if self.ROM == None:
            return False
        
        self.prompt = Toplevel()
        self.prompt.title("Insertion Offest")
        self.prompt.grid_columnconfigure(0, minsize=100)
        self.prompt.grid_columnconfigure(1, minsize=100)
        self.prompt.grid_columnconfigure(2, minsize=100)
        
        msg = Message(self.prompt, text="Please provide an offset in the rom to compile to:", width=300)
        msg.grid(row=0, column=0, columnspan=3, pady=5)
        
        hex_note = Message(self.prompt, text="0x")
        hex_note.grid(row=1, column=0, sticky=E)
        
        self.field = Entry(self.prompt)
        self.field.grid(row=1, column=1, columnspan=2, pady=5, sticky=W)
        
        button = Button(self.prompt, text="Cancel", command=self.prompt.destroy, width=12)
        button.grid(row=2, column=0, pady=5, columnspan=2)
        
        button = Button(self.prompt, text="Compile", command=self.accept_prompt_input, width=12)
        button.grid(row=2, column=1, pady=5, columnspan=2)

        

    def doTestCompile(self):
        binary = os.path.join(self.path, "temp.bin")
        error = self.createBinary("temp.asm", binary)
        if not error:
            os.remove(binary)
            self.do_popup("Assembler", "Compile Successful.")
            return True
        else:
            return False
        
            
        
        
    def doBinCompile(self):
        open_file = tkFileDialog.asksaveasfile(mode='w', defaultextension=".bin", title="Compile Binary as...")
        #os.chdir(self.path)
        if open_file == None:
            return False
        binary = open_file.name
        open_file.close()
        os.remove(binary)
        #Maybe I should find a better way of getting a save as name....:P
        
        error = self.createBinary("temp.asm", binary)
        if error:
            return True
        
    def createBinary(self, name, temp_bin):
    
        missing_file = self.verify_requirements()
        if missing_file:
            self.do_error("The file "+missing_file+" is missing. Compile aborted.")
            return True
        
        source = os.path.join(self.path, name)
        
        with open(os.path.join(self.path, name), "w+") as data:
            textoutput = self.text.get(0.0, END)
            data.write(textoutput.rstrip())
            data.write("\n")
        
        as_proccess = subprocess.Popen(["as", "-mthumb", "-mthumb-interwork", "--fatal-warnings", source], bufsize=2048, shell=True, stderr=subprocess.PIPE)
        (as_output, as_err) = as_proccess.communicate()
        
        as_proccess.wait()
        if as_err != "":
            self.do_error(as_err)
            os.remove(source)
            os.remove("a.out")
            return True

        
        objcopy_proccess = subprocess.Popen("objcopy -O binary a.out "+temp_bin,  bufsize=2048, shell=True, stderr=subprocess.PIPE)
        (objcopy_output, objcopy_err) = objcopy_proccess.communicate()
        
        objcopy_proccess.wait()
        if objcopy_err != "":
            self.do_error(objcopy_err)
            os.remove(source)
            os.remove("a.out")
            return True
            
        
        #clean-up temp files
        os.remove(source)
        os.remove("a.out")
        return False
        
    def doRomInsertOrg(self):
        info = Toplevel()
        info.title(".org Info")
        
        msg_ = Message(info, text=".org Rom Insertion is for compiling ASM scripts \
that begin with a .org and therefore have a lot of free space in the produced \
binary. When using the method, make sure that the insertion offset in the next \
prompt exactly matches the .org offset, or there will be issues.", width=400, pady=5)
        msg_.pack()
        
        button_ = Button(info, text="Dismiss", pady=5, command=info.destroy, width=12)
        button_.pack()
    
    
        self.root.wait_window(info)
        
        self.binary = os.path.join(self.path, "temp.bin")
        error = self.createBinary("temp.asm", self.binary)
        if error:
            return False
            
        self.ROM = tkFileDialog.askopenfile(mode='r+b', title="Select Rom...", filetypes=[("Rom Files","*.gba"), ("Binary Files",'*.bin'),('All Files','*')])
        if self.ROM == None:
            return False
        
        self.prompt = Toplevel()
        self.prompt.title("Insertion Offest")
        self.prompt.grid_columnconfigure(0, minsize=100)
        self.prompt.grid_columnconfigure(1, minsize=100)
        self.prompt.grid_columnconfigure(2, minsize=100)
        
        msg = Message(self.prompt, text="Please provide an offset in the rom to compile to:", width=300)
        msg.grid(row=0, column=0, columnspan=3, pady=5)
        
        hex_note = Message(self.prompt, text="0x")
        hex_note.grid(row=1, column=0, sticky=E)
        
        self.field = Entry(self.prompt)
        self.field.grid(row=1, column=1, columnspan=2, pady=5, sticky=W)
        
        button = Button(self.prompt, text="Cancel", command=self.prompt.destroy, width=12)
        button.grid(row=2, column=0, pady=5, columnspan=2)
        
        button = Button(self.prompt, text="Compile", command=self.accept_prompt_input_org, width=12)
        button.grid(row=2, column=1, pady=5, columnspan=2)
        
        
    def accept_prompt_input_org(self):
        offset = self.field.get()
        offset = int(offset, 16)
        try: offset = hex(offset)
        except:
            self.do_error("Please type a valid hexadecimal number.")
            return False
        #0x08YYYYYY
        if len(offset) >= 6:
            pure_offset = offset[-6:]
        else:
            pure_offset = offset[2:]
        pure_offset_dec = int(pure_offset, 16)
        if (pure_offset_dec % 4) != 0:
            self.do_error("Offset must end in a 0, 4, 8, or C")
            return False
        
        self.ROM.seek(pure_offset_dec)
        
        with open(self.binary, "rb") as binary:
            binary.seek(0,os.SEEK_END)
            length = binary.tell()
            length -= pure_offset_dec
            for i in range(length):
                char = self.ROM.read(1)
                if char != '\xff':
                    self.yes_or_no = Toplevel()
                    self.yes_or_no.title("Free Space Warning")
                    self.yes_or_no.grid_columnconfigure(0, minsize=100)
                    self.yes_or_no.grid_columnconfigure(1, minsize=100)
                    self.yes_or_no.grid_columnconfigure(2, minsize=100)
                    
                    msg = Message(self.yes_or_no, text="There is not enough free space at the specified offset. Are you sure you want to compile?", width=300)
                    msg.grid(row=0, column=0, columnspan=3, pady=5)

                    button = Button(self.yes_or_no, text="No", command=self.cancelRomInsert, width=12)
                    button.grid(row=2, column=0, pady=5, columnspan=2)
                    
                    button = Button(self.yes_or_no, text="Yes", command=self.yes_or_no.destroy, width=12)
                    button.grid(row=2, column=1, pady=5, columnspan=2)
                    
                    self.root.wait_window(self.yes_or_no)
                    break
                    
            if self.ROM.closed:
                return
            else:
                self.ROM.seek(pure_offset_dec)
                binary.seek(pure_offset_dec)
                self.ROM.write(binary.read())
                self.ROM.close()
                self.prompt.destroy()
                
                
                
#Options Menu Functions:
#----------------------------------------------------------------------

    def doPreferences(self):
        self.preferences = Toplevel()
        self.preferences.title("Preferences")
        self.preferences.grid_columnconfigure(0, minsize=100)
        
        fg_msg = Message(self.preferences, text="Foreground Color", width=100)
        fg_msg.grid(row=0, column=0, pady=5)
        
        fg_button = Button(self.preferences, text="Color Chooser", command=self.deal_with_fg_color , width=15)
        fg_button.grid(row=0, column=1, pady=5, padx=5)
        
        bg_msg = Message(self.preferences, text="Background Color", width=100)
        bg_msg.grid(row=1, column=0, pady=5)
        
        bg_button = Button(self.preferences, text="Color Chooser", command=self.deal_with_bg_color , width=15)
        bg_button.grid(row=1, column=1, pady=5, padx=5)
        
    def deal_with_fg_color(self):
        color = askcolor()
        self.text.config(fg=color[1])
        self.preferences.deiconify()
        
    def deal_with_bg_color(self):
        color = askcolor()
        self.text.config(bg=color[1])
        self.preferences.deiconify()
        


#Help Menu Functions:
#----------------------------------------------------------------------

    def do_about(self):
        about = Toplevel()
        about.title("About")
        
        msg = Message(about, text="This simple text editor was created by karatekid552 in order to simplify \
the creation and insertion of assembly code in GBA ROM hacking.  It is written in Python using Tkinter and \
is completely open-source. Feel free to modify, but please give credit. Enjoy!", width=400, pady=5)
        msg.pack()
        
        msg2 = Message(about, text="Credits:\n-HackMew for his thumb.bat file \
which the compiling feature is based upon.\n-What is Second Life ? for posting the very simple text editor, \
that became the basis of this program, on his blog.", width=400, pady=5)
        msg2.pack()
        
        button = Button(about, text="Close", pady=5, command=info.destroy, width=12)
        button.pack()

#------------------------------------------------------------------------------
    def __init__(self):
            # Set up the screen, the title, and the size.
            self.root = Tk()
            self.root.title("THUMB Editor")
            self.root.minsize(width=500,height=400)
            self.path = module_path()
                   
            # Set up basic Menu
            menubar = Menu(self.root)
   
            # Set up a separate menu that is a child of the main menu
            filemenu = Menu(menubar,tearoff=0)
            filemenu.add_command(label="New File", command=self.doNew, accelerator="Ctrl+N")
            
            #create an options menu:
            option_menu = Menu(menubar,tearoff=0)
            option_menu.add_command(label="Preferences", command=self.doPreferences)
            
            #Create a menu for compiling.
            compile_menu = Menu(menubar,tearoff=0)
            compile_menu.add_command(label="Test Compile", command=self.doTestCompile, accelerator="Ctrl+Shift+P")
            compile_menu.add_command(label="Output to .bin", command=self.doBinCompile, accelerator="Ctrl+P")
            compile_menu.add_command(label="Insert into Rom", command=self.doRomInsert, accelerator="Ctrl+U")
            compile_menu.add_command(label="Insert into Rom via .org", command=self.doRomInsertOrg, accelerator="Ctrl+Shift+U")
            
            #Create a help menu:
            help_menu = Menu(menubar,tearoff=0)
            help_menu.add_command(label="About", command=self.do_about)
   
            # Try out openDialog
            filemenu.add_command(label="Open", command=self.doOpen, accelerator="Ctrl+O")
   
            # Try out the saveAsDialog
            filemenu.add_command(label="Save", command=self.doSaveAs, accelerator="Ctrl+Shift+S")
            
            
            menubar.add_cascade(label="File", menu=filemenu)
            menubar.add_cascade(label="Options", menu=option_menu)
            menubar.add_cascade(label="Compile", menu=compile_menu)
            menubar.add_cascade(label="Help", menu=help_menu)
            self.root.config(menu=menubar)
   
            # Set up the text widget
            self.text = Text(self.root)
            self.text.pack(expand=YES, fill=BOTH) # Expand to fit vertically and horizontally

app = App()
app.root.mainloop()
