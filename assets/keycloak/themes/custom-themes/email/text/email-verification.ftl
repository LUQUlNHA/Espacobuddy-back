Olá ${user.firstName! "usuário"},

Obrigado por se registrar no Espaço Buddy!

Para concluir seu registro, por favor, verifique seu endereço de e-mail clicando no link abaixo:
${link}

<#if linkExpiration??>
Este link expira em ${linkExpiration} minutos.
<#else>
O tempo de expiração do link não está disponível.
</#if>

Se você não se registrou, por favor, ignore este e-mail.

Atenciosamente,
Urban Eden
