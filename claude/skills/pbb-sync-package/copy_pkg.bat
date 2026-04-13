@echo off
robocopy "\\pubg-pds\PBB\Builds\%1" "C:\Users\taewoo\Desktop\%1" /E /MT:16 /NFL /NDL /NJH /NP
