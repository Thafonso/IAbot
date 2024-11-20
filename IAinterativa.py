from flet import *
from sqlalchemy import create_engine, Column as SQLColumn, Integer, String
from sqlalchemy.orm import sessionmaker, declarative_base
import bcrypt
import openai
from sqlalchemy.exc import NoResultFound 

base = declarative_base()

class User(base):
    __tablename__ = 'users'

    id = SQLColumn("Id", Integer, primary_key=True, autoincrement=True)
    nome = SQLColumn("Nome", String, nullable=False)
    email = SQLColumn("Email", String, nullable=False)
    senha = SQLColumn("Senha", String, nullable=False)

class App(UserControl):
    def __init__(self): # __init__ = inicializa a classe
        self.engine = create_engine('sqlite:///meubanco.db') # Cria ou faz conexão com DB
        base.metadata.create_all(self.engine) # Cria as tabelas 
        self.Session = sessionmaker(bind=self.engine) # Cria uma sessão
        

    def sv_user(self, nome, email, senha):
        salt = bcrypt.gensalt() # gera um "salt" -> um valor aleatório adicionado a uma senha antes de realizar o Hashing
        hashed_senha = bcrypt.hashpw(senha.encode('utf-8'), salt) # encode.(UTF-8) -> Codifica uma str para bytes


        session = self.Session()
        nw_user = User(nome=nome, email=email, senha=hashed_senha) # Armazena o Hash da senha
        session.add(nw_user)
        session.commit()
        session.close() 
        print(f"User salvo: {nome}, email: {email}, Senha: {senha}")

    def close_db(self):
        print("DB Fechado")

# Consulta ao DB
def verificacao_user(email, senha):
    session = App().Session()
    try:
        # query por email - busca 
        user = session.query(User).filter_by(email=email).one()
        
        # Comparação de senha - usando bcrypt
        if bcrypt.checkpw(senha.encode('utf-8'), user.senha):
            return True, user.nome  # Usuário existente
        else:
            return False, "Senha incorreta"
        
    except NoResultFound: # Excessão específica do SQLalchemy, gerada quando uma "query" não retorna nenhum resultado
        return False, "Usuário não encontrado"  # Usuário não existe
    finally:
        session.close()

# Chave de API OpenAI
openai.api_key = ""
# Faz a IA responder 
def chat_resposta(messages):
    try:
        resposta = openai.ChatCompletion.create(
            model= "gpt-3.5-turbo",
            messages= messages,
        )
        return resposta["choices"][0]["message"]["content"]
    except Exception as e :
        return f"Erro ao responder: {str(e)}"


def main(page: Page):

    meu_bot = App()  
    page.on_close  = meu_bot.close_db


    page.theme_mode = ThemeMode.DARK

      # declarar função antes de usar
      # Mudança de tema claro para escuro 
    def mudar_tema(e):
        if page.theme_mode == ThemeMode.DARK:
            page.theme_mode = ThemeMode.LIGHT
        else:
            page.theme_mode = ThemeMode.DARK
        page.update()

    # Barra de serviço 
    page.appbar = AppBar(
        leading=IconButton(icons.ROCKET, on_click= lambda e: (page.clean(), show_screen1())),
        bgcolor= "#003377",
        title=Text("ChatBot", color= "FFFFFF"),
        center_title= True,
        actions= [
            IconButton(icons.WB_SUNNY_OUTLINED, on_click=mudar_tema),
            PopupMenuButton(
                items=[ # Usar Lambda - Definir função antes de usa-lá
                    PopupMenuItem(text="Login", on_click= lambda e: (page.clean(), show_screenL())), 
                    PopupMenuItem(),
                    PopupMenuItem(text="ChatBot", on_click=lambda e: (page.clean(), show_screen3())),
                    PopupMenuItem(),
                    PopupMenuItem(text="Sair", on_click=lambda e: (page.clean(), show_screen1())),
                ]
            )
        ]
    )

    # Página inicial
    def show_screen1():
        page.clean()
        page.add( 
            Column(
                controls=[
                    Text(f"Olá, Sou seu Assistente ChatBOT!"),
                    ElevatedButton("Login", on_click= lambda e: (page.clean(), show_screenL()), width=150, height=50),
                    ElevatedButton("Cadastrar", on_click= lambda e: (page.clean(), show_screen2()), width=150, height=50),
                    ],
                alignment=MainAxisAlignment.CENTER,
                horizontal_alignment=CrossAxisAlignment.CENTER,
                width=400,
                height=300,
                )
        )

    # Cadastro    
    def show_screen2():
        def cadastro(e):
            if not entrada_nome.value:
                entrada_nome.error_text = "Por favor, Digite seu nome!"
                page.update()
            if not entrada_email.value:
                entrada_email.error_text = "Por favor, Digite seu email!"
                page.update()
            if not entrada_senha.value:
                entrada_senha.error_text= "Por favor, Digite sua Senha!"
                page.update()
            else: 
                nome = entrada_nome.value
                email = entrada_email.value
                senha = entrada_senha.value

                meu_bot.sv_user(nome, email, senha)
                print(f"Nome: {nome} \n Email: {email} \n Senha: {senha}")
                page.clean() # Limpar a Página
                page.add(Text(f"Boa noite {nome}\n Seja Bem vindo!"))
                show_screen3()


            
        entrada_nome = TextField(label="Seu nome")
        entrada_email = TextField(label="Seu email")
        entrada_senha = TextField(label="Sua Senha", password=True) # Password=True -> indica que é uma senha e oculta a escrita
        page.add(
            Column(
                controls=[
                    entrada_nome,
                    entrada_email,
                    entrada_senha,
                    ElevatedButton("entrar", on_click=cadastro),
                ],
                alignment=MainAxisAlignment.CENTER,
                horizontal_alignment=CrossAxisAlignment.CENTER,
                width=400,
                height=300,
                ),
        )
        
    # Fazer Login
    def show_screenL():
            def login(e):
                if not entrada_email.value:
                    entrada_email.error_text = "Por favor, Digite seu email!"
                    page.update()
                if not entrada_senha.value:
                    entrada_senha.error_text= "Por favor, Digite sua Senha!"
                    page.update()
                else: 
                    email = entrada_email.value
                    senha = entrada_senha.value

                    existente, resultado = verificacao_user(email, senha)

                    if existente:
                        page.clean()
                        page.add(Text(f"Seja Bem-vindo, {resultado}!"))
                        show_screen3()
                    else:
                        page.clean()
                        page.add(Text(f"Usuário não existente: {resultado}"))
    
            entrada_email = TextField(label="Seu email")
            entrada_senha = TextField(label="Sua Senha", password=True)
            page.add(
                    entrada_email,
                    entrada_senha,
                    ElevatedButton("entrar", on_click=login)
                )    

    # Interação com a IA
    def show_screen3():
        page.title = "Chat"
        page.vertical_alignment = MainAxisAlignment.START

        # Caixa de menssagens
        msg_input = TextField(hint_text="Envie sua Mensagem...", autofocus=True)
        msg_list = Column(controls=[], scroll=ScrollMode)

        
        def enviar_msg(e):
            user_msg = msg_input.value
            if user_msg:
                # Mensagem do User
                msg_list.controls.append(Text(f"Você: {user_msg}", size=20, color='green'))

                # lista de msg para manter o histórico da conversa com IA
                # Dessa forma a IA tem como responder com base nas pergunas passadas
                lista_msg = [{"role": "user", "content": user_msg}]
                ia_resposta = chat_resposta(lista_msg)

                msg_list.controls.append(Text(f"Bot: {ia_resposta}", size=20, color='green'))

                msg_input.value = ""
                page.update()

        enviar_button = IconButton(icons.SEND, on_click=enviar_msg)
        
        page.clean()
        page.add(
            Column(
                controls=[ # Mensagens com rolagem automatizada
                    Container( # Faz com que a colum ocupe todo o espaço que está disponível
                        content=msg_list,
                        expand=True,
                        alignment=alignment.top_left,
                    ),

                    # Input com botão                    
                    Row(
                        controls= [msg_input, enviar_button],
                        alignment=MainAxisAlignment.START,
                        spacing=10,
                    ),
                ],
                expand=True
            ),
        )

    show_screen1() # faz com que inicie com a tela de inicialização do App



    


app(target=main)
