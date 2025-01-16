# Cool Compiler
A compiler that targets x86_64 Linux architecture for the [Classroom Object Oriented Language](https://theory.stanford.edu/~aiken/software/cool/cool-manual.pdf) (Cool). Given a valid .cl file, a .s file is generated that can be executed using gcc.

## Start
To compile:

`python main.py <file.cl>`

`gcc -no-pie file.S -o file`

`./myfile`
