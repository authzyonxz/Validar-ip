# 🤖 Proxy Bot — Atualização de IP

Bot do Telegram para atualização de IP das keys do proxy.

## 📋 Funcionalidades

- Consulta o IP atual de uma key
- Solicita o novo IP ao usuário
- Exibe confirmação antes de aplicar a mudança
- Chama a API de atualização e retorna o resultado
- Após sucesso, exibe link do canal oficial do WhatsApp

## 🚀 Deploy na Railway

### 1. Faça o upload do projeto

Suba a pasta do projeto no GitHub ou faça o deploy direto pelo CLI da Railway.

### 2. Configure as variáveis de ambiente

No painel da Railway, vá em **Variables** e adicione:

| Variável     | Valor                                          |
|--------------|------------------------------------------------|
| `BOT_TOKEN`  | Token do seu bot (obtido no @BotFather)        |
| `API_BASE`   | `http://212.227.7.153:9945`                    |
| `MASTER_KEY` | Sua chave mestra da API                        |

### 3. Deploy

A Railway detectará automaticamente o `Procfile` e iniciará o bot com:

```
python bot.py
```

## 🔄 Fluxo do Bot

```
/start
  └─> Solicita a KEY
        └─> Consulta IP atual via /check
              └─> Solicita o novo IP
                    └─> Exibe confirmação (botões: ✅ Confirmar / ❌ Cancelar)
                          ├─> Confirmar → Chama /update → Exibe resultado + link WhatsApp
                          └─> Cancelar → Cancela operação
```

## 📡 API utilizada

- **Check:** `GET /check?key=MASTER&generated_key=KEY`
- **Update:** `GET /update?key=MASTER&generated_key=KEY&new_ip=NOVO_IP`
