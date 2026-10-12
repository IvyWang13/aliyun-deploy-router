"""Offline regressions for search failures and damaged skill installations."""
import contextlib
import importlib.util
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import urllib.error
import urllib.parse

ROOT = Path(__file__).resolve().parents[1]


def load(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / 'scripts' / (name + '.py'))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


search = load('search_issues')
install = load('check_install')


def payload(items=None, incomplete=False, total=None):
    items = items or []
    return {'items': items, 'total_count': len(items) if total is None else total,
            'incomplete_results': incomplete}


def issue():
    return {'number': 8, 'title': 'example failure', 'state': 'closed',
            'html_url': 'https://github.com/example/repo/issues/8',
            'updated_at': '2026-10-11T00:00:00Z', 'comments': 2, 'body': None}


class SearchTests(unittest.TestCase):
    def run_search(self, data=None, error=None, args=None):
        response = io.BytesIO(json.dumps(data).encode())
        output = io.StringIO()
        argv = ['search_issues.py', '--repo', 'example/repo', '--query', 'safe error']
        with patch('sys.argv', args or argv), patch.object(search.urllib.request, 'urlopen',
                side_effect=error, return_value=response) as network, contextlib.redirect_stdout(output):
            code = search.main()
        return code, json.loads(output.getvalue())['results'], network

    def test_closed_issue_is_returned(self):
        code, results, network = self.run_search(payload([issue()]))
        self.assertEqual(code, 0)
        self.assertEqual(results[0]['items'][0]['state'], 'closed')
        query = urllib.parse.parse_qs(urllib.parse.urlsplit(network.call_args.args[0].full_url).query)['q'][0]
        self.assertNotIn('is:open', query)
        self.assertIn('repo:example/repo is:issue', query)

    def test_empty_success(self):
        code, results, _ = self.run_search(payload())
        self.assertEqual((code, results[0]['total_count']), (0, 0))

    def test_partial_is_not_success(self):
        code, results, _ = self.run_search(payload(incomplete=True))
        self.assertEqual(code, 3)
        self.assertEqual(results[0]['status'], 'partial')

    def test_truncation_is_visible(self):
        _, results, _ = self.run_search(payload([issue()], total=20))
        self.assertTrue(results[0]['truncated'])

    def test_http_errors_are_not_empty_results(self):
        for status in (403, 429, 422, 500):
            with self.subTest(status=status):
                error = urllib.error.HTTPError('https://api.github.com', status, 'error', {}, None)
                code, results, _ = self.run_search(error=error)
                self.assertEqual(code, 1)
                self.assertNotIn('total_count', results[0])

    def test_network_errors(self):
        for error in (urllib.error.URLError('offline'), TimeoutError(), ConnectionResetError()):
            with self.subTest(error=type(error).__name__):
                code, results, _ = self.run_search(error=error)
                self.assertEqual((code, results[0]['status']), (1, 'error'))

    def test_malformed_payload(self):
        for data in (None, [], {}, {'items': None, 'total_count': 0}, payload([None]),
                     payload(total='zero'), payload(incomplete='false')):
            with self.subTest(data=data):
                code, results, _ = self.run_search(data)
                self.assertEqual((code, results[0]['status']), (1, 'error'))

    def test_unexpected_repo_and_pr_rejected(self):
        for update in ({'html_url': 'https://github.com/other/repo/issues/8'}, {'pull_request': {}}):
            data = issue()
            data.update(update)
            code, _, _ = self.run_search(payload([data]))
            self.assertEqual(code, 1)

    def test_invalid_arguments_never_call_network(self):
        for args in (['--query', 'repo:other/repo'], ['--query', ''], ['--limit', '0'],
                     ['--repo', 'https://github.com/example/repo']):
            with self.subTest(args=args), patch('sys.argv', ['search_issues.py', '--repo', 'example/repo',
                    '--query', 'safe'] + args), patch.object(search.urllib.request, 'urlopen') as network, \
                    contextlib.redirect_stderr(io.StringIO()):
                with self.assertRaises(SystemExit) as error:
                    search.main()
                self.assertEqual(error.exception.code, 2)
                network.assert_not_called()


class InstallTests(unittest.TestCase):
    def fixture(self, root):
        for name in install.REQUIRED:
            path = root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text('fixture', encoding='utf-8')

    def test_current_install(self):
        self.assertTrue(install.check(ROOT)['ok'])

    def test_missing_reference_detected(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            self.fixture(root)
            (root / 'references/routes.md').unlink()
            self.assertFalse(install.check(root)['ok'])

    def test_broken_and_cyclic_links(self):
        for target in ('missing.py', 'search_issues.py'):
            with self.subTest(target=target), tempfile.TemporaryDirectory() as temp:
                root = Path(temp)
                self.fixture(root)
                path = root / 'scripts/search_issues.py'
                path.unlink()
                path.symlink_to(target)
                self.assertFalse(install.check(root)['ok'])

    def test_valid_linked_directory(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / 'real'
            root.mkdir()
            self.fixture(root)
            linked = Path(temp) / 'linked'
            linked.symlink_to(root, target_is_directory=True)
            self.assertTrue(install.check(linked)['ok'])

    def test_empty_file_detected(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            self.fixture(root)
            (root / 'SKILL.md').write_text('')
            self.assertFalse(install.check(root)['ok'])


if __name__ == '__main__':
    unittest.main()
