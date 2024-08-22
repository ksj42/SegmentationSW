@echo off

rem Change directory to your Git repository
cd H:
cd H:\Project\08_clavicle_software_python\sw

rem Add all changes
git add .

rem Commit with a specified message (using the current date and time)
set timestamp=%date% %time%
set commit_message=Automated commit on %timestamp%
git commit -m "%commit_message%"

rem Push changes to the remote repository (assuming origin is your remote and main is the branch)
git push origin main

rem Pause to keep the console window open (optional)
pause
