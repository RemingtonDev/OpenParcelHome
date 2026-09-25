"""D4: one fixed-code permission check followed by at most one opening."""
import asyncio
import uuid
from .protocol import SERVICE, TX, RX, Reassembler, opening_frame
from .diagnostics import permission_frame, query


async def checked_open_once(target,code,message_id,finder,client_factory,reserve,*,enabled=False):
    if enabled is not True: raise PermissionError('Checked opening not enabled')
    target=str(uuid.UUID(target)).upper()
    frames=[permission_frame(code,message_id),opening_frame(code,(message_id+1)%8190)]
    device=await asyncio.wait_for(finder(target,timeout=10),12)
    if device is None or str(uuid.UUID(device.address)).upper()!=target:
        raise RuntimeError('Target unavailable or mismatched')
    client=client_factory(device,timeout=15,pair=False)
    inbox=asyncio.Queue(maxsize=32)
    parser=Reassembler()
    failed=False
    count=0
    report={'dispatch_reserved':False,'queries':[],'cleanup_ok':False,
            'opening_write_attempted':False,'outcome':'not-dispatched'}
    subscribed=False
    def notification(sender,data):
        nonlocal failed,count
        if failed: return
        count+=1
        try:
            if count>64: raise ValueError('Too many notifications')
            message=parser.feed(bytes(data))
            if message is not None: inbox.put_nowait(message)
        except (ValueError,TypeError,asyncio.QueueFull):
            failed=True
            while not inbox.empty(): inbox.get_nowait()
            inbox.put_nowait(ValueError('Unsupported notification stream'))
    try:
        await asyncio.wait_for(client.connect(),20)
        service=client.services.get_service(SERVICE)
        if service is None: raise ValueError('Expected service absent')
        chars={c.uuid.lower():c for c in service.characteristics}
        if TX not in chars or RX not in chars or 'write' not in chars[TX].properties or 'notify' not in chars[RX].properties:
            raise ValueError('Expected characteristics absent')
        await asyncio.wait_for(client.start_notify(chars[RX],notification),5)
        subscribed=True
        reserve(target)
        report['dispatch_reserved']=True
        for index,operation in enumerate(['permissions','opening']):
            if failed or parser.buffer or not inbox.empty():
                raise ValueError('Unexpected notification state')
            if operation=='opening':
                report['opening_write_attempted']=True
                report['outcome']='unknown-check-physical-box'
            result=await query(client,chars[TX],inbox,frames[index],(message_id+index)%8190,operation)
            report['queries'].append(result)
            if failed or parser.buffer or not inbox.empty():
                raise ValueError('Unexpected trailing notification state')
            if result['status']!=0: break
            if operation=='permissions' and result.get('permission')!='always-open':
                report['stop_reason']='requires-always-open-permission'
                break
    except Exception as exc:
        report['error_type']=type(exc).__name__
    finally:
        failed=True
        clean=True
        if subscribed:
            try: await asyncio.wait_for(client.stop_notify(chars[RX]),5)
            except Exception: clean=False
        try: await asyncio.wait_for(client.disconnect(),5)
        except Exception: clean=False
        report['cleanup_ok']=clean
    return report
