# Segurança no Desenvolvimento de Aplicações: SQL Injection

Neste encontro iremos abordar a proteção de dados na nuvem no contexto de desenvolvimento de aplicações seguras e proteção contra ataques de SQL Injection.

---
## Horário de Atendimento

### Presencialmente, todas as terças e quintas, das 8h30 às 18h. 

### No slack, ao longo da semana assim que possível.

---
## 1) Vantagens para o seu Projeto

Entender os riscos de SQL Injection em projetos que envolvem banco de dados SQL reduz vulnerabilidades, já que o SQL Injection é o ataque mais famoso que visa explorar falhas de segurança em aplicações que interagem com bancos de dados, permitindo que invasores insiram ou manipulem consultas SQL maliciosas.

O SQL Injection está na mesma calçada da fama de DDoS. Aqui na [Wikipedia](https://en.wikipedia.org/wiki/SQL_injection#Examples) você encontra um histórico dos principais ataques.

<img src="https://github.com/agodoi/sqlinjection/blob/main/imgs/sql_injection-01.jpg" width="700">


Dependendo da forma que você interage com as aplicações de RDS do seu projeto, o invasor pode apagar seu banco em alguns segundos.

### 1.1) Proteção de Dados Sensíveis
   - A maioria das aplicações lida com a sincronização de dados entre back-end e front-end. Proteger o banco de dados contra SQL Injection garante que informações críticas do sistema sejam mantidas seguras, impedindo o vazamento de dados internos que poderiam prejudicar a operação.

---
### 1.2) Maior Confiabilidade do Sistema
   - Ao implementar mecanismos que evitam SQL Injection, como **prepared statements** ou **ORM (Object-Relational Mapping)**, a confiabilidade do sistema aumenta, pois ele não será vulnerável a manipulações externas. Isso é crucial para garantir que a aplicação continue funcionando corretamente, sem interferências de usuários maliciosos.

---
### 1.3) Conformidade com Normas de Segurança
   - Empresas que lidam com dados de usuários estão frequentemente sujeitas a regulamentações de privacidade e segurança de dados (como LGPD). A prevenção de ataques de SQL Injection é uma prática de segurança recomendada que ajuda a empresa a se manter em conformidade com essas normas, evitando multas e danos à reputação.

---
### 1.4) Redução de Custos com Incidentes de Segurança
   - Investir na prevenção de ataques como o SQL Injection pode evitar incidentes de segurança caros, tanto em termos de reparo de sistemas quanto em possíveis responsabilidades legais. Isso é especialmente importante para sistemas que operam em múltiplas localidades e lidam com grandes volumes de transações.

---
### 1.5) Melhoria na Experiência do Usuário Final
   - Um sistema que sofre menos com falhas de segurança e funciona de forma eficiente oferece uma melhor experiência para o usuário final. Em qualquer plataforma que atenda clientes finais, evitar SQL Injection garante que os usuários possam confiar no sistema e na integridade dos dados exibidos.

---
### 1.6) Preparação para Escalabilidade
   - Aplicações que precisam suportar grandes volumes de transações se beneficiam de medidas de segurança contra SQL Injection, que permitem que a plataforma escale de forma segura, sem se tornar mais vulnerável à medida que o volume de usuários e transações cresce.

---
## 2) Como funciona o ataque?


### 2.1) Um atacante insere código SQL malicioso em um campo de entrada de um site ou aplicação, isto é, ele usa a sua API, a sua aplicação para chegar no seu RDS.

---
### 2.2) Esse código é então executado pelo banco de dados, podendo alterar sua operação original.

---
### 2.3) Exemplos de ações possíveis

* Recuperação de dados sensíveis;

* Deleção de tabelas;

* Elevação de privilégios no sistema;

* Download completo da sua base.

#### Imagine os preços de um produto sendo alterados para baixo, criando uma corrida frenética no site. Ou, um roubo de cartões de crédito + CVC.

---
### 2.4) Exemplo de código vulnerável

Imagine uma aplicação de login em um banco de dados, como a da imagem abaixo. O formulário e o servidor completos deste exemplo (propositalmente vulneráveis) estão no arquivo [`app.py`](./src/app.py), dentro da subpasta `src` do repositório, você vai baixá-lo e executá-lo na prática guiada do item **2.8**.

<img src="https://github.com/agodoi/m07cc-semana09/blob/main/imgs/preview_login.png" width="800">

Se for digitada a entrada:

* Username: godoi
  
* Password: admin12345

A consulta SQL montada será: ```SELECT id FROM users WHERE username='godoi' AND password='admin12345'```

Com esta consulta o banco de dados SQL vai procurar por uma linha no banco de dados cuja coluna **username** seja **godoi** e cuja coluna **password** seja **admin12345**. Se encontrar, retorna o valor da coluna id para essa linha.

|id|username|password|
|-|-|-|
|1|admin|jklfjdaskfjalk|
|2|godoi|admin12345|
|3|bill|gates|
|4|jeff|beazos|
|5|joao|cabrobro|
|6|ratinho|sbt|

#### Explicação:

```
sql = "SELECT id FROM users WHERE username='" + user + "' AND password='" + pass + "'";
```

- O código está montando uma string SQL de forma dinâmica, concatenando os valores das variáveis ```user``` e ```pass``` diretamente na consulta SQL.
  
- A consulta tenta selecionar o ```id``` de um usuário a partir de uma tabela ```users```, onde o campo ```username``` deve corresponder ao valor da variável ```user```, e o campo ```password``` deve corresponder ao valor da variável ```pass```.

- A expressão ```user + "' AND password='" + pass + "'"``` insere diretamente os valores de ```user``` e ```pass``` na string SQL. Isso é uma forma arriscada de construir consultas SQL, pois o conteúdo de ```user``` e ```pass``` não está sendo verificado ou tratado de forma segura.

---
### 2.5) Exemplo 1 de código malicioso

Imagine que foi digitado o seguinte:

|Variável|Dado|
|-|-|
|Username:| ```godoi```|
|Password:| ```XxxXxxX' OR 1=1```|
| |Falso OR True = True|

#### Lembrando: na Álgebra de Boole, Falso + True = True



<img src="https://github.com/agodoi/m07cc-semana09/blob/main/imgs/preview_login2.png" width="800">


#### Explicação

* Neste caso, o SQL injection foi usado para contornar a autenticação do usuário.

* O atacante só precisa conhecer o username ```godoi```. Por isso, deve-se evitar o ```admin```

* A consulta SQL montada tem erro de sintaxe (' a mais no final):

```
SELECT id FROM users WHERE username= 'godoi' AND password='XxxXxxX' OR 1=1'
```

* Esse payload **sozinho quebra a consulta** (por causa da aspa a mais no final). Para o ataque **funcionar de fato**, fecha-se a aspa — ```' OR '1'='1``` — ou comenta-se o resto da linha com ```--```, como no item 2.6. Você vai testar as duas formas na prática do item 2.8.

* Inserção de comentário: algumas sequências de caracteres são delimitadores de início de comentários:

   - MySQL, MS-SQL, Oracle, PostgreSQL, SQLite:
      * ' OR '1'='1' --
      * ' OR '1'='1' /*
   - MySQL:
      * ' OR '1'='1' #

   - Access (using null characters):
     * ' OR '1'='1' %00
     * ' OR '1'='1' %16

   - Uso de caracteres especiais: o problema não é o caractere em si, mas montar a consulta por **concatenação** sem tratamento. Uma aplicação que concatena a entrada diretamente tende a ser vulnerável a caracteres como os abaixo, já uma aplicação com **consulta parametrizada** os aceita sem risco:

      * **'** aspas simples
      * **"** aspas dupla
      * **;** ponto e vírgula


* A condição ```OR 1=1``` sempre será verdadeira, o que pode levar à execução de uma consulta que ignora o nome de usuário e senha corretos, permitindo ao invasor obter acesso sem fornecer uma senha válida.

---
### 2.6) Exemplo 2 de código malicioso

Imagine que foi digitado o seguinte:

|Variável|Dado|
|-|-|
|Username:| ```' OR 1=1 --```|
|Password:| ``` ```|
| |Falso OR True = True|

#### Lembrando: na Álgebra de Boole, Falso + True = True


<img src="https://github.com/agodoi/m07cc-semana09/blob/main/imgs/preview_login3.png" width="800">

#### Explicação

```
SELECT id FROM users WHERE username= ' ' OR 1=1 --' AND password=' '
```

* Nesse caso, nem mesmo username válido é preciso.

* O atacante nem sempre sabe qual servidor SQL está em execução. Assim, a condição **Sempre TRUE** pode variar e é detectada por tentativa e erro:
   - '1'='1' 
   - 1=1
   - true


* Em SQL, pode-se encadear vários comandos em um separando-os por **;**
   - ```1=1; drop table users```
   - Múltiplas seleções podem ser formadas para um único resultado com o comando UNION

---
### 2.7) Ataques em HTTP/GET

Ao se usar HTTP/GET, as variáveis do formulário ficam expostas na barra de navegação e oferecem um ponto de partida para manipulação. Por exemplo:
```http://testphp.vulnweb.com/artists.php?artist=1```

O formulário tem um método **get** que expõe a variável ```artist=1```. Veja a foto e o site [http://testphp.vulnweb.com/artists.php?artist=2](http://testphp.vulnweb.com/artists.php?artist=2)

> **Atenção:** o `testphp.vulnweb.com` é um site externo, mantido pela Acunetix para treino. Ele costuma estar no ar, mas pode ficar indisponível sem aviso, ao contrário do seu laboratório local (item 2.8), que você controla. O próprio `app.py` também aceita ataques via **GET** direto na barra de endereço, servindo de alternativa caso o site externo esteja fora.



<img src="https://github.com/agodoi/sqlinjection/blob/main/imgs/tela_banco_04.png" width="800">


---
### 2.8) Prática guiada: monte o laboratório e capture as senhas no Wireshark

Agora que você já viu a teoria, vamos fazer o ataque de verdade. Nesta prática você vai subir um site de banco **fictício** e propositalmente vulnerável, ver a senha trafegando em **texto puro** no Wireshark e **burlar o login** com os ataques dos itens 2.5 e 2.6.

> ⚠️ Ambiente 100% local, inseguro de propósito. Use **somente** na sua própria máquina ou na rede de laboratório da aula.

O servidor é um único arquivo `app.py`, escrito em **Python puro (sem instalar nenhuma biblioteca)**, com o banco **SQLite já embutido**, a mesma tabela `users` do item 2.4.

**O que você precisa**

- **Python 3** instalado. Teste no terminal: `py --version` (Windows) ou `python3 --version` (Linux/Mac).
- **Wireshark** instalado: [wireshark.org](https://www.wireshark.org/).
- Estar na **mesma rede Wi-Fi** do professor (deixa a captura mais fácil de ver).

**Passo 1: Baixar o programa**

Baixe o arquivo `app.py` da pasta `src` do repositório e salve numa pasta na sua máquina.

**Passo 2: Subir o servidor**

Abra o terminal na pasta onde está o `app.py` e rode:

```
py app.py
```

(No Linux/Mac use `python3 app.py`. Se no Windows aparecer a mensagem *"Python was not found"* abrindo a Microsoft Store, instale o Python em [python.org](https://www.python.org/downloads/) marcando a caixa **"Add python.exe to PATH"**, ou use o comando `py`.)

Deve aparecer no terminal:

```
LABORATORIO SQL INJECTION no ar (SEM HTTPS, de proposito)
Acesse na propria maquina:  http://localhost:8000
Acesse pela rede local:     http://SEU_IP:8000
```

**Passo 3: Descobrir o IP da máquina do servidor**

É o endereço que os alunos vão digitar no navegador:
- **Windows:** `ipconfig` → procure "Endereço IPv4" (ex.: `192.168.0.15`).
- **Linux:** `ip a` → procure o `inet` da placa Wi-Fi.
- **Mac:** `ifconfig` ou Preferências → Rede.

**Passo 4: Abrir a página**

No navegador, acesse `http://SEU_IP:8000` (ou `http://localhost:8000` na própria máquina). Aparece a tela de login do **Banco Aurora** (banco fictício).

**Passo 5: Preparar o Wireshark**

Abra o Wireshark, dê **duplo clique na interface Wi-Fi** (a captura começa) e, no filtro do topo, digite e tecle Enter:

```
http.request
```

Isso mostra apenas as requisições HTTP, para não se perder no meio de milhares de pacotes.

**Passo 6: Login normal (para ver a senha em texto puro)**

- Usuário: `godoi`
- Senha: `admin12345`
- Clique em **Entrar** → **ACESSO LIBERADO**.

A página mostra **a consulta SQL que o servidor realmente executou**. No Wireshark, surgirá uma linha como:

```
GET /login?username=godoi&password=admin12345&enviar=Entrar HTTP/1.1
```

👉 Repare: **a senha aparece limpa**, sem nenhuma proteção. É o efeito de usar **HTTP (sem "S")**. Clicando com o botão direito → **Follow → HTTP Stream**, você vê toda a conversa em texto. Com **HTTPS/TLS**, esse mesmo tráfego apareceria criptografado e ilegível.

**Passo 7: O ataque de SQL Injection (itens 2.5 e 2.6)**

- **Ataque A (item 2.5):** Usuário `godoi` / Senha `XxxXxxX' OR '1'='1` → **entra como admin**, mesmo com a senha errada.
- **Ataque B (item 2.6):** Usuário `' OR 1=1 --` / Senha em branco → **entra como admin**, sem saber usuário nem senha.

> Observação importante: o payload exato do item 2.5 (`XxxXxxX' OR 1=1`, sem fechar a aspa) gera **erro de sintaxe**, exatamente como o próprio material aponta. Por isso, no laboratório, usamos a forma com as **aspas balanceadas** (`' OR '1'='1`) ou a versão com **comentário `--`** do item 2.6.

Olhe a consulta SQL que a página mostra. No ataque B ela vira:

```
SELECT id, username FROM users WHERE username='' OR 1=1 --' AND password=''
```

O `OR 1=1` é sempre verdadeiro e o `--` comenta o resto da linha, ignorando a checagem de senha. Como `OR 1=1` casa com **todas** as linhas, o banco devolve a primeira (o `admin`).

> Nota: neste laboratório o SQLite **não deixa** encadear `; drop table users` (o `execute` aceita só um comando), então os alunos podem atacar à vontade **sem destruir o banco**, o cenário destrutivo do item 2.6 é explicado, mas não acontece aqui.

**Passo 8: A defesa (fechar o buraco)**

Abra o `app.py` e, dentro de `do_GET`, procure estas duas linhas:

```python
sucesso, sql, quem = login_vulneravel(usuario, senha)
# sucesso, sql, quem = login_seguro(usuario, senha)
```

Inverta o comentário para ativar a versão segura:

```python
# sucesso, sql, quem = login_vulneravel(usuario, senha)
sucesso, sql, quem = login_seguro(usuario, senha)
```

Salve, pare o servidor (`Ctrl + C`) e rode de novo. Repita os ataques A e B → agora dá **ACESSO NEGADO**. A versão segura usa **prepared statement** (`WHERE username=? AND password=?`), tratando a entrada como **dado**, nunca como **código SQL**, a mesma ideia dos itens 3.2 a 3.4.

> Isso resolve o SQL Injection, mas **não** resolve a captura no Wireshark: a senha só para de aparecer com **HTTPS/TLS**.

**Perguntas para fechar com a turma**

1. Por que a senha apareceu em texto puro no Wireshark? O que mudaria com HTTPS?
2. Por que `OR 1=1 --` conseguiu burlar o login?
3. O prepared statement parou o ataque. Ele também esconde a senha no Wireshark? (não!)
4. Ligando com a seção 4: quais serviços da AWS (WAF, RDS, Secrets Manager, Cognito) ajudariam a defender esse mesmo login em produção?

---
## 3) Prevenções

### 3.1) Prevenção usando ASP (Active Server Pages)

A prevenção é simples, mas o sucesso do ataque acaba sendo consequência da falta de preparo dos desenvolvedores. O serviço AWS WAF (Web Application Firewall) não detecta as vulnerabilidades do seu código; ele inspeciona o **tráfego** e sinaliza alarmes em situações conhecidas de ataque ou em situações de grande número de erros ou **UNIONS** dentro de solicitações (veja o item 4.1).

As linguagens modernas para web fazem a defesa baseada na preparação das consultas SQL antes de serem submetidas ao banco

Em ASP, que é uma tecnologia da Microsoft para gerar páginas da web de forma dinâmica, indica-se não operar com as strings de consulta diretamente:

```
user = getRequestString("username");
txtSQL = "SELECT * FROM users WHERE UserId = @0";
db.Execute(txtSQL, user);

id = 999
user = getRequestString("username");
pass = getRequestString("password");
txtSQL = "INSERT INTO users (id,user,pass) Values(@0, @1, @2)";
db.Execute(txtSQL, id, user, pass);
```

#### Explicação:

Este código está realizando duas operações SQL separadas: uma **consulta** e uma **inserção** no banco de dados. Vamos entender cada parte do código didaticamente.

- **```getRequestString("username")```**: Esta função está obtendo o valor do campo `username` da requisição (pode ser de um formulário HTML, por exemplo). Este valor é atribuído à variável `user`.
  
- **```txtSQL = "SELECT * FROM users WHERE UserId = @0";```**: Aqui está sendo criada uma string SQL, que é um comando de **SELECT** para buscar todos os dados (```*```) da tabela ```users```, onde o valor da coluna ```UserId``` corresponde ao valor que será fornecido na execução da consulta. O ```@0``` é um **placeholder**, ou seja, será substituído pelo valor de ```user``` na execução da consulta.

- **```db.Execute(txtSQL, user);```**: Este comando está executando a consulta no banco de dados. O método ```db.Execute``` substitui o placeholder ```@0``` pelo valor de ```user``` e então executa a consulta. O objetivo aqui é buscar todas as informações de um usuário específico com o ```UserId``` que foi recebido na requisição.

- **id = 999**: está sendo definida uma variável ```id``` com valor fixo de **999**. Isso sugere que um novo usuário será inserido no banco de dados com esse ID.

- **```user = getRequestString("username"); e pass = getRequestString("password");```**: assim como no exemplo anterior, o código obtém os valores dos campos ```username``` e ```password``` da requisição e os armazena nas variáveis ```user``` e ```pass```, respectivamente.

- **```txtSQL = "INSERT INTO users (id, user, pass) Values(@0, @1, @2)";```**: esta linha está montando uma string SQL para um comando de **inserção** (INSERT INTO) na tabela ```users```. A instrução indica que serão inseridos valores para as colunas ```id```, ```user```, e ```pass```. Os placeholders ```@0```, ```@1```, e ```@2``` serão substituídos pelos valores de ```id```, ```user```, e ```pass```, respectivamente.

- **```db.Execute(txtSQL, id, user, pass);```**: finalmente, a execução do comando SQL acontece. O método ```db.Execute``` insere no banco de dados um novo usuário com os valores fornecidos: **id = 999**, o ```username``` obtido pela requisição, e a ```password``` também obtida pela requisição.


#### Considerações Importantes:

1. **Segurança e SQL Injection**: embora o código utilize placeholders (```@0```, ```@1```, etc.), que geralmente são seguros contra **SQL Injection**, é importante garantir que a implementação de ```db.Execute``` use **prepared statements** para evitar vulnerabilidades. Se a implementação interna da função não proteger os valores inseridos, ainda há risco de SQL Injection.

2. **Inserção fixa de ```id```**: o valor de ```id``` está sendo definido de forma fixa como **999**, o que pode causar problemas se a tabela ```users``` já tiver uma entrada com esse ```id```, resultando em um erro de inserção. Normalmente, o ```id``` seria gerado automaticamente pelo banco de dados, especialmente se for uma chave primária com auto-incremento.

3. **Senhas não seguras**: o código está inserindo a senha diretamente no banco de dados, o que não é uma prática segura. Idealmente, as senhas devem ser **hasheadas** (usando, por exemplo, ```bcrypt```) antes de serem armazenadas.

---
### 3.2) Usando PHP para Objetos

```
$stmt = $pdo->prepare('SELECT * FROM users WHERE name = :name');
$stmt->execute([ 'name' => $name ]);
foreach ($stmt as $row) { // Do something with $row }
```

#### Explicação

Este código usa **PDO** (PHP Data Objects) para realizar uma consulta ao banco de dados de forma segura, evitando vulnerabilidades como SQL injection. Vamos analisar o que ele faz em cada linha.

- **```$pdo->prepare()```**: Essa linha está preparando uma **declaração SQL** que será executada posteriormente. A consulta seleciona todos os dados (```*```) da tabela ```users``` onde o campo ```name``` é igual ao valor que será passado como parâmetro. O **```:name```** é um **placeholder nomeado** que será substituído pelo valor real durante a execução. Este uso de placeholders torna a consulta mais segura e protege contra SQL injection, uma vez que o valor será tratado de forma segura pelo PDO.

- **```$stmt->execute()```**: Aqui a consulta SQL preparada é executada, com o valor de ```:name``` sendo substituído pela variável ```$name```. A função ```execute()``` recebe um array associativo que mapeia o placeholder ```:name``` para o valor de ```$name```. O valor de ```$name``` pode ter sido obtido de um formulário, por exemplo, mas como é passado de forma segura, o PDO trata o dado para evitar qualquer injeção de código.

- **```foreach```**: Este laço percorre os resultados da consulta. Cada linha de resultado da tabela ```users``` será armazenada na variável ```$row``` a cada iteração. O ```$row``` será um array associativo que contém os dados retornados pelo banco de dados para cada linha que corresponde ao critério de consulta (onde o campo ```name``` é igual ao valor passado). **Dentro do ```foreach```** você pode realizar operações com os dados retornados, como exibi-los ou processá-los de acordo com a lógica da aplicação.

---
### 3.3) Usando MySQLi

```
$stmt = $dbConnection->prepare('SELECT * FROM employees WHERE name = ?');
$stmt->bind_param('s', $name); // 's' variable type => 'string'
$stmt->execute();
$result = $stmt->get_result();
while ($row = $result->fetch_assoc()) { // Do something with $row } 
```

#### Explicação

Este código está utilizando o estilo de prepared statements do **MySQLi** em PHP para realizar uma consulta ao banco de dados de forma segura, protegendo contra ataques de **SQL Injection**. Vamos comentar cada parte do código para explicar seu funcionamento:

- **```$dbConnection->prepare()```**: Esta função prepara uma declaração SQL no banco de dados. A consulta SQL aqui seleciona todos os dados (```*```) da tabela ```employees``` onde o campo ```name``` é igual a um valor que será fornecido. O **```?```** é um **placeholder**, que será substituído pelo valor real durante a execução da consulta. Ele permite que o valor seja passado de forma segura para a consulta, evitando que código malicioso seja injetado.

- **```$stmt->bind_param()```**: Esta função faz a **associação** de parâmetros para os placeholders na consulta SQL. O primeiro argumento ```s``` indica que o parâmetro que será passado é do tipo **string** (```s``` significa **string**). Outros tipos possíveis seriam ```i``` para inteiros, ```d``` para decimais (doubles), etc. O segundo argumento, ```$name```, é o valor real que será passado para substituir o ```?``` na consulta SQL. Este valor pode ser obtido de um formulário ou outra fonte de entrada de dados.

- **```$stmt->execute()```**: Aqui a consulta SQL é **executada** no banco de dados, com o valor associado ao placeholder sendo passado corretamente. Este método executa a consulta com o valor de ```$name``` já vinculado ao parâmetro ```?```, realizando assim a busca no banco de dados.

- **```$stmt->get_result()```**: Esta função obtém o **resultado** da consulta SQL. A variável ```$result``` armazenará o conjunto de resultados retornados pela consulta, que pode conter múltiplas linhas da tabela ```employees``` se houver vários registros que correspondam ao valor de ```$name```.

- **```while ($row = $result->fetch_assoc())```**: Este loop **itera sobre cada linha** de resultados retornada pela consulta. **```$result->fetch_assoc()```**: Esta função retorna cada linha de resultados da consulta como um array associativo, onde as chaves são os nomes das colunas da tabela ```employees```. Dentro do laço ```while```, você pode fazer algo com os dados em ```$row```. Por exemplo, exibir os valores das colunas, armazenar em outra estrutura, ou processá-los de acordo com a lógica de negócios da sua aplicação.

#### Exemplo de como manipular os dados:

Dentro do loop ```while```, você pode acessar as colunas da tabela ```employees``` assim:

```php
while ($row = $result->fetch_assoc()) {
    echo "Nome: " . $row['name'] . "<br>";
    echo "Cargo: " . $row['position'] . "<br>";
}
```

Neste exemplo, supondo que a tabela ```employees``` tenha as colunas ```name``` e ```position```, o código acima exibiria o nome e o cargo de cada funcionário que corresponde ao nome passado na consulta.

---
### 3.4) Usando JavaScript (Node.js)

```
var sql = "SELECT * FROM table WHERE userid = ?";
var inserts = [message.author.id];
sql = mysql.format(sql, inserts); 
```

#### Explicação

Esse código está utilizando **MySQL** no Node.js (ou ambiente JavaScript similar) para realizar uma consulta SQL de forma segura. Ele prepara uma consulta SQL e insere valores dinamicamente, prevenindo **SQL Injection** ao usar a função ```mysql.format()```. Vamos explicar cada parte:

- **```var sql = "SELECT * FROM table WHERE userid = ?";```** esta linha está criando uma **string SQL** que seleciona todos os dados (```*```) da tabela chamada ```table```, onde o valor da coluna ```userid``` será substituído por um valor dinâmico. O símbolo **```?```** é um **placeholder**. Ele será substituído posteriormente por um valor real, que será fornecido através da variável ```inserts```.

- **```var inserts = [message.author.id];```** esta linha cria um **array** chamado ```inserts```, onde o valor dentro do array é **```message.author.id```**. Em **```message.author.id```**, esta variável provavelmente contém o ID de um usuário, possivelmente extraído de uma mensagem em um sistema (como Discord ou outra plataforma de mensagens). Esse ID será usado para substituir o ```?``` na string SQL.

- **```sql = mysql.format(sql, inserts);```** a função **```mysql.format()```** substitui o placeholder ```?``` na consulta SQL pelo valor fornecido no array ```inserts```. Em **```mysql.format()```** garante que o valor seja corretamente escapado para prevenir **SQL Injection**, tratando a variável como um dado, em vez de permitir que seja interpretada como parte da consulta SQL. Neste caso, ele substitui o ```?``` por ```message.author.id```. Exemplo de resultado após ```mysql.format()```. Suponha que o ```message.author.id``` tenha o valor **12345**. Após o uso de ```mysql.format()```, a consulta SQL final poderia se parecer com:

```sql
SELECT * FROM table WHERE userid = '12345';
```

- Ao usar ```mysql.format()```, a função substitui o placeholder ```?``` de maneira segura, escapando corretamente os valores e impedindo que entradas maliciosas sejam executadas como parte do SQL. Por exemplo, se alguém tentasse injetar uma string perigosa como ```"' OR '1'='1"```, ela seria tratada como uma simples string e não como parte do SQL.

---
## 4) Segurança de banco de dados na AWS (defesa em profundidade)

> **Importante:** a prevenção **real** do SQL Injection acontece no **código**, com **consultas parametrizadas / prepared statements** (seção 3). Os serviços a seguir **não substituem** isso: o **WAF** ajuda a bloquear tentativas de ataque, e os demais reduzem a **superfície** e o **impacto** de um ataque bem-sucedido. Isso é o que se chama de *defesa em profundidade*, várias camadas de proteção, não uma bala de prata.

### 4.1) AWS WAF (Web Application Firewall)
   - Função: O AWS WAF ajuda a proteger suas aplicações web contra explorações comuns, incluindo tentativas de SQL Injection.
   - Como configurar para SQL Injection:
     - No AWS WAF, crie regras personalizadas que bloqueiam ou limitam tentativas de SQL Injection.
     - Habilite a regra "SQL Injection Match Condition", que detecta padrões comuns de injeções de SQL nas requisições.

     Exemplo de configuração:
     - Adicione uma regra de SQL Injection à ACL do AWS WAF.
     - Associe essa ACL à distribuição do Amazon CloudFront ou ao API Gateway.
     - Preços: [https://aws.amazon.com/pt/waf/pricing/](https://aws.amazon.com/pt/waf/pricing/)
   - Limitação: o WAF inspeciona o **tráfego** e barra padrões conhecidos de ataque, mas **não corrige** a falha no seu código nem bloqueia 100% dos payloads. Ele é uma camada extra, não um substituto da consulta parametrizada.

---
### 4.2) Amazon RDS (Relational Database Service)
   - Função: Gerenciamento de bancos de dados com criptografia automática de dados e recursos que reduzem a superfície de ataque. **Não previne SQL Injection por si só**, mas ajuda a limitar o dano caso um ataque ocorra.
   - Configurações para melhorar a segurança:
     - IAM Authentication: Use autenticação baseada no IAM para evitar senhas SQL hardcoded.
     - Encrypted connections: Garanta que as conexões com o banco sejam feitas via SSL para impedir interceptações.
     - Auditoria de Logs: Ative logs de auditoria para monitorar e registrar consultas suspeitas.

---
### 4.3) Amazon Cognito
   - Função: Gerenciamento de autenticação de usuários com foco na segurança.
   - Como se relaciona com SQL Injection:
     - Cognito assume o fluxo de **autenticação** fora da sua aplicação. Assim, aquele formulário de login deixa de ser um ponto de entrada seu para SQL Injection, pois você não escreve mais a consulta de login manualmente.
     - **Atenção:** isso não "imuniza" o resto do sistema. Todas as **demais** consultas da sua aplicação (busca, listagem, cadastro, etc.) continuam exigindo consultas parametrizadas. Cognito cuida do login, não das outras queries.

---

### 4.4) AWS Secrets Manager
   - Função: Protege segredos usados pela aplicação (como senhas de banco de dados) e faz a rotação automática.
   - Como se relaciona com segurança:
     - Guardar credenciais fora do código evita que senhas vazem junto com o código-fonte e reduz o impacto de um vazamento.
     - **Observação:** credencial hardcoded é um problema de segurança **diferente** do SQL Injection, já o Secrets Manager melhora a postura geral de segurança, mas **não** previne injeção de SQL.

     Exemplo de Integração:
     ```php
     $secret = SecretsManagerClient::getSecretValue(['SecretId' => 'dbCredentials']);
     $dbConnection = new PDO("mysql:host=$secret->host;dbname=$secret->dbname", $secret->username, $secret->password);
     ```

---
### 4.5) Outras Boas Práticas de Segurança na AWS
   
   - Least Privilege Principle (Princípio do Menor Privilégio): Assegure-se de que os usuários e aplicações tenham apenas as permissões necessárias. Evite dar privilégios administrativos sem necessidade.
   - Multi-Factor Authentication (MFA): Habilite MFA para usuários IAM para aumentar a segurança das credenciais.
   - Security Groups & NACLs: Limite o acesso ao banco de dados usando regras de Security Groups e Network ACLs, permitindo apenas o tráfego necessário.
   - Monitoramento com CloudWatch e GuardDuty: Monitore atividades incomuns e potencialmente maliciosas em suas aplicações e infraestrutura, incluindo tentativas de SQL Injection.

---
## 5) Outros códigos SQL de ataque (histórico / opcional)

> **Nota:** os exemplos abaixo são **históricos e opcionais**. Baseiam-se em mensagens de erro do **Microsoft SQL Server 2000 / OLE DB / ASP** e servem para ilustrar a *enumeração de esquema por mensagens de erro*, uma técnica de descoberta em que o atacante aprende a estrutura do banco a partir dos próprios erros retornados. Eles **não** usam o ambiente do laboratório (SQLite/Python) e podem ser tratados como conteúdo avançado. Lembre-se: em SQL, o comentário de linha é `--` (dois hifens).


### 5.1) ```Username: ' having 1=1 --```

-- Error
Microsoft OLE DB Provider for ODBC Drivers error '80040e14’
[Microsoft][ODBC SQL Server Driver][SQL Server]Column 'users.id' is invalid in the select list because it is not contained in an aggregate function and there is no GROUP BY clause

/process_login.asp, line 35

**Conquista do hacker:** Ele descobre que existe uma tabela **users** e que a primeira coluna é ```users.id```
Usando o comando ```HAVING 1=1 --``` faria com que qualquer coisa após o -- fosse desconsiderada, porque é um comentário em SQL. Por exemplo, a parte da consulta que verifica a senha seria ignorada, o que poderia permitir o login sem fornecer uma senha válida.

---
### 5.2) ```Username: ' group by users.id having 1=1 --```

-- Error
Microsoft OLE DB Provider for ODBC Drivers error '80040e14’
[Microsoft][ODBC SQL Server Driver][SQL Server]Column 'users.username' is invalid in the select list because it is not contained in an aggregate function and there is no GROUP BY clause

/process_login.asp, line 35 

**Conquista do hacker:** ele descobre que a segunda coluna da tabela users é ```username```

---
### 5.3) ```Username: ' group by users.id, users.username having 1=1 --```

-- Error
Microsoft OLE DB Provider for ODBC Drivers error '80040e14’
[Microsoft][ODBC SQL Server Driver][SQL Server]Column 'users.password' is invalid in the select list because it is not contained in an aggregate function and there is no GROUP BY clause

/process_login.asp, line 35 

**Conquista do hacker:** ele descobre que a terceira coluna da tabela users é ```password```.

---
### 5.4) ```Username: ' union select sum(username) from users --```

-- Error

Microsoft OLE DB Provider for ODBC Drivers error '80040e07' [Microsoft][ODBC SQL Server Driver][SQL Server]The sum or average aggregate operation cannot take a varchar data type as an argument

/process_login.asp, line 35

**Conquista do hacker:** ele descobre que a segunda coluna (```username```) é do tipo **varchar**.

---
### 5.5) De posse dos campos do banco de dados, pode-se encadear (com “;”) um comando de inserção:

```Username: '; insert into users values(9999, 'willy', 'foobar') --```

---
### 5.6) Username: ' union select @@version,1,1,1 --

-- Error

Microsoft OLE DB Provider for ODBC Drivers error '80040e07' [Microsoft]
[ODBC SQL Server Driver][SQL Server]Syntax error converting the nvarchar value
'Microsoft SQL Server 2000 - 8.00.760 (Intel X86)

Dec 17 2002 14:22:05 Copyright (c) 1988-2003 Microsoft Corporation Standard Edition on Windows NT 5.2 (Build 3790: Service Pack 1)' to a column of data type int. 

/process_login.asp, line 35

**Conquista do hacker:** versão do banco de dados (Microsoft SQL Server 2000) e sistema operacional (Windows NT)

---
## 6) Atividade

Cada grupo deve montar uma apresentação de até 5min explicando o que pretende fazer para impedir ataques no seu RDS e vir explicar para os demais.

Todos os grupos terão 25min para montar essa apresentação.
