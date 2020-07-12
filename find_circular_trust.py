#!/usr/bin/env python3

import boto3
import json
import matplotlib.pyplot as plt
import networkx as nx

from collections import defaultdict


def getCycles(aws_roles):
    g = nx.DiGraph()
    for jsonRole in aws_roles:
        g.add_nodes_from([jsonRole["Arn"]])

    for jsonRole in aws_roles:
        for statement in jsonRole['AssumeRolePolicyDocument']['Statement']:
            if statement['Effect'] == "Allow" and 'AWS' in statement['Principal']:
                arns = statement['Principal']['AWS']
                source = jsonRole['Arn']
                if isinstance(arns, list):
                    for arn in arns:
                        dest = arn
                        g.add_edges_from([(source, dest)])
                else:
                    dest  =arns
                    g.add_edges_from([(source, dest)])
                
    cycles = list(nx.simple_cycles(g))
    return cycles

if __name__ == "__main__":
    client = boto3.client('iam')
    aws_roles = client.list_roles()['Roles']

    cycles = getCycles(aws_roles)
    for c in cycles:
        print(f"Found cycle: {c}")
