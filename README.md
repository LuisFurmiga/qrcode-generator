# Gerador de QR Code

Este projeto é um **Gerador de QR Code** com interface gráfica construída em **Tkinter**. Ele permite a geração de QR Codes personalizados com diferentes estilos, cores e a inclusão de uma logo.

## **Recursos**

- Geração de QR Codes para:
  - URLs, textos, telefones, SMS, e-mails, contatos (vCard), localização, WhatsApp e Wi-Fi.
- Personalização de cores do QR Code e fundo.
- Diferentes estilos de QR Code: padrão, arredondado, círculos, barras e quadrados espaçados.
- Opção de incluir uma logo centralizada no QR Code.
- Interface amigável com suporte a rolagem.
- Execução em **thread separada** para não travar a interface durante a geração.

---

## **Instalação**

Certifique-se de ter o **Python 3.8+** instalado. Em seguida, instale as dependências necessárias:

```sh
pip install pillow qrcode[pil]
```

Caso queira instalar tudo automaticamente, execute o script `requirements.py`:

```sh
python requirements.py
```

---

## **Como Executar**

Para rodar o gerador de QR Code, execute:

```sh
python main.py
```

Isso abrirá a interface gráfica do programa.

---

## **Estrutura do Projeto**

```
📁 qrcode-generator/
├── main.py           # Arquivo principal que inicia a interface gráfica
├── view.py           # Interface gráfica construída com Tkinter
├── viewmodel.py      # Lógica intermediária entre a view e o model
├── model.py          # Manipulação do QR Code (cores, estilos, inserção de logo)
├── requirements.py   # Instalação automática de dependências
```

### **Descrição dos Arquivos**

- main.py : Inicia o programa e carrega a interface.
- view.py : Responsável pela interface gráfica do usuário.
- viewmodel.py : Controlador que faz a ponte entre a interface (`view.py`) e o gerador de QR Code (`model.py`).
- model.py : Lógica de geração do QR Code com personalizações.
- requirements.py : Script para instalação automática de dependências.

---

## **Como Usar**

1. **Escolha o tipo de QR Code** no menu suspenso.
2. **Preencha os campos necessários** conforme o tipo selecionado.
3. **Selecione as cores** para o QR Code e o fundo.
4. **Escolha um estilo** de QR Code.
5. **Opcionalmente, inclua uma logo** no QR Code.
6. Clique em **"Gerar QR Code"** para visualizar e salvar a imagem gerada.

---

## **Tecnologias Utilizadas**

- **Python 3.8+**
- **Tkinter** (Interface gráfica)
- **Pillow** (Manipulação de imagens)
- **QRCode[pil]** (Geração dos QR Codes)
- **Threading** (Execução assíncrona para não travar a UI)

---

## **Contribuição**

Sinta-se à vontade para contribuir com melhorias! Faça um **fork** do projeto, crie um **branch** e envie um **pull request**.

---
