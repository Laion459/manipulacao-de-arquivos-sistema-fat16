import os
import struct
import datetime

# Função para listar o conteúdo do diretório raiz
def listar_conteudo(diretorio_raiz):
    with open(diretorio_raiz, 'rb') as file:
        file.seek(512)  # Ignorar o boot sector
        for _ in range(224):  # Número de entradas no diretório raiz em um disco FAT16 de tamanho padrão
            entry = file.read(32)  # Cada entrada tem 32 bytes
            if entry[0] == 0x00:  # Entrada vazia
                continue
            if entry[0] == 0xE5:  # Entrada apagada
                continue
            name = entry[:8].decode('utf-8', errors='replace').strip()
            extension = entry[8:11].decode('utf-8', errors='replace').strip()
            size = struct.unpack('<I', entry[28:32])[0]
            print(f"Nome: {name}.{extension}, Tamanho: {size} bytes")

# Função para listar o conteúdo de um arquivo
def listar_conteudo_arquivo(nome_arquivo, diretorio_raiz):
    with open(diretorio_raiz, 'rb') as file:
        file.seek(512)  # Ignorar o boot sector
        while True:
            entry = file.read(32)
            if entry[0] == 0x00:  # Fim do diretório raiz
                break
            if entry[0] == 0xE5:  # Entrada apagada
                continue
            if entry[:11] == nome_arquivo.encode('utf-8').ljust(11, b'\x20'):
                start_cluster = struct.unpack('<H', entry[26:28])[0]
                file.seek((start_cluster - 2) * 512)  # Ir para o início do arquivo
                conteudo = file.read()
                print(conteudo.decode('utf-8', errors='replace'))  # Exibir conteúdo do arquivo
                break
        else:
            print("Arquivo não encontrado")

# Função para exibir os atributos de um arquivo
def exibir_atributos(nome_arquivo, diretorio_raiz):
    with open(diretorio_raiz, 'rb') as file:
        file.seek(512)  # Ignorar o boot sector
        while True:
            entry = file.read(32)
            if entry[0] == 0x00:  # Fim do diretório raiz
                break
            if entry[0] == 0xE5:  # Entrada apagada
                continue
            if entry[:11] == nome_arquivo.encode('utf-8').ljust(11, b'\x20'):
                attributes = struct.unpack('<B', entry[11:12])[0]
                read_only = bool(attributes & 0x01)
                hidden = bool(attributes & 0x02)
                system_file = bool(attributes & 0x04)
                create_time = datetime.datetime.fromtimestamp(struct.unpack('<H', entry[14:16])[0])
                last_modified_time = datetime.datetime.fromtimestamp(struct.unpack('<H', entry[22:24])[0])
                print(f"Nome: {nome_arquivo}, Atributos: ")
                print(f"Somente Leitura: {read_only}")
                print(f"Oculto: {hidden}")
                print(f"Arquivo de Sistema: {system_file}")
                print(f"Data/Hora de Criação: {create_time}")
                print(f"Data/Hora da Última Modificação: {last_modified_time}")
                break
        else:
            print("Arquivo não encontrado")

# Função para renomear um arquivo
def renomear_arquivo(nome_atual, novo_nome, diretorio_raiz):
    with open(diretorio_raiz, 'r+b') as file:
        file.seek(512)  # Ignorar o boot sector
        while True:
            entry = file.read(32)
            if entry[0] == 0x00:  # Fim do diretório raiz
                break
            if entry[0] == 0xE5:  # Entrada apagada
                continue
            if entry[:11] == nome_atual.encode('utf-8').ljust(11, b'\x20'):
                file.seek(file.tell() - 32)  # Voltar para o início da entrada
                file.write(novo_nome.encode('utf-8').ljust(11, b'\x20'))  # Escrever o novo nome
                break
        else:
            print("Arquivo não encontrado")

# Função para apagar um arquivo
def apagar_arquivo(nome_arquivo, diretorio_raiz):
    with open(diretorio_raiz, 'r+b') as file:
        file.seek(512)  # Ignorar o boot sector
        while True:
            entry = file.read(32)
            if entry[0] == 0x00:  # Fim do diretório raiz
                break
            if entry[0] == 0xE5:  # Entrada apagada
                continue
            if entry[:11] == nome_arquivo.encode('utf-8').ljust(11, b'\x20'):
                file.seek(file.tell() - 32)  # Voltar para o início da entrada
                file.write(b'\xE5')  # Marcar a entrada como apagada
                break
        else:
            print("Arquivo não encontrado")

# Função para exibir o menu
def exibir_menu():
    print("\nMenu:")
    print("1. Listar conteúdo do diretório raiz")
    print("2. Listar conteúdo de um arquivo")
    print("3. Exibir atributos de um arquivo")
    print("4. Renomear um arquivo")
    print("5. Apagar um arquivo")
    print("0. Sair")

# Função principal
if __name__ == "__main__":
    diretorio_raiz = "disco1.img"  # Caminho para a imagem do disco FAT16

    while True:
        exibir_menu()
        opcao = input("Escolha uma opção: ")

        if opcao == "1":
            print("\nConteúdo do diretório raiz:")
            listar_conteudo(diretorio_raiz)
        elif opcao == "2":
            nome_arquivo = input("Digite o nome do arquivo: ")
            print(f"\nConteúdo do arquivo {nome_arquivo}:")
            listar_conteudo_arquivo(nome_arquivo, diretorio_raiz)
        elif opcao == "3":
            nome_arquivo = input("Digite o nome do arquivo: ")
            print(f"\nAtributos do arquivo {nome_arquivo}:")
            exibir_atributos(nome_arquivo, diretorio_raiz)
        elif opcao == "4":
            nome_atual = input("Digite o nome atual do arquivo: ")
            novo_nome = input("Digite o novo nome do arquivo: ")
            renomear_arquivo(nome_atual, novo_nome, diretorio_raiz)
            print(f"\nRenomeando arquivo {nome_atual} para {novo_nome}:")
        elif opcao == "5":
            nome_arquivo = input("Digite o nome do arquivo a ser apagado: ")
            apagar_arquivo(nome_arquivo, diretorio_raiz)
            print(f"\nApagando arquivo {nome_arquivo}:")
        elif opcao == "0":
            print("Saindo...")
            break
        else:
            print("Opção inválida. Por favor, escolha uma opção válida.")
