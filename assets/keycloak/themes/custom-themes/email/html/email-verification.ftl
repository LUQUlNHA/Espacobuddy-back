<!DOCTYPE html>
<html>
  <head>
    <meta charset="utf-8">
    <title>Verificação de Email - Espaço Buddy</title>
    <style>
      /* Estilos gerais para o email */
      body {
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
        background-color: #f2f4f6;
        margin: 0;
        padding: 0;
      }
      .container {
        max-width: 600px;
        margin: 30px auto;
        background: #ffffff;
        border-radius: 8px;
        overflow: hidden;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
      }
      .header {
        background: linear-gradient(135deg, #2c3e50, #3498db);
        color: #ffffff;
        text-align: center;
        padding: 20px;
      }
      .header h1 {
        margin: 0;
        font-size: 28px;
      }
      .content {
        padding: 30px 20px;
        color: #555555;
        line-height: 1.6;
      }
      .content p {
        margin: 0 0 20px;
      }
      .button {
        display: inline-block;
        background-color: #3498db;
        color: #ffffff !important;
        text-decoration: none;
        padding: 15px 25px;
        border-radius: 5px;
        font-weight: bold;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.15);
      }
      .footer {
        text-align: center;
        font-size: 12px;
        color: #999999;
        padding: 20px;
        background-color: #f2f4f6;
      }
    </style>
  </head>
  <body>
    <div class="container">
      <div class="header">
        <h1>Urban Eden</h1>
      </div>
      <div class="content">
        <p>Olá ${user.firstName! "usuário"},</p>
        <p>Obrigado por se registrar no <strong>Urban Eden</strong>!</p>
        <p>Para concluir seu registro, por favor, verifique seu endereço de e-mail clicando no botão abaixo:</p>
        <p style="text-align: center;">
          <a href="${link}" class="button">Verificar Email</a>
        </p>
        <#if linkExpiration??>
          <p>Este link expira em <strong>${linkExpiration} minutos</strong>.</p>
        <#else>
          <p>O tempo de expiração do link não está disponível.</p>
        </#if>
        <p>Se você não se registrou, por favor, ignore este e-mail.</p>
      </div>
      <div class="footer">
        <p>&copy; ${.now?string("yyyy")} Urban Eden. Todos os direitos reservados.</p>
      </div>
    </div>
  </body>
</html>
