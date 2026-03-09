#!/usr/bin/env python3

import boto3
import networkx as nx
import argparse
import sys
import json

def get_iam_client(profile_name=None):
    try:
        session = boto3.Session(profile_name=profile_name)
        return session.client('iam')
    except Exception as e:
        print(f"[-] Error initializing session: {e}")
        sys.exit(1)

def iam_list_roles(iam_client):
    roles = []
    paginator = iam_client.get_paginator('list_roles')
    try:
        for page in paginator.paginate():
            roles.extend(page['Roles'])
        return roles
    except Exception as e:
        print(f"[-] Error listing roles: {e}")
        return []

def get_cycles(aws_roles):
    g = nx.DiGraph()
    all_role_arns = [role["Arn"] for role in aws_roles]
    g.add_nodes_from(all_role_arns)

    for role in aws_roles:
        target_role_arn = role['Arn']
        policy = role.get('AssumeRolePolicyDocument', {})
        statements = policy.get('Statement', [])
        
        if isinstance(statements, dict):
            statements = [statements]

        for stmt in statements:
            if stmt.get('Effect') != "Allow":
                continue

            # 1. Extract direct Principals
            principal = stmt.get('Principal', {})
            aws_principals = principal.get('AWS', [])
            if isinstance(aws_principals, str):
                aws_principals = [aws_principals]

            # 2. Extract ARNs from Conditions (Crucial for sts-lab-4)
            condition_arns = []
            condition = stmt.get('Condition', {})
            for op in ['StringEquals', 'StringLike', 'ArnEquals', 'ArnLike']:
                if op in condition:
                    val = condition[op].get('aws:PrincipalArn', [])
                    if isinstance(val, str): val = [val]
                    condition_arns.extend(val)

            # Combine trust sources
            potential_sources = aws_principals + condition_arns

            for source in potential_sources:
                if source == "*":
                    # If '*' with no ARN condition, all roles can assume this
                    if not condition_arns:
                        for other_role in all_role_arns:
                            if other_role != target_role_arn:
                                g.add_edge(other_role, target_role_arn)
                elif source in all_role_arns:
                    # Edge: source -> target_role (source can assume target)
                    g.add_edge(source, target_role_arn)

    return list(nx.simple_cycles(g))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Find AWS IAM AssumeRole trust cycles.")
    parser.add_argument("--profile", help="AWS CLI profile name", default=None)
    parser.add_argument("--juggler", action="store_true", help="Output compact JSON array for AWSRoleJuggler")
    args = parser.parse_args()

    iam = get_iam_client(args.profile)
    roles = iam_list_roles(iam)
    cycles = get_cycles(roles)
    
    if not cycles:
        if args.juggler:
            print("[]")
        else:
            print("[+] No trust cycles found.")
    else:
        # Extract unique roles involved in any cycle
        roles_in_cycles = set()
        for c in cycles:
            roles_in_cycles.update(c)
        
        output_list = sorted(list(roles_in_cycles))

        if args.juggler:
            # separators=(',', ':') removes all whitespace from the JSON output
            print(json.dumps(output_list, separators=(',', ':')))
        else:
            print(f"[*] Found {len(cycles)} cycle(s):")
            for i, c in enumerate(cycles, 1):
                print(f" Cycle {i}: {' -> '.join(c)} -> {c[0]}")
            
            print("\n[+] Array for RoleJuggler (Compact):")
            print(json.dumps(output_list, separators=(',', ':')))