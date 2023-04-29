import logging as log
import os
import re
import hashlib
from datetime import datetime
from PIL import ImageTk, Image
from tkinter import Frame, ttk, Text, LabelFrame, Scrollbar, Menu, font, \
    BooleanVar, TclError, Tk, HORIZONTAL, VERTICAL, WORD, SUNKEN, INSERT, CURRENT, NONE, END, messagebox, \
    SEL_FIRST, SEL_LAST
from tkinter.filedialog import askopenfilename
from tkinter.filedialog import asksaveasfilename

palabrasReservadas = ('false', 'do', 'append', 'none', 'true', 'and', 'print', 'as', 'assert', 'async', 'await', 'break', 'class', 'continue', 'def', 'del', 'elif', 'else', 'except', 'finally', 'for', 'from', 'global', 'if', 'import', 'in', 'is', 'lambda', 'nonlocal', 'not', 'or', 'pass', 'raise', 'return', 'try', 'while', 'with', 'yield')
operadores = ('+', '-', '*', '/', '=', '<', '>')
numeros = ('0', '1', '2', '3', '4', '5', '6', '7', '8', '9')
delimitadores = ('(', ')', ':', ',', ';')
operadoresCompuestos = ('==', '<=', '>=', '+=', '-=')

class Interface(Frame):
    def __init__(self, master=None, *_):
        Frame.__init__(self, master)
        self.master = master

        # settings variables
        self.word_wrap = BooleanVar()
        self.word_wrap.set(True)
        
        # init methods
        self.__init_main_window()
        self.__build_menu_bar()
        self.__bind_shortcuts()
        self.toggle_word_wrap()
        self.context_menu = Menu(self.master, tearoff=0)

        self.last_hash = get_signature(self.text_area.get(1.0, END))
        self.last_hash2 = get_signature(self.text_area2.get(1.0, END))
        self.last_hash3 = get_signature(self.text_area3.get(1.0, END))



    def __init_main_window(self):
        self.text_area = Text(self.master, undo=True)
        self.text_area.config(font=font.Font(family="Courier New", size=10), wrap=WORD)

        self.text_area2 = Text(self.master, undo=True)
        self.text_area2.config(font=font.Font(family="Courier New", size=10), wrap=WORD)

        self.text_area3 = Text(self.master, undo=True)
        self.text_area3.config(font=font.Font(family="Courier New", size=10), wrap=WORD)

        # To add scrollbar
        self.scroll_bar_x = Scrollbar(self.master, orient=HORIZONTAL)
        self.scroll_bar_y = Scrollbar(self.master, orient=VERTICAL)
        __file = None

        try:
            self.master.iconbitmap('./images/notepad.ico')
        except TclError:
            pass

        # Set the window text
        self.master.title('Untitled - Notepad')

        self.text_area.grid(row=0, column=0)
        self.text_area2.grid(row=0, column=1)
        self.text_area3.grid(row=1, column=0, columnspan=2, sticky='nsew')

        # To make the text area auto resizable
        self.master.grid_rowconfigure(0, weight=1)
        self.master.grid_rowconfigure(1, weight=4)
        self.master.grid_columnconfigure(0, weight=1)
        self.master.grid_columnconfigure(1, weight=4)

        self.text_area.focus()
        self.text_area2.focus()
        self.text_area3.focus()


    def __build_menu_bar(self):
        # main and submenus
        self.menu_bar = Menu(self.master)
        self.file_menu = Menu(self.menu_bar, tearoff=0)
        self.analyzer_menu = Menu(self.menu_bar, tearoff=0)

        # File Menu
        self.menu_bar.add_cascade(label='Archivo', underline=0, menu=self.file_menu)
        self.file_menu.add_command(label='Nuevo', underline=0, accelerator='Ctrl+N', command=new_file)
        self.file_menu.add_command(label='Abrir...', underline=0, accelerator='Ctrl+O', command=open_file)
        self.file_menu.add_command(label='Guardar', underline=0, accelerator='Ctrl+S', command=save_file)
        self.file_menu.add_command(label='Guardar como...', underline=5, command=save_file_as)
        self.file_menu.add_separator()
        self.file_menu.add_command(label='Sobre el creador', underline=5, command=show_about)
        self.file_menu.add_separator()
        self.file_menu.add_command(label='Salir', underline=1, command=self.quit_application)

        # Analyzer Menu
        self.menu_bar.add_cascade(label='Compilador', underline=0, menu=self.analyzer_menu)
        self.analyzer_menu.add_command(label='Compilar', underline=4, command=self.compilar)
        self.analyzer_menu.add_command(label='Tabla de simbolos', underline=4, command=self.compilar)
        self.analyzer_menu.add_separator()
        self.analyzer_menu.add_command(label='Limpiar', underline=0, command=self.limpiarAnalisis)

        # MASTER CONFIG
        self.master.config(menu=self.menu_bar)


    def show_context_menu(self, event):
        try:
            self.context_menu = Menu(self.master, tearoff=0)
            self.context_menu.add_command(label='Deshacer', underline=2, accelerator='Ctrl+Z', command=self.undo)
            self.context_menu.add_separator()
            self.context_menu.add_command(label='Cortar', underline=2, accelerator='Ctrl+X', command=self.cut)
            self.context_menu.add_command(label='Copiar', underline=0, accelerator='Ctrl+C', command=self.copy)
            self.context_menu.add_command(label='Pegar', underline=0, accelerator='Ctrl+V', command=self.paste)
            self.context_menu.add_separator()
            self.context_menu.add_command(label='Seleccionar todo', underline=2, accelerator='Ctrl+A',
                                          command=self.select_all)
            self.context_menu.tk_popup(event.x_root, event.y_root)

            self.context_menu.add_command(label='Dev', underline=0, command=self.obtenertexto)


        finally:
            self.context_menu.grab_release()

    def toggle_word_wrap(self):
        if self.word_wrap.get():
            self.text_area.config(wrap=WORD)
            self.scroll_bar_x.grid_forget()
            log.info("word wrap on, scroll bar off")
        else:
            self.text_area.config(wrap=NONE)
            self.scroll_bar_x.grid(column=0, row=1, sticky='nsew')
            log.info("word wrap off, scroll bar on")

    def __bind_shortcuts(self):
        self.master.bind_class('Text', '<Control-a>', self.select_all)
        self.master.bind_class('Text', '<Control-A>', self.select_all)
        self.master.bind_class('Text', '<Control-s>', save_file)
        self.master.bind_class('Text', '<Control-S>', save_file)
        self.master.bind_class('Text', '<Control-n>', new_file)
        self.master.bind_class('Text', '<Control-N>', new_file)
        self.text_area.bind_class(self.text_area, '<Button-3>', self.show_context_menu)

    def quit_application(self):
        if notepad.has_changed():
            save_box = messagebox.askquestion('Confirmar', '¿Quieres guardar antes de cerrar?',
                                              icon='warning')
            if save_box == 'yes':
                save_file()
        self.master.destroy()
        exit()

    def obtenertexto(self):
        print(notepad.get_text())

    def undo(self, *_):
        self.text_area.event_generate('<<Undo>>')


    def on_click(self, *_):
        try:
            self.context_menu.destroy()
        except AttributeError:
            log.warning('error occurred while trying to exit context menu, probably not instansiated')


    def cut(self, *_):
        self.text_area.event_generate('<<Cut>>')

    def copy(self, *_):
        self.text_area.event_generate('<<Copy>>')

    def paste(self, *_):
        self.text_area.event_generate('<<Paste>>')

    def select_all(self, *_):
        self.text_area.tag_add('sel', '1.0', 'end')

    def time_date(self, *_):
        now = datetime.now()
        s = now.strftime("%I:%M %p %m/%d/%Y")
        self.text_area.insert(INSERT, s)

    def run(self):
        # Run main application
        self.master.mainloop()

    def set_title(self, string):
        self.master.title(string + ' - Notepad')

    def clear_text(self):
        self.text_area.delete(1.0, END)

    def get_text(self):
        return self.text_area.get(1.0, END)

    def write_text(self, text, start_index=1.0):
        self.text_area.insert(start_index, text)

    def has_changed(self):
        if get_signature(self.text_area.get(1.0, END)) == self.last_hash:
            log.info('file has changed')
            return False
        else:
            log.info('file has not changed')
            return True
        
    def limpiarAnalisis(self):
        self.text_area2.delete('1.0', 'end-1c')
        self.text_area3.delete('1.0', 'end-1c')
        os.system('clear')
    
    def compilar(self):
        entrada = self.text_area.get(1.0, 'end-1c')

        salida = ''
        lineas = entrada.split('\n')

        for linea in lineas:  # Examinamos linea por linea

            if linea == '':  #Ignora las lineas vacias
                continue
            
            linea = linea.lower()

            #linea clasificada para el conversor lexico
            lineaConvertida = ''  #Str donde se va guardando los tokens de la linea clasificados
            indice = 0
            caracterActual = linea[indice]
            token = ''

            while indice< len(linea): #Analiza caracter por caracter de la linea
                if caracterActual == ' ' or (caracterActual in operadores) or (caracterActual in delimitadores):
                    tokenClasificado = self.clasificarToken(token)
                    if tokenClasificado != None:
                        lineaConvertida += tokenClasificado

                    if caracterActual in operadores and (indice+1 < len(linea)) and (linea[indice+1] in operadores): # == +=
                        caracterActual += linea[indice+1]

                        lineaConvertida += f'OP[{caracterActual}], '
                        indice = indice+2
                        if indice >= len(linea): break
                        caracterActual = linea[indice]
                        continue

                    elif caracterActual in operadores:
                        lineaConvertida += f'OP[{caracterActual}], '

                    elif caracterActual in delimitadores:
                        lineaConvertida += f'DEL[{caracterActual}], '
                    
                    token = ''

                elif indice == len(linea) - 1:  #Cuando estamos en el ultimo caracter de la linea
                    token += caracterActual
                    tokenClasificado = self.clasificarToken(token)

                    if tokenClasificado != None:
                        lineaConvertida += tokenClasificado

                else:
                    token += caracterActual
                
                indice = indice + 1
                if indice == len(linea): break
                caracterActual = linea[indice]
            

            lineaConvertida = lineaConvertida[:-2]
            salida += f"{lineaConvertida}\n"
        

        #añado la salida al cuadro de texto de conversor lexico
        salida += '\n'
        self.text_area2.insert(INSERT, salida)



    def clasificarToken(self, cadena):
        if cadena.startswith(numeros) and cadena.endswith(numeros):
            if cadena.find('.') != -1:
                return f'FLOAT[{cadena}], '
            return f'NUM[{cadena}], '
        elif cadena.startswith('"') and cadena.endswith('"'):
            return f'LT[{cadena}], '
        elif cadena in palabrasReservadas:
            return f'PR[{cadena}], '
        elif cadena == '':
            return None
        else:
            return f'ID[{cadena}], '


def get_index(index):
    return tuple(map(int, str.split(index, ".")))

def open_file():
    global FILE
    line = ''

    if notepad.has_changed():
        save_box = messagebox.askquestion('Confirmar', '¿Quieres guardar antes de cerrar el archivo?',
                                          icon='warning')
        if save_box == 'yes':
            save_file()

    FILE = askopenfilename(defaultextension='.txt',
                           initialdir='.',
                           filetypes=[('All Files', '*.*'),
                                      ('Text Documents', '*.txt'),
                                      ('Log Files', '*.log')])

    try:
        log.info("attempting to open file " + str(FILE))
        f = open(FILE, 'r')
        notepad.clear_text()
        lines = f.read()
        f.close()
        notepad.write_text(lines)
        line = lines[:4]
        notepad.set_title(os.path.basename(FILE))
        log.info(str(FILE) + " opened")

    except TypeError:
        log.error('TypeError', FILE)
    except FileNotFoundError:
        log.error('FileNotFoundError', FILE)

    if line.upper() == '.LOG':
        log.info(FILE + ' is a log, appending time stamp.')
        notepad.time_date()


def new_file():
    global FILE
    if notepad.has_changed():
        save_box = messagebox.askquestion('Confirmar', '¿Quieres guardar antes de cerrar el archivo?',
                                          icon='warning')
        if save_box == 'yes':
            save_file()

    notepad.set_title('Untitled')
    FILE = ''
    notepad.clear_text()


def save_file_as():
    global FILE

    try:
        FILE = asksaveasfilename(initialfile='*.txt', defaultextension='.txt',
                                 filetypes=[('All Files', '*.*'), ('Text Documents', '*.txt')])

        if FILE != '':
            # Try to save the file
            notepad.set_title(os.path.basename(FILE))
            f = open(FILE, 'w')
            f.write(notepad.get_text())
            # Change the window title
            f.close()

    except TclError:
        messagebox.showerror('Notepad', 'Error guardando el archivo.')


def save_file(*_):
    global FILE

    if FILE != '':
        try:
            print(FILE)
            f = open(FILE, 'w')
            f.write(notepad.get_text())
            f.close()

        except TclError:
            save_file_as()
    else:
        save_file_as()



def show_about():
    messagebox.showinfo('Notepad', 'Javier González Borja 0910-18-133645')


def get_signature(contents):
    m = hashlib.md5()
    m.update(contents.encode('utf-8'))
    return m.hexdigest()


# global vars
FILE = ''  # path to current file
log.basicConfig(level=log.INFO)


window = Tk()
window.geometry("1200x600")
notepad = Interface(window)
notepad.run()
