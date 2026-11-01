"""Small, asserted fixes following inspection of actual published screenshots."""
from pathlib import Path
root=Path(__file__).resolve().parent
p=root/'index.html';s=p.read_text()
replacements={
    'model.rotation.y=Math.PI;let group=new T.Group();':'model.rotation.y=0;let group=new T.Group();',
    'player.position.set(-11.5,.2,31);':'player.position.set(-11.5,.2,37);',
    'player.position.set(-11.5,0.2,31);':'player.position.set(-11.5,0.2,37);',
    "camYaw=0;camPitch=.12;setWanted(0)}":"camYaw=0;camPitch=.12;setWanted(0);if(hero){animateHuman(hero,'idle');hero.mixer.update(.25);}if(ready){policeUpdate(0);updateHUD();}}",
}
for old,new in replacements.items():
    if old in s:s=s.replace(old,new)
p.write_text(s)
# First frame must show the evaluated idle pose and updated HUD, not an unadvanced T-pose.
for name in ['prepare_and_test.py','publish_verified.py']:
    p=root/name;s=p.read_text()
    s=s.replace("page.click('#play');shot('01_third_person.png')","page.click('#play');ev('CITYBOUND.step(30)');shot('01_third_person.png')")
    s=s.replace("page.click('#play');page.evaluate('CITYBOUND.render()')","page.click('#play');page.evaluate('CITYBOUND.step(30);CITYBOUND.render()')")
    p.write_text(s)
assert 'model.rotation.y=0;let group=new T.Group();' in (root/'index.html').read_text()
assert 'camPitch=.12;setWanted(0);if(hero)' in (root/'index.html').read_text()
print('VISUAL_FIXES avatar facing, spawn separation, evaluated idle, fresh HUD')
