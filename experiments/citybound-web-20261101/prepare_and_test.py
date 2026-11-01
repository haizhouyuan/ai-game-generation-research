"""Bundle licensed game resources and run real-browser checks; no secrets required."""
from pathlib import Path
import hashlib,json,os,subprocess,sys,time,urllib.request,urllib.error
ROOT=Path(__file__).resolve().parent
BASE='https://raw.githubusercontent.com/mrdoob/three.js/r160/'
FILES={
'vendor/three.module.js':BASE+'build/three.module.js',
'vendor/loaders/GLTFLoader.js':BASE+'examples/jsm/loaders/GLTFLoader.js',
'vendor/utils/BufferGeometryUtils.js':BASE+'examples/jsm/utils/BufferGeometryUtils.js',
'vendor/utils/SkeletonUtils.js':BASE+'examples/jsm/utils/SkeletonUtils.js',
'vendor/environments/RoomEnvironment.js':BASE+'examples/jsm/environments/RoomEnvironment.js',
'assets/hero.glb':BASE+'examples/models/gltf/Soldier.glb',
'assets/car.glb':'https://raw.githubusercontent.com/JaronKBragg7337/spectral-gt-rs/main/spectral_gt_rs_game_ready.glb',
'licenses/three-MIT.txt':BASE+'LICENSE',
'licenses/Spectral-GT-RS-CC0.txt':'https://raw.githubusercontent.com/JaronKBragg7337/spectral-gt-rs/main/LICENSE',
'licenses/Spectral-GT-RS-README.md':'https://raw.githubusercontent.com/JaronKBragg7337/spectral-gt-rs/main/README.md',
}
manifest=[]
for path,url in FILES.items():
    p=ROOT/path;p.parent.mkdir(parents=True,exist_ok=True)
    for attempt in range(3):
        try:
            with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'CITYBOUND-build/1.0'}),timeout=90) as response:data=response.read()
            if len(data)<100:raise ValueError('Unexpected tiny resource: '+url)
            p.write_bytes(data);break
        except Exception:
            if attempt==2:raise
            time.sleep(2*(attempt+1))
    if p.suffix=='.glb' and p.read_bytes()[:4]!=b'glTF':raise ValueError('Invalid GLB '+path)
    print('RESOURCE',path,p.stat().st_size,flush=True)
    manifest.append({'path':path,'source':url,'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
(ROOT/'ASSET_MANIFEST.json').write_text(json.dumps(manifest,indent=2))
(ROOT/'THIRD_PARTY_NOTICES.txt').write_text('''CITYBOUND browser prototype — third-party notices

Three.js r160, copyright three.js contributors, MIT. See licenses/three-MIT.txt.
Source: https://github.com/mrdoob/three.js/tree/r160

Character and Idle/Walk/Run animations: Adobe Mixamo Soldier, distributed in the official three.js animation examples. Used solely as an embedded game character, not a standalone asset pack. Adobe permits characters and animations in personal/commercial games. Do not extract for standalone redistribution.
https://helpx.adobe.com/creative-cloud/faq/mixamo-faq.html
https://github.com/mrdoob/three.js/blob/r160/examples/webgl_animation_skinning_blending.html

Car: Spectral GT RS by JaronKBragg7337, CC0 1.0 Universal. See licenses/Spectral-GT-RS-CC0.txt and the retained original README.
https://github.com/JaronKBragg7337/spectral-gt-rs
Changes: scale, orientation, selected paint factors and game police light bars.

Game scene, UI and gameplay: independently authored for this CITYBOUND prototype. No recovery of the deleted original project is claimed. No account system, payments, analytics, or private user content are included.
''')
(ROOT/'robots.txt').write_text('User-agent: *\nDisallow: /\n')
# Browser tests are conducted on the actual HTTP-served build, not mock model objects.
from playwright.sync_api import sync_playwright
EVID=Path.cwd()/'citybound-evidence';EVID.mkdir(exist_ok=True)
server=subprocess.Popen([sys.executable,'-m','http.server','8765','--directory',str(ROOT)],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
time.sleep(1)
results=[];errors=[];failed=[];requests=[]
def record(name,passed,detail=None):
    results.append({'test':name,'passed':bool(passed),'detail':detail});print('CHECK',name,passed,flush=True)
try:
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True,args=['--no-sandbox','--use-angle=swiftshader','--enable-unsafe-swiftshader','--disable-dev-shm-usage'])
        page=browser.new_page(viewport={'width':1280,'height':800},device_scale_factor=1)
        page.on('pageerror',lambda e:errors.append(str(e)))
        page.on('requestfailed',lambda r:failed.append({'url':r.url,'failure':r.failure}))
        page.on('request',lambda r:requests.append(r.url))
        page.goto('http://127.0.0.1:8765/',wait_until='load',timeout=120000)
        page.wait_for_function('window.CITYBOUND && window.CITYBOUND.ready',timeout=150000)
        page.evaluate('window.__STOP_RENDER=true');page.wait_for_timeout(250)
        def ev(s):return page.evaluate(s)
        def state():return ev('CITYBOUND.getState()')
        def shot(name):
            ev('CITYBOUND.render()');page.screenshot(path=str(EVID/name))
        record('Real imported character and animation clips',state()['characterMeshes']>0 and len(state()['animations'])>=3,state())
        shot('00_menu.png');page.click('#play');shot('01_third_person.png')
        a=state()['player'];ev("CITYBOUND.keys.add('KeyW');CITYBOUND.step(120);CITYBOUND.keys.clear()")
        q=state();record('Third-person walking',q['player'][2]<a[2]-4,{'before':a,'after':q['player']})
        ev('CITYBOUND.reset();CITYBOUND.setCamera(Math.PI,0.02)');shot('02_character_front.png')
        ev('CITYBOUND.reset();CITYBOUND.teleport(-9.1,29)');page.keyboard.press('e');record('Enter vehicle',state()['mode']=='drive',state())
        ev('CITYBOUND.setCamera(-.6,.12)');shot('03_vehicle.png')
        ev("CITYBOUND.keys.add('KeyW');CITYBOUND.step(120);CITYBOUND.keys.clear()")
        record('Vehicle accelerates and drives',state()['speed']>10 and state()['car'][2]<20,state())
        page.keyboard.press('e');record('Moving exit is prevented',state()['mode']=='drive')
        ev("CITYBOUND.keys.add('Space');CITYBOUND.step(150);CITYBOUND.keys.clear()")
        page.keyboard.press('e');record('Stop then exit vehicle',state()['mode']=='foot')
        ev('CITYBOUND.start(true)');a=ev('CITYBOUND.cops.map(c=>c.group.position.toArray())');ev('CITYBOUND.step(180)');b=ev('CITYBOUND.cops.map(c=>c.group.position.toArray())');record('Police pursue two-star target',state()['wanted']==2 and a!=b,{'before':a,'after':b})
        ev('CITYBOUND.setCamera(2.5,.16)');shot('04_chase.png')
        ev('CITYBOUND.reset();CITYBOUND.teleport(-163,-146);CITYBOUND.setWanted(1);CITYBOUND.step(600)');record('Garage conceals player and clears wanted',state()['wanted']==0 and state()['player'][1]<-3,state())
        page.keyboard.press('Escape');record('Pause works',state()['paused']);page.click('#resume')
        ev('CITYBOUND.reset();CITYBOUND.setCamera(.2,.10)');shot('05_final.png')
        record('No uncaught JavaScript errors',not errors,errors)
        record('No failed asset requests',not failed,failed)
        record('All runtime resources served from game origin',all(u.startswith(('http://127.0.0.1:8765/','blob:','data:')) for u in requests),requests)
        record('WebGL has no error',ev('CITYBOUND.renderer.getContext().getError()')==0)
        browser.close()
finally:
    server.terminate()
report={'environment':'GitHub Actions Linux, real Chromium with SwiftShader software renderer, 1280x800; screenshots from actual WebGL frames; fixed simulation steps used for repeatable gameplay checks. Not a macOS performance certification.','results':results,'page_errors':errors,'failed_requests':failed}
(EVID/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
if not results or not all(r['passed'] for r in results):raise SystemExit('Browser verification failed; publication stopped')
print('VERIFIED',len(results),'checks passed',flush=True)
