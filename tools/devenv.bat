@echo off
rem Sets up Clang + the VS 2022 Build Tools libraries, CMake and Ninja, then runs the given command.
call "C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\VC\Auxiliary\Build\vcvars64.bat" >nul 2>nul
set "PATH=C:\Program Files\LLVM\bin;%PATH%"
%*
