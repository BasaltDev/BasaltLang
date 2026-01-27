# Basalt
## A rock-solid programming language
Basalt is a lightweight programming language built by 1 person over the course of ~3-4 days designed for simplicity and ease-of-use (don't quote me on that) written in Python.

## 🔥 Key Features:
- **Dynamic Typing**: In Basalt, unlike many other programming languages and like many other pr``ogramming languages, you don't have to state the type of your variable.
- **Default Immutability**: A lot of times, you may have realized in your broken code that you accidentally overwrote a variable's value. In Basalt, we make it easier for you. ```basalt
let [var] = [val]``` makes your variable immutable. And don't worry, we added keywords for mutable variables and to make variables mutable/immutable.
- **Comma-Less Syntax**: Are you annoyed by constantly typing commas everywhere in your code? (probably not) Well, Basalt removes them for you. Commas are useless, anyway.
- **Compound Data Types**: Basalt supports compound data types such as *lists* (```let list_object = ["a" "b" "c"]```) and *dictionaries* (```let dict_object = {"a": "b" "c": "d"}```), and it even includes custom methods for lists and dictionaries.
- **Context-Aware File I/O**: I'd like to bet that at least one or two newly-developed languages struggle with context-aware file I/O. You want to write to a file in ```C:\Directory1``` but instead it writes to a file in ```C:\LanguageDirectory```. Basalt doesn't struggle with these small issues.

## 🛠️ Installation:
(DISCLAIMER: Basalt.exe is only available for the Windows operating system and you may need to download the original Python source code if you're on a different OS)
1. Download ```basalt.exe``` from the Releases tab (or download the source code, we don't judge)
2. Add to **PATH**: Move the exe to a folder (e.g. ```C:\Basalt```) and add that folder to your System Environment Variables
3. **Verify**: Open a terminal and type:
    ```basalt --version```
If it successfully installed, then congrats! You can now write scripts in Basalt.

## 📜 Running your first script:
To run a Basalt file, use the ```-r``` flag:
```basalt -r your_script.basalt```

## 🏗️ Technical Specs:
- Written In: *Python*
- Size: 9mb (source code is ~70kb)
- Core logic: Hand-written lexer and (questionable but working) interpreter

## ⚠️ DISCLAIMER:
- Don't expect the interpreter to work all the time. It may or may not break at times.

## 🔑 License
This project is licensed under the MIT license (see the LICENSE file for details)

Created by **BasaltDev**.
