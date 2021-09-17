@echo off
REM This file requires first to set a file %USERPROFILE%/.pypirc
REM -------------
REM [distutils]
  REM index-servers =
    REM pypi
    REM unpackai

REM [pypi]
  REM username = __token__
  REM password = # either a user-scoped token or a project-scoped token you want to set as the default

REM [unpackai]
  REM repository = https://upload.pypi.org/legacy/
  REM username = __token__
  REM password = # a project token 
REM -------------
@echo on

del /Q dist

@echo.
@pause
@echo.

python setup.py sdist bdist_wheel

@echo.
@pause
@echo.

twine check dist/*

@echo.
@pause
@echo.

twine upload --repository unpackai dist

@echo.
@pause
@echo.
