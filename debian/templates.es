Template: apt-listchanges/frontend
Type: select
Choices: pager, xterm-pager, text, mail, none
Choices-es: paginador, paginador-xterm, texto, correo, ninguno
Default: pager
Description: How should changelogs be displayed with apt?
 apt-listchanges can display changelog entries in a number of different
 ways.
 .
 pager - Use your preferred pager
 .
 xterm-pager - Use your preferred pager in an xterm in the background
 .
 text  - Print changelogs to your terminal (without pausing)
 .
 mail  - Only send changelogs via mail
 .
 none  - Do not run automatically from apt
 .
 This setting can be overridden by a command-line option or an environment
 variable.  Note that you can still send a copy via mail with all of the
 frontends except 'none'.
Description-es: ¿Cómo quieres que se muestren las bitácoras con apt?
 apt-listchanges puede mostrar las bitácoras de varias maneras.
 .
 paginador - Usa tu paginador preferido
 .
 paginador-xterm - Usa tu paginador preferido sobre una xterm en el fondo
 .
 texto   - Imprime las bitácoras en tu terminal (sin hacer ninguna pausa)
 .
 correo  - Sólo envía las bitácoras por correo
 .
 ninguno - No ejecutar automáticamente desde apt
 .
 Puedes reemplazar esta configuración usando una opción en la línea de
 comandos o con una variable de entorno. Ten en cuenta que puedes mandar
 una copia por correo con todas las interfaces excepto "ninguno".

Template: apt-listchanges/email-address
Type: string
Default: root
Default-es: root
Description: To whom should apt-listchanges mail changelog entries?
 apt-listchanges can email a copy of displayed changelogs.  To what email
 address should they be sent?
 .
 Leave this empty if you do not want any email to be sent.
Description-es: ¿A quién debe enviar las bitácoras apt-listchanges?
 apt-listchanges puede enviar una copia de las bitácoras mostradas. ¿A qué
 dirección de correo quieres que sean enviadas?

Template: apt-listchanges/confirm
Type: boolean
Default: true
Description: Should apt-listchanges prompt for confirmation after displaying changelogs?
 After giving you a chance to display changelog entries, apt-listchanges
 can ask whether or not you would like to continue. This is useful when
 running from apt, as it gives you a chance to abort the upgrade if you see
 a change you do not want to apply (yet).
 .
 This setting does not apply to the 'mail' or 'none' frontends, and can be
 overridden with a command line option.
Description-es: ¿Debería apt-listchanges pedir confirmación después de mostrar las bitácoras?
 Después de darte la oportunidad de mostrar las bitácoras, apt-listchanges
 puede preguntar si quieres o no continuar. Ésto es útil cuando se ejecuta
 desde apt, ya que te da la oportunidad de abortar la actualización si ves
 algún cambio que no quieres aplicar (todavía).
 .
 Esta opción no afecta a las interfaces "mail" o "ninguno" y se puede
 reemplazar desde la línea de comandos.

Template: apt-listchanges/overwrite_etc_apt_listchanges_conf
Type: boolean
Default: true
Description: Should apt-listchanges overwrite your /etc/apt/listchanges.conf?
 apt-listchanges can configure all of the options in
 /etc/apt/listchanges.conf by asking you questions.  This file is read and
 processed every time apt-listchanges is run, and is used to set defaults. 
 All of the options can be overridden on the command line.
 .
 If you want to edit /etc/apt/listchanges.conf manually for whatever
 reason, answer "no" now.
Description-es: ¿Debería apt-listchanges sobreescribir /etc/apt/listchanges.conf?
 apt-listchanges puede configurar todas las opciones en
 /etc/apt/listchanges.conf haciéndote preguntas.  Este fichero es leído y
 procesado cada vez que se ejecuta apt-listchanges, y se usa para
 establecer opciones por defecto. Todas las opciones pueden reemplazarse en
 la línea de comandos.
 .
 Si quieres editar /etc/apt/listchanges.conf manualmente por alguna razón,
 contesta "no" ahora.

Template: apt-listchanges/save-seen
Type: boolean
Default: true
Description: Should apt-listchanges skip changelogs that have already been seen?
 apt-listchanges has the capability to keep track of which changelog
 entries have already been displayed, and to skip them in future
 invocations. This is useful, for example, when retrying an upgrade.
Description-es: Debería apt-listchanges ignorar los cambios que ya se han visto?
 apt-listchanges puede hacer un seguimiento de las bitácoras que ya se han
 mostrado anteriormente, e ignorarlos en futuras ejecuciones. Esto
 es útil, por ejemplo, cuando se reintenta una actualización.
