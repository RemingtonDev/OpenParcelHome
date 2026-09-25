"""Prepared status/code-permission queries; deliberately no opening operation."""
import asyncio
import struct
import uuid
from .protocol import SERVICE, TX, RX, Reassembler


def _request_id(value):
    if type(value) is not int or not 0 <= value < 8190:
        raise ValueError('Invalid request identifier')
    return value


def status_frame(message_id):
    return struct.pack('>HHH', 0x8000, _request_id(message_id), 0)


def permission_frame(code, message_id):
    if not isinstance(code,str) or not code or len(code)>10 or not code.isascii() or not code.isdecimal() or int(code)>0x7fffffff:
        raise ValueError('Invalid numeric code')
    return struct.pack('>HHHI', 0x8000, _request_id(message_id), 37, int(code))


def acknowledgement_frame(message_id):
    if type(message_id) is not int or not 0 <= message_id <= 0x3fff:
        raise ValueError('Invalid response identifier')
    return struct.pack('>HH', 0x8000, 0x8000 | message_id)


def summarise(operation, message):
    if len(message.body)<2:
        raise ValueError('Missing response status')
    status=int.from_bytes(message.body[-2:],'big',signed=True)
    body=message.body[:-2]
    summary={'operation':operation,'status':status,'data_length':len(body)}
    if status==0 and operation=='permissions':
        if len(body)!=1 or body[0]>3:
            raise ValueError('Unsupported permission response')
        summary['permission']=['none','open-if-empty','always-open','single-open'][body[0]]
    if status==0 and operation=='status':
        if len(body)<3:
            raise ValueError('Truncated box status')
        summary['box_open']=body[2]==1
        if len(body)>=19:
            summary['firmware_integer']=int.from_bytes(body[15:19],'big',signed=True)
    return summary


async def query(client, tx, inbox, frame, request_id, operation):
    # A stale notification is not silently associated with a new command.
    if not inbox.empty():
        raise ValueError('Unexpected queued response')
    await asyncio.wait_for(client.write_gatt_char(tx,frame,response=True),5)
    async def responses():
        ack=await inbox.get()
        if isinstance(ack,Exception): raise ack
        if ack.kind!=2 or ack.message_id!=request_id or ack.body:
            raise ValueError('Expected matching request acknowledgement')
        response=await inbox.get()
        if isinstance(response,Exception): raise response
        if response.kind!=0:
            raise ValueError('Unsupported response kind')
        summary=summarise(operation,response)
        # The box chooses its response ID; do not require equality with request ID.
        await asyncio.wait_for(client.write_gatt_char(tx,acknowledgement_frame(response.message_id),response=True),5)
        return summary
    return await asyncio.wait_for(responses(),10)


async def diagnose(target,code,message_id,finder,client_factory,reserve,*,enabled=False):
    if enabled is not True: raise PermissionError('Diagnostics not enabled')
    target=str(uuid.UUID(target)).upper()
    frames=[status_frame(message_id),permission_frame(code,(message_id+1)%8190)]
    device=await asyncio.wait_for(finder(target,timeout=10),12)
    if device is None or str(uuid.UUID(device.address)).upper()!=target:
        raise RuntimeError('Target unavailable or mismatched')
    client=client_factory(device,timeout=15,pair=False)
    inbox=asyncio.Queue(maxsize=32)
    parser=Reassembler()
    failed=False
    count=0
    report={'diagnostic_dispatch_reserved':False,'queries':[],'cleanup_ok':False}
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
        report['diagnostic_dispatch_reserved']=True
        for index,operation in enumerate(['status','permissions']):
            result=await query(client,chars[TX],inbox,frames[index],(message_id+index)%8190,operation)
            report['queries'].append(result)
            if result['status']!=0: break
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
