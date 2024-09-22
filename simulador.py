import tkinter as tk
from tkinter import filedialog, messagebox
import json

class SingletonRegister:
    def __init__(self, name: str, value: int):
        self.name = name
        self.value = value

class NormaMachineSimulator:
    def __init__(self, root):
        self.root = root
        self.root.title("Simulador de Máquina Norma")

        # Configurar o layout
        self.frame_left = tk.Frame(root)
        self.frame_left.pack(side=tk.LEFT, padx=16, pady=16)

        self.frame_right = tk.Frame(root)
        self.frame_right.pack(side=tk.RIGHT, padx=16, pady=16)

        # Configurar campos de entrada
        tk.Label(self.frame_left, text="Número de Registradores:").grid(row=0, column=0, sticky=tk.W)
        self.num_registradores = tk.Entry(self.frame_left, width=25)
        self.num_registradores.grid(row=0, column=1, padx=16)

        tk.Label(self.frame_left, text="Valores Iniciais dos Registradores (separados por vírgula):").grid(row=1, column=0, sticky=tk.W)
        self.valores_iniciais = tk.Entry(self.frame_left, width=25)
        self.valores_iniciais.grid(row=1, column=1, padx=16)

        tk.Label(self.frame_left, text="Nomes dos Registradores (separados por vírgula):").grid(row=2, column=0, sticky=tk.W)
        self.nomes_registradores = tk.Entry(self.frame_left, width=25)
        self.nomes_registradores.grid(row=2, column=1, padx=16)

        tk.Label(self.frame_left, text="Programa (instruções rotuladas):").grid(row=3, column=0, sticky=tk.W)
        self.text_programa = tk.Text(self.frame_left, width=30, height=10)
        self.text_programa.grid(row=3, column=1, padx=16)

        # Botões
        tk.Button(self.frame_left, text="Carregar JSON", command=self.carregar_json).grid(row=4, column=0, pady=10, sticky=tk.W)
        tk.Button(self.frame_right, text="Executar Programa", command=self.executar_programa).pack(side=tk.LEFT, padx=10)
        tk.Button(self.frame_right, text="Limpar Saída", command=self.limpar_saida).pack(side=tk.LEFT, padx=10)

        # Saída
        self.text_output = tk.Text(self.frame_right, width=80, height=35)
        self.text_output.pack()

        # Inicializar variáveis
        self.registradores = {}
        self.programa = {}

    def carregar_json(self):
        arquivo = filedialog.askopenfilename(defaultextension=".json", filetypes=[("Arquivos JSON", "*.json")])
        if not arquivo:
            return

        try:
            with open(arquivo, "r", encoding='utf-8') as f:
                dados = json.load(f)
                # Carregar registradores
                self.registradores = dados.get("registradores", {})
                num_registradores = len(self.registradores)
                self.num_registradores.delete(0, tk.END)
                self.num_registradores.insert(0, num_registradores)
                
                valores = list(self.registradores.values())
                self.valores_iniciais.delete(0, tk.END)
                self.valores_iniciais.insert(0, ",".join(map(str, valores)))
                
                nomes = list(self.registradores.keys())
                self.nomes_registradores.delete(0, tk.END)
                self.nomes_registradores.insert(0, ",".join(nomes))
                
                # Carregar programa
                self.programa = dados.get("programa", {})
                self.text_programa.delete(1.0, tk.END)
                for linha in sorted(self.programa.keys(), key=lambda x: int(x)):
                    self.text_programa.insert(tk.END, f"{linha}: {self.programa[linha]}\n")
                
                self.text_output.insert(tk.END, "JSON carregado com sucesso.\n")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao carregar JSON: {e}")

    def executar_programa(self):
        self.text_output.delete(1.0, tk.END)

        lista_registradores = self.nomes_registradores.get().split(",")
        lista_valores = self.valores_iniciais.get().split(",")
        lista_singleton_register = []
        lista_de_execucao = []
        lista_instrucoes = []

        def get_register(name):
            for register in lista_singleton_register:
                if register.name == name:
                    return register
            return None

        def add(register):
            register.value += 1

        def sub(register):
            register.value -= 1

        def mod(register, value):
            register.value %= value

        def inc(register):
            register.value += 1

        def dec(register):
            register.value -= 1

        def goto(linha):
            return linha

        def end():
            return False  # Termina a execução

        def sum(register1, register2):
            register1.value += register2.value

        def count(register, value):
            register.value = value

        def get_register_in_parentheses(instrucao):
            return instrucao.split("(")[1].split(")")[0]

        try:
            # Inicializar registradores
            for i in range(len(lista_registradores)):
                singletonRegister = SingletonRegister(lista_registradores[i], int(lista_valores[i]))
                lista_singleton_register.append(singletonRegister)

            for linha in sorted(self.programa.keys(), key=lambda x: int(x)):
                lista_de_execucao.append(self.programa[linha])

            # Processar instruções
            pc = 0  # Contador de programa
            while pc < len(lista_de_execucao):
                instrucao = lista_de_execucao[pc]
                self.text_output.insert(tk.END, f"Executando linha {pc + 1}: {instrucao}\n")

                if instrucao.startswith("if"):
                    reg_name = get_register_in_parentheses(instrucao)
                    registrador = get_register(reg_name)
                    if registrador and registrador.value != 0:
                        self.text_output.insert(tk.END, f"{reg_name} é não zero. Continuando com o próximo bloco.\n")
                        pc += 1
                    else:
                        # Procurar o próximo `goto` para pular para a parte `else`
                        while pc < len(lista_de_execucao) and not lista_de_execucao[pc].startswith("else"):
                            pc += 1
                        if pc < len(lista_de_execucao):
                            self.text_output.insert(tk.END, f"Pulando para o bloco `else`\n")
                            pc += 1
                elif instrucao.startswith("else"):
                    # Procurar o próximo `goto` após o `else`
                    while pc < len(lista_de_execucao) and not lista_de_execucao[pc].startswith("goto"):
                        pc += 1
                    if pc < len(lista_de_execucao):
                        linha = int(lista_de_execucao[pc].split("goto")[1].strip())
                        pc = goto(linha) - 1  # Ajuste de índice
                        self.text_output.insert(tk.END, f"Indo para linha {linha}\n")
                elif instrucao.startswith("add"):
                    reg_name = get_register_in_parentheses(instrucao)
                    registrador = get_register(reg_name)
                    if registrador:
                        add(registrador)
                        self.text_output.insert(tk.END, f"Registrador {reg_name} incrementado para {registrador.value}\n")
                    pc += 1
                elif instrucao.startswith("sub"):
                    reg_name = get_register_in_parentheses(instrucao)
                    registrador = get_register(reg_name)
                    if registrador:
                        sub(registrador)
                        self.text_output.insert(tk.END, f"Registrador {reg_name} decrementado para {registrador.value}\n")
                    pc += 1
                elif instrucao.startswith("mod"):
                    reg_name = get_register_in_parentheses(instrucao)
                    registrador = get_register(reg_name)
                    valor = int(instrucao.split(",")[1].strip())
                    if registrador:
                        mod(registrador, valor)
                        self.text_output.insert(tk.END, f"Registrador {reg_name} modificado para {registrador.value}\n")
                    pc += 1
                elif instrucao.startswith("inc"):
                    reg_name = get_register_in_parentheses(instrucao)
                    registrador = get_register(reg_name)
                    if registrador:
                        inc(registrador)
                        self.text_output.insert(tk.END, f"Registrador {reg_name} incrementado para {registrador.value}\n")
                    pc += 1
                elif instrucao.startswith("dec"):
                    reg_name = get_register_in_parentheses(instrucao)
                    registrador = get_register(reg_name)
                    if registrador:
                        dec(registrador)
                        self.text_output.insert(tk.END, f"Registrador {reg_name} decrementado para {registrador.value}\n")
                    pc += 1
                elif instrucao.startswith("goto"):
                    linha = int(instrucao.split("goto")[1].strip())
                    pc = goto(linha) - 1  # Ajuste de índice
                    self.text_output.insert(tk.END, f"Indo para linha {linha}\n")
                elif instrucao.startswith("end"):
                    self.text_output.insert(tk.END, "Programa finalizado.\n")
                    break

            self.text_output.insert(tk.END, "Estado final dos registradores:\n")
            for reg in lista_singleton_register:
                self.text_output.insert(tk.END, f"{reg.name}: {reg.value}\n")

        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao executar programa: {e}")

    def limpar_saida(self):
        self.text_output.delete(1.0, tk.END)

if __name__ == "__main__":
    root = tk.Tk()
    app = NormaMachineSimulator(root)
    root.mainloop()
