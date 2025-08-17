# Desafio aiqfome - Favorites API

O aiqfome está expandindo seus canais de integração e precisa de uma API robusta para gerenciar os "produtos favoritos" de usuários na plataforma. Essa funcionalidade será usada por apps e interfaces web para armazenar e consultar produtos marcados como favoritos pelos clientes. A API terá alto volume de uso e integrará com outros sistemas internos e externos.

# Setup do projeto

## 0. Pré-requisitos

- **Python** 3.13 ou superior
- **Pip**: Gerenciador de pacotes
- **Docker**: Plataforma para gerenciar contêineres
- **Docker compose**: Ferramenta para definir e executar aplicativos multicontêiner

## 1. Instalar as dependências

**⚠️ Atenção**: Não é necessário criar um `virtualenv`. Os contêineres foram configurados para ignorará-los, visando maior velocidade e menor uso de armazenamento. Se um venv for detectado, a inicialização do contêiner falhará devido à configuração `poetry config virtualenvs.create false` presente no build do `development/Dockerfile.dev`.

```bash
$ pip install -r development/requirements-dev.txt # Instala somente o poetry e o taskipy. O requirements.txt da raiz é utilizado apenas para o deploy
```

## 2. Definir as variáveis de ambiente

- A documentação de cada variável de ambiente pode ser encontrada no arquivo `settings.py`, dentro do diretório `app/__core__/application`

```bash
$ cp .env.example .env
```

## 3. Iniciar a aplicação

```bash
$ poetry run task start
```

# Primeiros passos na aplicação

## 1. Crie um cliente

- Ao executar a requisição abaixo, você receberá como resposta o `id` do cliente criado, ele será usado mais para frente em outras consultas, então pode guardá-lo em um bloco de notas.
- Uma nota técnica, é que eu usei o algoritmo `argon2` ao invés do `bcrypt` para criptografar a senha, pois em tempos de GPU e programação distribuída, algoritmos `memory-hard` se tornam uma melhor opção visando maior segurança

```bash
$ curl --location 'http://localhost:8080/auth/sign-up' \
    --header 'Content-Type: application/json' \
    --data-raw '{
        "email": "gabriel.cenciati@aiqfome.com",
        "name": "Gabriel Cenciati",
        "password": "minhasenhasupersegura2025"
    }'
```

## 2. Faça login

- Ao se logar com sucesso, você receberá um `access_token`, caso esteja usando o Postman, ele já coloca automaticamente o token nos cookies, se não, você precisa adicioná-lo manualmente com o valor retornado. O token de acesso garante que o cliente terá acesso somente as configurações de conta e favoritos dele mesmo e de mais nenhum outro cliente

```bash
$ curl --location 'http://localhost:8080/auth/sign-in' \
    --header 'Content-Type: application/json' \
    --data-raw '{
        "email": "gabriel.cenciati@aiqfome.com",
        "password": "minhasenhasupersegura2025"
    }'
```

## 3. Liste os clientes

- Caso você tenha perdido o ID do cliente que criou, você pode listar todos os clientes e encontrá-lo, no entanto, é necessário passar o header `x-aiqfome-api-key` na requisição, pois esse é um **endpoint privado** da aplicação, que dá acesso a todos os clientes cadastrados (id, nome, e-mail, data de criação e de atualização)

```bash
$ curl --location 'http://localhost:8080/customers' \
    --header 'x-aiqfome-api-key: 1f02aa3aeb1b37b4e120a32d24bfda37215766e2b46272196287521fe76be3eb' \
    --header 'Cookie: access_token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3ODI5M2RlNC0zNmU2LTQ1MDctOWVkYS1iMzc0OTc0ZjBmMDgiLCJleHAiOjE3NTU1NjUzMTd9.kize7KcOFQ7SFjVdBOfezde5jwHC_dOVa6oJO9QhGaI'
```

## 4. Favorite o seu primeiro produto!!

- Escolha um produto e favorite-o! Caso ele não exista, fique tranquilo(a) que a API irá te informar. Lembrando, que todos os cURLs de exemplo estão com um token de exemplo, portanto lembre-se de sempre utilizar o token fornecido pelo endpoint de sign in.
- E aqui vai mais uma nota técnica importante, uma vez que todo produto precisa ser validado na API externa, ao cliente **consultar ou favoritar** um produto, a aplicação automaticamente e em "paralelo", atualiza a tabela de cache `products_cache` com as informações **frescas** dele para que da próxima vez que qualquer cliente consultar ou favoritar o mesmo produto, a resposta não dependa da API externa. Obviamente, esses dados não ficarão frescos para sempre, por conta disso foi implementado uma estratégia de `stale-while-revalidate`, onde existe tanto um `soft_ttl` quanto um `hard_ttl` para controlar o tempo de vida dos dados no cache
- Para ilustrar melhor essa questão do sistema de cache, fiz um diagrama usando o `draw.io` indicando o passo a passo do fluxo

![cache_diagram](./docs/images/products_cache_flow.png)

```bash
$ curl --location --request POST 'http://localhost:8080/customers/78293de4-36e6-4507-9eda-b374974f0f08/favorites/5' \
    --header 'Cookie: access_token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3ODI5M2RlNC0zNmU2LTQ1MDctOWVkYS1iMzc0OTc0ZjBmMDgiLCJleHAiOjE3NTU1NjUzMTd9.kize7KcOFQ7SFjVdBOfezde5jwHC_dOVa6oJO9QhGaI'
```

## 5. Liste os produtos favoritados

```bash
$ curl --location 'http://localhost:8080/customers/78293de4-36e6-4507-9eda-b374974f0f08/favorites' \
    --header 'Cookie: access_token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3ODI5M2RlNC0zNmU2LTQ1MDctOWVkYS1iMzc0OTc0ZjBmMDgiLCJleHAiOjE3NTU1NjUzMTd9.kize7KcOFQ7SFjVdBOfezde5jwHC_dOVa6oJO9QhGaI'
```

- Abaixo temos um exemplo de resposta desse que talvez seja o endpoint mais importante de todo o sistema. Perceba que ela vem paginada, paginação essa que pode ser controlada nos query parameters `page` e `per_page`

```json
{
  "data": [
    {
      "id": 14,
      "title": "Samsung 49-Inch CHG90 144Hz Curved Gaming Monitor (LC49HG90DMNXZA) – Super Ultrawide Screen QLED ",
      "image_url": "https://fakestoreapi.com/img/81Zt42ioCgL._AC_SX679_t.png",
      "price": 999.99,
      "review": {
        "rate": 2.2,
        "count": 140
      }
    },
    {
      "id": 13,
      "title": "Acer SB220Q bi 21.5 inches Full HD (1920 x 1080) IPS Ultra-Thin",
      "image_url": "https://fakestoreapi.com/img/81QpkIctqPL._AC_SX679_t.png",
      "price": 599.0,
      "review": {
        "rate": 2.9,
        "count": 250
      }
    }
  ],
  "pagination": {
    "page": 1,
    "per_page": 20,
    "total_pages": 1,
    "total_items": 2
  }
}
```

# Explore os outros endpoints

- Para uma análise mais detalhada dos endpoints e seus respectivos contratos, é possível consultar a documentação completa da API. Ela foi gerada automaticamente com o `Swagger` nativo do `FastAPI` e está disponível em `http://localhost:8080/docs`

![documentation](./docs/images/api_docs.png)

# Estrutura do projeto

- A estrutura de pastas do projeto reflete as camadas de responsabilidade que implementei. Fiz usando um mix de conceitos presentes tanto na `Clean Architecture`, quanto no `DDD`, em alguns momentos sendo mais "purista" e em outros menos, de forma que eu conseguisse balancear a flexibilidade e complexidade do software, além de conseguir manter a legibilidade e a manutenibilidade.

```bash
desafio-aiqfome/
├── app/
│   ├── __core__/                  # O núcleo da aplicação, onde está tudo referente às regras de negócio
│   │   ├── application/           # Camada de aplicação, onde estão as "engrenagens" que colocam em prática as regras de negócio
│   │   │   ├── gateways/          # Interfaces para serviços externos (JWT, Product Catalog)
│   │   │   ├── presenters/        # Camada de apresentação, onde estão os formatadores das respostas da API
│   │   │   └── use_case/          # Casos de uso da aplicação (Sign In, Sign Up, Favorite product, etc.)
│   │   ├── domain/                # Camada de domínio (Entidades, Value Objects, etc.)
│   │   │   ├── entity/            # Entidades de negócio (Customer, Product)
│   │   │   ├── exception/         # Exceções customizadas do domínio
│   │   │   ├── repository/        # Interfaces dos repositórios
│   │   │   └── value_object/      # Objetos de valor (Password, etc.)
│   │   ├── settings.py            # Configurações da aplicação
│   │   ├── logger.py              # Configuração do logger
│   │   ├── task_manager.py        # Gerenciador de tarefas assíncronas
│   │   └── retry_with_backoff.py  # Utilitário para retry com backoff (Usei para o Product Catalog)
│   ├── infra/                     # Camada de infraestrutura (Implementações concretas)
│   │   ├── dependency.py          # Injeção de dependências
│   │   ├── fakestore/             # Integração com API externa do Fake Store
│   │   ├── http/                  # Camada HTTP (FastAPI)
│   │   │   ├── middleware/        # Middlewares (Fiz o Correlation ID para facilitar na identificação das requests)
│   │   │   └── router/            # Rotas da API (Auth, Customers, Favorites)
│   │   ├── jwt/                   # Implementação do serviço JWT
│   │   ├── postgres/              # Camada de persistência (PostgreSQL)
│   │   │   ├── orm/               # Modelos ORM que espelham as entidades, mas estão "sujos" com framework (SQLModel)
│   │   │   └── repository/        # Implementações dos repositórios
│   │   └── security.py            # Configurações de segurança que são usadas nos Controllers
│   ├── __main__.py                # Bootstrap da aplicação
│   └── __init__.py
├── development/                   # Arquivos para serem usados no desenvolvimento
│   ├── Dockerfile.dev             # Dockerfile para rodar o projeto localmente
│   ├── init.sql                   # Script de inicialização do banco que roda no build do PostgreSQL
│   └── requirements-dev.txt       # Dependências de desenvolvimento
├── docs/                          # Documentação do projeto
│   └── images/                    # Imagens da documentação
├── tests/                         # Testes automatizados
│   ├── integration/               # Testes de integração
│   └── unit/                      # Testes de unidade
├── .dockerignore                  # Arquivo de configuração do Docker para ignorar arquivos e pastas
├── .env.example                   # Exemplo de arquivo de variáveis de ambiente
├── docker-compose.yaml            # Configuração do Docker Compose para rodar o projeto localmente
├── Dockerfile                     # Dockerfile de produção
├── poetry.lock                    # Lock file do Poetry
├── pyproject.toml                 # Configuração do Poetry
├── requirements.txt               # Dependências de produção
└── README.md                      # Documentação
```

# Tabelas do banco de dados

- A tabela de `customers` conta com uma constraint em e-mail, perceba que eu **não** apliquei o `LOWER(email)`, pois isso é responsabilidade da entidade de `Customer`, de converter e-mails para lowercase, de forma que o índice criado com essa constraint sempre seja usado, agilizando consultas pelo campo e-mail. Analogamente, nenhuma tabela possui valores default, pois também é responsabilidade de cada entidade de negócio controlar isso
- A tabela de `products_cache` é a tabela de cache para os produtos, ela é atualizada automaticamente quando um cliente consulta ou favorita um produto. Adicionei o campo `fetched_at` que não aparece nas respostas da API, mas é usado internamente para controlar o tempo de vida dos dados no cache
- Por fim, a tabela `customer_favorite_products` é onde armazeno os produtos favoritos de cada cliente, ela possui uma PRIMARY KEY composta por `customer_id` e `product_id`, fazendo com que não seja possível favoritar o mesmo produto mais de uma vez por cliente

```sql
CREATE TABLE IF NOT EXISTS customers (
    id UUID PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL,
    CONSTRAINT "uq_customers_email" UNIQUE (email)
);

CREATE TABLE IF NOT EXISTS products_cache (
    id BIGINT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    image_url TEXT NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    review_rate DECIMAL(10, 2),
    review_count INT,
    fetched_at TIMESTAMPTZ NOT NULL
);

CREATE TABLE IF NOT EXISTS customer_favorite_products (
    customer_id UUID NOT NULL,
    product_id BIGINT NOT NULL,
    favorited_at TIMESTAMPTZ NOT NULL,
    PRIMARY KEY (customer_id, product_id),
    CONSTRAINT "fk_customerfavoriteproducts_customer"
        FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE CASCADE
);
```

# Como executar os testes e os linters

```bash
$ poetry run task test_unit # Roda todos os testes de unidade
$ poetry run task test_integration # Roda todos os testes de integração
$ poetry run task test # Roda toda a suite de testes
```

```bash
$ poetry run task lint # Roda todos os formatters e linters
```

```bash
$ poetry run task --list # Exibe mais informações sobre todos os comandos pré-definidos
```

# Possíveis próximos passos

- Na parte de autenticação, adicionar um sistema de `refresh token` e garantir a invalidação do token do usuário no sign out
- Implementar um sistema de `rate limiting` para proteger os endpoints de abusos e ataques
- No endpoint de listagem de clientes `/customers`, adicionar opções de filtragem para tornar a busca mais poderosa
- Com o apoio do `PGTune`, calibrar os parâmetros de configuração do `PostgreSQL` com base na infraestrutura de hardware do servidor (vCPU, RAM, storage, etc.), de forma que os recursos do banco sejam melhor utilizados
