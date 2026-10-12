"""ネットワークへ書き込まず、配布保護とローカルGit並行更新を検証。"""
import argparse
import importlib.util
import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

spec = importlib.util.spec_from_file_location('distribute', Path(__file__).with_name('distribute.py'))
d = importlib.util.module_from_spec(spec)
spec.loader.exec_module(d)


class ProtectionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.source = self.root / 'week03'
        self.source.mkdir()
        for name in d.FILES:
            (self.source / name).write_text('確定済み教材\n', encoding='utf-8')
        self.hashes = d.payload(self.source)
        self.repo = d.ORG + '/prog_basic_2026_123456'
        self.roster = self.root / 'targets.txt'
        self.roster.write_text(self.repo, encoding='utf-8')
        self.args = argparse.Namespace(source=self.source, roster=self.roster,
                                       out=self.root / 'result.json', plan=self.root / 'plan.json')

    def test_unfinished_rejected(self):
        (self.source / 'TASK.md').write_text('未確定', encoding='utf-8')
        with self.assertRaises(ValueError):
            d.payload(self.source)

    def test_existing_student_files_protected(self):
        entries = {p: dict(type='blob', mode='100644', sha=h) for p, h in self.hashes.items()}
        self.assertEqual(d.classify({}, self.hashes), 'ADD')
        self.assertEqual(d.classify(entries, self.hashes), 'ALREADY')
        entries['week03/price_check.py']['sha'] = 'student-edit'
        self.assertEqual(d.classify(entries, self.hashes), 'BLOCKED')
        self.assertEqual(d.classify({'week03': dict(type='blob', mode='120000', sha='link')}, self.hashes), 'BLOCKED')

    def test_plan_is_read_only(self):
        with patch.object(d, 'snapshot', return_value=('main', 'a' * 40, {})), patch.object(d, 'run') as run:
            self.assertEqual(d.plan(self.args), 0)
            run.assert_not_called()

    def test_public_rejected(self):
        with patch.object(d, 'api', return_value={'private': False}):
            with self.assertRaises(ValueError):
                d.snapshot(self.repo)

    def test_changed_head_and_payload_block_apply(self):
        record = dict(version=1, payload=self.hashes,
                      targets=[dict(repo=self.repo, state='ADD', branch='main', head='a' * 40)])
        d.write_json(self.args.plan, record)
        with patch.object(d, 'snapshot', return_value=('main', 'b' * 40, {})), patch.object(d, 'run') as run:
            with self.assertRaises(ValueError):
                d.apply(self.args)
            run.assert_not_called()
        (self.source / 'answer.md').write_text('変更', encoding='utf-8')
        with patch.object(d, 'snapshot') as snapshot:
            with self.assertRaises(ValueError):
                d.apply(self.args)
            snapshot.assert_not_called()

    def test_extra_file_and_duplicate_roster(self):
        entries = {p: dict(type='blob', mode='100644', sha=h) for p, h in self.hashes.items()}
        entries['week03/notes.md'] = dict(type='blob', mode='100644', sha='student')
        self.assertEqual(d.classify(entries, self.hashes), 'BLOCKED')
        self.roster.write_text(self.repo + '\n' + self.repo)
        with self.assertRaises(ValueError):
            d.roster(self.roster)

    def test_actual_git_add_preserves_week02_and_detects_race(self):
        remote = self.root / 'remote.git'
        d.run('git', 'init', '--bare', str(remote))
        teacher = self.root / 'teacher'
        d.run('git', 'clone', str(remote), str(teacher))
        for k, v in [('user.name', 'Test'), ('user.email', 'test@example.invalid')]:
            d.run('git', 'config', k, v, cwd=teacher)
        (teacher / 'week02').mkdir()
        old = teacher / 'week02' / 'hello.py'
        old.write_text('print("student answer")\n')
        d.run('git', 'add', '.', cwd=teacher)
        d.run('git', 'commit', '-m', 'student answer', cwd=teacher)
        d.run('git', 'push', 'origin', 'HEAD:refs/heads/main', cwd=teacher)
        d.run('git', '--git-dir', str(remote), 'symbolic-ref', 'HEAD', 'refs/heads/main')
        head = d.run('git', 'rev-parse', 'HEAD', cwd=teacher)
        base_sha = d.run('git', 'rev-parse', 'HEAD:week02/hello.py', cwd=teacher)
        d.write_json(self.args.plan, dict(version=1, payload=self.hashes,
                     targets=[dict(repo=self.repo, state='ADD', branch='main', head=head)]))

        def snap(repo, ref=None):
            current = d.run('git', '--git-dir', str(remote), 'rev-parse', 'refs/heads/main')
            text = d.run('git', '--git-dir', str(remote), 'ls-tree', '-r', ref or current)
            entries = {}
            for line in text.splitlines():
                mode_type_sha, path = line.split('\t')
                mode, kind, sha = mode_type_sha.split()
                entries[path] = dict(mode=mode, type=kind, sha=sha)
            return 'main', current, entries

        real_run = d.run
        def local_run(*args, cwd=None):
            if args[:3] == ('gh', 'repo', 'clone'):
                dest = args[4]
                real_run('git', 'clone', '--no-checkout', str(remote), dest)
                real_run('git', 'config', 'user.name', 'Test', cwd=dest)
                real_run('git', 'config', 'user.email', 'test@example.invalid', cwd=dest)
                return ''
            return real_run(*args, cwd=cwd)

        with patch.object(d, 'snapshot', side_effect=snap), patch.object(d, 'run', side_effect=local_run):
            self.assertEqual(d.apply(self.args), 0)
        result = json.loads(self.args.out.read_text())[0]
        self.assertEqual(result['status'], 'VERIFIED')
        self.assertEqual(d.run('git', '--git-dir', str(remote), 'rev-parse', 'main:week02/hello.py'), base_sha)
        # 教員cloneは古いheadのまま。学生の次の更新をremoteへpushした後、古い教員pushは拒否。
        student = self.root / 'student'
        d.run('git', 'clone', str(remote), str(student))
        d.run('git', 'config', 'user.name', 'Student', cwd=student)
        d.run('git', 'config', 'user.email', 'student@example.invalid', cwd=student)
        (student / 'week02/hello.py').write_text('print("new student answer")\n')
        d.run('git', 'add', '.', cwd=student)
        d.run('git', 'commit', '-m', 'student newer', cwd=student)
        d.run('git', 'push', 'origin', 'main', cwd=student)
        with self.assertRaises(subprocess.CalledProcessError):
            d.run('git', 'push', 'origin', 'HEAD:refs/heads/main', cwd=teacher)


if __name__ == '__main__':
    unittest.main()
