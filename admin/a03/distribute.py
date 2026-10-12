"""A03配布: gh + git。planは読み取りのみ。applyは検証済みplanに限定。"""
import argparse
import hashlib
import json
import re
import subprocess
import tempfile
from pathlib import Path
from urllib.parse import quote

FILES = ('TASK.md', 'price_check.py', 'answer.md')
ORG = 'yamagata-u-system-Innovation'


def run(*args, cwd=None):
    return subprocess.run(args, cwd=cwd, check=True, capture_output=True,
                          text=True, encoding='utf-8').stdout.strip()


def api(endpoint):
    return json.loads(run('gh', 'api', endpoint))


def blob(data):
    return hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()


def payload(source):
    result = {}
    for name in FILES:
        p = source / name
        if p.is_symlink() or not p.is_file():
            raise ValueError(f'通常ファイルが必要: {name}')
        data = p.read_bytes()
        data.decode('utf-8')
        result['week03/' + name] = blob(data)
    task = (source / 'TASK.md').read_text(encoding='utf-8')
    if any(s in task for s in ('［', '未確定', '準備中', '確認前')):
        raise ValueError('TASK.mdが未確定です。教員が確定版へ編集してください')
    return result


def roster(path):
    repos = [s.strip() for s in path.read_text(encoding='utf-8-sig').splitlines()
             if s.strip() and not s.lstrip().startswith('#')]
    if not repos or len(repos) != len(set(repos)):
        raise ValueError('対象一覧が空、または重複しています')
    for repo in repos:
        if not re.fullmatch(ORG + r'/prog_basic_2026_[0-9]+', repo):
            raise ValueError('学生用リポジトリ名ではありません: ' + repo)
    return repos


def snapshot(repo, ref=None):
    meta = api('repos/' + repo)
    if not meta['private'] or meta.get('archived') or meta.get('disabled'):
        raise ValueError('有効な非公開リポジトリではありません')
    if not meta.get('permissions', {}).get('push'):
        raise ValueError('push権限がありません')
    branch = meta['default_branch']
    head = api(f'repos/{repo}/git/ref/heads/{quote(branch, safe="")}')['object']['sha']
    tree = api(f'repos/{repo}/git/trees/{ref or head}?recursive=1')
    if tree.get('truncated'):
        raise ValueError('tree一覧が省略されています')
    entries = {x['path']: x for x in tree['tree']}
    return branch, head, entries


def classify(entries, hashes):
    present = {p: x for p, x in entries.items()
               if p == 'week03' or p.startswith('week03/')}
    if not present:
        return 'ADD'
    actual = {p: x['sha'] for p, x in present.items() if x['type'] != 'tree'}
    if actual == hashes and all(entries[p]['mode'] == '100644' for p in hashes):
        return 'ALREADY'
    return 'BLOCKED'


def write_json(path, value):
    # 同名の過去plan/結果を破壊しない。
    with path.open('x', encoding='utf-8') as f:
        json.dump(value, f, ensure_ascii=False, indent=2)


def plan(args):
    hashes = payload(args.source)
    rows = []
    for repo in roster(args.roster):
        try:
            branch, head, entries = snapshot(repo)
            state = classify(entries, hashes)
            rows.append(dict(repo=repo, branch=branch, head=head, state=state))
        except Exception as e:
            rows.append(dict(repo=repo, state='BLOCKED', reason=str(e)))
    result = dict(version=1, payload=hashes, targets=rows)
    write_json(args.out, result)
    for row in rows:
        print(row['repo'], row['state'])
    print('差分: ADD対象には次の3ファイルだけを新規追加:', ', '.join(hashes))
    return 1 if any(r['state'] == 'BLOCKED' for r in rows) else 0


def apply(args):
    data = json.loads(args.plan.read_text(encoding='utf-8'))
    hashes = payload(args.source)
    if data.get('version') != 1 or data['payload'] != hashes:
        raise ValueError('plan作成後に教材が変わっています。planを作り直してください')
    targets = roster(args.roster)
    if targets != [r['repo'] for r in data['targets']]:
        raise ValueError('planと対象一覧が一致しません')
    if any(r['state'] not in ('ADD', 'ALREADY') for r in data['targets']):
        raise ValueError('BLOCKEDがあるため配布しません。解決後に再planしてください')
    # 全対象を先に再検証。1件でも変化していれば一括処理開始前に停止。
    for row in data['targets']:
        branch, head, entries = snapshot(row['repo'])
        if (branch, head, classify(entries, hashes)) != (row['branch'], row['head'], row['state']):
            raise ValueError('対象がplan後に変化: ' + row['repo'])
    results = []
    # 結果を先に排他的に作成し、各件ごとに永続化する。
    with args.out.open('x', encoding='utf-8') as log:
        for row in data['targets']:
            result = dict(repo=row['repo'], before=row['head'])
            try:
                if row['state'] == 'ALREADY':
                    result['status'] = 'ALREADY'
                else:
                    with tempfile.TemporaryDirectory(prefix='a03-') as temp:
                        work = Path(temp) / 'repo'
                        run('gh', 'repo', 'clone', row['repo'], str(work), '--', '--no-checkout')
                        run('git', 'checkout', '--detach', row['head'], cwd=work)
                        if (work / 'week03').exists() or (work / 'week03').is_symlink():
                            raise ValueError('week03が既存です')
                        (work / 'week03').mkdir()
                        for name in FILES:
                            (work / 'week03' / name).write_bytes((args.source / name).read_bytes())
                        run('git', '-c', 'core.autocrlf=false', 'add', '--', *hashes, cwd=work)
                        changed = run('git', 'diff', '--cached', '--name-status', cwd=work).splitlines()
                        if sorted(changed) != sorted('A\t' + p for p in hashes):
                            raise ValueError('許可した新規追加以外の差分があります')
                        for p, sha in hashes.items():
                            if run('git', 'rev-parse', ':' + p, cwd=work) != sha:
                                raise ValueError('Git変換後の内容が教材と不一致: ' + p)
                        run('git', 'commit', '-m', 'A03を配布', cwd=work)
                        new = run('git', 'rev-parse', 'HEAD', cwd=work)
                        result['commit'] = new
                        branch, head, entries = snapshot(row['repo'])
                        if branch != row['branch'] or head != row['head']:
                            raise ValueError('push直前に学生が更新。再planしてください')
                        # 通常pushのみ。競合更新ならnon-fast-forwardで拒否。force/rebaseしない。
                        run('git', 'push', 'origin', 'HEAD:refs/heads/' + branch, cwd=work)
                        result['status'] = 'PUSHED_VERIFY_PENDING'
                        # 配布commitの完全なtreeを検証（3ファイル以外は不変）。
                        _, current, after = snapshot(row['repo'], new)
                        expected = {p: (x['mode'], x['type'], x['sha'])
                                    for p, x in entries.items() if x['type'] != 'tree'}
                        expected.update({p: ('100644', 'blob', sha) for p, sha in hashes.items()})
                        actual = {p: (x['mode'], x['type'], x['sha'])
                                  for p, x in after.items() if x['type'] != 'tree'}
                        if actual != expected:
                            raise ValueError('配布commitの検証失敗')
                        result['status'] = 'VERIFIED' if current == new else 'VERIFIED_HEAD_ADVANCED'
            except Exception as e:
                result['error'] = str(e)
                result.setdefault('status', 'FAILED_OR_UNKNOWN')
            results.append(result)
            log.seek(0)
            json.dump(results, log, ensure_ascii=False, indent=2)
            log.truncate()
            log.flush()
            print(result['repo'], result['status'])
            if result.get('error'):
                print('処理停止。結果を確認してから再planしてください')
                return 1
    return 0


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=('plan', 'apply'))
    parser.add_argument('--source', type=Path, required=True, help='確定版week03ディレクトリ')
    parser.add_argument('--roster', type=Path, required=True, help='教員専用の対象一覧')
    parser.add_argument('--out', type=Path, required=True, help='新規plan/結果ファイル')
    parser.add_argument('--plan', type=Path)
    args = parser.parse_args()
    if args.mode == 'apply' and args.plan is None:
        parser.error('applyには--planが必要')
    try:
        return plan(args) if args.mode == 'plan' else apply(args)
    except Exception as e:
        print('停止:', e)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
