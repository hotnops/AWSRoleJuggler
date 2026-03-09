#!/usr/bin/env python3

from argparse import ArgumentParser
import boto3
import time
import sys

def assume_role(client, arn):
    print(f"[*] Attempting to assume: {arn}")
    try:
        response = client.assume_role(
            RoleArn=arn,
            RoleSessionName='juggle',
            DurationSeconds=3600
        )

        if not response or 'Credentials' not in response:
            print(f"[!] Failed to assume {arn}. No credentials found.")
            return None
        
        creds = response['Credentials']
        print(f"[+] Successfully assumed {arn}")
        print(f"[*] Expiration: {creds['Expiration']}")
        
        # Output for easy copy-pasting into environment variables
        print(f"\nexport AWS_ACCESS_KEY_ID={creds['AccessKeyId']}")
        print(f"export AWS_SECRET_ACCESS_KEY={creds['SecretAccessKey']}")
        print(f"export AWS_SESSION_TOKEN={creds['SessionToken']}\n")

        session = boto3.Session(
            aws_access_key_id=creds['AccessKeyId'],
            aws_secret_access_key=creds['SecretAccessKey'],
            aws_session_token=creds['SessionToken']
        )
        return session.client('sts')
    
    except Exception as e:
        print(f"[!] Error: {e}")
        return None

def juggle_roles(role_list, profile=None):
    try:
        session = boto3.Session(profile_name=profile)
        client = session.client('sts')
    except Exception as e:
        print(f"[!] Initial session error: {e}")
        sys.exit(1)

    if not role_list:
        print("[!] No roles provided.")
        return

    # Start the chain
    current_idx = 0
    total_roles = len(role_list)
    
    # First jump
    client = assume_role(client, role_list[current_idx])
    if not client:
        print("[!] Initial jump failed.")
        return

    print("[*] Juggling started. Press Ctrl+C at any time to skip the timer or exit.")

    try:
        while True:
            try:
                # Original logic: sleep for 9 minutes
                print(f"[*] Current Role: {role_list[current_idx]}")
                print("[*] Sleeping for 9m. (Ctrl+C for manual jump/exit)")
                time.sleep(540)
            except KeyboardInterrupt:
                print("\n\n--- INTERRUPT ---")
                choice = input("[?] [j]ump to next role / [q]uit script? ").lower().strip()
                if choice == 'q':
                    print("[*] Exiting...")
                    return
                print("[*] Jumping to next role in the cycle...")

            # Move to the next role in the list (looping back to start if at the end)
            current_idx = (current_idx + 1) % total_roles
            next_role = role_list[current_idx]
            
            new_client = assume_role(client, next_role)
            if new_client:
                client = new_client
            else:
                print(f"[!] Jump to {next_role} failed. Retrying in next cycle.")
    
    except Exception as e:
        print(f"[!] Critical Error: {e}")

if __name__ == "__main__":
    parser = ArgumentParser(description="AWS Role Juggler with Manual Jump")
    parser.add_argument('-r', '--role-list', nargs='+', default=[])
    parser.add_argument('-p', '--profile', help="Initial AWS profile", default=None)
    args = parser.parse_args()

    # Clean input list from JSON-like strings
    cleaned = []
    for r in args.role_list:
        r = r.replace('[','').replace(']','').replace('"','').replace("'", "")
        cleaned.extend([i.strip() for i in r.split(',') if i.strip()])

    juggle_roles(cleaned, args.profile)