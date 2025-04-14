Olá ${user.firstName! "usuário"},

Você solicitou a redefinição da senha para sua conta no Espaço Buddy.

Para redefinir sua senha, copie e cole o seguinte link em seu navegador:
${link}

<#if linkExpiration??>
Este link expira em ${linkExpiration} minutos.
<#else>
O tempo de expiração do link não está disponível.
</#if>

Se você não solicitou a redefinição de senha, ignore este e-mail.

Atenciosamente,
Urban Eden
