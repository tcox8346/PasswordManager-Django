Set-Variable -Name currentuser -Description "This value stores the directory path which the project will be set" -Value $env:UserName
Set-Variable -Name desired-path -Description "This value stores the directory path which the project will be set" -Value $currentuser/Project_2/TanajCox/CredentialManagementService/

Write-Information -MessageData (This requires python to be installed on the system and available as a system variable)

pip3 install "pipenv"