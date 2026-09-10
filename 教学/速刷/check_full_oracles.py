#!/usr/bin/env python3
"""Offline mathematical regressions, not a certificate of full independent double audit.

Run: python 教学/速刷/check_full_oracles.py [--batch national_04] [--json]
Requires Python 3.10+ stdlib, committed intake/shards, and optionally reviews.
Never reads work/raw files or images. Never writes reviews, reports, or bytecode.
Numerical constants/models are frozen snapshots bound to input hashes; changed
stems/options fail closed until a human re-parameterizes the solver. Source
answer fields are never inputs. Extra review fields including displayImages are
accepted; presentation assets are the responsibility of the main build.

New batch: add full_audit/oracles/<batch>.py exposing BATCH and run(ctx), and
problem-only snapshot records in _snapshots.py. The runner discovers it.
Unimplemented batches and subresult-only checks are reported, not passed as solves.
"""
from __future__ import annotations
import sys
sys.dont_write_bytecode=True
if not __debug__:
    raise SystemExit("Oracle assertions must not be disabled: do not use -O/-OO or PYTHONOPTIMIZE.")
import argparse
import importlib.util
import json
import traceback
from pathlib import Path

HERE=Path(__file__).resolve().parent
ORACLES=HERE/'full_audit'/'oracles'
sys.path.insert(0,str(ORACLES))
from _common import Context, serial
from _snapshots import SNAPSHOTS
from _coverage import EXPECTED_CASE_INDICES, REQUIRED_UNIQUE_INDICES

# Expected coverage is intentionally NOT 100 for supplementary source scripts.
# This release baseline detects accidentally dropped cases without inventing checks.
EXPECTED_CASE_ROWS={**{f'national_{i:02}':100 for i in range(1,5)},
    **{f'provincial_{i:02}':100 for i in (1,3,4,5,6)},
    'provincial_02':17,'provincial_07':70,'provincial_08':5}


def execute(audit_dir,batches=None,compare_reviews=True):
    wanted=set(batches or SNAPSHOTS)
    unknown=wanted-set(SNAPSHOTS)
    if unknown:raise ValueError('Unknown batch: '+', '.join(sorted(unknown)))
    results=[]
    for batch in sorted(wanted):
        ctx=None
        try:
            ctx=Context(batch,audit_dir,SNAPSHOTS[batch],compare_reviews)
            path=ORACLES/(batch+'.py')
            if not path.is_file():
                report=ctx.finish();report['status']='not_implemented';results.append(report);continue
            spec=importlib.util.spec_from_file_location('oracle_'+batch,path)
            mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
            assert mod.BATCH==batch
            mod.run(ctx)
            report=ctx.finish()
            expected=EXPECTED_CASE_ROWS.get(batch)
            if expected is not None and report['caseRows']!=expected:
                report['errors'].append({'type':'oracle_coverage_regression','expected':expected,'actual':report['caseRows']})
            actual_indices={c['index'] for c in report['cases']}
            expected_indices=set(EXPECTED_CASE_INDICES.get(batch,actual_indices))
            if actual_indices!=expected_indices:
                report['errors'].append({'type':'oracle_case_set_changed','missing':sorted(expected_indices-actual_indices),'extra':sorted(actual_indices-expected_indices)})
            matched={c['index'] for c in report['cases'] if c['uniqueOptionMatched']}
            lost_matches=set(REQUIRED_UNIQUE_INDICES.get(batch,()))-matched
            if lost_matches:
                report['errors'].append({'type':'unique_option_check_regression','indices':sorted(lost_matches),'uids':[ctx.inputs[i]['uid'] for i in sorted(lost_matches)]})
            report['status']='failed' if report['errors'] else 'passed'
            report['assertionCount']=getattr(ctx,'assertion_count',None)
        except Exception as exc:
            report=ctx.finish() if ctx else {'batch':batch,'cases':[],'errors':[]}
            report['status']='failed';report['errors'].append({'type':'execution_or_input_failure','exception':repr(exc),'traceback':traceback.format_exc()})
        results.append(report)
    metrics=['inputRows','schemaRows','caseRows','computationRows','aliasReuseRows','manualOnlyRows','conditionalComputationRows','propertyOnlyRows','uniqueOptionMatches','reviewAnswersChecked','uncoveredRows','aliasPropertyRows','manualImageComputationRows','patternAssumptionRows','freshReviewAnswersChecked']
    totals={k:sum(r.get(k,0) for r in results) for k in metrics}
    totals['failedBatches']=sum(r['status']=='failed' for r in results)
    totals['pendingBatches']=[r['batch'] for r in results if r['status']=='not_implemented']
    return {'scope':'offline arithmetic/enumeration regression; NOT full-question double audit','boundaries':['schemaRows counts only basic structure, separately from mathematical coverage','computationRows includes conditional models and supplementary subresults; inspect propertyOnlyRows and cases','aliasReuseRows do not count as fresh computations','finite samples cannot prove a unique pattern or a global geometric optimum','snapshots contain manually transcribed effective questions; no image interpretation runs in CI','provincial_02/07 contain only 17/70 supplementary checks; provincial_08 now executes five independently parameterized computations'], 'totals':totals,'batches':results}

def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__,formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--audit-dir',type=Path,default=HERE/'full_audit')
    parser.add_argument('--batch',action='append',help='Repeat for multiple batches; default all submitted batches')
    parser.add_argument('--no-review',action='store_true',help='Compute without review/schema/answer comparison')
    parser.add_argument('--self-test',action='store_true',help='Run isolated offline CI/mutation tests in an automatically cleaned temporary directory')
    parser.add_argument('--require-all-batches',action='store_true',help='Fail if any selected batch lacks an executable oracle module')
    parser.add_argument('--json',action='store_true',help='Full case evidence as JSON on stdout')
    parser.add_argument('--require-complete',action='store_true',help='Fail if any input row lacks an executable computation (including manual/alias rows)')
    args=parser.parse_args(argv)
    if args.self_test:
        from _selftest import run_selftest
        result=run_selftest(Path(__file__).resolve(),args.audit_dir)
        print(json.dumps(result,ensure_ascii=False,indent=2))
        return 0
    try: report=execute(args.audit_dir,args.batch,not args.no_review)
    except Exception as exc:
        print(json.dumps({'error':str(exc)},ensure_ascii=False));return 2
    if args.json:
        print(json.dumps(report,ensure_ascii=False,indent=2,default=serial))
    else:
        print('batch           input schema compute alias manual property option checked uncovered status')
        for r in report['batches']:
            keys=['inputRows','schemaRows','computationRows','aliasReuseRows','manualOnlyRows','propertyOnlyRows','uniqueOptionMatches','reviewAnswersChecked','uncoveredRows']
            print(f"{r['batch']:15}"+' '.join(f'{r.get(k,0):6}' for k in keys)+' '+r['status'])
            for error in r['errors']: print(json.dumps(error,ensure_ascii=False,default=serial))
        print('TOTAL '+json.dumps(report['totals'],ensure_ascii=False))
        print('CAUTION: computed rows include model-dependent/subresult checks; schema completeness is NOT full mathematical double audit.')
    incomplete=report['totals']['computationRows']!=report['totals']['inputRows']
    return int(bool(report['totals']['failedBatches'] or args.require_complete and incomplete or args.require_all_batches and report['totals']['pendingBatches']))

if __name__=='__main__':
    raise SystemExit(main())
