# Autograd
Autograd is a simple autograder to extract and compile code files from PTI classes.

## Language Support
- C++
- Python 2 and 3
- Fortran

## Requirements
- Python 3
- Compilers suitable for the language


## Usage
1. Create a folder named `files`
2. Extract collective zip files downloaded from moodle onto the folder created before
3. Create input files with the name `inputXY.txt` with X is the problem number and Y is the sequence of inputs
3. Run `autograder.py`

## Further Versions
- Move file located in subfolders when extracting the files and also detecting on what to do when encountering multi-zipped files
- Add option to compile/extract again or not
- Add more language support (C, Pascal)