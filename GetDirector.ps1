# PowerShell script to retrieve all managers up to the Director-Level of each user in a file.
# GetDirector
# Author: JR Aquino
#
# NOTE: This script requires the ActiveDirectory PowerShell Module included in the Remote Server Administration Tools (RSAT) for Windows
# https://learn.microsoft.com/en-US/troubleshoot/windows-server/system-management-components/remote-server-administration-tools
# https://www.microsoft.com/download/details.aspx?id=45520 <- Download Link
import-module ActiveDirectory

Function Get-Manager($EmailAddress)
{
    # $EmailAddress of a user possibly reporting to a manager.
    # Retrieve the manager of this user, if there is one.
    #$ManagerDN = Get-ADUser -Identity $ReportDN -Properties Manager | Select Manager
    $UserObject = Get-ADUser -Filter "UserPrincipalName -eq'$EmailAddress'" -Properties Title | Select Title, UserPrincipalName
    $ManagerDN = Get-ADUser -Filter "UserPrincipalName -eq'$EmailAddress'" -Properties Manager, Title | Select -ExpandProperty Manager
    # Check if there is a manager.
    If ($ManagerDN)
    {
        # Call the Get-Director function to walk the management chain.
        Get-Director $ManagerDN
    }
    # Return the chain of management
    Return 'Employee: ' + $UserObject.UserPrincipalName + ',', $UserObject.Title, [Environment]::NewLine
}

Function Get-Director($NewDN)
{
    # Recursive function to retrieve the manager of an employee.
    # $NewDN is the DN of a manager.
    # Retrieve the manager of this manager, if there is one.
    $DirectorObject = Get-ADUser -Filter "DistinguishedName -eq'$NewDN'" -Properties Title | Select Title, UserPrincipalName
    $DirectorDN = Get-ADUser -Filter "DistinguishedName -eq'$NewDN'" -Properties Manager, Title | Select -ExpandProperty Manager
    # Check if there is a manager.
    #If ($DirectorDN -ne $NewDN) # This Commented Line is necessary to prevent a Loop if an Employee is listed as their Own Manager
    # If a Manager's Title is not director, keep walking the management chain
    If (-not($DirectorObject.Title -match 'director'))
    {
        # Call the function recursively, to find the manager of this manager.
        Get-Director $DirectorDN
    }
    # Return the semicolon delimited string of DN values.
    Return 'Manager: ' + $DirectorObject.UserPrincipalName + ',', $DirectorObject.Title
}

# Retrieve users in the specified filename: users.txt.
$Users = Get-Content -Path .\users.txt


# Enumerate the users in the OU.
ForEach ($User In $Users)
{
    # Collect all managers for the users in the list.
    $Result = Get-Manager $User
    # Output the result for this user.
    $Result
}
