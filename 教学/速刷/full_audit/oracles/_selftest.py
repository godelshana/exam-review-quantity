"""Offline/mutation CI tests. Only TemporaryDirectory is written; never the repo.
Run via check_full_oracles.py --self-test. No third-party test framework required.
"""
from __future__ import annotations
import ast
import hashlib
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path


def run_selftest(runner,audit_dir):
    audit_dir=Path(audit_dir).resolve()
    results=[]
    def record(name):results.append(name)
    def digest_tree(root):
        return {str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest()
                for p in root.rglob('*') if p.is_file()}
    with tempfile.TemporaryDirectory(prefix='full-oracles-') as temp:
        root=Path(temp).resolve();app=root/'isolated_app';app.mkdir()
        audit=app/'full_audit';audit.mkdir();mods=audit/'oracles';mods.mkdir()
        reviews=audit/'reviews';reviews.mkdir()
        isolated=app/runner.name;isolated.write_bytes(runner.read_bytes())
        for p in (runner.parent/'full_audit'/'oracles').glob('*.py'):
            (mods/p.name).write_bytes(p.read_bytes())
        for p in audit_dir.glob('*_0?.json'):
            if p.stem.startswith(('national_','provincial_')):
                (audit/p.name).write_bytes(p.read_bytes())
                (reviews/p.name).write_bytes((audit_dir/'reviews'/p.name).read_bytes())
        (audit/'intake.json').write_bytes((audit_dir/'intake.json').read_bytes())
        assert not (audit/'work').exists() and not (root/'真题库').exists()
        # No source, answer, filesystem, network or image access in batch modules.
        for p in mods.glob('*_0?.py'):
            source=p.read_text('utf-8');tree=ast.parse(source)
            for n in ast.walk(tree):
                if isinstance(n,ast.Call):
                    name=n.func.id if isinstance(n.func,ast.Name) else n.func.attr if isinstance(n.func,ast.Attribute) else ''
                    assert name not in {'open','read_text','read_bytes','write_text','write_bytes','exec','eval','__import__'},(p.name,name)
                if isinstance(n,ast.Constant) and isinstance(n.value,str):
                    assert n.value not in {'answerIndex','sourceAnswer','sourceAnswerIndex','computedAnswer'},(p.name,n.value)
        record('batch_modules_have_no_file_network_image_or_answer_key_inputs')

        # Python isolated/no-site flags ensure installed SciPy/PIL cannot help.
        # An audit hook prohibits socket creation and any attempted file writes.
        bootstrap=r"""
import sys,runpy,os
sys.dont_write_bytecode=True
script=sys.argv[1];sys.argv=sys.argv[1:]
def guard(event,args):
    if event.startswith('socket.'):
        raise RuntimeError('network forbidden in offline test')
    if event=='open':
        path,mode,flags=args
        if (isinstance(mode,str) and any(c in mode for c in 'wax+')) or (isinstance(flags,int) and flags & (os.O_WRONLY|os.O_RDWR|os.O_CREAT|os.O_TRUNC|os.O_APPEND)):
            raise RuntimeError('filesystem write forbidden in oracle process')
        if isinstance(path,(str,bytes)) and os.fsdecode(path).lower().endswith(('.pdf','.png','.jpg','.jpeg','.webp','.gif')):
            raise RuntimeError('image/PDF read forbidden in oracle process')
sys.addaudithook(guard)
runpy.run_path(script,run_name='__main__')
"""
        def run(*args,expected=0,optimize=False):
            before=digest_tree(root)
            command=[sys.executable,'-I','-S','-B','-X','utf8']
            if optimize:command.append('-O')
            command+=['-c',bootstrap,str(isolated),*args]
            process=subprocess.run(command,cwd=root,capture_output=True,encoding='utf-8',timeout=120)
            assert process.returncode==expected,(args,process.returncode,process.stdout[-5000:],process.stderr)
            assert digest_tree(root)==before,'oracle process modified its isolated data tree'
            if '--json' in args:
                return json.loads(process.stdout)
            return process.stdout+process.stderr
        baseline=run('--require-all-batches','--json')
        assert baseline['totals']['inputRows']==1105
        assert not baseline['totals']['failedBatches'] and not baseline['totals']['pendingBatches']
        assert len(baseline['batches'])==12
        record('all_12_batches_1105_inputs_offline_without_work_images_raw_or_site_packages')
        record('no_writes_no_reports_no_bytecode_in_guarded_process')

        # Delete ONLY known copied shard files; intake fallback must be equivalent.
        shards={p:p.read_bytes() for p in audit.glob('*_0?.json')}
        for p in shards:
            assert p.resolve().is_relative_to(root)
            p.unlink()
        fallback=run('--require-all-batches','--json')
        assert fallback['totals']==baseline['totals']
        for path,content in shards.items():path.write_bytes(content)
        record('intake_only_fallback_matches_shard_coverage_and_results')

        rp=reviews/'national_01.json';qp=audit/'national_01.json'
        rbytes=rp.read_bytes();qbytes=qp.read_bytes()
        def write_json(path,data):path.write_text(json.dumps(data,ensure_ascii=False),'utf-8')
        def has_error(report,kind):return any(e['type']==kind for b in report['batches'] for e in b['errors'])
        r=json.loads(rbytes);r[0]['answerIndex']=(r[0]['answerIndex']+1)%4
        write_json(rp,r)
        bad=run('--batch','national_01','--json',expected=1)
        assert has_error(bad,'mathematical_option_mismatch')
        rp.write_bytes(rbytes)
        record('wrong_review_answer_fails_against_computation')

        q=json.loads(qbytes);q[0]['s']+=' (changed constraint)';write_json(qp,q)
        bad=run('--batch','national_01','--json',expected=1)
        assert 'problem changed' in str(bad)
        qp.write_bytes(qbytes)
        record('changed_shard_stem_fails_parameter_fingerprint')

        r=json.loads(rbytes);r[0]['correctedStem']=(r[0].get('correctedStem')or json.loads(qbytes)[0]['s'])+' 额外增加1'
        write_json(rp,r);bad=run('--batch','national_01','--json',expected=1)
        assert 'effective review stem/options changed' in str(bad)
        rp.write_bytes(rbytes)
        record('changed_effective_corrected_stem_fails_model_binding')

        r=json.loads(rbytes);r[0]['correctedOptions']=list(reversed(r[0].get('correctedOptions')or json.loads(qbytes)[0]['o']))
        write_json(rp,r);bad=run('--batch','national_01','--json',expected=1)
        assert 'effective review stem/options changed' in str(bad)
        rp.write_bytes(rbytes)
        record('reordered_effective_options_cannot_reuse_old_alignment')

        q=json.loads(qbytes);q[0]['sourceAnswer']='WRONG';q[0]['sourceAnswerIndex']=999
        write_json(qp,q);same=run('--batch','national_01','--json')
        base=next(b for b in baseline['batches'] if b['batch']=='national_01')
        assert same['batches'][0]['cases']==base['cases']
        qp.write_bytes(qbytes)
        record('source_answer_mutation_has_no_effect_on_solver')

        r=json.loads(rbytes);r[0]['displayImages']=['missing_display_asset.png'];r[0]['imageRefs']=['missing_evidence.png']
        r[0]['correctedStem']=(r[0].get('correctedStem')or json.loads(qbytes)[0]['s'])+'\n![moved](真题库/图片/已审计/missing.png)'
        r[0]['futureSchemaExtension']={'allowed':True};write_json(rp,r)
        run('--batch','national_01','--json');rp.write_bytes(rbytes)
        record('extra_schema_and_display_image_relocation_do_not_trigger_math_failures')

        saved_reviews={p:p.read_bytes() for p in reviews.glob('*.json')}
        for path in saved_reviews:
            assert path.resolve().is_relative_to(root);path.unlink()
        no_review=run('--require-all-batches','--no-review','--json')
        assert no_review['totals']['schemaRows']==no_review['totals']['reviewAnswersChecked']==0
        assert no_review['totals']['computationRows']==baseline['totals']['computationRows']
        run('--batch','national_01','--json',expected=1)
        for path,content in saved_reviews.items():path.write_bytes(content)
        record('explicit_no_review_mode_runs_all_math_and_default_rejects_missing_reviews')

        model=mods/'national_01.py';model_bytes=model.read_bytes()
        source=model_bytes.decode('utf-8');needle='check(0,F(120)/F(5,2))'
        assert needle in source
        model.write_text(source.replace(needle,'check(0,F(121)/F(5,2))',1),'utf-8')
        bad=run('--batch','national_01','--json',expected=1)
        assert has_error(bad,'unique_option_check_regression')
        model.write_bytes(model_bytes)
        record('wrong_calculation_without_an_option_match_cannot_silently_pass')

        missing=mods/'provincial_08.py';saved=missing.read_bytes();missing.unlink()
        run('--require-all-batches','--batch','provincial_08','--json',expected=1)
        missing.write_bytes(saved)
        record('release_flag_fails_missing_batch_module')
        incomplete=run('--require-complete','--json',expected=1)
        assert incomplete['totals']['uncoveredRows']==113
        record('require_complete_truthfully_rejects_partial_math_coverage')
        output=run(optimize=True,expected=1)
        assert 'assertions must not be disabled' in output
        record('python_optimization_cannot_disable_assertions_and_fake_a_pass')

        # Standard-library numeric matching regression cases.
        from _common import option_match, numeric
        from fractions import Fraction as F
        for value,option,want in [(F(23888,100000),'在23%到25%之间',True),
            (F(588,1000),'在57%-59%之间',True),(F(3,20),'高于15%但低于20%',False),
            (F(7,39),'高于15%但低于20%',True),(F(1,5),'不高于15%',False),
            (F(15,100),'不高于15%',True),(F(1,2),'25%',False)]:
            assert option_match(value,option)==want,(value,option,want)
        assert numeric('__import__("os").system("echo bad")') is None
        record('numeric_parser_ranges_percent_boundaries_and_no_eval')
        totals=baseline['totals']
    return {'status':'passed','testsPassed':len(results),'tests':results,
            'baselineTotals':totals,'temporaryDirectoryCleaned':not root.exists()}
