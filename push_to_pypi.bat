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

@echo Cleaning Dist directory
del /Q dist

@echo.
@pause
@echo.

@echo Building
python setup.py sdist bdist_wheel

@echo.
@pause
@echo.

@echo Checking the build
twine check dist/*

@echo.
@pause
@echo.

@echo Pushing to TestPypi
twine upload --repository-url https://test.pypi.org/legacy/ dist/*

@echo.
@pause
@echo.

@echo Pushing to Pypi for real
twine upload --repository unpackai dist/*

@echo.
@pause
@echo.
