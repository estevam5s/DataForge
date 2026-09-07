> ⚠️ **DOCUMENTO HISTÓRICO — não reflete a implementação atual.**
>
> Guia de instalação antigo, com exemplos que não compilam. O atual é `doc/INSTALACAO.md`.
>
> **Documentação vigente:** [`doc/TUTORIAL.md`](TUTORIAL.md) · [`doc/REFERENCIA.md`](REFERENCIA.md) · [`doc/BIBLIOTECA_PADRAO.md`](BIBLIOTECA_PADRAO.md) · [`doc/INSTALACAO.md`](INSTALACAO.md)

---

# 🇧🇷 DataForge - Guia de Instalação em Português

Este guia fornece instruções completas para instalar e configurar o DataForge no Windows usando os comandos que **funcionaram com sucesso**.

## ✅ Instalação que Funcionou

### Passo 1: Clonar e Instalar
```bash
# Clonar o repositório
git clone https://github.com/estevam5s/DataForge.git
cd DataForge

# Instalar para o usuário atual (sem permissões de administrador)
pip install --user -e .
```

### Passo 2: Configurar PATH (OBRIGATÓRIO)
```bash
# Adicionar ao PATH da sessão atual
export PATH="$PATH:/c/Users/Restaurante/AppData/Roaming/Python/Python311/Scripts"

# Tornar permanente - adicionar ao ~/.bashrc
echo 'export PATH="$PATH:/c/Users/Restaurante/AppData/Roaming/Python/Python311/Scripts"' >> ~/.bashrc
```

### Passo 3: Verificar Instalação
```bash
# Verificar se funciona (comando global)
dataforge version

# Alternativa que sempre funciona (sem configurar PATH)
python -m dataforge version
```

## 🎯 Comandos Essenciais

### Executar Programas DataForge
```bash
# Executar arquivo .df
dataforge run examples/01_hello.df

# Ou usando módulo Python
python -m dataforge run examples/01_hello.df
```

### REPL Interativo
```bash
# Iniciar modo interativo
dataforge repl

# Ou usando módulo Python
python -m dataforge repl
```

### Ajuda e Informações
```bash
# Ver comandos disponíveis
dataforge --help

# Ver versão
dataforge version

# Verificar sintaxe sem executar
dataforge check meu_programa.df

# Ver tokens e AST (para desenvolvedores)
dataforge tokens meu_programa.df
dataforge ast meu_programa.df
```

## 📝 Exemplo Prático

### Criar seu primeiro programa
```bash
# Criar arquivo hello.df
echo 'out "Olá, DataForge!"
out "Bem-vindo ao futuro da programação!"' > hello.df

# Executar
dataforge run hello.df
```

### Testar REPL
```bash
# Iniciar REPL
dataforge repl

# No REPL, digite:
out "Teste do REPL!"
nome := "João"
out "Olá, " + nome
```

## 🔧 Solução de Problemas

### Problema: `dataforge: command not found`
**Solução**: Configurar PATH ou usar módulo Python
```bash
# Opção 1: Configurar PATH (recomendado)
export PATH="$PATH:/c/Users/Restaurante/AppData/Roaming/Python/Python311/Scripts"

# Opção 2: Sempre usar módulo Python
python -m dataforge version
python -m dataforge run arquivo.df
```

### Problema: Erro de permissão
**Solução**: Usar instalação de usuário
```bash
# SEMPRE usar --user (não precisa de admin)
pip install --user -e .
```

### Problema: Módulo não encontrado
**Solução**: Reinstalar com dependências
```bash
# Reinstalar completamente
pip uninstall dataforge-lang
pip install --user -e .
```

## 🚀 Configuração Avançada

### Tornar PATH Permanente no Windows

#### Git Bash (Recomendado)
```bash
# Adicionar ao .bashrc (já fizemos isso)
echo 'export PATH="$PATH:/c/Users/Restaurante/AppData/Roaming/Python/Python311/Scripts"' >> ~/.bashrc

# Recarregar configuração
source ~/.bashrc
```

#### PowerShell
```powershell
# Abrir PowerShell como usuário normal
$UserPath = [Environment]::GetEnvironmentVariable("PATH", "User")
$NewPath = "$UserPath;$env:APPDATA\Python\Python311\Scripts"
[Environment]::SetEnvironmentVariable("PATH", $NewPath, "User")

# Reiniciar terminal
```

#### Variáveis de Ambiente (Interface Gráfica)
1. Pressione `Win + R` → digite `sysdm.cpl`
2. Aba "Avançado" → "Variáveis de Ambiente"
3. Em "Variáveis do usuário", selecione "PATH" → "Editar"
4. Adicionar: `C:\Users\Restaurante\AppData\Roaming\Python\Python311\Scripts`

## 📚 Exemplos de Uso

### Calculadora Simples
```dataforge
// calculadora.df
out "=== Calculadora DataForge ==="

a := float(in "Primeiro número: ")
b := float(in "Segundo número: ")
operacao := in "Operação (+, -, *, /): "

match operacao:
    point "+":
        out "Resultado: " + (a + b)
    point "-":
        out "Resultado: " + (a - b)
    point "*":
        out "Resultado: " + (a * b)
    point "/":
        given b is 0:
            out "Erro: Divisão por zero!"
        otherwise:
            out "Resultado: " + (a / b)
    default:
        out "Operação inválida!"
```

### Executar:
```bash
dataforge run calculadora.df
```

### Sistema de Notas
```dataforge
// notas.df
out "=== Sistema de Notas ==="

nome := in "Nome do aluno: "
nota1 := float(in "Primeira nota: ")
nota2 := float(in "Segunda nota: ")
nota3 := float(in "Terceira nota: ")

media := (nota1 + nota2 + nota3) / 3

out "Aluno: " + nome
out "Média: " + media

given media bigger_equal 7.0:
    out "Status: APROVADO! 🎉"
orif media bigger_equal 5.0:
    out "Status: RECUPERAÇÃO 📚"
otherwise:
    out "Status: REPROVADO 😞"
```

## 🔄 Atualização

### Atualizar DataForge
```bash
# Ir para o diretório
cd DataForge

# Baixar atualizações
git pull origin main

# Reinstalar se necessário
pip install --user -e .

# Verificar nova versão
dataforge version
```

## 📖 Próximos Passos

1. **Explore os Exemplos**: `cd examples/` e execute os arquivos `.df`
2. **Leia a Documentação**: [README.md](README.md) completo
3. **Pratique no REPL**: `dataforge repl` para experimentar
4. **Crie Projetos**: Comece com programas simples

## 📞 Suporte em Português

Se encontrar problemas:

1. **Verifique Issues**: [GitHub Issues](https://github.com/estevam5s/DataForge/issues)
2. **Documentação**: [README.md](README.md) em inglês (mais completo)
3. **Comunidade**: [Discussions](https://github.com/estevam5s/DataForge/discussions)

### Ao Reportar Problemas, inclua:
- Sistema operacional (Windows 11, etc.)
- Versão do Python (`python --version`)
- Comando exato que causou erro
- Mensagem de erro completa

---

**Sucesso com DataForge! Agora você pode programar na linguagem do futuro! 🚀🇧🇷**