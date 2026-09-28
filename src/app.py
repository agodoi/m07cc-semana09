#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# =====================================================================
#  LABORATORIO DIDATICO - SQL INJECTION + CAPTURA NO WIRESHARK
#  ---------------------------------------------------------------------
#  Servidor HTTP simples (SEM HTTPS, de proposito) com um formulario
#  de login PROPOSITALMENTE VULNERAVEL a SQL Injection.
#
#  Objetivo pedagogico:
#    1) Mostrar no Wireshark que login/senha trafegam em TEXTO PLANO
#       quando NAO se usa HTTPS.
#    2) Demonstrar como uma consulta SQL montada por concatenacao de
#       string pode ser burlada (bypass de autenticacao).
#
#  ATENCAO: use SOMENTE na sua propria maquina / rede de laboratorio.
#  Nao possui dependencias: roda so com o Python padrao.
#
#  Como rodar:   python3 app.py
#  Depois abra:  http://SEU_IP:8000
# =====================================================================

import sqlite3
import html
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs

PORTA = 8000

# ---------------------------------------------------------------------
# 1) BANCO DE DADOS (SQLite em arquivo, recriado a cada inicio)
#    Espelha a tabela "users" do material de aula.
# ---------------------------------------------------------------------
def criar_banco():
    con = sqlite3.connect("banco.db")
    cur = con.cursor()
    cur.execute("DROP TABLE IF EXISTS users")
    cur.execute("""
        CREATE TABLE users (
            id       INTEGER PRIMARY KEY,
            username TEXT,
            password TEXT
        )
    """)
    usuarios = [
        (1, "admin",   "jklfjdaskfjalk"),
        (2, "godoi",   "admin12345"),
        (3, "bill",    "gates"),
        (4, "jeff",    "beazos"),
        (5, "joao",    "cabrobro"),
        (6, "ratinho", "sbt"),
    ]
    cur.executemany("INSERT INTO users VALUES (?, ?, ?)", usuarios)
    con.commit()
    con.close()


# ---------------------------------------------------------------------
# 2) PAGINA DE LOGIN (baseada no HTML do material de aula)
#    O metodo GET foi escolhido de proposito: assim usuario e senha
#    aparecem na propria URL, ficando MUITO faceis de ver no Wireshark.
# ---------------------------------------------------------------------
PAGINA_LOGIN = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Banco Inteli | Internet Banking</title>
  <style>
    :root{
      --navy:#0a2540; --navy2:#0d2f52; --teal:#00a676; --teal-d:#008a63;
      --ink:#1a2733; --muted:#5b6b7a; --line:#e3e8ee; --bg:#eef2f6; --white:#fff;
    }
    *{box-sizing:border-box;margin:0;padding:0}
    body{
      font-family:-apple-system,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;
      color:var(--ink); background:var(--bg); line-height:1.5;
    }
    a{color:inherit;text-decoration:none}

    /* ---------- topo ---------- */
    header{background:var(--navy); color:#fff}
    .nav{max-width:1120px; margin:0 auto; padding:0 24px; height:64px;
         display:flex; align-items:center; gap:32px}
    .brand{display:flex; align-items:center; gap:10px; font-weight:700; font-size:19px; letter-spacing:.2px}
    .brand svg{display:block}
    .menu{display:flex; gap:26px; margin-left:12px; font-size:14.5px}
    .menu span{opacity:.85; cursor:pointer}
    .menu span:hover{opacity:1}
    .nav .right{margin-left:auto; display:flex; align-items:center; gap:8px; font-size:13.5px; opacity:.9}

    /* ---------- corpo ---------- */
    .hero{max-width:1120px; margin:0 auto; padding:56px 24px;
          display:grid; grid-template-columns:1.1fr .9fr; gap:56px; align-items:center}
    .pitch h1{font-size:38px; line-height:1.15; color:var(--navy); font-weight:700; letter-spacing:-.5px}
    .pitch p.sub{margin-top:16px; font-size:17px; color:var(--muted); max-width:46ch}
    .feats{margin-top:32px; display:flex; flex-direction:column; gap:16px}
    .feat{display:flex; align-items:center; gap:12px; font-size:15px; color:var(--ink)}
    .feat .ic{width:38px; height:38px; border-radius:10px; background:#e6f7f1;
              display:flex; align-items:center; justify-content:center; flex:0 0 auto}

    /* ---------- cartao de login ---------- */
    .card{background:var(--white); border:1px solid var(--line); border-radius:14px;
          box-shadow:0 10px 30px rgba(10,37,64,.10); padding:32px; max-width:400px; margin-left:auto; width:100%}
    .card .lock{display:flex; align-items:center; gap:8px; color:var(--teal-d); font-size:13px; font-weight:600; margin-bottom:6px}
    .card h2{font-size:22px; color:var(--navy); margin-bottom:4px}
    .card .hint{font-size:13.5px; color:var(--muted); margin-bottom:22px}
    label{display:block; font-size:13px; color:var(--muted); margin:0 0 6px 2px}
    .field{position:relative; margin-bottom:16px}
    .field input{width:100%; padding:13px 14px; font-size:15px; border:1px solid #cfd8e3;
                 border-radius:9px; outline:none; transition:border-color .15s, box-shadow .15s; background:#fbfcfe}
    .field input:focus{border-color:var(--teal); box-shadow:0 0 0 3px rgba(0,166,118,.15)}
    .btn{width:100%; padding:14px; font-size:15.5px; font-weight:700; color:#fff; cursor:pointer;
         background:var(--teal); border:0; border-radius:9px; transition:background .15s}
    .btn:hover{background:var(--teal-d)}
    .row{display:flex; justify-content:space-between; align-items:center; margin:4px 2px 20px; font-size:13px}
    .row a{color:var(--teal-d); font-weight:600}
    .row label.remember{display:flex; align-items:center; gap:7px; color:var(--muted); margin:0}
    .divider{height:1px; background:var(--line); margin:22px 0 16px}
    .openacc{text-align:center; font-size:14px; color:var(--muted)}
    .openacc a{color:var(--teal-d); font-weight:700}

    /* ---------- rodape ---------- */
    footer{background:var(--navy2); color:#c6d2df; margin-top:40px}
    .foot{max-width:1120px; margin:0 auto; padding:34px 24px; display:flex; flex-wrap:wrap; gap:40px; font-size:13px}
    .foot .col{display:flex; flex-direction:column; gap:9px; min-width:150px}
    .foot .col b{color:#fff; font-size:13.5px; margin-bottom:3px}
    .foot .col span{opacity:.8; cursor:pointer}
    .legal{border-top:1px solid rgba(255,255,255,.12); text-align:center; font-size:12px;
           color:#8ea3b8; padding:16px 24px}
    .labtag{background:#fff7e6; color:#8a6d00; border:1px solid #ffe1a3; font-size:12px;
            text-align:center; padding:7px 12px}

    @media (max-width:860px){
      .hero{grid-template-columns:1fr; gap:36px; padding:36px 20px}
      .menu,.nav .right{display:none}
      .card{margin:0 auto}
    }
  </style>
</head>
<body>

  <!-- faixa discreta de laboratorio (uso educacional) -->
  <div class="labtag">Ambiente de laboratorio.</div>

  <header>
    <div class="nav">
      <a class="brand" href="/">
        <!-- logo em SVG (marca ficticia) -->
        <svg width="30" height="30" viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg">
          <circle cx="20" cy="20" r="20" fill="#00a676"/>
          <path d="M11 27L20 11l9 16H24l-4-7-4 7h-5z" fill="#fff"/>
        </svg>
        Banco Inteli
      </a>
      <nav class="menu">
        <span>Para voce</span><span>Empresas</span><span>Cartoes</span>
        <span>Emprestimos</span><span>Investimentos</span>
      </nav>
      <div class="right">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="2"><circle cx="11" cy="11" r="7"/><path d="M21 21l-4-4"/></svg>
        Buscar &nbsp;|&nbsp; Ajuda
      </div>
    </div>
  </header>

  <main class="hero">
    <section class="pitch">
      <h1>Seu banco digital, simples e seguro.</h1>
      <p class="sub">Acesse sua conta, pague contas, transfira via Pix e acompanhe seus investimentos - tudo em um so lugar.</p>
      <div class="feats">
        <div class="feat">
          <span class="ic">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#00a676" stroke-width="2"><rect x="4" y="10" width="16" height="11" rx="2"/><path d="M8 10V7a4 4 0 0 1 8 0v3"/></svg>
          </span>
          Protecao de dados e criptografia de ponta a ponta
        </div>
        <div class="feat">
          <span class="ic">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#00a676" stroke-width="2"><path d="M12 2l8 4v6c0 5-3.5 8-8 10-4.5-2-8-5-8-10V6l8-4z"/><path d="M9 12l2 2 4-4"/></svg>
          </span>
          Autenticacao em duas etapas para todas as contas
        </div>
        <div class="feat">
          <span class="ic">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#00a676" stroke-width="2"><circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/></svg>
          </span>
          Atendimento 24 horas, todos os dias
        </div>
      </div>
    </section>

    <section>
      <form class="card" action="/login" method="get">
        <div class="lock">
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="#008a63" stroke-width="2"><rect x="4" y="10" width="16" height="11" rx="2"/><path d="M8 10V7a4 4 0 0 1 8 0v3"/></svg>
          Ambiente seguro
        </div>
        <h2>Acesse sua conta</h2>
        <p class="hint">Entre com seus dados para continuar.</p>

        <div class="field">
          <label for="username">Usuario ou CPF</label>
          <input id="username" type="text" name="username" autocomplete="off" placeholder="Digite seu usuario ou CPF">
        </div>
        <div class="field">
          <label for="password">Senha</label>
          <input id="password" type="password" name="password" autocomplete="off" placeholder="Digite sua senha">
        </div>

        <div class="row">
          <label class="remember"><input type="checkbox"> Lembrar de mim</label>
          <a href="/">Esqueci minha senha</a>
        </div>

        <button class="btn" type="submit" name="enviar" value="Entrar">Entrar</button>

        <div class="divider"></div>
        <p class="openacc">Ainda nao e cliente? <a href="/">Abra sua conta</a></p>
      </form>
    </section>
  </main>

  <footer>
    <div class="foot">
      <div class="col"><b>Banco Inteli</b><span>Sobre nos</span><span>Trabalhe conosco</span><span>Sustentabilidade</span></div>
      <div class="col"><b>Produtos</b><span>Conta corrente</span><span>Cartao de credito</span><span>Investimentos</span></div>
      <div class="col"><b>Ajuda</b><span>Central de atendimento</span><span>Seguranca</span><span>Ouvidoria</span></div>
      <div class="col"><b>Seguranca</b><span>Nunca pedimos sua senha por telefone</span><span>Denuncie fraudes</span></div>
    </div>
    <div class="legal">
      (c) Banco Inteli - CNPJ 00.000.000/0001-00 (ficticio). Simulacao criada para aula de seguranca da informacao.
    </div>
  </footer>

</body>
</html>
"""


def pagina_resultado(sucesso, sql, usuario_logado=None):
    """Monta a pagina que mostra o resultado + a consulta SQL executada."""
    if sucesso:
        cor = "#00a676"
        icone = ('<svg width="56" height="56" viewBox="0 0 24 24" fill="none" '
                 'stroke="#00a676" stroke-width="2"><circle cx="12" cy="12" r="10"/>'
                 '<path d="M8 12l3 3 5-6"/></svg>')
        titulo = "Acesso liberado"
        sub = f"Bem-vindo(a) ao Banco Inteli, <b>{html.escape(str(usuario_logado))}</b>."
    else:
        cor = "#d64545"
        icone = ('<svg width="56" height="56" viewBox="0 0 24 24" fill="none" '
                 'stroke="#d64545" stroke-width="2"><circle cx="12" cy="12" r="10"/>'
                 '<path d="M15 9l-6 6M9 9l6 6"/></svg>')
        titulo = "Acesso negado"
        sub = "Usuario ou senha invalidos."
    return f"""
<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Banco Inteli | {titulo}</title>
  <style>
    *{{box-sizing:border-box;margin:0;padding:0}}
    body{{font-family:-apple-system,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;
      background:#eef2f6; color:#1a2733; min-height:100vh;
      display:flex; flex-direction:column; align-items:center; justify-content:center; padding:24px}}
    .box{{background:#fff; border:1px solid #e3e8ee; border-radius:14px;
      box-shadow:0 10px 30px rgba(10,37,64,.10); padding:40px; max-width:560px; width:100%; text-align:center}}
    .box h1{{font-size:24px; color:{cor}; margin:14px 0 6px}}
    .box p.sub{{color:#5b6b7a; font-size:15px}}
    .sqlbox{{margin-top:26px; text-align:left; background:#0a2540; border-radius:10px; padding:16px 18px}}
    .sqlbox .lbl{{color:#8fb0cf; font-size:12px; margin-bottom:8px}}
    .sqlbox code{{color:#ffd479; font-size:13.5px; word-break:break-all; font-family:Consolas,Monaco,monospace}}
    .back{{display:inline-block; margin-top:24px; background:#00a676; color:#fff; font-weight:700;
      padding:12px 26px; border-radius:9px; font-size:14.5px}}
    .back:hover{{background:#008a63}}
  </style>
</head>
<body>
  <div class="box">
    {icone}
    <h1>{titulo}</h1>
    <p class="sub">{sub}</p>
    <div class="sqlbox">
      <div class="lbl">Consulta SQL que o servidor realmente executou:</div>
      <code>{html.escape(sql)}</code>
    </div>
    <a class="back" href="/">Voltar ao login</a>
  </div>
</body>
</html>
"""


# ---------------------------------------------------------------------
# 3) LOGICA DE LOGIN *VULNERAVEL*  (o coracao da demonstracao)
#    A consulta e montada por CONCATENACAO de string, exatamente o
#    erro que o material ensina a evitar.
# ---------------------------------------------------------------------
def login_vulneravel(usuario, senha):
    con = sqlite3.connect("banco.db")
    cur = con.cursor()

    # >>> AQUI ESTA A FALHA (concatenacao direta da entrada do usuario) <<<
    sql = "SELECT id, username FROM users WHERE username='" + usuario + \
          "' AND password='" + senha + "'"

    try:
        cur.execute(sql)          # execute() nao permite ; multiplo -> nao apaga o banco
        linha = cur.fetchone()
    except sqlite3.Error as e:
        con.close()
        return (False, sql + "   -- ERRO SQL: " + str(e), None)

    con.close()
    if linha:
        return (True, sql, linha[1])   # linha[1] = username retornado
    return (False, sql, None)


# ---------------------------------------------------------------------
# 4) VERSAO SEGURA (para o professor mostrar o "depois")
#    Descomente a chamada no handler para comparar em aula.
# ---------------------------------------------------------------------
def login_seguro(usuario, senha):
    con = sqlite3.connect("banco.db")
    cur = con.cursor()
    sql = "SELECT id, username FROM users WHERE username=? AND password=?"
    cur.execute(sql, (usuario, senha))   # prepared statement: entrada vira DADO, nao codigo
    linha = cur.fetchone()
    con.close()
    if linha:
        return (True, sql + f"   -- parametros: ({usuario!r}, {senha!r})", linha[1])
    return (False, sql + f"   -- parametros: ({usuario!r}, {senha!r})", None)


# ---------------------------------------------------------------------
# 5) SERVIDOR HTTP
# ---------------------------------------------------------------------
class Handler(BaseHTTPRequestHandler):
    def _responder(self, corpo_html):
        dados = corpo_html.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(dados)))
        self.end_headers()
        self.wfile.write(dados)

    def do_GET(self):
        rota = urlparse(self.path)

        if rota.path == "/":
            self._responder(PAGINA_LOGIN)
            return

        if rota.path == "/login":
            params = parse_qs(rota.query)
            usuario = params.get("username", [""])[0]
            senha   = params.get("password", [""])[0]

            # >>> Troque aqui entre a versao VULNERAVEL e a SEGURA <<<
            sucesso, sql, quem = login_vulneravel(usuario, senha)
            # sucesso, sql, quem = login_seguro(usuario, senha)

            self._responder(pagina_resultado(sucesso, sql, quem))
            return

        # qualquer outra rota
        self._responder(PAGINA_LOGIN)

    # deixa o log do servidor mais limpo no terminal
    def log_message(self, formato, *args):
        print("  [req]", self.address_string(), self.requestline)


def main():
    criar_banco()
    servidor = ThreadingHTTPServer(("0.0.0.0", PORTA), Handler)
    print("=" * 60)
    print(" LABORATORIO SQL INJECTION no ar (SEM HTTPS, de proposito)")
    print(" Acesse na propria maquina:  http://localhost:%d" % PORTA)
    print(" Acesse pela rede local:     http://SEU_IP:%d" % PORTA)
    print(" (descubra o IP com:  ip a   |  ipconfig  |  ifconfig)")
    print(" Encerre com Ctrl+C")
    print("=" * 60)
    try:
        servidor.serve_forever()
    except KeyboardInterrupt:
        print("\nEncerrado.")


if __name__ == "__main__":
    main()
