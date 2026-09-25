#!/usr/bin/env python3
"""D4 checked opening experiment. Offline by default; one opening maximum."""
import argparse,asyncio,getpass,json,secrets,sys,warnings
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from openparcelhome.checked_opening import checked_open_once
from openparcelhome.diagnostics import permission_frame
from openparcelhome.protocol import opening_frame
from openparcelhome.experiment import attempt_path,reserve_attempt
from scripts.discover_services import load_target
from scripts.scan_advertisements import save_private


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--execute',action='store_true')
    parser.add_argument('--target-file',type=Path)
    args=parser.parse_args(argv)
    if not args.execute:
        permission_frame('123456',123); opening_frame('123456',124)
        print('Offline checked-opening check passed. No radio access or credential input.')
        return 0
    if args.target_file is None or not sys.stdin.isatty():
        parser.error('Live checked opening need an explicit target file and local interactive Terminal')
    try:
        target=load_target(args.target_file)
        directory=ROOT/'.local'/'checked-opening-attempts'
        if attempt_path(directory,target).exists():
            print('Previous checked-opening batch requires review. Nothing sent.')
            return 1
        print('One permission query; only ALWAYS_OPEN permits one opening with the same code. No configuration changes.')
        print('At most four writes: permission, its ACK, opening, its ACK. No retry. Be beside your empty, accessible box; verify keypad access first. Decline unexpected pairing prompts.')
        if input('Type CHECK AND OPEN ONCE to approve: ')!='CHECK AND OPEN ONCE': return 1
        with warnings.catch_warnings():
            warnings.simplefilter('error',getpass.GetPassWarning)
            code=getpass.getpass('Existing keypad code (hidden; never saved): ')
        permission_frame(code,0)
        from bleak import BleakClient,BleakScanner
        result=asyncio.run(checked_open_once(target,code,secrets.randbelow(8190),
            BleakScanner.find_device_by_address,BleakClient,
            lambda selected:reserve_attempt(directory,selected),enabled=True))
        del code
        path=save_private([result],ROOT/'.local'/'checked-opening-results')
        print(json.dumps(result,indent=2)); print(f'Sanitised result: {path}')
        print('Check actual door movement and normal keypad access. A zero status is not proof of opening. Do not repeat.')
        return 0 if len(result['queries'])==2 and all(q['status']==0 for q in result['queries']) and result['cleanup_ok'] and 'error_type' not in result else 1
    except KeyboardInterrupt:
        print('Interrupted. No automatic retry; check normal keypad access.')
        return 130
    except Exception as exc:
        print(f'Checked opening stopped ({type(exc).__name__}); no automatic retry.')
        return 1


if __name__=='__main__': raise SystemExit(main())
