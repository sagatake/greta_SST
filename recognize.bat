@echo off
rem ################### This is debug program ###########################################################
rem ##### if you find something strange please rename "recognize_bak.bat" to "recognize.bat" ############
rem #####################################################################################################


set GOOGLE_APPLICATION_CREDENTIALS=C:\Users\hirok\OneDrive\Desktop\SST_source\sample.json

echo Please speak ...

rem for /F %%A in ('python transcribe_streaming_mic.py') do (echo %%A)

python transcribe_streaming_mic_debug.py
rem python transcribe_streaming_mic.py

rem call cmd /c "nod.bat"

rem exit
