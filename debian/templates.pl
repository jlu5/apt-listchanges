Template: apt-listchanges/email-address
Type: string
Default: root
Description: To whom should apt-listchanges mail changelog entries?
 apt-listchanges can email a copy of displayed changelogs.  To what email
 address should they be sent?
 .
 Leave this empty if you do not want any email to be sent.
Description-pl: Do kogo apt-listchanges ma wysy³aæ dzienniki zmian?
 apt-listchanges mo¿e wysy³aæ kopie wy¶wietlanych dzienników zmian
 poczt± elektroniczn±. Pod jaki adres maj± byæ wysy³ane?
 .
 Je¶li listy nie powinny byæ wysy³ane nale¿y pozostawiæ to pole puste.

Template: apt-listchanges/frontend
Type: select
Choices: pager, browser, xterm-pager, xterm-browser, text, mail, none
Choices-pl: pager, przegl±darka, pager w xtermie, przegl±darka w xtermie, tekst, poczta, nic
Default: pager
Description: How should changelogs be displayed with apt?
 apt-listchanges can display changelog entries in a number of different
 ways.
 .
 pager - Use your preferred pager
 .
 browser - Display HTML-formatted changelogs using a web browser
 .
 xterm-pager - Like pager, but in an xterm in the background
 .
 xterm-browser - Like browser, but in an xterm in the background
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
Description-pl: Jak maj± byæ wy¶wietlane dzienniki zmian gdy u¿ywany jest apt?
 apt-listchanges mo¿e wy¶wietlaæ dzienniki zmian na ró¿ne sposoby.
 .
 pager - u¿ywa preferowanego programu stronicuj±cego (pagera)
 .
 przegl±darka - wy¶wietla dzienniki skonwertowane do HTML w przegl±darce
 .
 pager w xtermie - pager uruchomiony w tle w emulatorze terminala
 .
 przegl±darka w xtermie - przegl±darka uruchomiona w tle w emulatorze terminala
 .
 tekst - wypisuje dzienniki zmian na terminalu (bez stronicowania)
 .
 poczta - wy³±cznie wysy³a dzienniki poczt± elektroniczn±
 .
 nic - apt-listchanges nie jest uruchamiany automatycznie gdy uzywany jest apt
 .
 To ustawienie mo¿na przes³oniæ parametrem linii poleceñ lub zmienn± ¶rodowiska.
 Ka¿da metoda oprócz "nic" pozwala na wysy³anie kopii dzienników zmian poczt±.

Template: apt-listchanges/save-seen
Type: boolean
Default: true
Description: Should apt-listchanges skip changelogs that have already been seen?
 apt-listchanges has the capability to keep track of which changelog
 entries have already been displayed, and to skip them in future
 invocations. This is useful, for example, when retrying an upgrade.
Description-pl: Czy apt-listchanges ma pomijaæ wpisy ju¿ wcze¶niej wy¶wietlone?
 apt-listchanges mo¿e ¶ledziæ, które wpisy w dziennikach zmian zosta³y
 wcze¶niej wy¶wietlone i pomijaæ je przy kolejnych wywo³aniach.
 Jest to u¿yteczne, na przyk³ad, przy wznawianiu uaktualnienia.

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
Description-pl: Czy pytaæ o potwierdzenie po wy¶wietleniu dzienników zmian?
 Po wy¶wietleniu dzienników zmian apt-listchanges mo¿e pytaæ o kontynuacjê
 dzia³ania.
 Jest to u¿yteczne gdy apt-listchanges jest uruchamiany przez apt, gdy¿ daje
 mo¿liwo¶æ przerwania uaktualniania w przypadku zauwa¿enia zmian, których
 nie chce siê (na razie) wprowadzaæ.
 .
 To ustawienie nie dotyczy metod "poczta" i "nic". Mo¿e byæ ono przes³oniête
 parametrem linii poleceñ.

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
Description-pl: Czy nadpisywaæ plik /etc/apt/listchanges.conf?
 apt-listchanges mo¿e skonfigurowaæ wszystkie swoje opcje zapisywane
 w /etc/apt/listchanges.conf zadaj±c pytania. Plik ten jest odczytywany
 przy ka¿dym uruchomieniu apt-listchanges i u¿ywany do ustalenia domy¶lnych
 warto¶ci opcji, jednak wszystkie opcje mog± byæ ustalone z linii poleceñ.
 .
 Je¶li z jakich¶ powodów preferowana jest rêczna edycja pliku
 /etc/apt/listchanges.conf nale¿y odpowiedzieæ "nie".
