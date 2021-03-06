#venv pyi-env-name

#http://my-python3-code.blogspot.com/2012/08/basic-tkinter-text-editor-online-example.html
from baseconv import *
import tkFileDialog
import os, platform, time, math, sys, subprocess
from Tkinter import *
import Tkinter as tk
from module_locator import *
from tkColorChooser import askcolor
import tkMessageBox


class CustomText(tk.Text):
    
    def __init__(self, *args, **kwargs):
        tk.Text.__init__(self, *args, **kwargs)
        self.highlight = True
        self.config(undo = True)
        self.tk.eval('''
            proc widget_proxy {widget widget_command args} {

                # call the real tk widget command with the real args
                set result [uplevel [linsert $args 0 $widget_command]]

                # generate the event for certain types of commands
                if {([lindex $args 0] in {insert replace delete}) ||
                    ([lrange $args 0 2] == {mark set insert}) || 
                    ([lrange $args 0 1] == {xview moveto}) ||
                    ([lrange $args 0 1] == {xview scroll}) ||
                    ([lrange $args 0 1] == {yview moveto}) ||
                    ([lrange $args 0 1] == {yview scroll})} {

                    event generate  $widget <<Change>> -when tail
                }

                # return the result from the real widget command
                return $result
            }
            ''')
        self.tk.eval('''
            rename {widget} _{widget}
            interp alias {{}} ::{widget} {{}} widget_proxy {widget} _{widget}
        '''.format(widget=str(self)))
        
        self.label_color = "#ff0000"
        self.large_color = "#00ff00"
        self.comment_color = "#0000ff"
        
        self.flag = False
    def edit_redo(self, *args):
        """Redo the last undone edit

        When the undo option is true, reapplies the last
        undone edits provided no other edits were done since
        then. Generates an error when the redo stack is empty.
        Does nothing when the undo option is false.
        """
        return self.edit("redo")
        
    def edit_undo(self, *args):
        """Undoes the last edit action

        If the undo option is true. An edit action is defined
        as all the insert and delete commands that are recorded
        on the undo stack in between two separators. Generates
        an error when the undo stack is empty. Does nothing
        when the undo option is false
        """
        return self.edit("undo")
        
    def highlighting(self, *args):
        if not self.highlight: return
        #DEBUGGER COLORS
        #self.label_color = "#ff0000"
        #self.large_color = "#00ff00"
        #self.comment_color = "#0000ff"
        self.labels = []
        
        if self.flag: self.tag_delete("COMMENT","LABEL","LARGE")
        
        #Highlight Comments
        self.tag_configure("COMMENT",foreground=self.comment_color)
        self.highlight_pattern(r"(?w)/\*.*\*/", "COMMENT")
        
        
        #Highlight LABELS
        self.tag_configure("LABEL",foreground=self.label_color)
        self.highlight_pattern(r"\m[^.\t ]*:", "LABEL")
        self.tag_lower("LABEL", belowThis="COMMENT")
        
        #Highlight large numbers
        self.tag_configure("LARGE",foreground=self.large_color)
        self.highlight_pattern(r"\.[^\t ]*", "LARGE")
        self.tag_lower("LARGE", belowThis="COMMENT")
        
        #highlight all labels elsewhere
        for label in self.labels: self.highlight_sub_pattern(label, "LABEL")
        
        self.flag = True

    def highlight_pattern(self, pattern, tag, start="1.0", end="end", regexp=True):
        """Apply the given tag to all text that matches the given pattern

        If 'regexp' is set to True, pattern will be treated as a regular expression
        """

        start = self.index(start)
        end = self.index(end)
        self.mark_set("matchStart",start)
        self.mark_set("matchEnd",start)
        self.mark_set("searchLimit", end)
        self.global_line = 0.0
        count = tk.IntVar()
        
        while True:
            index = self.search(pattern, "matchEnd","searchLimit",
                                count=count, regexp=regexp)
            if index == "": break
            
            
            self.mark_set("matchStart", index)
            self.mark_set("matchEnd", "%s+%sc" % (index,count.get()))
            text = self.get("matchStart","matchEnd")
            #text for words which shouldn't be marked:
            if text[:5] == ".word": continue
            if text[:6] == ".align": continue
            if text[:6] == ".thumb": continue
            if text[:5] == ".org": continue
            if text[:6] == ".text": continue
            if text[:8] == ".global": 
                self.global_line = int(float(index))
                continue
            if tag == "LABEL":
                self.labels.append(text[0:-1])
            self.tag_add(tag, "matchStart","matchEnd")
            
    def highlight_sub_pattern(self, pattern, tag, start="1.0", end="end", regexp=False):
        _start = self.index(start)
        _end = self.index(end)
        self.mark_set("matchStart",_start)
        self.mark_set("matchEnd",_start)
        self.mark_set("searchLimit", _end)

        _count = tk.IntVar()
        while True:
            _index = self.search(pattern, "matchEnd","searchLimit",
                                count=_count, regexp=regexp)
            if _index == "": break
            self.mark_set("matchStart", _index)
            self.mark_set("matchEnd", "%s+%sc" % (_index,_count.get()))
            if self.global_line != 0.0:
                if self.global_line == int(float(_index)):
                    continue
            
            self.tag_add(tag, "matchStart","matchEnd")
        
class TextLineNumbers(tk.Canvas):
    def __init__(self, *args, **kwargs):
        tk.Canvas.__init__(self, *args, **kwargs)
        self.textwidget = None

    def attach(self, text_widget):
        self.textwidget = text_widget

    def redraw(self, *args):
        '''redraw line numbers'''
        self.delete("all")

        i = self.textwidget.index("@0,0")
        
        
        while True :
            dline= self.textwidget.dlineinfo(i)
            if dline is None: break
            y = dline[1]
            linenum = str(i).split(".")[0]
            self.create_text(2,y,anchor="nw", text=linenum)
            i = self.textwidget.index("%s+1line" % i)
            p = float(i)-1.0
            self.config(width=10*(len(str(p))-2))
            
        


class App:
#File Menu Functions:
#----------------------------------------------------------------------
    def doNew(self, *args):
        # Clear the text
        self.text.delete(0.0, END)
        self.open_file = None
        self.root.title("THUMB Editor: New File")
        self.modded = False

    def doSaveAs(self, *args):
        # Returns the saved file
        if self.open_file != None:
            self.current_dir = os.path.dirname(self.open_file.name)
        else: self.current_dir = "."
        
        file = tkFileDialog.asksaveasfile(mode='w', defaultextension=".asm", initialdir=self.current_dir)
        if file == None:
            return False
        textoutput = self.text.get(0.0, END) # Gets all the text in the field
        
        file.write(textoutput.rstrip()) # With blank perameters, this cuts off all whitespace after a line.
        file.write("\n") # Then we add a newline character.
        file.close()
        self.open_file = open(file.name, "r+")
        if self.open_file != None:
            self.root.title("THUMB Editor: "+self.open_file.name)
        else:
            self.root.title("THUMB Editor: New File")
        self.modded = False
        
    def doSave(self, *args):
        #Save to currently open file.
        if self.open_file != None:
            self.open_file.seek(0)
            self.open_file.truncate()
            textoutput = self.text.get(0.0, END) # Gets all the text in the field
            self.open_file.write(textoutput.rstrip()) # With blank perameters, this cuts off all whitespace after a line.
            self.open_file.write("\n")
            self.open_file.close()
            self.modded = False
        else: self.doSaveAs()

    def doOpen(self, *args):
        # Returns the opened file
        if self.open_file != None:
            self.current_dir = os.path.dirname(self.open_file.name)
        else: self.current_dir = "."
        tmp = tkFileDialog.askopenfile(mode='r+', initialdir=self.current_dir)
        if tmp == None:
            return False
        else: self.open_file = tmp
        fileContents = self.open_file.read() # Get all the text from file.

        # Set current text to file contents
        self.text.delete(0.0, END)
        self.text.insert(0.0, fileContents)
        self.modded = False
        
        if self.open_file != None:
            self.root.title("THUMB Editor: "+self.open_file.name)
        else:
            self.root.title("THUMB Editor: New File")

#Base Converter
#----------------------------------------------------------------------  

    def base_converter(self):
        self.base = Toplevel(padx=5, pady=5)
        self.base.title("Base Converter")
        

        self.base_text_input = Entry(self.base)
        self.base_text_input.pack()
        
        self.base_var_a = IntVar(master=self.base)
        self.base_var_a.set(2)
        self.base_var_b = IntVar(master=self.base)
        self.base_var_b.set(2)
        
        Label(self.base, text="Convert:").pack()
        
        Radiobutton(self.base, text="Binary", variable=self.base_var_a, value=2).pack(anchor=W)
        Radiobutton(self.base, text="Decimal", variable=self.base_var_a, value=10).pack(anchor=W)
        Radiobutton(self.base, text="Hexadecimal", variable=self.base_var_a, value=16).pack(anchor=W)
        
        Label(self.base, text="To:").pack()
        
        Radiobutton(self.base, text="Binary", variable=self.base_var_b, value=2).pack(anchor=W)
        Radiobutton(self.base, text="Decimal", variable=self.base_var_b, value=10).pack(anchor=W)
        Radiobutton(self.base, text="Hexadecimal", variable=self.base_var_b, value=16).pack(anchor=W)
        
        Button(self.base, text="Convert", command=self.do_conversion).pack()
        
        Label(self.base, text="Result:").pack()
        
        self.base_text_result = Entry(self.base)
        self.base_text_result.pack()
        
        
    def do_conversion(self, *args):
        import re
        num = self.base_text_input.get()
        a = self.base_var_a.get()
        b = self.base_var_b.get()
        if a == 2:
            re1=re.compile(r"^[^01]+$")
            if re1.search(num):
                self.do_error("Invalid character in base 2.")
                return
            num = BINARY(num)
            
        elif a == 10:
            re1=re.compile(r"^[^0-9]+$")
            if  re1.search(num):
                self.do_error("Invalid character in base 10.")
                return
            num = DECIMAL(num)
            
        elif a == 16:
            re1=re.compile(r"^[^A-Fa-f0-9]+$")
            if  re1.search(num):
                self.do_error("Invalid character in base 16.")
                return
            num = HEXADECIMAL(num)
        else: return


        if b == 2:
            num.base = BINARY
        elif b == 10:
            num.base = DECIMAL
        elif b == 16:
            num.base = HEXADECIMAL
        else: return

        self.base_text_result.delete(0, END)
        self.base_text_result.insert(0, num)

        
        
        
#Compile Menu Functions:
#--------------------------------------------------------------
		          
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
        w = self.root.winfo_screenwidth()
        h = self.root.winfo_screenheight()
        x = str((w/2)-200)
        y = str((h/2)-200)
        error_pop_up.geometry('+'+x+'+'+y)
        error_pop_up.title("Error")
        error_pop_up.grid_columnconfigure(0, minsize=200)
        
        msg = Message(error_pop_up, text=error_msg, width=200)
        msg.grid(row=0, column=0, pady=5)

        button = Button(error_pop_up, text="Dismiss", command=error_pop_up.destroy, width=12)
        button.grid(row=2, column=0, pady=5)
        
    def do_popup(self, title, msg):
        pop_up = Toplevel()
        w = self.root.winfo_screenwidth()
        h = self.root.winfo_screenheight()
        x = str((w/2)-200)
        y = str((h/2)-200)
        pop_up.geometry('+'+x+'+'+y)
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
        
    def doRomInsert(self, *args):
        self.binary = os.path.join(self.path, "temp.bin")
        error = self.createBinary("temp.asm", self.binary)
        if error:
            return False
            
        if self.open_file != None:
            self.current_dir = os.path.dirname(self.open_file.name)
        else: self.current_dir = "."
        
        self.ROM = tkFileDialog.askopenfile(mode='r+b', title="Select Rom...", 
        initialdir=self.current_dir,
        filetypes=[("Rom Files","*.gba"), ("Binary Files",'*.bin'),('All Files','*')])
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

        

    def doTestCompile(self, *args):
        binary = os.path.join(self.path, "temp.bin")
        error = self.createBinary("temp.asm", binary)
        if not error:
            os.remove(binary)
            self.do_popup("Assembler", "Compile Successful.")
            return True
        else:
            return False
        
            
        
        
    def doBinCompile(self, *args):
        if self.open_file != None:
            self.current_dir = os.path.dirname(self.open_file.name)
        else: self.current_dir = "."
        
        open_file = tkFileDialog.asksaveasfile(
        mode='w', 
        initialdir=self.current_dir,
        defaultextension=".bin", 
        title="Compile Binary as...")

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
        
        assembler = "\""+os.path.join(self.path,"as")+"\""
        
        as_proccess = subprocess.Popen(
        assembler+" -mthumb "+"-mthumb-interwork "+"--fatal-warnings "+"\""+source+"\"", 
        bufsize=2048, shell=True, 
        stderr=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stdin=subprocess.PIPE)
        

        (as_output, as_err) = as_proccess.communicate()
        
        as_proccess.wait()
        if as_err != "":
            self.do_error(as_err)
            os.remove(source)
            return True
        
        objcopy = "\""+os.path.join(self.path,"objcopy")+"\""
        a_out = "\""+os.path.join(self.path,"a.out")+"\""
        
        objcopy_proccess = subprocess.Popen(
        objcopy+" -O binary "+a_out+" "+"\""+temp_bin+"\"",  
        bufsize=2048, 
        shell=True, 
        stderr=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stdin=subprocess.PIPE)

        
        (objcopy_output, objcopy_err) = objcopy_proccess.communicate()
        
        objcopy_proccess.wait()
        if objcopy_err != "":
            self.do_error(objcopy_err)
            os.remove(source)
            os.remove("a.out")
            return True
            

        os.remove(source)
        os.remove("a.out")
        #as_proccess.terminate()
        #objcopy_proccess.terminate()
        #as_proccess.kill()
        #objcopy_proccess.kill()
        return False
        
    def doRomInsertOrg(self, *args):
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
        w = self.root.winfo_screenwidth()
        h = self.root.winfo_screenheight()
        x = str((w/2)-200)
        y = str((h/2)-200)
        self.preferences.geometry('+'+x+'+'+y)
        self.preferences.title("Preferences")
        self.preferences.grid_columnconfigure(0, minsize=150)
        
        options_message = Message(self.preferences, text="-Basic Options-", width=200)
        options_message.grid(row=0, column=0, pady=5, columnspan = 2)
        
        fg_msg = Message(self.preferences, text="Foreground Color", width=150)
        fg_msg.grid(row=1, column=0, pady=5)
        
        fg_button = Button(self.preferences, text="Color Chooser", command=self.deal_with_fg_color , width=15)
        fg_button.grid(row=1, column=1, pady=5, padx=5)
        
        bg_msg = Message(self.preferences, text="Background Color", width=150)
        bg_msg.grid(row=2, column=0, pady=5)
        
        bg_button = Button(self.preferences, text="Color Chooser", command=self.deal_with_bg_color , width=15)
        bg_button.grid(row=2, column=1, pady=5, padx=5)
        
        cursor_msg = Message(self.preferences, text="Cursor Color", width=150)
        cursor_msg.grid(row=3, column=0, pady=5)
        
        cursor_button = Button(self.preferences, text="Color Chooser", command=self.deal_with_cursor_color , width=15)
        cursor_button.grid(row=3, column=1, pady=5, padx=5)
        
        highlight_message = Message(self.preferences, text="-Syntax Highlighting-", width=200)
        highlight_message.grid(row=4, column=0, columnspan = 2, pady=5, padx=5)
        
        label_msg = Message(self.preferences, text="Label Color", width=150)
        label_msg.grid(row=5, column=0, pady=5)
        
        label_button = Button(self.preferences, text="Color Chooser", command=self.deal_with_labels_color , width=15)
        label_button.grid(row=5, column=1, pady=5, padx=5)
        
        large_msg = Message(self.preferences, text="Defined Number Color", width=150)
        large_msg.grid(row=6, column=0, pady=5)
        
        large_button = Button(self.preferences, text="Color Chooser", command=self.deal_with_large_color , width=15)
        large_button.grid(row=6, column=1, pady=5, padx=5)
        
        comment_msg = Message(self.preferences, text="Comment Color", width=150)
        comment_msg.grid(row=7, column=0, pady=5)
        
        comment_button = Button(self.preferences, text="Color Chooser", command=self.deal_with_comment_color , width=15)
        comment_button.grid(row=7, column=1, pady=5, padx=5)
        
        
        
        
    def deal_with_fg_color(self):
        color = askcolor()
        self.text.config(fg=color[1])
        self.preferences.deiconify()
        self.preference_storer("store")
        
    def deal_with_bg_color(self):
        color = askcolor()
        self.text.config(bg=color[1])
        self.preferences.deiconify()
        self.preference_storer("store")
        
    def deal_with_labels_color(self):
        color = askcolor()
        self.text.label_color = color[1]
        self.preferences.deiconify()
        self.preference_storer("store")
        
    def deal_with_large_color(self):
        color = askcolor()
        self.text.large_color = color[1]
        self.preferences.deiconify()
        self.preference_storer("store")
        
    def deal_with_comment_color(self):
        color = askcolor()
        self.text.comment_color = color[1]
        self.preferences.deiconify()
        self.preference_storer("store")

    def deal_with_cursor_color(self):
        color = askcolor()
        self.text.config(insertbackground=color[1])
        self.preferences.deiconify()
        self.preference_storer("store")






    def preference_storer(self, method):
        opts_b = ["fg", "bg", "insertbackground"]
        opts_sh = [self.text.label_color, self.text.large_color, self.text.comment_color]
        
        #with open(os.path.join(self.path, "preferences.ini"), "w+") as prefs: prefs.close()
        
        with open(os.path.join(self.path, "preferences.ini"), "r+") as prefs:
            
            if method == "store":
                for opt in opts_b:
                    tmp = self.text.config(opt)
                    prefs.write(tmp[4]+"\n")
                    
                for opt in opts_sh:
                    tmp = opt
                    prefs.write(tmp+"\n")
                return
            
            if method == "load":
                line = prefs.read(1)
                if line == "":
                    return
                prefs.seek(0)
                tmp = prefs.readline()
                self.text.config(fg=tmp[0:7])
                tmp = prefs.readline()
                self.text.config(bg=tmp[0:7])
                tmp = prefs.readline()
                self.text.config(insertbackground=tmp[0:7])
                tmp = prefs.readline()
                self.text.label_color = tmp[0:7]
                tmp = prefs.readline()
                self.text.large_color = tmp[0:7]
                tmp = prefs.readline()
                self.text.comment_color = tmp[0:7]
                
                return
#Edit Menu Functions:
#----------------------------------------------------------------------
    def selectall(self, *args):
        self.text.tag_add(SEL, "1.0", END)
        self.text.mark_set(INSERT, "1.0")
        self.text.see(INSERT)
        return 'break'
        
    def insert_comment(self, *args):
        self.text.insert(INSERT, "/**/")
        cursor = self.text.index(INSERT)
        cursor = cursor.split(".")
        self.text.mark_set(INSERT, "%d.%d" % (int(cursor[0]), int(cursor[1]) - 2))
        




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
that became the basis of this program, on his blog.\n-Bryan Oakley for his extremely detailed example of how \
to add line numbers and whose code I merged with mine.\n-Zachary Voase for his base converter library that \
made that feature so much easier.", width=400, pady=5)
        msg2.pack()
        
        button = Button(about, text="Close", pady=5, command=about.destroy, width=12)
        button.pack()

#------------------------------------------------------------------------------
    def __init__(self):
        # Set up the screen, the title, and the size.
        self.root = Tk()
        
        self.root.minsize(width=500,height=400)
        self.path = module_path()
        os.chdir(self.path)
        
        
        self.root.protocol('WM_DELETE_WINDOW', self.ask_if_need_to_save)

        
               
        # Set up basic Menu
        menubar = Menu(self.root)

        # Set up a separate menu that is a child of the main menu
        filemenu = Menu(menubar,tearoff=0)
        filemenu.add_command(label="New File", command=self.doNew, accelerator="Ctrl+n")
        
        #set up an Edit Menu
        edit_menu = Menu(menubar, tearoff=0)
        edit_menu.add_command(label="Cut", accelerator="Ctrl+x", command=lambda: self.text.event_generate('<Control-x>'))
        edit_menu.add_command(label="Copy", accelerator="Ctrl+c", command=lambda: self.text.event_generate('<Control-c>'))
        edit_menu.add_command(label="Paste", accelerator="Ctrl+v", command=lambda: self.text.event_generate('<Control-v>'))
        edit_menu.add_command(label="Select All", command=self.selectall, accelerator="Ctrl+a")
        edit_menu.add_command(label="Insert Comment", command=self.insert_comment, accelerator="Ctrl+q")
        
        
        
        #create an options menu:
        option_menu = Menu(menubar,tearoff=0)
        option_menu.add_command(label="Preferences", command=self.doPreferences)
        
        #Create a menu for compiling.
        compile_menu = Menu(menubar,tearoff=0)
        compile_menu.add_command(label="Test Compile", command=self.doTestCompile, accelerator="Ctrl+Shift+p")
        compile_menu.add_command(label="Output to .bin", command=self.doBinCompile, accelerator="Ctrl+p")
        compile_menu.add_command(label="Insert into Rom", command=self.doRomInsert, accelerator="Ctrl+u")
        compile_menu.add_command(label="Insert into Rom via .org", command=self.doRomInsertOrg, accelerator="Ctrl+Shift+u")
        
        #Create a help menu:
        help_menu = Menu(menubar,tearoff=0)
        help_menu.add_command(label="About", command=self.do_about)
        help_menu.add_command(label="Base Converter", command=self.base_converter)

        # Try out openDialog
        filemenu.add_command(label="Open", command=self.doOpen, accelerator="Ctrl+o")

        # Try out the saveAsDialog
        filemenu.add_command(label="Save as", command=self.doSaveAs, accelerator="Ctrl+Shift+s")
        filemenu.add_command(label="Save", command=self.doSave, accelerator="Ctrl+s")
        
        
        
        menubar.add_cascade(label="File", menu=filemenu)
        menubar.add_cascade(label="Edit", menu=edit_menu)
        
        menubar.add_cascade(label="Options", menu=option_menu)
        menubar.add_cascade(label="Compile", menu=compile_menu)
        menubar.add_cascade(label="Help", menu=help_menu)
        self.root.config(menu=menubar)

        # Set up the text widget
        self.text = CustomText(self.root)
        self.vsb = tk.Scrollbar(orient="vertical", command=self.text.yview)
        self.xsb = tk.Scrollbar(orient="horizontal", command=self.text.xview)
        self.text.configure(wrap=NONE, xscrollcommand=self.xsb.set, yscrollcommand=self.vsb.set, insertbackground="#FFFFFF")
        self.linenumbers = TextLineNumbers(self.root, width=10)
        self.linenumbers.attach(self.text)

        self.vsb.pack(side="right", fill="y")
        self.xsb.pack(side="bottom", fill="x")
        self.linenumbers.pack(side="left", fill="y")
        self.text.pack(side="right", fill="both", expand=True)

        self.text.bind("<<Change>>", self._on_change)
        self.text.bind("<Configure>", self._on_change)
        self.text.bind("<Control-Key-n>", self.doNew)
        self.text.bind("<Control-Key-a>", self.selectall)
        self.text.bind("<Control-Key-P>", self.doTestCompile)
        self.text.bind("<Control-Key-p>", self.doBinCompile)
        self.text.bind("<Control-Key-u>", self.doRomInsert)
        self.text.bind("<Control-Key-U>", self.doRomInsertOrg)
        self.text.bind("<Control-Key-o>", self.doOpen)
        self.text.bind("<Control-Key-S>", self.doSaveAs)
        self.text.bind("<Control-Key-s>", self.doSave)
        self.text.bind("<Control-Key-z>", self.text.edit_undo)
        self.text.bind("<Control-Key-y>", self.text.edit_redo)
        self.text.bind("<Control-Key-q>", self.insert_comment)
        
        self.text.bind("<<Modified>>", self.on_mod)
        
        
        edit_menu.add_command(label="Undo", command=self.text.edit_undo, accelerator="Ctrl+z")
        edit_menu.add_command(label="Redo", command=self.text.edit_redo, accelerator="Ctrl+y")
        
        self.preference_storer("load")

        if len(sys.argv) > 1:
            file_name = sys.argv[1]
            self.open_file = open(str(file_name), "r+")
            fileContents = self.open_file.read() # Get all the text from file.

            # Set current text to file contents
            self.text.delete(0.0, END)
            self.text.insert(0.0, fileContents)
            self.saved_text = self.text.get(0.0, END)
            
        else:
            self.open_file = None
            self.saved_text = None
        self.modded = False
            
        if self.open_file != None:
            self.root.title("THUMB Editor: "+self.open_file.name)
        else:
            self.root.title("THUMB Editor: New File")
            
    def on_mod(self, *args):
        self.modded = True
    
    def ask_if_need_to_save(self):
        if self.open_file != None:
            
            if self.modded == True:
                result = tkMessageBox.askyesnocancel("Save changes?", 
                "Save changes to "+self.open_file.name+" before quitting?")
                
                if result == True:
                    self.doSave()
                    self.root.destroy()
                elif result == False:
                    self.root.destroy()
                
            else: self.root.destroy()
        else:
            if self.modded == True:
                result = tkMessageBox.askyesnocancel("Save changes?", 
                    "Save changes before quitting?")
                
                if result == True:
                    self.doSaveAs()
                    self.root.destroy()
                elif result == False:
                    self.root.destroy()
            else: 
                self.root.destroy()
            
                    
            

    def _on_change(self, event):
        self.linenumbers.redraw()
        self.text.highlighting()


app = App()
app.root.mainloop()
