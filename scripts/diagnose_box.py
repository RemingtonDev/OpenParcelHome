#!/usr/bin/env python3
"""Owner-reviewed diagnostic batch. Offline by default; never opens the box."""
import argparse,asyncio,getpass,json,secrets,sys,warnings
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from openparcelhome.diagnostics import diagnose,status_frame,permission_frame
from openparcelhome.experiment import attempt_path,reserve_attempt
from scripts.discover_services import load_target
from scripts.scan_advertisements import save_private


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--execute',action='store_true')
    parser.add_argument('--target-file',type=Path)
    args=parser.parse_args(argv)
    if not args.execute:
        status_frame(123); permission_frame('123456',124)
        print('Offline diagnostic check passed. No radio access or credential input.')
        return 0
    if args.target_file is None or not sys.stdin.isatty():
        parser.error('Live diagnostics need an explicit target file and local interactive Terminal')
    try:
        target=load_target(args.target_file)
        directory=ROOT/'.local'/'diagnostic-attempts'
        if attempt_path(directory,target).exists():
            print('Previous diagnostic batch requires review. Nothing sent.')
            return 1
        print('Two queries: status, then code permission if status succeeds. No opening or configuration changes.')
        print('At most two query writes and two response acknowledgements. Decline unexpected pairing prompts.')
        if input('Type DIAGNOSE ONCE to approve: ')!='DIAGNOSE ONCE': return 1
        with warnings.catch_warnings():
            warnings.simplefilter('error',getpass.GetPassWarning)
            code=getpass.getpass('Existing keypad code (hidden; never saved): ')
        permission_frame(code,0)
        from bleak import BleakClient,BleakScanner
        result=asyncio.run(diagnose(target,code,secrets.randbelow(8190),
            BleakScanner.find_device_by_address,BleakClient,
            lambda selected:reserve_attempt(directory,selected),enabled=True))
        del code
        path=save_private([result],ROOT/'.local'/'diagnostic-results')
        print(json.dumps(result,indent=2)); print(f'Sanitised result: {path}')
        print('Do not repeat. Confirm normal keypad access afterwards.')
        return 0 if len(result['queries'])==2 and result['cleanup_ok'] else 1
    except KeyboardInterrupt:
        print('Interrupted. No automatic retry; check normal keypad access.')
        return 130
    except Exception as exc:
        print(f'Diagnostic stopped ({type(exc).__name__}); no automatic retry.')
        return 1


if __name__=='__main__': raise SystemExit(main())
