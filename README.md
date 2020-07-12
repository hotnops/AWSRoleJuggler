# AWSRoleJuggler
A toolset to juggle AWS roles for persistent access

#Usage
First, use the find_cicular_trust.py tool to locate roles that create a circular trust. This is assuming the calling environment already has credentials loaded for the AWS environment:
```
./find_circular_trust.py 
Found cycle: ['arn:aws:iam::123456789:role/GitRole', 'arn:aws:iam::123456789:role/BuildRole', 'arn:aws:iam::123456789:role/ArtiRole']
```
Next, use the aws_role_juggler.py script to keep a role session alive for an indefinite period of time. In this example, we want to keep the BuildRole alive past the 1 hour max, so we provide the roles in the proper order:
```
python aws_role_juggler.py -r arn:aws:iam::123456789:role/BuildRole arn:aws:iam::123456789:role/GitRole arn:aws:iam::123456789:role/ArtiRole
```
Even though the session is requested for an hour, it is refreshed every 15 minutes, and the credentials are output to screen.
