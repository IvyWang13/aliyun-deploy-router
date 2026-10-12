#!/usr/bin/env python3
"""Read-only public GitHub issue search. Pass sanitized keywords, never raw logs."""
import argparse
import json
import http.client
import re
import sys
import urllib.error
import urllib.parse
import urllib.request


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', action='append', required=True, help='Public owner/repo; repeat to search multiple repositories')
    parser.add_argument('--query', required=True, help='Sanitized error keywords or quoted phrases; no scope qualifiers')
    parser.add_argument('--limit', type=int, default=10)
    args = parser.parse_args()
    if not 1 <= args.limit <= 30:
        parser.error('--limit must be between 1 and 30')
    if not args.query.strip():
        parser.error('--query must not be empty')
    if re.search(r'(?i)(?:^|\s)-?(?:repo|org|user|is|type|state):', args.query):
        parser.error('--query must not override repository or issue scope')
    for repo in args.repo:
        if not re.fullmatch(r'[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+', repo):
            parser.error('--repo must use owner/repo format')

    results = []
    for repo in dict.fromkeys(args.repo):
        query = f'repo:{repo} is:issue {args.query.strip()}'
        url = 'https://api.github.com/search/issues?' + urllib.parse.urlencode({
            'q': query, 'per_page': args.limit,
        })
        request = urllib.request.Request(url, headers={
            'Accept': 'application/vnd.github+json',
            'User-Agent': 'aliyun-deploy-router-public-issue-search',
            'X-GitHub-Api-Version': '2022-11-28',
        })
        try:
            with urllib.request.urlopen(request, timeout=25) as response:
                data = json.load(response)
            if not isinstance(data, dict):
                raise ValueError('Invalid response object')
            items = data['items']
            if (not isinstance(items, list) or type(data['total_count']) is not int
                    or data['total_count'] < 0 or type(data.get('incomplete_results')) is not bool):
                raise ValueError('Invalid search response')
            for item in items:
                if not isinstance(item, dict):
                    raise ValueError('Invalid issue object')
                if ('pull_request' in item or not isinstance(item.get('html_url'), str)
                        or not item['html_url'].startswith(f'https://github.com/{repo}/issues/')
                        or not isinstance(item.get('title'), str)
                        or item.get('state') not in ('open', 'closed')
                        or type(item.get('number')) is not int
                        or type(item.get('comments')) is not int
                        or not isinstance(item.get('updated_at'), str)
                        or (item.get('body') is not None and not isinstance(item['body'], str))):
                    raise ValueError('Unexpected issue payload or repository')
            results.append({
                'repo': repo,
                'status': 'partial' if data['incomplete_results'] else 'ok',
                'total_count': data['total_count'],
                'incomplete_results': data.get('incomplete_results', False),
                'returned_count': len(items),
                'truncated': data['total_count'] > len(items),
                'items': [{
                    'number': item['number'],
                    'title': item['title'],
                    'state': item['state'],
                    'url': item['html_url'],
                    'updated_at': item['updated_at'],
                    'comments': item['comments'],
                    'body_excerpt': (item.get('body') or '')[:2000],
                } for item in items],
            })
        except urllib.error.HTTPError as error:
            results.append({'repo': repo, 'status': 'error', 'http_status': error.code,
                            'message': 'GitHub API request failed; this is not a zero-result search.'})
        except (urllib.error.URLError, OSError, http.client.HTTPException, ValueError, KeyError, TypeError) as error:
            results.append({'repo': repo, 'status': 'error',
                            'message': f'Search unavailable ({type(error).__name__}); retry with another GitHub or web tool.'})
    print(json.dumps({'results': results}, ensure_ascii=False, indent=2))
    if any(result['status'] == 'error' for result in results):
        return 1
    return 3 if any(result['status'] == 'partial' for result in results) else 0


if __name__ == '__main__':
    sys.exit(main())
