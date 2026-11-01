"""Publish the verified static game; preserve ownership link encrypted, never in public logs."""
import base64,concurrent.futures,hashlib,json,mimetypes,time,urllib.request
from pathlib import Path
from cryptography.hazmat.primitives import hashes,serialization
from cryptography.hazmat.primitives.asymmetric import padding
ROOT=Path(__file__).resolve().parent
EVID=Path.cwd()/'citybound-evidence';EVID.mkdir(exist_ok=True)
report=json.loads((EVID/'report.json').read_text())
assert report['results'] and all(r['passed'] for r in report['results']),'Refusing to publish unverified build'
PUBLIC_KEY=b'''-----BEGIN PUBLIC KEY-----
MIICIjANBgkqhkiG9w0BAQEFAAOCAg8AMIICCgKCAgEAlgv7vF4F99hqDukbdJci
HwOvghpaduW3VpBOM+83ss8NqU1NLz2kOaOLCP50EHt8y0/c9Sz6DdjTMjTXDXmj
x99ewjf4ETRJD4dghV1i0hTy2QaTHSYWvj+59nmvbUfll87Tl/QHn2pSVFNNOwJs
DPYUqyfCmOvCQTiutt7alWjGAuP0Ix3rafUUzb3oWtm980ji1f7UyZDLS/GG3jnl
ZShH0tte1Wuun0WwMrEBClO2KAEEJhsD8N1ZXESZKPxmenNro6tQcxuikDTGmTpv
k3kXnErrx5tVa98VSEtWV2mSQiXt9zdWAZHSnBG826TewxHICHFIf5sU0ELL0mTK
BKoz7gFoYj1xUH0+pG9A5vATQjZoUikluw0mXRxe9wVApZdMNSnwKT3baRTzdWYM
XjQ7DzQ4QBDs+xlEOXF2aeFuMHOXcdStsd98DlIEZLoxAvLcKc41u0gxoVkSpicF
KUO5DFPIMnV3QEWcjMwgwMCXY2daj1zqYpsGPqWfp70Xc8XkZjqyYNo2fzfwlCyY
McqknZdKIvZc1Ty50s+6ZVYliMuFkjj0CUfh5+iMm+kumqJ/YhqShKczZDp/tOqv
T1fd5ta3WhIvlP/2kLNanBdR5bD/VAKd7gVaGsDKY+1gqB6sDIMyT23c/Ols+H2Z
kZbm1QesnwPcn0jgp9kpz9MCAwEAAQ==
-----END PUBLIC KEY-----'''
def req(url,payload=None,method='GET',headers=None):
    data=json.dumps(payload).encode() if payload is not None else None
    h={'User-Agent':'CITYBOUND-release/1.0','X-HereNow-Client':'chatgpt/direct-api'}
    if data is not None:h['Content-Type']='application/json'
    if headers:h.update(headers)
    with urllib.request.urlopen(urllib.request.Request(url,data=data,headers=h,method=method),timeout=120) as r:
        return json.loads(r.read())
files=[]
for p in sorted(ROOT.rglob('*')):
    if not p.is_file() or p.suffix=='.py' or '__pycache__' in str(p):continue
    ct={'.js':'text/javascript; charset=utf-8','.html':'text/html; charset=utf-8','.glb':'model/gltf-binary','.txt':'text/plain; charset=utf-8','.json':'application/json'}.get(p.suffix,mimetypes.guess_type(p.name)[0] or 'application/octet-stream')
    files.append({'path':p.relative_to(ROOT).as_posix(),'size':p.stat().st_size,'contentType':ct,'hash':hashlib.sha256(p.read_bytes()).hexdigest()})
created=req('https://here.now/api/v1/publish',{'files':files,'displayName':'CITYBOUND · 霓城漫游','displayDescription':'第三人称城市漫游、网格角色与车辆、警方追捕。独立网页试玩版。'},'POST')
claim=created.get('claimUrl','')
if claim:
    pub=serialization.load_pem_public_key(PUBLIC_KEY)
    encrypted=base64.b64encode(pub.encrypt(claim.encode(),padding.OAEP(mgf=padding.MGF1(hashes.SHA256()),algorithm=hashes.SHA256(),label=None))).decode()
else:encrypted=None
handoff={'siteUrl':created['siteUrl'],'expiresAt':created.get('expiresAt'),'encryptedClaimUrl':encrypted,'anonymous':created.get('anonymous',False)}
(EVID/'handoff.json').write_text(json.dumps(handoff,indent=2))
# Only ciphertext is printed; the claim token is a site-ownership credential.
print('HANDOFF_ENCRYPTED',json.dumps(handoff),flush=True)

def upload(item):
    data=(ROOT/item['path']).read_bytes()
    request=urllib.request.Request(item['url'],data=data,headers=item.get('headers',{}),method=item.get('method','PUT'))
    with urllib.request.urlopen(request,timeout=180) as response:
        assert 200<=response.status<300
    print('UPLOADED',item['path'],len(data),flush=True)
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
    list(pool.map(upload,created['upload']['uploads']))
final=req(created['upload']['finalizeUrl'],{'versionId':created['upload']['versionId']},'POST')
assert final.get('success'),final
url=final['siteUrl'];print('PUBLISHED_URL',url,flush=True)
# Check the actual public HTTPS page and gameplay, not merely a deployment status.
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    browser=p.chromium.launch(headless=True,args=['--no-sandbox','--use-angle=swiftshader','--enable-unsafe-swiftshader','--disable-dev-shm-usage'])
    page=browser.new_page(viewport={'width':1280,'height':800})
    errors=[];failed=[]
    page.on('pageerror',lambda e:errors.append(str(e)))
    page.on('requestfailed',lambda r:failed.append({'url':r.url,'failure':r.failure}))
    response=page.goto(url,wait_until='load',timeout=120000)
    assert response and response.status==200
    page.wait_for_function('window.CITYBOUND && window.CITYBOUND.ready',timeout=180000)
    page.evaluate('window.__STOP_RENDER=true');page.wait_for_timeout(300)
    page.click('#play');page.evaluate('CITYBOUND.render()')
    page.screenshot(path=str(EVID/'live_third_person.png'))
    page.evaluate('CITYBOUND.setCamera(Math.PI,.02);CITYBOUND.render()')
    page.screenshot(path=str(EVID/'live_character_front.png'))
    a=page.evaluate('CITYBOUND.getState().player')
    page.keyboard.down('w');page.evaluate('CITYBOUND.step(120)');page.keyboard.up('w')
    b=page.evaluate('CITYBOUND.getState().player')
    assert a!=b,'Public page keyboard movement failed'
    page.evaluate('CITYBOUND.reset();CITYBOUND.teleport(-9.1,29)');page.keyboard.press('e')
    assert page.evaluate('CITYBOUND.getState().mode')=='drive'
    page.evaluate('CITYBOUND.setCamera(-.6,.1);CITYBOUND.render()')
    page.screenshot(path=str(EVID/'live_vehicle.png'))
    page.evaluate('CITYBOUND.start(true);CITYBOUND.step(120);CITYBOUND.setCamera(2.4,.12);CITYBOUND.render()')
    page.screenshot(path=str(EVID/'live_chase.png'))
    assert page.evaluate('CITYBOUND.getState().wanted')==2
    assert not errors and not failed,{'errors':errors,'failed':failed}
    live={'url':url,'httpStatus':response.status,'ready':True,'keyboardMovement':a!=b,'enterCar':True,'twoStarChase':True,'state':page.evaluate('CITYBOUND.getState()'),'pageErrors':errors,'failedRequests':failed,'expiresAt':handoff['expiresAt']}
    (EVID/'live_verification.json').write_text(json.dumps(live,ensure_ascii=False,indent=2))
    print('LIVE_VERIFIED',json.dumps(live,ensure_ascii=False),flush=True)
    browser.close()
