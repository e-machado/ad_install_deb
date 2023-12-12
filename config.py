import os
import subprocess
import shutil

subprocess.run(['apt','update'])

# instalacao de pacotes necessarios para configuracao do sistema
subprocess.run(['apt','install','-y','vim','htop','gpm','gvfs','openssh-server','ocsinventory-agent','python3-pip','libsmbclient-dev','rdesktop','gitso','sssd','realmd','sssd-tools','libnss-sss','libpam-sss','adcli','samba-common-bin','oddjob','oddjob-mkhomedir','samba-common','samba','winbind','libnss-winbind','libpam-winbind','krb5-user','packagekit','gparted','libu2f-udev'])

# instalacao de pacotes da pasta .deb
for f in os.listdir('deb'):
    subprocess.run(['dpkg','-i','deb/'+f]) 

# instalacao de pacotes de icones
if os.path.exists('/usr/share/icons/Win11'):
        os.system(f"rm -rf /usr/share/icons/Win11")
if os.path.exists('/usr/share/icons/Win11-dark'):
        os.system(f"rm -rf /usr/share/icons/Win11-dark")
subprocess.run(['unzip','icon/*','-d','/usr/share/icons/']) 

# instalacao de papel de parede
shutil.copytree('wallpaper/','/usr/share/backgrounds/linuxmint', dirs_exist_ok=True) 
for root, dirs, files in os.walk('/usr/share/backgrounds/linuxmint'):
    for dire in dirs:
        dir_path = os.path.join(root, dire)
        os.chmod(dir_path, 0o777)
    for file in files:
        file_path = os.path.join(root, file)
        os.chmod(file_path, 0o777)


# configuração do tema e icones do sistema
shutil.copy2('icon/mint-artwork.gschema.override', '/usr/share/glib-2.0/schemas/mint-artwork.gschema.override')
subprocess.run(['glib-compile-schemas','/usr/share/glib-2.0/schemas/'])

# atualiza pacotes instalados do sistema
subprocess.run(['apt','update'])
subprocess.run(['apt','upgrade','-y'])


# instalacao de pacotes para rodar o script de logon
subprocess.run(['python3','-m','pip','install','impacket'])
subprocess.run(['python3','-m','pip','install','termcolor'])
subprocess.run(['python3','-m','pip','install','pysmbc'])

# adiciona maquina ao dominio
dominio = input("Domínio: ")
usuario = input("Usuário para adicionar a máquina no Domínio: ")

subprocess.run(['realm','join', dominio, '-U', usuario])

# permite criacao da pasta ao efetuar o login
subprocess.run(['pam-auth-update','--enable','mkhomedir'])

#função altera arquivo evitando duplicatas

def add_line_to_file(sed_par, line_content, file_path):
    # Verificar se a linha já existe no arquivo
    check_duplicate_command = f"grep -q '{line_content}' {file_path}"
    result = subprocess.run(check_duplicate_command, shell=True)

    # Se a linha não existir, adicionar a linha
    if result.returncode != 0:
        add_line_command = f"sed -i '{sed_par} {line_content}' {file_path}"
        subprocess.run(add_line_command, shell=True)
        print(f"Linha adicionada no arquivo {file_path}")
    else:
        print(f"A linha já existe no arquivo {file_path} e não será duplicada.")

# alteracao no arquivo de configuracao do SSSD e retira o nome do dominio na criacao da pasta do usuario
add_line_to_file(5, "default_domain_suffix = guarulhos.sp.gov.br", "/etc/sssd/sssd.conf")
add_line_to_file('$i', "ad_gpo_access_control = permissive", "/etc/sssd/sssd.conf")
subprocess.run(['sed','-i','s/@%d//g','/etc/sssd/sssd.conf']) 

# alteracao no arquivo smb.conf
subprocess.run(['sed','-i','s/workgroup = WORKGROUP/workgroup = GUARULHOS.SP.GOV.BR/g','/etc/samba/smb.conf'])

# configurando arquivo CUPS para nao detectar impressoras automaticamente e permitir DOMAIN USERS
subprocess.run(['sed','-i','56 s/^#//','/etc/cups/cups-browsed.conf'])
subprocess.run(['sed','-i','s/SystemGroup lpadmin root/SystemGroup lpadmin root "domain users"/g','/etc/cups/cups-files.conf'])

# permite que a tela de login entre com usuarios do AD


add_line_to_file('$i','greeter-show-manual-login=true','/etc/lightdm/lightdm.conf.d/70-linuxmint.conf')
add_line_to_file('$i','greeter-hide-users=true','/etc/lightdm/lightdm.conf.d/70-linuxmint.conf')
add_line_to_file('$i','session-cleanup-script=/etc/init.d/scriptlogoff','/etc/lightdm/lightdm.conf.d/70-linuxmint.conf')
shutil.copy2('greeter/slick-greeter.conf', '/etc/lightdm/slick-greeter.conf')

# montagem da pasta SISTEMAS$
subprocess.run(['mkdir','/etc/skel/.config/autostart'])
shutil.copy2('scripts/start.desktop','/etc/skel/.config/autostart/start.desktop')
subprocess.run(['chmod','755','/etc/skel/.config/autostart/start.desktop'])
shutil.copy2('scripts/scriptlogon','/etc/init.d/scriptlogon')
subprocess.run(['chmod','755','/etc/init.d/scriptlogon'])
shutil.copy2('scripts/scriptlogoff','/etc/init.d/scriptlogoff')
subprocess.run(['chmod','755','/etc/init.d/scriptlogoff'])

# retirar diferenças no registro da quebra de linha feito pelo Windows e pelo Linux
subprocess.run(['sed','-i','-e','s/\r$//','/etc/init.d/scriptlogon'])
subprocess.run(['sed','-i','-e','s/\r$//','/etc/init.d/scriptlogoff'])

# ativa permissao SUDO para tecnicos do HelpDesk
add_line_to_file('$i','"%sge06 - administradores guarux@guarulhos.sp.gov.br" ALL=(ALL) ALL','/etc/sudoers')

# remove pacotes que nao serao mais usados
subprocess.run(['apt','autoremove','-y'])

# reinicia o sistema
subprocess.run(['reboot']) 
