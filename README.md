# Segurança no Desenvolvimento de Aplicações: SQL Injection

Neste encontro iremos abordar a proteção de dados na nuvem no contexto de desenvolvimento de aplicações seguras e proteção contra ataques de SQL Injection.

---
## Horário de Atendimento

### Presencialmente, todas as terças e quintas, das 8h30 às 18h. 

### No slack, ao longo da semana assim que possível.

---
## 1) Vantagens para o seu Projeto

Entender os riscos de SQL Injection no projeto da venda de ingressos minimiza as vulnerabilidades, já que o SQL Injection é o ataque mais famosos que visa explorar falhas de segurança em aplicações que interagem com bancos de dados, permitindo que invasores insiram ou manipulem consultas SQL maliciosas.

O SQL Injection está na mesma calçada da fama de DDoS. Aqui na [Wikipedia](https://en.wikipedia.org/wiki/SQL_injection#Examples) você encontra um histórico dos principais ataques.

<img src="https://github.com/agodoi/sqlinjection/blob/main/imgs/sql_injection-01.jpg" width="800">


Dependendo da forma que você interage com as aplicações de RDS do seu projeto, o invasor pode apagar seu banco em alguns segundos.

### 1.1) Proteção de Dados Sensíveis
   - O sistema de inventário de ingressos lida com a sincronização de dados de estoque entre back e front-end. Proteger o banco de dados contra SQL Injection garante que informações críticas, como quantidades de estoque e detalhes dos eventos, sejam mantidas seguras, impedindo o vazamento de dados internos que poderiam prejudicar a operação.

---
### 1.2) Maior Confiabilidade do Sistema
   - Ao implementar mecanismos que evitam SQL Injection, como **prepared statements** ou **ORM (Object-Relational Mapping)**, a confiabilidade do sistema aumenta, pois ele não será vulnerável a manipulações externas. Isso é crucial para garantir que o sistema de venda de ingressos continue funcionando corretamente, sem interferências de usuários maliciosos.

---
### 1.3) Conformidade com Normas de Segurança
   - Empresas como a PulseStage estão frequentemente sujeitas a regulamentações de privacidade e segurança de dados (como LGPD). A prevenção de ataques de SQL Injection é uma prática de segurança recomendada que ajuda a empresa a se manter em conformidade com essas normas, evitando multas e danos à reputação.

---
### 1.4) Redução de Custos com Incidentes de Segurança
   - Investir na prevenção de ataques como o SQL Injection pode evitar incidentes de segurança caros, tanto em termos de reparo de sistemas quanto em possíveis responsabilidades legais. Isso é especialmente importante para um sistema que opera em múltiplas localidades e lida com grandes volumes de transações, como o sistema de inventário distribuído descrito.

---
### 1.5) Melhoria na Experiência do Usuário Final
   - Um sistema que sofre menos com falhas de segurança e funciona de forma eficiente oferece uma melhor experiência para o usuário final. No caso do e-commerce B2B e B2C, evitar SQL Injection garante que os clientes possam confiar na plataforma e na exatidão dos prazos de entrega e disponibilidade de produtos.

---
### 1.6) Preparação para Escalabilidade
   - O sistema descrito precisa suportar grandes volumes de transações. Implementar medidas de segurança contra SQL Injection permite que a plataforma escale de forma segura, sem se tornar mais vulnerável à medida que o volume de usuários e transações cresce.

---
## 2) Como funciona o ataque?


#### 2.1) Um atacante insere código SQL malicioso em um campo de entrada de um site ou aplicação, isto é, ele usa a sua API, a sua aplicação para chegar no seu RDS.

---
#### 2.2) Esse código é então executado pelo banco de dados, podendo alterar sua operação original.

---
#### 2.3) Exemplos de ações possíveis

* Recuperação de dados sensíveis;

* Deleção de tabelas,

* Elevação de privilégios no sistema;

* Download completo da sua base.

### Imagine os valores dos ingressos sendo alterados para baixo, criando uma corrida frenética nos sites. Ou, um roubo de cartões de crédito + CVC.

---
#### 2.4) Exemplo de código vulnerável

Imagine uma aplicação como essa de login em um banco de dados.

```
<html>
<head><title>Pagina de Login</title></head>
  <body bgcolor='000000' text='cccccc'>
    <font face='tahoma' color='cccccc'>
    <center><H1>LOGIN</H1>
    <form action='processa_login.asp' method='post'>
      <table>
        <tr><td>Username:</td><td>
        <input type=text name=username size=100% width=100>
        </input></td></tr>
        <tr><td>Password:</td><td>
        <input type=password name=password size=100% width=100>
        </input></td></tr>
      </table>
      <input type=submit name=enviar><input type=reset name=Redefinir>
    </form>
  </body>
</html>

```

<img src="https://github.com/agodoi/sqlinjection/blob/main/imgs/tela_banco_01.png" width="800">

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

- A expressão ```user + "' AND password='" + pass + "``` insere diretamente os valores de ```user``` e ```pass``` na string SQL. Isso é uma forma arriscada de construir consultas SQL, pois o conteúdo de ```user``` e ```pass``` não está sendo verificado ou tratado de forma segura.

---
#### 2.5) Exemplo 1 de código malicioso

Imagine que foi digitado o seguinte:

|Variável|Dado|
|-|-|
|Username:| ```godoi```|
|Password:| ```XxxXxxX' OR 1=1```|
| |Falso OR True = True|

#### Lembrando: na Álgebra de Boole, Falso + True = True



<img src="https://github.com/agodoi/sqlinjection/blob/main/imgs/tela_banco_02.png" width="800">


#### Explicação

* Neste caso, o SQL injection foi usado para contornar a autenticação do usuário.

* O atacante só precisa conhecer o username ```godoi```. Por isso, deve-se evitar o ```admin```

* A consulta SQL montada tem erro de sintaxe (' a mais no final):

```
SELECT id FROM users WHERE username= 'godoi' AND password='XxxXxxX' OR 1=1'
```

* Inserção de comentário: algumas sequências de caracteres são delimitadores de início de comentários:

   - MySQL, MS-SQL, Oracle, PostgreSQL, SQLite:
      * ' OR '1'='1' --
      * ' OR '1'='1' /*
   - MySQL:
      * ' OR '1'='1' #

   - Access (using null characters):
     * ' OR '1'='1' %00
     * ' OR '1'='1' %16

   - Uso de caracteres especiais: se sua aplicações aceita os caracteres especiais, é provável que ela esteja vulnerável. 

      * **'** aspas simples
      * **"** aspas dupla
      * **;** ponto e vírgula


* A condição ```OR 1=1``` sempre será verdadeira, o que pode levar à execução de uma consulta que ignora o nome de usuário e senha corretos, permitindo ao invasor obter acesso sem fornecer uma senha válida.

---
#### 2.6) Exemplo 2 de código malicioso

Imagine que foi digitado o seguinte:

|Variável|Dado|
|-|-|
|Username:| ```' OR 1=1 --```|
|Password:| ``` ```|
| |Falso OR True = True|

#### Lembrando: na Álgebra de Boole, Falso + True = True


<img src="https://github.com/agodoi/sqlinjection/blob/main/imgs/tela_banco_03.png" width="800">

#### Explicação

```
SELECT id FROM users WHERE username= ' ' OR 1=1 --' AND password=' '
```

* Nesse caso, nem mesmo username válido é preciso.

* O atacante nem sempre sabe qual servidor SQL está em execução. Assim, a condição **Sempre TRUE** pode variar e é detectado por tentativa e erro:
   - '1'='1' 
   - 1=1
   - =
   - true


* Em SQL, pode-se encadear vários comandos em um separando-os por **;**
   - ```1=1; drop table users```
   - Múltiplas seleções podem ser formadas para um único resultado com o comando UNION

---
#### 2.7) Ataques em HTTP/GET

Ao se usar HTTP/GET, as variáveis do formulário ficam expostas na barra de navegação e oferecem um ponto de partida para manipulação. Por exemplo:
```http://testphp.vulnweb.com/artists.php?artist=1```

O formulário tem um método **get** que expõe a variável ```artist=1```. Veja a foto e o site [http://testphp.vulnweb.com/artists.php?artist=2](http://testphp.vulnweb.com/artists.php?artist=2)



<img src="https://github.com/agodoi/sqlinjection/blob/main/imgs/tela_banco_04.png" width="800">


---
### 3) Prevenções

#### 3.1) Prevenção usando ASP (Active Server Pages)

A prevenção é simples, mas o sucesso do ataque acaba sendo consequência da falta de preparo dos desenvolvedores. O serviço AWS WAF (Web Application Firewalls) não detectam as vulnerabilidades, mas sinalizam alarmes em situações conhecidas de ataque ou em situações de grande número de erros ou **UNIONS** dentro de solicitações.

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
#### 3.2) Usando PHP para Objetos

```
$stmt = $pdo->prepare('SELECT * FROM users WHERE name = :name’);
$stmt->execute([ 'name' => $name ]);
foreach ($stmt as $row) { // Do something with $row }
```

#### Explicação

Este código usa **PDO** (PHP Data Objects) para realizar uma consulta ao banco de dados de forma segura, evitando vulnerabilidades como SQL injection. Vamos analisar o que ele faz em cada linha.

- **```$pdo->prepare()```**: Essa linha está preparando uma **declaração SQL** que será executada posteriormente. A consulta seleciona todos os dados (```*```) da tabela ```users``` onde o campo ```name``` é igual ao valor que será passado como parâmetro. O **```:name```** é um **placeholder nomeado** que será substituído pelo valor real durante a execução. Este uso de placeholders torna a consulta mais segura e protege contra SQL injection, uma vez que o valor será tratado de forma segura pelo PDO.

- **```$stmt->execute()```**: Aqui a consulta SQL preparada é executada, com o valor de ```:name``` sendo substituído pela variável ```$name```. A função ```execute()``` recebe um array associativo que mapeia o placeholder ```:name``` para o valor de ```$name```. O valor de ```$name``` pode ter sido obtido de um formulário, por exemplo, mas como é passado de forma segura, o PDO trata o dado para evitar qualquer injeção de código.

- **```foreach```**: Este laço percorre os resultados da consulta. Cada linha de resultado da tabela ```users``` será armazenada na variável ```$row``` a cada iteração. O ```$row``` será um array associativo que contém os dados retornados pelo banco de dados para cada linha que corresponde ao critério de consulta (onde o campo ```name``` é igual ao valor passado). **Dentro do ```foreach```** você pode realizar operações com os dados retornados, como exibi-los ou processá-los de acordo com a lógica da aplicação.

---
#### 3.3) Usando MySQLi

```
$stmt = $dbConnection->prepare('SELECT * FROM employees WHERE name = ?’);
$stmt->bind_param('s', $name); // 's' variable type => 'string’
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
#### 3.4) Usando Java

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
## 4) Prevenção de SQL Injection usando AWS

### 4.1) AWS WAF (Web Application Firewall)
   - Função: O AWS WAF ajuda a proteger suas aplicações web contra explorações comuns, incluindo SQL Injection.
   - Como configurar para SQL Injection:
     - No AWS WAF, crie regras personalizadas que bloqueiam ou limitam tentativas de SQL Injection.
     - Habilite a regra "SQL Injection Match Condition", que detecta padrões comuns de injeções de SQL nas requisições.

     Exemplo de configuração:
     - Adicione uma regra de SQL Injection à ACL do AWS WAF.
     - Associe essa ACL à distribuição do Amazon CloudFront ou ao API Gateway.
     - Preços: [https://aws.amazon.com/pt/waf/pricing/](https://aws.amazon.com/pt/waf/pricing/)

---
#### 4.2) Amazon RDS (Relational Database Service)
   - Função: Gerenciamento seguro de bancos de dados, com encriptação automática de dados e proteção contra falhas de segurança comuns.
   - Configurações para melhorar a segurança:
     - IAM Authentication: Use autenticação baseada no IAM para evitar senhas SQL hardcoded.
     - Encrypted connections: Garanta que as conexões com o banco sejam feitas via SSL para impedir interceptações.
     - Auditoria de Logs: Ative logs de auditoria para monitorar e registrar consultas suspeitas.

---
#### 4.3) Amazon Cognito
   - Função: Gerenciamento de autenticação de usuários com foco na segurança.
   - Como ajuda a prevenir SQL Injection:
     - Cognito permite que sua aplicação autentique usuários sem precisar manipular diretamente as senhas no código-fonte. Isso reduz o risco de injeções maliciosas em campos sensíveis.
     - Integre a autenticação com Cognito para criar uma camada extra de segurança.

---

#### 4.4) AWS Secrets Manager
   - Função: Protege segredos necessários pela aplicação (como senhas de banco de dados) e faz a rotação automática.
   - Como utilizar:
     - Configure o AWS Secrets Manager para gerenciar credenciais do banco de dados.
     - Garanta que as credenciais não estejam hardcoded no código, eliminando vetores de ataque comuns.

     Exemplo de Integração:
     ```php
     $secret = SecretsManagerClient::getSecretValue(['SecretId' => 'dbCredentials']);
     $dbConnection = new PDO("mysql:host=$secret->host;dbname=$secret->dbname", $secret->username, $secret->password);
     ```

---
#### 4.5) Outras Boas Práticas de Segurança na AWS
   
   - Least Privilege Principle (Princípio do Menor Privilégio): Assegure-se de que os usuários e aplicações tenham apenas as permissões necessárias. Evite dar privilégios administrativos sem necessidade.
   - Multi-Factor Authentication (MFA): Habilite MFA para usuários IAM para aumentar a segurança das credenciais.
   - Security Groups & NACLs: Limite o acesso ao banco de dados usando regras de Security Groups e Network ACLs, permitindo apenas o tráfego necessário.
   - Monitoramento com CloudWatch e GuardDuty: Monitore atividades incomuns e potencialmente maliciosas em suas aplicações e infraestrutura, incluindo tentativas de SQL Injection.

---
## 5) Outros códigos SQL de ataque


### 5.1) ```Username: ' having 1=1—```

-- Error
Microsoft OLE DB Provider for ODBC Drivers error '80040e14’
[Microsoft][ODBC SQL Server Driver][SQL Server]Column 'users.id' is invalid in the select list because it is not contained in an aggregate function and there is no GROUP BY clause

/process_login.asp, line 35

**Conquista do hacker:** Ele descobre que existe uma tabela **users** e que a primeira coluna é ```users.id```
Usando o comando ```HAVING 1=1 --``` faria com que qualquer coisa após o -- fosse desconsiderada, porque é um comentário em SQL. Por exemplo, a parte da consulta que verifica a senha seria ignorada, o que poderia permitir o login sem fornecer uma senha válida.

---
### 5.2) ```Username: ' group by users.id having 1=1—```

-- Error
Microsoft OLE DB Provider for ODBC Drivers error '80040e14’
[Microsoft][ODBC SQL Server Driver][SQL Server]Column 'users.username' is invalid in the select list because it is not contained in an aggregate function and there is no GROUP BY clause

/process_login.asp, line 35 

**Conquita do hacker:** ele descobre que a segunda coluna da tabela users é ```username```

---
### 5.3) ```Username: ' group by users.id, users.username having 1=1—```

-- Error
Microsoft OLE DB Provider for ODBC Drivers error '80040e14’
[Microsoft][ODBC SQL Server Driver][SQL Server]Column 'users.password' is invalid in the select list because it is not contained in an aggregate function and there is no GROUP BY clause

/process_login.asp, line 35 

**Conquita do hacker:** ele descobre que a terceira coluna da tabela users é ```password```.

---
### 5.4) ```Username: ' union select sum(username) from users—```

-- Error

Microsoft OLE DB Provider for ODBC Drivers error '80040e07' [Microsoft][ODBC SQL Server Driver][SQL Server]The sum or average aggregate operation cannot take a varchar data type as an argument

/process_login.asp, line 35

**Conquita do hacker:** ele descobre que a segunda coluna da tabela username tem variável do tipo **varchar**.

---
### 5.5) De posse dos campos do banco de dados, pode-se encadear (com “;”) um comando de inserção:

```Username: '; insert into users values(9999, ‘willy', 'foobar')--```

---
### 5.6) Username: ' ' union select @@version,1,1,1—-

-- Error

Microsoft OLE DB Provider for ODBC Drivers error '80040e07' [Microsoft]
[ODBC SQL Server Driver][SQL Server]Syntax error converting the nvarchar value
'Microsoft SQL Server 2000 - 8.00.760 (Intel X86)

Dec 17 2002 14:22:05 Copyright (c) 1988-2003 Microsoft Corporation Standard Edition on Windows NT 5.2 (Build 3790: Service Pack 1)' to a column of data type int. 

/process_login.asp, line 35

**Conquita do hacker:** versão do banco de dados (Microsoft SQL Server 2000) e sistema operacional (Windows NT)

---
## 6) Atividade

Cada grupo deve montar uma apresentação de até 5min explicando o que pretende fazer para impedir ataques no seu RDS e vir explicar para os demais.

Todos os grupos terão 25min para montar essa apresentação.
