import subprocess

def remove_from_domain(domain, username):
    # Desconectar da máquina do domínio
    subprocess.run(['realm', 'leave', '--user', username])

def change_hostname(new_hostname):
    # Alterar o nome da máquina nos arquivos /etc/hostname e /etc/hosts
    with open('/etc/hostname', 'w') as hostname_file:
        hostname_file.write(new_hostname)

    with open('/etc/hosts', 'r') as hosts_file:
        hosts_lines = hosts_file.readlines()

    with open('/etc/hosts', 'w') as hosts_file:
        for line in hosts_lines:
            if line.startswith('127.0.1.1'):
                hosts_file.write(f'127.0.1.1\t{new_hostname}\n')
            else:
                hosts_file.write(line)

    subprocess.run(['hostname',new_hostname])

def join_domain(domain, username):
    # Reingressar no domínio usando realm join
    subprocess.run(['realm', 'join', '--user', username, domain])

def main():
    
    print("ATENÇÂO: remova a conta do computador no Active Directory agora!!!")
    # Solicitar informações do usuário
    new_hostname = input("Digite o novo nome da máquina: ")
    if len(new_hostname) > 15:
        print("O nome da máquina não pode ter mais de 15 caracteres.")
        return
    domain = input("Digite o nome do domínio: ")
    username = input("Digite o nome do usuário para ingressar no domínio: ")

    try:
        # Remover a máquina do domínio
        remove_from_domain(domain, username)

        # Alterar o nome da máquina nos arquivos /etc/hostname e /etc/hosts
        change_hostname(new_hostname)

        # Reingressar no domínio
        join_domain(domain, username)

        print("Operações concluídas com sucesso! Por favor reinicie a máquina")
    except Exception as e:
        print(f"Ocorreu um erro: {e}")

if __name__ == "__main__":
    main()

