"""Apply the approved MuscleLove brand after any existing site build. No network."""
import argparse
from collections import Counter
import hashlib
import json
import os
from pathlib import Path
import re
from bs4 import BeautifulSoup

VERSION = '20261010-network-v1'
ASSETS = '/ai-tool-hub/assets/'
ART = [
    ('musclelove-flex.png', '両腕で力こぶのポーズを取る、筋肉質な架空の日本人成人女性', 1536, 1024),
    ('musclelove-towel.png', 'タオルを頭上に上げる、筋肉質な架空の日本人成人女性', 1536, 1024),
    ('musclelove-stretch.png', '両腕を上げて髪をまとめる、筋肉質な架空の日本人成人女性', 1024, 1536),
]
SKIP = {'.git','node_modules','templates','layouts','themes','scripts','blog_engine','references','.venv','90_旧版'}

def index_for(value):
    return int(hashlib.sha256(value.encode('utf-8')).hexdigest()[:8],16)

def image(soup, art, eager=False):
    name,alt,w,h=art
    return soup.new_tag('img',src=ASSETS+'images/'+name,alt=alt,width=str(w),height=str(h),loading='eager' if eager else 'lazy',decoding='async')

def fragment(text):
    return BeautifulSoup(text,'html.parser')

def article_page(relative,soup):
    return bool({'articles','posts','post'}.intersection(relative.parts) or soup.find('meta',property='og:type',content='article') or soup.select_one('article.post-single') or any(re.search(r'"@type"\s*:\s*"(?:Article|BlogPosting|NewsArticle)"',s.get_text()) for s in soup.find_all('script',type='application/ld+json')))

def _html_candidates(root):
    """全候補の境界を変更前に検査し、リンク経由の読み書きを拒否する。"""
    def checked(path):
        info=path.lstat()
        if path.is_symlink() or getattr(info,'st_file_attributes',0) & 0x400:
            raise ValueError('Linked deployment path is not allowed')
        if not path.resolve().is_relative_to(root):
            raise ValueError('Deployment path escapes root')
        return info
    checked(root)
    report=root/'ml-image-report.json'
    if report.exists() or report.is_symlink():
        info=checked(report)
        if not report.is_file() or info.st_nlink!=1:
            raise ValueError('Invalid deployment report file')
    candidates=[]
    def walk(directory):
        for entry in sorted(os.scandir(directory),key=lambda item:item.name):
            path=Path(entry.path)
            if entry.name in SKIP:
                continue
            info=checked(path)
            if path.is_dir():
                walk(path)
            elif path.suffix=='.html':
                if not path.is_file() or info.st_nlink!=1:
                    raise ValueError('Invalid deployment file')
                candidates.append(path)
    walk(root)
    return candidates


def run(root,project):
    root=Path(root).absolute()
    candidates=_html_candidates(root)
    root=root.resolve()
    if not (root/'index.html').is_file():
        raise ValueError('No index.html; refusing an empty deployment')
    counts=Counter()
    samples=[]
    for path in sorted(candidates):
        relative=path.relative_to(root)
        if SKIP.intersection(relative.parts):
            continue
        original=path.read_text(encoding='utf-8')
        soup=BeautifulSoup(original,'html.parser')
        if not soup.body or not soup.head or not soup.h1:
            continue
        if any(str(m.get('http-equiv','')).lower()=='refresh' for m in soup.find_all('meta')):
            continue
        art=ART[index_for(project+'/'+relative.as_posix())%2]
        for node in soup.select('link[href="/assets/css/visual.css"],script[src="/assets/js/visual.js"]'):
            node.decompose()
        for tag_id,tag,attr,name in [('ml-network-css','link','href','css/network.css'),('ml-network-js','script','src','js/network.js')]:
            existing=soup.find(id=tag_id)
            if existing:
                existing.decompose()
            attrs={'id':tag_id,attr:ASSETS+name}
            attrs.update({'rel':'stylesheet'} if tag=='link' else {'defer':''})
            soup.head.append(soup.new_tag(tag,attrs=attrs))
        soup.body['class']=list(dict.fromkeys(soup.body.get('class',[])+['ml-network-page']))
        soup.body['data-ml-brand']=VERSION
        for node in soup.select('.ml-network-nav,.ml-network-dock,.ml-network-cta'):
            node.decompose()
        soup.body.insert(0,fragment('''<nav class="ml-network-nav" aria-label="MuscleLoveネットワーク"><a class="ml-network-logo" href="/ai-tool-hub/">Muscle<span>Love</span><small>STRONG BODY. CREATIVE MIND.</small></a><a href="/ai-tool-hub/#discover">ほかのブログを探す ↗</a></nav>'''))
        cover=soup.select_one('.ml-project-cover')
        if cover is None:
            cover=soup.new_tag('figure',attrs={'class':'ml-cover ml-project-cover'})
            soup.h1.insert_after(cover)
        cover.clear()
        cover['class']=['ml-cover','ml-project-cover','ml-network-cover']
        cover.append(image(soup,art,eager=True))
        caption=soup.new_tag('figcaption')
        caption.string='MuscleLove / 強く、美しく。つくる力も、鍛えよう。 · 架空の成人女性のAIイラスト'
        cover.append(caption)
        card_selectors='a.article-card,a.card,article.card,article.post-entry,article.article-card,.post-card,.article-item'
        for i,card in enumerate(soup.select(card_selectors)):
            if not card.get_text(strip=True):
                continue
            card_art=ART[(index_for(project)+i)%len(ART)]
            for existing in card.select('img.ml-card-image,img.ml-network-card-image'):
                existing.decompose()
            img=image(soup,card_art)
            img['class']='ml-card-image ml-network-card-image'
            img['alt']=''
            img['data-ml-art']=card_art[0]
            card.insert(0,img)
            card['class']=list(dict.fromkeys(card.get('class',[])+['ml-network-card']))
            counts['cards_with_brand']+=1
        dock=fragment('''<aside class="ml-network-dock" aria-label="MuscleLove"><div class="ml-network-dock-copy"><strong>Muscle<span>Love</span></strong><p>強く、美しく。</p><a href="/ai-tool-hub/">ハブへ ↗</a></div></aside>''')
        dock.aside.insert(0,image(soup,ART[2],eager=True))
        soup.body.append(dock)
        cta=fragment('''<section class="ml-network-cta" aria-label="MuscleLoveの公式案内"><div><small>MUSCLELOVE COMMUNITY</small><h2>筋肉美と、つくる楽しさを。</h2><p>次のヒントも、ここから。</p></div><div><a href="https://x.com/MuscleGirlLove7" target="_blank" rel="noopener">公式X ↗</a><a href="https://www.patreon.com/MuscleLove" target="_blank" rel="noopener">Patreon ↗</a></div></section>''')
        footer=soup.find('footer')
        if footer:
            footer.insert_before(cta)
        else:
            soup.body.append(cta)
        for attr,key in [('property','og:image'),('name','twitter:image')]:
            meta=soup.find('meta',attrs={attr:key})
            if not meta:
                meta=soup.new_tag('meta',attrs={attr:key})
                soup.head.append(meta)
            meta['content']='https://musclelove-777.github.io'+ASSETS+'images/'+art[0]
        for img in soup.select('img[data-ml-fallback]'):
            img['data-ml-fallback']=ASSETS+'images/'+ART[0][0]
        for tag_id in ['ml-network-css','ml-network-js']:
            tag=soup.find(id=tag_id)
            tag.extract()
            soup.head.append(tag)
        counts['pages']+=1
        is_article=article_page(relative,soup)
        counts['articles']+=int(is_article)
        counts['articles_with_image']+=int(is_article and bool(cover.img))
        if is_article and len(samples)<2:
            samples.append(relative.as_posix())
        new=re.sub(r'(<!DOCTYPE[^>]*>)\s*',r'\1\n',str(soup),count=1,flags=re.I)
        if new != original:
            path.write_text(new,encoding='utf-8')
    assert counts['pages'] and counts['articles']==counts['articles_with_image']
    result={'status':'PASS','project':project,'brand_version':VERSION,**counts,'article_samples':samples,'missing':[]}
    (root/'ml-image-report.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    return result

if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--root',required=True,type=Path)
    p.add_argument('--project',required=True)
    args=p.parse_args()
    print(json.dumps(run(args.root,args.project),ensure_ascii=False))
