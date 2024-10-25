#!/usr/bin/env python3

'''A Python module that provides stats about nginx, including top 10 IPs'''

from pymongo import MongoClient


if __name__ == '__main__':
    '''Prints the log stats in the nginx collection'''
    # Connect to MongoDB
    con = MongoClient('mongodb://localhost:27017')
    collection = con.logs.nginx

    # General log statistics
    print(f'{collection.estimated_document_count()} logs')

    # Count and display HTTP method stats
    methods = ['GET', 'POST', 'PUT', 'PATCH', 'DELETE']
    print('Methods:')

    for req in methods:
        print(f'\tmethod {req}: {collection.count_documents({"method": req})}')

    # Count and display GET /status requests
    status_check_count = collection.count_documents({'method': 'GET', 'path': '/status'})
    print(f'{status_check_count} status check')

    # Top 10 most present IPs
    print('IPs:')
    
    # Use aggregation to group by IP and count occurrences, sort by count in descending order
    top_ips = collection.aggregate([
        {'$group': {'_id': '$ip', 'count': {'$sum': 1}}},
        {'$sort': {'count': -1}},
        {'$limit': 10}
    ])

    # Display the top 10 IPs
    for ip in top_ips:
        print(f'\t{ip["_id"]}: {ip["count"]}')
