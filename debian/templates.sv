Template: apt-listchanges/apt-hook-p
Type: boolean
Default: true
Description: Should apt-listchanges be automatically run by apt?
 One way to use apt-listchanges is to configure apt to run apt-listchanges on
 packages that have been downloaded for installation or upgrade.  This way,
 each time you perform an installation or upgrade using apt,
 apt-listchanges will show you the changes that are about to be made
 to your system.
 .
 I can perform this configuration for you if you like.  Since you can also run
 apt-listchanges manually on .deb archives, this step is optional.
Description-sv: Ska apt-listchanges köras automatiskt av apt?
 Ett sätt att använda apt-listchanges är att konfigurera apt att köra
 apt-listchanges på paket som har laddats ner för installation eller
 uppgradering. Varje gång du utför en installation eller uppgradering kommer
 då apt-listchanges att visa alla ändringar som är på väg att göras på ditt
 system.
 .
 Jag kan utföra denna konfiguration om du vill. Eftersom du också kan köra
 apt-listchanges manuellt på .deb arkiv så är detta steg frivilligt.

Template: apt-listchanges/frontend
Type: select
Choices: pager, xterm-pager, newt, text, mail
Default: pager
Description: How should changelogs be displayed by default?
 apt-listchanges can display changelog entries in a number of different ways.
 .
 pager - Use your preferred pager
 .
 xterm-pager - Use your preferred pager in an xterm in the background
 .
 newt - Use a terminal graphics interface, using text-mode windows
 (you will need to install libnewt-perl to use this)
 .
 text  - Print changelogs to your terminal (without pausing)
 .
 mail  - Send changelogs via email (you will be prompted for an address)
 .
 This setting can be overridden by a command-line option.
Choices-sv: pager, xterm-pager, newt, text, post
Description-sv: Hur ska förändringsloggar visas som standard?
 apt-listchanges kan visa poster från förändringloggar på flera sätt.
 .
 pager - Använd din föredragna "pager"
 .
 xterm-pager - Använd din föredragna "pager" i en xterm som körs i bakgrunden
 .
 newt - Använd ett grafiskt läge för terminalen, som använder fönster i text-läge
 (du måste installera libnewt-perl för att använda detta)
 .
 text - Skriv ut förändringsloggar till din terminal (utan att pausa)
 .
 post - Skicka förändringsloggar via e-post (en adress kommer att efterfrågas)
 .
 Denna inställning kan åsidosättas genom en flagga på kommandoraden.

Template: apt-listchanges/email-address
Type: string
Default: root
Description: To whom should apt-listchanges mail changelog entries?
 You have chosen to have changelog entries sent via email.  To what email
 address should they be sent?
Description-sv: Till vem ska apt-listchanges skicka poster från förändringsloggar?
 Du har valt att få poster från förändringsloggar skickade via e-post. Till
 vilken e-post adress ska dessa skickas?

Template: apt-listchanges/confirm
Type: boolean
Default: true
Description: Should apt-listchanges prompt for confirmation after displaying changelogs?
 After giving you a chance to display changelog entries,
 apt-listchanges can ask whether or not you would like to continue.
 This is useful when running from apt, as it gives you a chance to
 abort the upgrade if you see a change you do not want to apply (yet).
 .
 This setting only applies when running from apt.  Otherwise, it can be
 requested with a command line option.
Description-sv: Ska apt-listchanges begära konfirmation efter att ha visat förändringsloggar?
 Efter att ha gett dig en möjlighet att visa poster från förändringsloggar
 kan apt-listchanges fråga dig om du vill fortsätta. Detta är användbart
 när den körs från apt eftersom det ger dig en möjlighet att avbryta
 uppgradering om du ser en förändring som du inte vill ska ske (ännu.)

Template: apt-listchanges/overwrite_etc_apt_listchanges_conf
Type: boolean
Default: true
Description: Should apt-listchanges overwrite your /etc/apt/listchanges.conf?
 apt-listchanges can configure all of the options in
 /etc/apt/listchanges.conf by asking you questions.  This file is read
 and processed every time apt-listchanges is run, and is used to set
 defaults.  All of the options can be overridden on the command line.
 .
 If you want to edit /etc/apt/listchanges.conf manually for whatever
 reason, answer "no" now.
Description-sv: Ska apt-listchanges skriva över din /etc/apt/listchanges.conf
 apt-listchanges kan konfigurera alla alternativ i /etc/apt/listchanges.conf
 genom att fråga dig frågor. Denna fil läses och behandlas vara gång
 apt-listchanges körs, och den används för att ställa in normalvärden.
 Alla alternativen kan åsidosättas på kommandoraden.
