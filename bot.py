import openai


chave_api = ""

openai.api_key = chave_api


def enviar_msg(mensagem, lista_msg=[]):
    lista_msg.append({"role": "user", "content": mensagem})

    
    resposta = openai.ChatCompletion.create(
        model= "gpt-3.5-turbo",
        messages= lista_msg,
    )  

    return resposta["choices"][0]["message"]

# lista de msg para manter o histórico da conversa com IA
# Dessa forma a IA tem como responder com base nas pergunas passadas
lista_msg = []

while True: # Loop infinito, até o user querer 'sair' da conversa
    texto = input("Escreva sua mensagem aqui ou 'sair' para encerrar:")

    if texto == "sair":
        break
    else:
        resposta = enviar_msg(texto, lista_msg)
        lista_msg.append(resposta)
        print("bot:", resposta["content"])



#print(enviar_msg("Em que ano o Santos ganhou a libertadores?"))
