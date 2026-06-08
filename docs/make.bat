@ECHO OFF

set SPHINXBUILD=python -m sphinx
set SOURCEDIR=.
set BUILDDIR=_build

if "%1" == "" goto help

%SPHINXBUILD% -b %1 %SOURCEDIR% %BUILDDIR%/%1
goto end

:help
%SPHINXBUILD% -M help %SOURCEDIR% %BUILDDIR%

:end
