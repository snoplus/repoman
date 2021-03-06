#!/usr/bin/env python

import sys
import os
import subprocess
import json
from wsgiref.simple_server import make_server

import config

def main(env, start_response):
    if env['REQUEST_METHOD'] != 'POST':
        status = '501 NOT IMPLEMENTED'

    else:
        request_length = int(env['CONTENT_LENGTH'])
        request_body = env['wsgi.input'].read(request_length)
        doc = json.loads(request_body)

        repo_name = doc['repository']['name']
        target_dir = os.path.abspath(os.path.join(config.mirror_dir, repo_name))

        print 'updating %s repository in %s' % (repo_name, target_dir)

        if os.path.exists(target_dir):
            cmd = ['git', 'pull']
            cwd = target_dir
        else:
            cmd = ['git', 'clone', doc['git_url']]
            cwd = config.mirror_dir

        subprocess.Popen(cmd, cwd=cwd)

        status = '200 OK'

    headers = [('Content-type', 'text/plain')]
    start_response(status, headers)
    return []

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print 'Usage:', sys.argv[0], '<port>'
        sys.exit(1)

    port = int(sys.argv[1])
    httpd = make_server('', port, main)

    print 'mirror starting on localhost:%i' % port
    print 'mirror directory:', config.mirror_dir
    httpd.serve_forever()

