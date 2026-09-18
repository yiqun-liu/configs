@echo off
rem mate — Windows shim: runs mate.py (same directory) with the PATH python.
rem
rem L1  @echo off            do not echo batch commands to the console; the
rem                          leading @ silences this line itself.
rem L3  python ...           launch mate.py via the Python on PATH. %~dp0
rem                          expands to this shim's drive+directory, so
rem                          mate.py is found next to it wherever the shim
rem                          is invoked from; %* forwards all arguments.
python "%~dp0mate.py" %*
