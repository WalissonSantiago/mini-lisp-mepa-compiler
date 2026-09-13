# Mini-Lisp MEPA Compiler

Compilador educacional desenvolvido em Python para uma linguagem inspirada em Lisp.  
O projeto implementa as principais etapas de um processo de compilação: análise léxica, análise sintática, análise semântica e geração de código intermediário para MEPA.

A proposta é demonstrar, de forma simples e didática, como um compilador pode transformar um programa escrito em uma pequena linguagem de alto nível em uma representação intermediária executável por uma máquina abstrata.

## Funcionalidades

O compilador possui suporte para:

- números inteiros e de ponto flutuante;
- identificadores e variáveis;
- atribuição de valores com `set`;
- impressão de valores com `print`;
- blocos de instruções com `begin`;
- estruturas condicionais com `if`;
- estruturas de repetição com `while`;
- operações aritméticas;
- operações relacionais;
- construção de tabela de símbolos;
- detecção de erros léxicos, sintáticos e semânticos;
- geração de código intermediário MEPA.

## Estrutura do compilador

O projeto foi dividido em quatro etapas principais.

### 1. Análise léxica

O analisador léxico percorre o código-fonte e transforma os elementos da linguagem em tokens.

Entre os elementos reconhecidos estão:

- parênteses;
- números inteiros;
- números de ponto flutuante;
- identificadores;
- operadores;
- palavras reservadas.

As palavras reservadas atualmente suportadas são:

```text
if
while
begin
set
print
```

Quando um caractere inválido é encontrado, o compilador informa um erro léxico e a linha correspondente.

### 2. Análise sintática

Após a tokenização, o analisador sintático verifica se as expressões seguem a estrutura esperada pela linguagem.

A sintaxe utiliza a notação baseada em listas, característica de linguagens da família Lisp.

Exemplo:

```lisp
(begin
  (set numero 10)
  (print (+ numero 5))
)
```

Durante essa etapa também são verificadas estruturas malformadas, como ausência de parênteses ou quantidade incorreta de argumentos.

### 3. Análise semântica

A análise semântica verifica o significado das expressões após a estrutura sintática ter sido validada.

Entre as verificações realizadas estão:

- uso de variáveis não inicializadas;
- validação do identificador utilizado em `set`;
- inferência simples de tipos;
- construção da tabela de símbolos.

Cada símbolo registrado possui:

- nome;
- endereço MEPA;
- tipo presumido;
- escopo.

Neste projeto, o escopo utilizado é global.

### 4. Geração de código MEPA

Depois que o programa passa pelas etapas anteriores, o compilador gera instruções intermediárias no formato MEPA.

Algumas das instruções utilizadas são:

```text
INPP
PARA
CRCT
CRVL
ARMZ
IMPR
SOMA
SUBT
MULT
DIVI
MODU
DSVF
DSVS
```

Também são gerados rótulos para representar estruturas condicionais e de repetição.

## Operadores suportados

### Aritméticos

```text
+
-
*
/
%
```

### Relacionais

```text
==
!=
>
<
>=
<=
```

## Exemplo de programa

```lisp
(begin
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
)
```

Esse exemplo cria a variável `passo`, executa um laço de repetição e utiliza uma condição para decidir qual valor será impresso.

## Como executar

É necessário ter o Python 3 instalado.

Clone o repositório:

```bash
git clone https://github.com/SEU-USUARIO/mini-lisp-mepa-compiler.git
cd mini-lisp-mepa-compiler
```

Execute o arquivo principal:

```bash
python compiler.py
```

Caso o arquivo principal do seu projeto possua outro nome, substitua `compiler.py` pelo nome correspondente.

Ao executar o programa sem argumentos, são executados os testes de demonstração incluídos no código.

Também é possível compilar um arquivo `.lisp` diretamente:

```bash
python compiler.py examples/arithmetic.lisp
```

O programa aceita somente arquivos com extensão `.lisp`.

## Exemplos

A pasta [`examples`](./examples) contém programas que podem ser utilizados para testar o compilador.

```text
examples/
├── arithmetic.lisp
├── control_flow.lisp
├── variables.lisp
├── invalid_lexical.lisp
├── invalid_syntax.lisp
└── invalid_semantic.lisp
```

Os três primeiros arquivos representam programas válidos. Os arquivos iniciados por `invalid_` foram criados propositalmente com erros e podem ser utilizados para observar as mensagens produzidas em cada etapa de análise.

## Estrutura sugerida do repositório

```text
mini-lisp-mepa-compiler/
├── compiler.py
├── README.md
├── .gitignore
└── examples/
    ├── arithmetic.lisp
    ├── control_flow.lisp
    ├── variables.lisp
    ├── invalid_lexical.lisp
    ├── invalid_syntax.lisp
    └── invalid_semantic.lisp
```

## Exemplo de saída

Para uma entrada válida, o programa apresenta:

1. lista de tokens e lexemas;
2. tabela de símbolos;
3. código intermediário MEPA.

Isso permite acompanhar cada etapa do processo de compilação e facilita a compreensão do funcionamento interno do compilador.

## Objetivo do projeto

Este projeto possui finalidade educacional e foi desenvolvido como uma implementação simplificada dos conceitos fundamentais de compiladores.

O foco não é reproduzir todos os recursos de uma linguagem Lisp completa, mas apresentar de forma prática conceitos como tokenização, construção de estruturas sintáticas, análise de símbolos, validação semântica e geração de código intermediário.

## Tecnologias utilizadas

- Python 3
- Expressões regulares com o módulo `re`
- Biblioteca padrão do Python

Não há dependências externas.

## Licença

Caso deseje disponibilizar o projeto como código aberto, uma licença como a MIT pode ser adicionada ao repositório.

---

Desenvolvido como projeto de estudo sobre construção de compiladores e geração de código intermediário.
