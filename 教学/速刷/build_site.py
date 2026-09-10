"""发布白名单：完整批次+独审报告指纹门禁；拒绝把原始数据目录发布上网。"""
from pathlib import Path
import json, hashlib, shutil, re
ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[1]
SITE = REPO / '_site'
REQUIRED = {
    '手写模拟题_100.js': 'math_and_independent_review_passed',
    '原创复合24.js': 'math_and_independent_review_passed',
    '精选GLM题库.js': 'screened_only',
}
ASSETS = ['刷题页面.html', 'core.js', 'app.js', 'training_families.js', *REQUIRED,
          'datasets/banks.js', 'datasets/authored_policy.js', 'authored_methods.js', 'release_manifest.json']

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def verify_manifest(manifest, root=ROOT):
    if set(manifest.get('audited', {})) != set(REQUIRED):
        raise ValueError('必须明确列出全部三个批次；空清单或部分清单不能发布')
    for name, status in REQUIRED.items():
        record = manifest['audited'][name]
        if record.get('status') != status:
            raise ValueError(f'{name}: 审计级别不符，初筛不可冒充独立数审')
        if digest(root/name) != record.get('sha256'):
            raise ValueError(f'{name}: 内容已改变，必须重新数学与题面审计')
        if status == 'math_and_independent_review_passed':
            review = record.get('independentReview', {})
            report = root/review.get('file', '')
            if report.parent.resolve() != root.resolve() or not report.is_file():
                raise ValueError(f'{name}: 缺少同目录独立审计报告')
            if digest(report) != review.get('sha256'):
                raise ValueError(f'{name}: 独立报告指纹已改变')
            approvals=re.findall(r'^RELEASE_APPROVED_SHA256: ([0-9a-f]{64})$',report.read_text(encoding='utf-8'),re.M)
            if not approvals or approvals[-1]!=record['sha256']:
                raise ValueError(f'{name}: 报告末次明确放行标记未绑定当前题库指纹')
    return True

def main():
    manifest = json.loads((ROOT/'release_manifest.json').read_text(encoding='utf-8'))
    verify_manifest(manifest)
    # Data checks must also run when build_site is invoked outside CI.
    import subprocess, sys, os
    subprocess.run([sys.executable, str(ROOT/'build_datasets.py'), '--check'], check=True)
    subprocess.run([sys.executable, str(ROOT/'test_datasets.py')], check=True)
    subprocess.run([sys.executable, str(ROOT/'build_authored_methods.py'), '--check'], check=True)
    subprocess.run([sys.executable, str(ROOT/'audit_datasets_independent.py')], check=True)
    SITE.mkdir(exist_ok=True)
    dest = SITE/'教学'/'速刷'
    dest.mkdir(parents=True, exist_ok=True)
    expected = {'index.html', '.nojekyll', 'version.json'} | {f'教学/速刷/{name}' for name in ASSETS}
    extra = {p.relative_to(SITE).as_posix() for p in SITE.rglob('*') if p.is_file()} - expected
    if extra:
        raise ValueError(f'发布目录存在白名单以外文件，请人工检查后移除：{extra}')
    for name in ASSETS:
        (dest/name).parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT/name, dest/name)
    shutil.copyfile(REPO/'index.html', SITE/'index.html')
    (SITE/'.nojekyll').touch()
    revision = os.environ.get('GITHUB_SHA')
    if not revision:
        git = subprocess.run(['git', 'rev-parse', 'HEAD'], cwd=REPO, capture_output=True, text=True)
        revision = git.stdout.strip() if git.returncode == 0 else 'local-build'
    version = {'revision': revision, 'validationYears': [2024, 2025, 2026],
               'assets': {'index.html': digest(SITE/'index.html'), **{f'教学/速刷/{name}': digest(dest/name) for name in ASSETS}}}
    (SITE/'version.json').write_text(json.dumps(version, ensure_ascii=False, indent=2)+'\n', encoding='utf-8', newline='\n')
    print('Site staged:', len(expected), 'whitelisted files; all review hashes matched')

if __name__ == '__main__':
    main()
