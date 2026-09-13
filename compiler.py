import re
import sys

# Primeiro módulo: analisador léxico

PADROES = [
    ("LPAR", r"\("),
    ("RPAR", r"\)"),
    ("FLOAT", r"\d+\.\d+"),
    ("INTEGER", r"\d+"),
    ("OP", r"==|!=|<=|>=|\+|-|\*|/|%|>|<"),
    ("KEYWORD", r"\b(if|while|begin|set|print)\b"),
    ("ID", r"[a-zA-Z_][a-zA-Z0-9_]*"),
    ("SKIP", r"[ \t]+"),
    ("NL", r"\n"),
    ("UNKNOWN", r"."),
]

class Token:
    def __init__(self, tipo, valor, linha):
        self.tipo = tipo
        self.valor = valor
        self.linha = linha

def tokenizar(codigo):
    regex = "|".join(
        f"(?P<{nome}>{padrao})"
        for nome, padrao in PADROES
    )

    tokens = []
    linha = 1

    for achado in re.finditer(regex, codigo):
        tipo = achado.lastgroup
        valor = achado.group()

        if tipo == "SKIP":
            continue

        if tipo == "NL":
            linha += 1
            continue

        if tipo == "UNKNOWN":
            raise Exception(
                f"erro léxico: caractere inválido "
                f"'{valor}' na linha {linha}."
            )

        if tipo == "KEYWORD":
            tipo = valor.upper()

        tokens.append(
            Token(tipo, valor, linha)
        )

    return tokens

# Segundo módulo: analisador sintático

class ParserMiniLisp:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def atual(self):
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return None

    def consumir(self):
        token = self.atual()
        if token is not None:
            self.pos += 1
        return token

    def parsear(self):
        if not self.tokens:
            raise Exception(
                "erro sintático: arquivo de entrada vazio."
            )

        ast = self.expressao()

        if self.atual() is not None:
            token = self.atual()
            raise Exception(
                f"erro sintático na linha {token.linha}: "
                f"token inesperado '{token.valor}'."
            )

        return ast

    def expressao(self):
        token = self.atual()

        if token is None:
            linha = (
                self.tokens[-1].linha
                if self.tokens
                else 1
            )
            raise Exception(
                f"erro sintático na linha {linha}: "
                "fim de arquivo inesperado. "
                "esperava-se ')'."
            )

        if token.tipo == "LPAR":
            return self.lista()

        tipos_validos = {
            "INTEGER",
            "FLOAT",
            "ID",
            "OP",
            "IF",
            "WHILE",
            "BEGIN",
            "SET",
            "PRINT"
        }

        if token.tipo in tipos_validos:
            return self.consumir()

        raise Exception(
            f"erro sintático na linha {token.linha}: "
            f"token inesperado '{token.valor}'."
        )

    def lista(self):
        abertura = self.consumir()
        itens = []

        while (
            self.atual() is not None
            and self.atual().tipo != "RPAR"
        ):
            itens.append(
                self.expressao()
            )

        if self.atual() is None:
            raise Exception(
                f"erro sintático na linha {abertura.linha}: "
                "fim de arquivo inesperado. "
                "esperava-se ')'."
            )

        self.consumir()
        self.validar_lista(itens)

        return itens

    def validar_lista(self, itens):
        if not itens:
            return
        if not isinstance(itens[0], Token):
            return

        cabeca = itens[0]
        quantidade = len(itens)

        regras = {
            "SET": (
                3,
                "estrutura 'set' malformada."
            ),
            "PRINT": (
                2,
                "estrutura 'print' malformada."
            ),
            "IF": (
                4,
                "estrutura 'if' malformada. "
                "esperava-se condição, bloco verdadeiro "
                "e bloco falso."
            ),
            "WHILE": (
                3,
                "estrutura 'while' malformada."
            ),
            "OP": (
                3,
                f"operador '{cabeca.valor}' "
                "precisa de dois operandos."
            ),
        }

        if cabeca.tipo in regras:
            esperado, mensagem = regras[cabeca.tipo]
            if quantidade != esperado:
                raise Exception(
                    f"erro sintático: {mensagem}"
                )

# Terceiro módulo: analisador semântico

class Simbolo:
    def __init__(self, nome, endereco, tipo):
        self.nome = nome
        self.endereco = endereco
        self.tipo = tipo
        self.escopo = "global"

class AnalisadorSemantico:
    def __init__(self):
        self.tabela = {}
        self.proximo_endereco = 0

    def analisar(self, ast):
        self.visitar(ast)
        return self.tabela

    def visitar(self, no):
        if isinstance(no, Token):
            if no.tipo == "INTEGER":
                return "inteiro"
            if no.tipo == "FLOAT":
                return "float"
            if no.tipo == "ID":
                if no.valor not in self.tabela:
                    raise Exception(
                        f"erro semântico: variável "
                        f"'{no.valor}' não inicializada."
                    )
                return self.tabela[no.valor].tipo

            raise Exception(
                f"erro semântico: símbolo inválido "
                f"'{no.valor}'."
            )

        if not isinstance(no, list) or not no:
            return "inteiro"

        cabeca = no[0]

        if not isinstance(cabeca, Token):
            raise Exception(
                "erro semântico: expressão inválida."
            )

        comando = cabeca.tipo

        if comando == "SET":
            variavel = no[1]

            if (
                not isinstance(variavel, Token)
                or variavel.tipo != "ID"
            ):
                raise Exception(
                    "erro semântico: o comando 'set' "
                    "deve receber um identificador."
                )

            tipo = self.visitar(no[2])

            if variavel.valor not in self.tabela:
                self.tabela[variavel.valor] = Simbolo(
                    variavel.valor,
                    self.proximo_endereco,
                    tipo
                )
                self.proximo_endereco += 1
            else:
                self.tabela[variavel.valor].tipo = tipo

            return tipo

        if comando == "PRINT":
            return self.visitar(no[1])

        if comando == "BEGIN":
            tipo = "inteiro"
            for item in no[1:]:
                tipo = self.visitar(item)
            return tipo

        if comando == "IF":
            self.visitar(no[1])
            tipo_then = self.visitar(no[2])
            tipo_else = self.visitar(no[3])

            if "float" in (tipo_then, tipo_else):
                return "float"
            return "inteiro"

        if comando == "WHILE":
            self.visitar(no[1])
            self.visitar(no[2])
            return "inteiro"

        if comando == "OP":
            tipo_esquerdo = self.visitar(no[1])
            tipo_direito = self.visitar(no[2])

            relacionais = {
                "==", "!=", ">", "<", ">=", "<="
            }

            if cabeca.valor in relacionais:
                return "inteiro"

            if "float" in (tipo_esquerdo, tipo_direito):
                return "float"

            return "inteiro"

        raise Exception(
            f"erro semântico: comando "
            f"'{cabeca.valor}' não suportado."
        )

# Quarto módulo: gerador de código intermediário

class GeradorMEPA:
    def __init__(self, tabela):
        self.tabela = tabela
        self.instrucoes = []
        self.rotulos = 0

    def emitir(self, instrucao):
        self.instrucoes.append(instrucao)

    def novo_rotulo(self):
        self.rotulos += 1
        return f"R{self.rotulos}"

    def gerar(self, ast):
        self.emitir("INPP")
        self.visitar(ast)
        self.emitir("PARA")
        return self.instrucoes

    def visitar(self, no):
        if isinstance(no, Token):
            if no.tipo in {"INTEGER", "FLOAT"}:
                self.emitir(f"CRCT {no.valor}")
            elif no.tipo == "ID":
                endereco = self.tabela[no.valor].endereco
                self.emitir(f"CRVL {endereco}")
            return

        if not no:
            return

        cabeca = no[0]
        comando = cabeca.tipo

        if comando == "SET":
            self.visitar(no[2])
            endereco = self.tabela[no[1].valor].endereco
            self.emitir(f"ARMZ {endereco}")

        elif comando == "PRINT":
            self.visitar(no[1])
            self.emitir("IMPR")

        elif comando == "BEGIN":
            for item in no[1:]:
                self.visitar(item)

        elif comando == "IF":
            rotulo_else = self.novo_rotulo()
            rotulo_fim = self.novo_rotulo()

            self.visitar(no[1])
            self.emitir(f"DSVF {rotulo_else}")
            self.visitar(no[2])
            self.emitir(f"DSVS {rotulo_fim}")
            self.emitir(f"{rotulo_else}: NADA")
            self.visitar(no[3])
            self.emitir(f"{rotulo_fim}: NADA")

        elif comando == "WHILE":
            rotulo_inicio = self.novo_rotulo()
            rotulo_fim = self.novo_rotulo()

            self.emitir(f"{rotulo_inicio}: NADA")
            self.visitar(no[1])
            self.emitir(f"DSVF {rotulo_fim}")
            self.visitar(no[2])
            self.emitir(f"DSVS {rotulo_inicio}")
            self.emitir(f"{rotulo_fim}: NADA")

        elif comando == "OP":
            self.visitar(no[1])
            self.visitar(no[2])

            operadores = {
                "+": "SOMA",
                "-": "SUBT",
                "*": "MULT",
                "/": "DIVI",
                "%": "MODU",
                "==": "CMIG",
                "!=": "CMDG",
                ">": "CMAG",
                "<": "CMEG",
                ">=": "CMEG",
                "<=": "CMME",
            }
            self.emitir(operadores[cabeca.valor])

# Funções usadas para compilar e mostrar os resultados

def compilar(codigo):
    tokens = tokenizar(codigo)
    parser = ParserMiniLisp(tokens)
    ast = parser.parsear()
    semantico = AnalisadorSemantico()
    tabela = semantico.analisar(ast)
    gerador = GeradorMEPA(tabela)
    mepa = gerador.gerar(ast)
    return tokens, tabela, mepa

def mostrar_tokens(tokens):
    print("\nLista de tokens/lexemas:")
    print(f"{'Num':<5} | {'token':<10} | {'lexema':<12} | linha")
    print("-" * 45)
    for numero, token in enumerate(tokens, 1):
        print(f"{numero:<5} | {token.tipo:<10} | {token.valor:<12} | {token.linha}")

def mostrar_tabela(tabela):
    print("\nTabela de símbolos:")
    if not tabela:
        print("Vazia")
        return
    print(f"{'Identificador':<15} | {'endereço mepa':<13} | {'tipo presumido':<14} | escopo")
    print("-" * 65)
    for simbolo in tabela.values():
        print(f"{simbolo.nome:<15} | {simbolo.endereco:<13} | {simbolo.tipo:<14} | {simbolo.escopo}")

def mostrar_mepa(mepa):
    print("\nCódigo mepa:")
    for instrucao in mepa:
        print(instrucao)

# Funções usadas nos testes da atividade

def teste_negativo(numero, descricao, codigo):
    print("\n" + "=" * 70)
    print(f"Teste negativo {numero} - {descricao}")
    print("=" * 70)
    print("\nEntrada em mini-lisp:")
    print(codigo.strip())
    try:
        compilar(codigo)
        print("\nErro: o programa foi aceito, mas deveria ser inválido.")
    except Exception as erro:
        print(f"\nMensagem de erro: {erro}")

def teste_positivo(numero, descricao, codigo):
    print("\n" + "=" * 70)
    print(f"Teste positivo {numero} - {descricao}")
    print("=" * 70)
    print("\nEntrada correta em mini-lisp:")
    print(codigo.strip())
    try:
        tokens, tabela, mepa = compilar(codigo)
        mostrar_tokens(tokens)
        mostrar_tabela(tabela)
        mostrar_mepa(mepa)
    except Exception as erro:
        print(f"\nErro inesperado: {erro}")

# Leitura opcional de arquivos .lisp

def ler_arquivo(caminho):
    if not caminho.lower().endswith(".lisp"):
        raise Exception("Erro: o arquivo informado deve possuir extensão .lisp.")
    with open(caminho, "r", encoding="utf-8") as arquivo:
        return arquivo.read()

# Exemplos usados para a demonstração

def executar_testes():
    # Programa 1 com erro léxico
    negativo_1 = """(begin
  (set preco 25)
  (print (+ preco @))
)"""

    # Programa 2 com erro sintático
    negativo_2 = """(begin
  (set numero 8)
  (print (* numero 2))
"""

    # Programa 3 com erro semântico
    negativo_3 = """(begin
  (print saldo)
)"""

    # Programa 1 correto com operações e prints
    positivo_1 = """(begin
  (print (+ 18 (* 4 6)))
  (print (- 75 (/ 20 4)))
)"""

    # Programa 2 correto com seleção e repetição
    positivo_2 = """(begin
  (set passo 1)
  (while (<= passo 4)
    (begin
      (if (>= passo 3)
        (print passo)
        (print 0)
      )
      (set passo (+ passo 1))
    )
  )
)"""

    teste_negativo(1, "erro léxico", negativo_1)
    teste_negativo(2, "erro sintático", negativo_2)
    teste_negativo(3, "erro semântico", negativo_3)
    teste_positivo(1, "operações e prints", positivo_1)
    teste_positivo(2, "seleção e repetição", positivo_2)

# Execução principal

if __name__ == "__main__":
    if len(sys.argv) == 2:
        try:
            codigo = ler_arquivo(sys.argv[1])
            teste_positivo(1, f"arquivo {sys.argv[1]}", codigo)
        except Exception as erro:
            print(erro)
    else:
        executar_testes()
        