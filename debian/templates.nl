Template: apt-listchanges/email-address
Type: string
Description: To whom should apt-listchanges mail changelog entries?
 You have chosen to have changelog entries sent via email.  To what email
 address should they be sent?
Description-nl: Naar wie wilt u dat apt-listchanges de wijzigingen stuurt?
 U heeft er voor gekozen om de wijzigingen via email te versturen. Naar
 welk emailadres wilt u deze wijzigingen versturen?

Template: apt-listchanges/frontend
Type: select
Choices: pager, xterm-pager, newt, text, mail
Choices-nl: pager, xterm-pager, newt, text, mail
Description: How should changelogs be displayed by default?
 apt-listchanges can display changelog entries in a number of different
 ways.
 .
 pager - Use your preferred pager
 .
 xterm-pager - Use your preferred pager in an xterm in the background
 .
 newt - Use a terminal graphics interface, using text-mode windows (you
 will need to install libnewt-perl to use this)
 .
 text  - Print changelogs to your terminal (without pausing)
 .
 mail  - Send changelogs via email (you will be prompted for an address)
 .
 This setting can be overridden by a command-line option.
Description-nl: Hoe wilt u de wijzigingen standaard zien?
 apt-listchanges kan de wijzigingen op een aantal verschillende manieren
 tonen.
 .
 pager - Gebruik uw favoriete pager
 .
 xterm-pager - Gebruik uw favoriete pager in een xterm in de achtergrond
 .
 newt - Gebruik een grafische terminal interface op basis van textmode
 schermen (u heeft libnewt-perl nodig om dit te gebruiken)
 .
 text - Print wijzigingen op uw terminal (zonder pauzes)
 .
 mail - Stuur wijzigingen via email (u wordt gevraagd een emailadres op
 te geven)
 .
 Deze instelling kan overschreven worden door een commandoregel optie.

Template: apt-listchanges/apt-hook-p
Type: boolean
Description: Should apt-listchanges be automatically run by apt?
 One way to use apt-listchanges is to configure apt to run apt-listchanges
 on packages that have been downloaded for installation or upgrade.  This
 way, each time you perform an installation or upgrade using apt,
 apt-listchanges will show you the changes that are about to be made to
 your system.
 .
 I can perform this configuration for you if you like.  Since you can also
 run apt-listchanges manually on .deb archives, this step is optional.
Description-nl: Wilt u apt-listchanges automatisch laten draaien door apt?
 Een manier om apt-listchanges te gebruiken is door apt zodanig te
 configureren dat apt-listchanges uitgevoerd wordt nadat pakketen zijn
 gedownload voor installatie of upgrade. Op deze manier zult u elke keer
 dat u iets installeert of upgrade met behulp van apt door
 apt-listchanges op de hoogte gebracht worden van de wijzigingen die
 zullen worden aangebracht aan uw systeem.
 .
 Ik kan deze instelling voor u maken als u dat wilt. Daar u
 apt-listchanges ook zelf kunt uitvoeren op .deb pakketen is deze stap
 optioneel.

Template: apt-listchanges/confirm
Type: boolean
Description: Should apt-listchanges prompt for confirmation after displaying changelogs?
 After giving you a chance to display changelog entries, apt-listchanges
 can ask whether or not you would like to continue. This is useful when
 running from apt, as it gives you a chance to abort the upgrade if you
 see a change you do not want to apply (yet).
 .
 This setting only applies when running from apt.  Otherwise, it can be
 requested with a command line option.
Description-nl: Wilt u apt-listchanges laten vragen om bevestiging nadat de wijzigingen zijn getoond?
 Nadat apt-listchanges u de wijzigingen heeft laten zien, kan
 apt-listchanges u vragen of u door wilt gaan of niet. Dit kan handig
 zijn als u apt-listchanges vanuit apt laat uitvoeren daar u hiermee de
 kans krijgt een upgrade af te gelasten als u een wijziging ziet die u
 (nog) niet wilt doorvoeren.
 .
 De instelling is alleen van toepassing als u apt-listchanges uitvoert
 vanuit apt. U kunt dit ook instellen met behulp van een commandoregel
 optie.

Template: apt-listchanges/overwrite_etc_apt_listchanges_conf
Type: boolean
Description: Should apt-listchanges overwrite your /etc/apt/listchanges.conf?
 apt-listchanges can configure all of the options in
 /etc/apt/listchanges.conf by asking you questions.  This file is read and
 processed every time apt-listchanges is run, and is used to set defaults.
 All of the options can be overridden on the command line.
 .
 If you want to edit /etc/apt/listchanges.conf manually for whatever
 reason, answer "no" now.
Description-nl: Wilt u apt-listchanges /etc/apt/listchanges.conf laten overschrijven?
 apt-listchanges kan alle opties in /etc/apt/listchanges.conf voor u
 instellen door u een aantal vragen te stellen. Dit bestand wordt elke
 keer dat u apt-listchanges uitvoert gelezen en verwerkt; ze wordt
 gebruikt om standaardinstellingen mee vast te stellen. Alle opties
 kunnen via de commandoregel overschreven worden.
 .
 Indien u, om welke reden dan ook, /etc/apt/listchanges.conf handmatig
 wilt aanpassen, antwoord dan Nee.
