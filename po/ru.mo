��          �   %   �      0    1  ,   4  \   a  9   �  @   �  K   9  C   �  �   �  p   t  6   �      L     e   l  �   �  ?   �  %   �  )    	      *	  <   K	     �	  ;   �	  ?   �	  ;   	
  a  E
  �   �  6   �  q   �  =   L  L   �  ]   �  T   5  �   �  �   [  @   �    &  P   3  �   �  �     X   �  7     1   D  -   v  V   �     �  G      ;   H  C   �                   	                                          
                                                                  After giving you a chance to display changelog entries, apt-listchanges can ask whether or not you would like to continue. This is useful when running from apt, as it gives you a chance to abort the upgrade if you see a change you do not want to apply (yet). How should changelogs be displayed with apt? If you want to edit /etc/apt/listchanges.conf manually for whatever reason, answer "no" now. Leave this empty if you do not want any email to be sent. Should apt-listchanges overwrite your /etc/apt/listchanges.conf? Should apt-listchanges prompt for confirmation after displaying changelogs? Should apt-listchanges skip changelogs that have already been seen? This setting can be overridden by a command-line option or an environment variable.  Note that you can still send a copy via mail with all of the frontends except 'none'. This setting does not apply to the 'mail' or 'none' frontends, and can be overridden with a command line option. To whom should apt-listchanges mail changelog entries? apt-listchanges can configure all of the options in /etc/apt/listchanges.conf by asking you questions.  This file is read and processed every time apt-listchanges is run, and is used to set defaults.  All of the options can be overridden on the command line. apt-listchanges can display changelog entries in a number of different ways. apt-listchanges can email a copy of displayed changelogs.  To what email address should they be sent? apt-listchanges has the capability to keep track of which changelog entries have already been displayed, and to skip them in future invocations. This is useful, for example, when retrying an upgrade. browser - Display HTML-formatted changelogs using a web browser mail  - Only send changelogs via mail none  - Do not run automatically from apt pager - Use your preferred pager pager, browser, xterm-pager, xterm-browser, text, mail, none root text  - Print changelogs to your terminal (without pausing) xterm-browser - Like browser, but in an xterm in the background xterm-pager - Like pager, but in an xterm in the background Project-Id-Version: apt-listchanges_2.42
POT-Creation-Date: 2002-11-17 00:23-0500
PO-Revision-Date: 2003-10-05 15:35+0600
Last-Translator: Ilgiz Kalmetev <translator@ilgiz.pp.ru>
Language-Team: russian <debian-russian@lists.debian.org>
MIME-Version: 1.0
Content-Type: text/plain; charset=KOI8-R
Content-Transfer-Encoding: 8bit
X-Generator: KBabel 1.0.1
 ����� ����������� ������� ��������� apt-listchanges ����� �������� ����� �� ���������� ��� ���. ��� ������� ��� ������� �� apt, ��� ��� ��������� �������� ���������� ������, ���� �� �������, ��� � ������ ��������� (����) �� ������������ ��� ���������. ����� ������� apt ������ ���������� ������� ���������? ���� �� �����-�� ������� �� ������ ��������������� ���� /etc/apt/listchanges.conf �������, �������� ������ "���". �������� ���� ������, ���� ������ �� ������ ���������� �����. ������ �� apt-listchanges �������������� ��� ���� /etc/apt/listchanges.conf? ������ �� apt-listchanges �������� ������� ������������� ����� ����������� ������� ���������? ������ �� apt-listchanges ���������� ������� ���������, ������� ��� ���������������? ��� ��������� ����� ���� ��������� ������ ��������� ������ ��� ���������� ���������. �������� ��������, ��� �� �� �������� ������ �������� ����� �� ����� ��� ����� �������� �����������, ����� "�� ����������". ��� ����� �� ��������� ��� ������������� ������ ����������� "�� �����" � "�� ����������", � ����� ���� ��������� ������ ��������� ������. ���� apt-listchanges ������ ���������� ������ ������� ���������? apt-listchanges ����� ��������� ��� ����� � ����� /etc/apt/listchanges.conf, ������� ��� �������. ���� ���� �������� � �������������� ��� ������ ������� apt-listchanges � ������������ ��� ��������� ���������. ��� ��������� ����� ���� �������������� � ��������� ������. apt-listchanges ����� ���������� ������ ������� ��������� ����������� ���������. apt-listchanges ����� ���������� ����� ������������ �������� ��������� �� ����������� �����. ���� ������ ���� ���������� ��� �����? apt-listchanges ����� ����������� �����������, ����� ������ ������� ��������� �� ��� ���������, � ���������� �� � �������. ��� �������, ��������, ��� ����������� �������. ������� - ���������� ������� ���������, ����������������� � HTML, � ������� ���-�������� �� ����� - ������ ���������� ������� ��������� �� ����� �� ���������� - �� ��������� �� apt ������������� ����������� - �������������� ���� ����������� �����������, �������, xterm-�����������, xterm-�������, �����, �� �����, �� ���������� root ����� - �������� ������� ��������� �� ����� ������ ��������� (��� ����) xterm-������� - ���������� ������ ��������, �� � ���� xterm xterm-����������� - ���������� ������ ������������, �� � ���� xterm 